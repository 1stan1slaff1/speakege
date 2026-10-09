#!/usr/bin/env python3
"""Generate a small OpenAI TTS test set using reusable chunks.

This is an experiment for SpeakEGE prompt audio.

It generates only the first N variants per task and writes files to:
    frontend/public/audio/ege_openai_test/

The app is not switched to these files automatically. Use them for listening and
comparison first.

Default mode is dry-run. Add --generate to call OpenAI.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import time
import types
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
DEMO_BANK_PATH = ROOT / "backend" / "app" / "questions" / "demo_bank.py"
OUTPUT_ROOT = ROOT / "frontend" / "public" / "audio" / "ege_openai_test"
TEST_MANIFEST_PATH = ROOT / "content" / "ege_openai_test_manifest.json"
CACHE_MANIFEST_PATH = ROOT / "content" / "openai_tts_chunk_cache.json"

DEFAULT_MODEL = "gpt-4o-mini-tts"
DEFAULT_VOICE = "fable"
DEFAULT_RESPONSE_FORMAT = "mp3"
DEFAULT_SPEED = 1.0
DEFAULT_VARIANTS_PER_TASK = 2
OPENAI_SPEECH_URL = "https://api.openai.com/v1/audio/speech"

DEFAULT_INSTRUCTIONS = """Voice Affect: Calm, composed, and reassuring; project quiet authority and confidence.

Tone: Sincere, empathetic, and gently authoritative—express genuine apology while conveying competence.

Pacing: Steady and moderate; unhurried enough to communicate care, yet efficient enough to demonstrate professionalism.

Emotion: Genuine empathy and understanding; speak with warmth, especially during apologies ("I'm very sorry for any disruption...").

Pronunciation: Clear and precise, emphasizing key reassurances ("smoothly," "quickly," "promptly") to reinforce confidence.

