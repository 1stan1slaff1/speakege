#!/usr/bin/env python3
"""Transcribe OpenAI test mp3s via Groq Whisper and flag ad-libs.

For each final file it compares the transcript with the expected text
(built by the same code as the variant scripts) and reports:
  OK       - transcript starts with the expected opening, no red flags
  FLAG     - opening mismatch and/or the word "sorry" in the transcript
  MISSING  - mp3 file does not exist yet

Default mode is dry-run (lists files, calls nothing).
Add --transcribe to call Groq (uses GROQ_API_KEY from env or backend/.env).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROQ_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
DEFAULT_OUTPUT = ROOT / "content" / "openai_audio_transcript_check.json"


def load_variant_b():
    name = "generate_openai_audio_variant_b"
    path = ROOT / "tools" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


vb = load_variant_b()


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def get_groq_api_key() -> str:
    key = os.environ.get("GROQ_API_KEY")
    if key:
        return key
    values = vb.read_env_file(ROOT / "backend" / ".env")
    key = values.get("GROQ_API_KEY")
    if not key:
        raise SystemExit("GROQ_API_KEY not found. Put it in backend/.env or export it.")
    return key


def encode_multipart(
    fields: dict[str, str],
    file_field: str,
    file_name: str,
    file_bytes: bytes,
    mime: str,
) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    buf = bytearray()

    def add_line(line: str) -> None:
        buf.extend(line.encode("utf-8") + b"\r\n")

    for key, value in fields.items():
        add_line(f"--{boundary}")
        add_line(f'Content-Disposition: form-data; name="{key}"')
        add_line("")
        add_line(value)
    add_line(f"--{boundary}")
    add_line(f'Content-Disposition: form-data; name="{file_field}"; filename="{file_name}"')
    add_line(f"Content-Type: {mime}")
    add_line("")
    buf.extend(file_bytes + b"\r\n")
    add_line(f"--{boundary}--")
    return bytes(buf), boundary


def transcribe(path: Path, api_key: str, timeout: int, max_retries: int) -> str:
    body, boundary = encode_multipart(
        {"model": "whisper-large-v3", "language": "en"},
        "file",
        path.name,
        path.read_bytes(),
        "audio/mpeg",
    )
    last_error: Exception | None = None
    for attempt in range(1, max_retries + 2):
        request = urllib.request.Request(
            GROQ_URL,
            data=body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))["text"]
        except urllib.error.HTTPError as error:
            last_error = RuntimeError(f"Groq {error.code}: {error.read().decode('utf-8', 'replace')[:200]}")
            if error.code not in {408, 409, 429, 500, 502, 503, 504}:
                raise last_error from error
        except (TimeoutError, ConnectionError, urllib.error.URLError) as error:
            last_error = error
        if attempt <= max_retries:
            time.sleep(3.0 * attempt)
    raise RuntimeError(f"Groq failed after {max_retries + 1} attempts: {last_error}") from last_error


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcribe OpenAI test mp3s and flag ad-libs.")
    parser.add_argument("--transcribe", action="store_true", help="Actually call Groq. Default is dry-run.")
    parser.add_argument("--variants-per-task", type=int, default=2)
    parser.add_argument("--start-variant", type=int, default=1)
    parser.add_argument("--head-chars", type=int, default=30, help="Normalized opening chars that must match.")
    parser.add_argument("--only", default="", help="Comma-separated final id substrings to check only, e.g. task4_variant02_intro,task4_variant10_intro.")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--sleep", type=float, default=0.5)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    build_args = argparse.Namespace(
        model=vb.DEFAULT_MODEL,
        voice=vb.DEFAULT_VOICE,
        speed=vb.DEFAULT_SPEED,
        response_format=vb.DEFAULT_RESPONSE_FORMAT,
        instructions=vb.DEFAULT_INSTRUCTIONS,
        variants_per_task=args.variants_per_task,
        start_variant=args.start_variant,
    )
    items = vb.build_final_audio_items(build_args)
    if args.only:
        wanted = [w.strip() for w in args.only.split(",") if w.strip()]
        items = [item for item in items if any(w in item.id for w in wanted)]
    existing = [item for item in items if item.file_path.exists() and item.file_path.stat().st_size > 1024]
    missing = [item for item in items if item not in existing]

    print(f"files: {len(items)}, existing: {len(existing)}, missing: {len(missing)}")
    if not args.transcribe:
        print("Dry-run only. Add --transcribe to call Groq.")
        return

    api_key = get_groq_api_key()
    results = []
    for index, item in enumerate(existing, start=1):
        rel = vb.relative_output_path(item.file_path)
        print(f"[{index}/{len(existing)}] {rel} ...", flush=True)
        try:
            transcript = transcribe(item.file_path, api_key, args.timeout, args.retries)
        except Exception as error:
            results.append({"id": item.id, "file": rel, "status": "ERROR", "error": str(error)[:200]})
            print(f"  ERROR: {error}")
            continue
        expected = vb.normalise_text(" ".join(chunk.text for chunk in item.chunks))
        transcript_norm = norm(transcript)
        expected_norm = norm(expected)
        flags = []
        if "sorry" in transcript_norm:
            flags.append("contains-sorry")
        if not transcript_norm.startswith(expected_norm[: args.head_chars]):
            flags.append("opening-mismatch")
        status = "FLAG" if flags else "OK"
        results.append(
            {
                "id": item.id,
                "file": rel,
                "status": status,
                "flags": flags,
                "expected_head": expected[:120],
                "transcript_head": transcript[:200],
            }
        )
        print(f"  {status} {','.join(flags)} :: {transcript[:100]}")
        if args.sleep:
            time.sleep(args.sleep)

    for item in missing:
        results.append({"id": item.id, "file": vb.relative_output_path(item.file_path), "status": "MISSING"})

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ok_count = sum(1 for r in results if r["status"] == "OK")
    flag_count = sum(1 for r in results if r["status"] == "FLAG")
    print(f"OK: {ok_count}, FLAG: {flag_count}, MISSING/ERROR: {len(results) - ok_count - flag_count}")
    print(f"report: {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
