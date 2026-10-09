#!/usr/bin/env python3
"""Generate OpenAI TTS audio as whole files (variant A, no concatenation).

Same texts as generate_openai_audio_variant_b.py, but each final mp3 is ONE
OpenAI TTS request. No seams, higher cost (no chunk reuse):

    frontend/public/audio/ege_openai_test/

Default mode is dry-run. Add --generate to call OpenAI.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WHOLE_MANIFEST_PATH = ROOT / "content" / "ege_openai_whole_manifest.json"


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

OUTPUT_ROOT = vb.OUTPUT_ROOT
WHOLE_CACHE_DIR = OUTPUT_ROOT / "_whole"


@dataclass
class WholeFile:
    id: str
    text: str
    cache_id: str
    file_path: Path


def build_whole_files(args: argparse.Namespace) -> list[WholeFile]:
    items = vb.build_final_audio_items(args)
    wholes: list[WholeFile] = []
    for item in items:
        text = vb.normalise_text(" ".join(chunk.text for chunk in item.chunks))
        digest = vb.chunk_id(
            text,
            model=args.model,
            voice=args.voice,
            speed=args.speed,
            instructions=args.instructions,
            response_format=args.response_format,
        )
        wholes.append(WholeFile(item.id, text, f"{item.id}_{digest}", item.file_path))
    return wholes


def cache_path(whole: WholeFile) -> Path:
    return WHOLE_CACHE_DIR / f"{whole.cache_id}.mp3"


def write_whole_manifest(wholes: list[WholeFile], args: argparse.Namespace) -> None:
    WHOLE_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "provider": "openai",
        "mode": "whole-file",
        "model": args.model,
        "voice": args.voice,
        "speed": args.speed,
        "response_format": args.response_format,
        "instructions": args.instructions,
        "variants_per_task": args.variants_per_task,
        "start_variant": args.start_variant,
        "final_files": [
            {
                "id": whole.id,
                "file_path": vb.relative_output_path(whole.file_path),
                "cache_path": vb.relative_output_path(cache_path(whole)),
                "characters": len(whole.text),
                "text": whole.text,
            }
            for whole in wholes
        ],
    }
    WHOLE_MANIFEST_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def is_cached(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 1024


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate OpenAI TTS variant-A (whole file) audio.")
    parser.add_argument("--generate", action="store_true", help="Actually call OpenAI and write audio. Default is dry-run.")
    parser.add_argument("--variants-per-task", type=int, default=vb.DEFAULT_VARIANTS_PER_TASK)
    parser.add_argument("--start-variant", type=int, default=1, help="First variant to generate (1-20). End is --variants-per-task.")
    parser.add_argument("--model", default=vb.DEFAULT_MODEL)
    parser.add_argument("--voice", default=vb.DEFAULT_VOICE)
    parser.add_argument("--speed", type=float, default=vb.DEFAULT_SPEED)
    parser.add_argument("--response-format", default=vb.DEFAULT_RESPONSE_FORMAT, choices=["mp3"])
    parser.add_argument("--instructions", default=vb.DEFAULT_INSTRUCTIONS)
    parser.add_argument("--force", action="store_true", help="Regenerate files even if cached.")
    parser.add_argument("--sleep", type=float, default=0.2, help="Seconds to sleep between OpenAI requests.")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--retry-delay", type=float, default=3.0)
    args = parser.parse_args()

    wholes = build_whole_files(args)
    to_generate = [w for w in wholes if args.force or not is_cached(cache_path(w))]

    write_whole_manifest(wholes, args)

    print("OpenAI TTS variant-A (whole file) plan")
    print(f"  model: {args.model}")
    print(f"  voice: {args.voice}")
    print(f"  speed: {args.speed}")
    print(f"  variants_per_task: {args.variants_per_task}")
    print(f"  start_variant: {args.start_variant}")
    print(f"  final mp3 files: {len(wholes)}")
    print(f"  cached files: {len(wholes) - len(to_generate)}")
    print(f"  files to generate: {len(to_generate)}")
    print(f"  characters to send now: {sum(len(w.text) for w in to_generate)}")
    print(f"  total characters: {sum(len(w.text) for w in wholes)}")
    print(f"  output root: {vb.relative_output_path(OUTPUT_ROOT)}")
    print(f"  whole manifest: {vb.relative_output_path(WHOLE_MANIFEST_PATH)}")

    if not args.generate:
        print("\nDry-run only. Add --generate to call OpenAI.")
        return

    api_key = vb.get_openai_api_key()
    for index, whole in enumerate(to_generate, start=1):
        path = cache_path(whole)
        path.parent.mkdir(parents=True, exist_ok=True)
        print(f"[{index}/{len(to_generate)}] generate {vb.relative_output_path(path)} :: {whole.text[:90]}")
        audio = vb.call_openai_tts(
            api_key=api_key,
            text=whole.text,
            model=args.model,
            voice=args.voice,
            instructions=args.instructions,
            response_format=args.response_format,
            speed=args.speed,
            timeout=args.timeout,
            max_retries=args.retries,
            retry_delay=args.retry_delay,
        )
        path.write_bytes(audio)
        if args.sleep > 0:
            time.sleep(args.sleep)

    print("Copying cache to final files...")
    for whole in wholes:
        whole.file_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(cache_path(whole), whole.file_path)

    write_whole_manifest(wholes, args)
    print("Done.")


if __name__ == "__main__":
    main()