Pauses: Brief pauses after offering assistance or requesting details, highlighting willingness to listen and support."""


class FakeQuestionAudio:
    def __init__(self, intro=None, start_cue=None, question_cues=None, end=None):
        self.intro = intro
        self.start_cue = start_cue
        self.question_cues = list(question_cues or [])
        self.end = end


class FakeQuestion:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.id = kwargs["id"]
        self.task_type = kwargs["task_type"]
        self.prompt_text = kwargs["prompt_text"]
        self.grading_prompt_text = kwargs.get("grading_prompt_text")
        self.reference_text = kwargs.get("reference_text")
        self.task2_prompts = list(kwargs.get("task2_prompts") or [])
        self.interviewer_intro = kwargs.get("interviewer_intro")
        self.interview_questions = list(kwargs.get("interview_questions") or [])
        self.audio = kwargs.get("audio")


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str


@dataclass
class FinalAudio:
    id: str
    question_id: str | None
    task_type: str
    role: str
    file_path: Path
    chunks: list[Chunk] = field(default_factory=list)


def normalise_text(text: str) -> str:
    replacements = {
        "1.5 minutes": "one and a half minutes",
        "2.5 minutes": "two and a half minutes",
        "12–15": "twelve to fifteen",
        "1–2": "one or two",
        "—": ", ",
        "–": "-",
        "“": '"',
        "”": '"',
        "’": "'",
        "•": "",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)
    return text


def chunk_id(text: str, *, model: str, voice: str, speed: float, instructions: str, response_format: str) -> str:
    payload = json.dumps(
        {
            "model": model,
            "voice": voice,
            "speed": speed,
            "instructions": instructions,
            "response_format": response_format,
            "text": normalise_text(text),
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def make_chunk(
    name: str,
    text: str,
    *,
    model: str,
    voice: str,
    speed: float,
    instructions: str,
    response_format: str,
) -> Chunk:
    clean = normalise_text(text)
    digest = chunk_id(clean, model=model, voice=voice, speed=speed, instructions=instructions, response_format=response_format)
    safe_name = re.sub(r"[^a-zA-Z0-9_.-]+", "_", name).strip("_")[:70]
    return Chunk(id=f"{safe_name}_{digest}", text=clean)


def relative_output_path(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_demo_bank():
    app_module = types.ModuleType("app")
    models_module = types.ModuleType("app.models")
    schemas_module = types.ModuleType("app.models.schemas")
    schemas_module.Question = FakeQuestion
    schemas_module.QuestionAudio = FakeQuestionAudio
    sys.modules.setdefault("app", app_module)
    sys.modules.setdefault("app.models", models_module)
    sys.modules["app.models.schemas"] = schemas_module

    spec = importlib.util.spec_from_file_location("speakege_demo_bank_for_openai_audio", DEMO_BANK_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {DEMO_BANK_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract_task4_parts(question: FakeQuestion) -> dict[str, str]:
    prompt = question.prompt_text
    project_match = re.search(r"school project [\"“](.+?)[\"”]", prompt)
    advantages_match = re.search(r"mention the advantages \(one or two\) of (.+?);", normalise_text(prompt))
    disadvantages_match = re.search(r"mention the disadvantages \(one or two\) of (.+?);", normalise_text(prompt))
    opinion_match = re.search(r"express your opinion on the subject of the project, (.+?)\. You will speak", normalise_text(prompt))
    # Regex after normalisation may miss the original dash wording; use a fallback.
    if not opinion_match:
        opinion_match = re.search(r"express your opinion on the subject of the project - (.+?)\. You will speak", normalise_text(prompt))

    return {
        "project_title": project_match.group(1) if project_match else "the project",
        "advantages_phrase": advantages_match.group(1) if advantages_match else "the two options shown in the photos",
        "disadvantages_phrase": disadvantages_match.group(1) if disadvantages_match else "the two options shown in the photos",
        "opinion_phrase": opinion_match.group(1) if opinion_match else "say which option you prefer and why",
    }


def build_final_audio_items(args: argparse.Namespace) -> list[FinalAudio]:
    bank = load_demo_bank()
    start_variant = max(1, getattr(args, "start_variant", 1) or 1)
    end_variant = max(start_variant, args.variants_per_task)

    def c(name: str, text: str) -> Chunk:
        return make_chunk(
            name,
            text,
            model=args.model,
            voice=args.voice,
            speed=args.speed,
            instructions=args.instructions,
            response_format=args.response_format,
        )

    chunks = {
        "task1_intro": c(
            "task1_intro",
            "Task 1. You are going to read the text aloud. You have one and a half minutes to read the text silently, then be ready to read it aloud. Remember that you will not have more than one and a half minutes for reading aloud.",
        ),
        "start_reading": c("start_reading", "Now start reading aloud, please."),
        "start_speaking": c("start_speaking", "Now start speaking, please."),
        "interview_end": c("interview_end", "Thank you very much for your interview."),
        "task2_study": c("task2_study", "Task 2. Study the advertisement."),
        "task2_direct_questions": c(
            "task2_direct_questions",
            "In one and a half minutes you are to ask four direct questions to find out about the following.",
        ),
        "task2_20_seconds": c("task2_20_seconds", "You have twenty seconds to ask each question."),
        "task3_intro_first": c("task3_intro_first", "Hello! It's Teenagers Round the World Channel."),
        "task3_intro_last": c("task3_intro_last", "Please answer five questions. So, let's get started."),
        "task4_project_prefix": c(
            "task4_project_prefix",
            "Task 4. Imagine that you and your friend are doing a school project called",
        ),
        "task4_found_photos": c(
            "task4_found_photos",
            "You have found two photos to illustrate it, but for technical reasons you cannot send them now. Leave a voice message to your friend explaining your choice of the photos and sharing some ideas about the project.",
        ),
        "task4_ready": c("task4_ready", "In two and a half minutes, be ready to do the following."),
        "task4_choice": c(
            "task4_choice",
            "Explain the choice of the illustrations for the project by briefly describing them and noting the differences.",
        ),
        "task4_advantages_prefix": c("task4_advantages_prefix", "Mention one or two advantages of"),
        "task4_disadvantages_prefix": c("task4_disadvantages_prefix", "Mention one or two disadvantages of"),
        "task4_opinion_prefix": c("task4_opinion_prefix", "Express your opinion on the subject of the project."),
        "task4_final": c(
            "task4_final",
            "You will speak for not more than three minutes. You have to talk continuously.",
        ),
    }

    items: list[FinalAudio] = []

    # Common and Task 1.
    items.append(FinalAudio("common_start_reading", None, "common", "start_reading", OUTPUT_ROOT / "common" / "start_reading.mp3", [chunks["start_reading"]]))
    items.append(FinalAudio("common_start_speaking", None, "common", "start_speaking", OUTPUT_ROOT / "common" / "start_speaking.mp3", [chunks["start_speaking"]]))
    items.append(FinalAudio("common_interview_end", None, "common", "interview_end", OUTPUT_ROOT / "common" / "interview_end.mp3", [chunks["interview_end"]]))
    items.append(FinalAudio("task1_intro", "task1_shared", "task1", "intro", OUTPUT_ROOT / "task1" / "intro.mp3", [chunks["task1_intro"]]))

    for variant_index, question in enumerate(bank.TASK2_QUESTIONS[start_variant - 1 : end_variant], start=start_variant):
        variant_dir = OUTPUT_ROOT / "task2" / f"variant{variant_index:02d}"
        prompt_list_text = ". ".join(f"{index}. {prompt}" for index, prompt in enumerate(question.task2_prompts, start=1)) + "."
        prompt_blocks = question.prompt_text.split("\n\n")
        title_block = prompt_blocks[1].replace("\n", " ")
        context_full = prompt_blocks[2] if len(prompt_blocks) > 2 else ""
        context_text = context_full.split(" In 1.5 minutes")[0].strip() or "You would like to get more information."
        items.append(
            FinalAudio(
                f"task2_variant{variant_index:02d}_intro",
                question.id,
                "task2",
                "intro",
                variant_dir / "intro.mp3",
                [
                    chunks["task2_study"],
                    c(f"task2_variant{variant_index:02d}_title", title_block),
                    c(f"task2_variant{variant_index:02d}_context", context_text),
                    chunks["task2_direct_questions"],
                    c(f"task2_variant{variant_index:02d}_prompts", prompt_list_text),
                    chunks["task2_20_seconds"],
                ],
            )
        )
        for question_index, prompt in enumerate(question.task2_prompts, start=1):
            items.append(
                FinalAudio(
                    f"task2_variant{variant_index:02d}_q{question_index}",
                    question.id,
                    "task2",
                    f"q{question_index}",
                    variant_dir / f"q{question_index}.mp3",
                    [c(f"task2_q{question_index}_{prompt}", f"Question {question_index}. Ask about {prompt}.")],
                )
            )

    for variant_index, question in enumerate(bank.TASK3_QUESTIONS[start_variant - 1 : end_variant], start=start_variant):
        variant_dir = OUTPUT_ROOT / "task3" / f"variant{variant_index:02d}"
        topic_match = re.search(r"discuss (.+?)\. Please answer", question.interviewer_intro or "")
        topic_text = topic_match.group(1) if topic_match else "this topic"
        items.append(
            FinalAudio(
                f"task3_variant{variant_index:02d}_intro",
                question.id,
                "task3",
                "intro",
                variant_dir / "intro.mp3",
                [
                    chunks["task3_intro_first"],
                    c(f"task3_variant{variant_index:02d}_topic", f"Our guest today is a teenager from Russia, and we are going to discuss {topic_text}."),
                    chunks["task3_intro_last"],
                ],
            )
        )
        for question_index, interview_question in enumerate(question.interview_questions, start=1):
            items.append(
                FinalAudio(
                    f"task3_variant{variant_index:02d}_q{question_index}",
                    question.id,
                    "task3",
                    f"q{question_index}",
                    variant_dir / f"q{question_index}.mp3",
                    [c(f"task3_variant{variant_index:02d}_q{question_index}", f"Question {question_index}. {interview_question}")],
                )
            )

    for variant_index, question in enumerate(bank.TASK4_QUESTIONS[start_variant - 1 : end_variant], start=start_variant):
        variant_dir = OUTPUT_ROOT / "task4" / f"variant{variant_index:02d}"
        parts = extract_task4_parts(question)
        items.append(
            FinalAudio(
                f"task4_variant{variant_index:02d}_intro",
                question.id,
                "task4",
                "intro",
                variant_dir / "intro.mp3",
                [
                    chunks["task4_project_prefix"],
                    c(f"task4_variant{variant_index:02d}_project", f"{parts['project_title']}.") ,
                    chunks["task4_found_photos"],
                    chunks["task4_ready"],
                    chunks["task4_choice"],
                    chunks["task4_advantages_prefix"],
                    c(f"task4_variant{variant_index:02d}_advantages", f"{parts['advantages_phrase']}.") ,
                    chunks["task4_disadvantages_prefix"],
                    c(f"task4_variant{variant_index:02d}_disadvantages", f"{parts['disadvantages_phrase']}.") ,
                    chunks["task4_opinion_prefix"],
                    c(f"task4_variant{variant_index:02d}_opinion", f"{parts['opinion_phrase']}.") ,
                    chunks["task4_final"],
                ],
            )
        )

    return items


def iter_unique_chunks(items: Iterable[FinalAudio]) -> list[Chunk]:
    chunks: dict[str, Chunk] = {}
    for item in items:
        for chunk in item.chunks:
            chunks[chunk.id] = chunk
    return sorted(chunks.values(), key=lambda chunk: chunk.id)


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def get_openai_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key
    env_values = read_env_file(ROOT / "backend" / ".env")
    key = env_values.get("OPENAI_API_KEY")
    if key:
        return key
    raise SystemExit(
        "OPENAI_API_KEY not found. Put it in backend/.env or run: export OPENAI_API_KEY='sk-...'"
    )


def chunk_file_path(chunk: Chunk) -> Path:
    return OUTPUT_ROOT / "_chunks" / f"{chunk.id}.mp3"


def strip_id3v2(data: bytes) -> bytes:
    if len(data) >= 10 and data[:3] == b"ID3":
        size = 0
        for byte in data[6:10]:
            size = (size << 7) | (byte & 0x7F)
        return data[10 + size :]
    return data


def strip_id3v1(data: bytes) -> bytes:
    if len(data) >= 128 and data[-128:-125] == b"TAG":
        return data[:-128]
    return data


def mp3_payload(data: bytes, *, first: bool) -> bytes:
    data = strip_id3v1(data)
    if not first:
        data = strip_id3v2(data)
    return data


def concatenate_mp3(chunk_paths: list[Path], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    parts = []
    for index, path in enumerate(chunk_paths):
        data = path.read_bytes()
        parts.append(mp3_payload(data, first=index == 0))
    output_path.write_bytes(b"".join(parts))


def call_openai_tts(
    *,
    api_key: str,
    text: str,
    model: str,
    voice: str,
    instructions: str,
    response_format: str,
    speed: float,
    timeout: int = 180,
    max_retries: int = 3,
    retry_delay: float = 3.0,
) -> bytes:
    payload = {
        "model": model,
        "voice": voice,
        "input": text,
        "instructions": instructions,
        "response_format": response_format,
        "speed": speed,
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    last_error: Exception | None = None

    for attempt in range(1, max_retries + 2):
        request = urllib.request.Request(
            OPENAI_SPEECH_URL,
            data=data,
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            last_error = RuntimeError(f"OpenAI TTS failed: HTTP {error.code}: {body}")

            # Retry transient API errors/rate limits, fail fast on auth/bad request.
            if error.code not in {408, 409, 429, 500, 502, 503, 504}:
                raise last_error from error
        except (TimeoutError, ConnectionError, urllib.error.URLError) as error:
            last_error = error

        if attempt <= max_retries:
            wait_seconds = retry_delay * attempt
            print(
                f"  retry {attempt}/{max_retries} after {type(last_error).__name__}: {last_error}; "
                f"waiting {wait_seconds:.1f}s",
                flush=True,
            )
            time.sleep(wait_seconds)

    raise RuntimeError(f"OpenAI TTS failed after {max_retries + 1} attempts: {last_error}") from last_error


def write_test_manifest(items: list[FinalAudio], chunks: list[Chunk], args: argparse.Namespace) -> None:
    TEST_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "provider": "openai",
        "model": args.model,
        "voice": args.voice,
        "speed": args.speed,
        "response_format": args.response_format,
        "instructions": args.instructions,
        "variants_per_task": args.variants_per_task,
        "start_variant": getattr(args, "start_variant", 1),
        "final_files": [
            {
                "id": item.id,
                "question_id": item.question_id,
                "task_type": item.task_type,
                "role": item.role,
                "file_path": relative_output_path(item.file_path),
                "chunks": [chunk.id for chunk in item.chunks],
            }
            for item in items
        ],
        "chunks": [
            {
                "id": chunk.id,
                "file_path": relative_output_path(chunk_file_path(chunk)),
                "characters": len(chunk.text),
                "text": chunk.text,
            }
            for chunk in chunks
        ],
    }
    TEST_MANIFEST_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_cache_manifest() -> dict:
    if not CACHE_MANIFEST_PATH.exists():
        return {"chunks": {}}
    return json.loads(CACHE_MANIFEST_PATH.read_text(encoding="utf-8"))


def save_cache_manifest(cache: dict) -> None:
    CACHE_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_MANIFEST_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate OpenAI TTS variant-B audio test files.")
    parser.add_argument("--generate", action="store_true", help="Actually call OpenAI and write audio. Default is dry-run.")
    parser.add_argument("--variants-per-task", type=int, default=DEFAULT_VARIANTS_PER_TASK)
    parser.add_argument("--start-variant", type=int, default=1, help="First variant to generate (1-20). End is --variants-per-task.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--voice", default=DEFAULT_VOICE)
    parser.add_argument("--speed", type=float, default=DEFAULT_SPEED)
    parser.add_argument("--response-format", default=DEFAULT_RESPONSE_FORMAT, choices=["mp3"])
    parser.add_argument("--instructions", default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--force", action="store_true", help="Regenerate chunks even if cached files exist.")
    parser.add_argument("--sleep", type=float, default=0.2, help="Seconds to sleep between OpenAI requests.")
    parser.add_argument("--timeout", type=int, default=180, help="HTTP read timeout per OpenAI request, in seconds.")
    parser.add_argument("--retries", type=int, default=3, help="Retries per chunk for timeouts, rate limits, and 5xx errors.")
    parser.add_argument("--retry-delay", type=float, default=3.0, help="Base retry delay in seconds; multiplied by attempt number.")
    args = parser.parse_args()

    items = build_final_audio_items(args)
    chunks = iter_unique_chunks(items)
    existing_chunks = [chunk for chunk in chunks if chunk_file_path(chunk).exists() and chunk_file_path(chunk).stat().st_size > 1024]
    chunks_to_generate = chunks if args.force else [chunk for chunk in chunks if chunk not in existing_chunks]

    write_test_manifest(items, chunks, args)

    print("OpenAI TTS variant-B test plan")
    print(f"  model: {args.model}")
    print(f"  voice: {args.voice}")
    print(f"  speed: {args.speed}")
    print(f"  response_format: {args.response_format}")
    print(f"  variants_per_task: {args.variants_per_task}")
    print(f"  start_variant: {getattr(args, 'start_variant', 1)}")
    print(f"  final mp3 files: {len(items)}")
    print(f"  unique chunks: {len(chunks)}")
    print(f"  cached chunks: {len(existing_chunks)}")
    print(f"  chunks to generate: {len(chunks_to_generate)}")
    print(f"  characters to send now: {sum(len(chunk.text) for chunk in chunks_to_generate)}")
    print(f"  total unique chunk characters: {sum(len(chunk.text) for chunk in chunks)}")
    print(f"  output root: {relative_output_path(OUTPUT_ROOT)}")
    print(f"  test manifest: {relative_output_path(TEST_MANIFEST_PATH)}")

    if not args.generate:
        print("\nDry-run only. Add --generate to call OpenAI.")
        return

    api_key = get_openai_api_key()
    cache = load_cache_manifest()
    cache.setdefault("chunks", {})

    for index, chunk in enumerate(chunks_to_generate, start=1):
        path = chunk_file_path(chunk)
        path.parent.mkdir(parents=True, exist_ok=True)
        print(f"[{index}/{len(chunks_to_generate)}] generate {relative_output_path(path)} :: {chunk.text[:90]}")
        audio = call_openai_tts(
            api_key=api_key,
            text=chunk.text,
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
        cache["chunks"][chunk.id] = {
            "file_path": relative_output_path(path),
            "characters": len(chunk.text),
            "model": args.model,
            "voice": args.voice,
            "speed": args.speed,
            "response_format": args.response_format,
            "generated_at_unix": int(time.time()),
        }
        save_cache_manifest(cache)
        if args.sleep > 0:
            time.sleep(args.sleep)

    print("Concatenating final files...")
    for item in items:
        concatenate_mp3([chunk_file_path(chunk) for chunk in item.chunks], item.file_path)

    write_test_manifest(items, chunks, args)
    print("Done.")


if __name__ == "__main__":
    main()
