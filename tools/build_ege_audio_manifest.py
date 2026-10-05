#!/usr/bin/env python3
"""Build a manifest of EGE oral exam prompt audio files.

The generated audio is static browser audio for the exam UI. It is intentionally
not the student's answer audio.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO_BANK_PATH = ROOT / "backend" / "app" / "questions" / "demo_bank.py"
MANIFEST_PATH = ROOT / "content" / "ege_audio_manifest.json"


class FakeQuestionAudio:
    def __init__(self, intro=None, start_cue=None, question_cues=None, end=None):
        self.intro = intro
        self.start_cue = start_cue
        self.question_cues = list(question_cues or [])
        self.end = end

    def model_dump(self):
        return {
            "intro": self.intro,
            "start_cue": self.start_cue,
            "question_cues": self.question_cues,
            "end": self.end,
        }


class FakeQuestion:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.grading_prompt_text = kwargs.get("grading_prompt_text")
        self.reference_text = kwargs.get("reference_text")
        self.task2_prompts = list(kwargs.get("task2_prompts") or [])
        self.interviewer_intro = kwargs.get("interviewer_intro")
        self.interview_questions = list(kwargs.get("interview_questions") or [])
        self.audio = kwargs.get("audio")


def load_demo_bank():
    # demo_bank.py imports app.models.schemas. Avoid installing backend deps here:
    # provide just the two small classes that demo_bank needs to instantiate.
    app_module = types.ModuleType("app")
    models_module = types.ModuleType("app.models")
    schemas_module = types.ModuleType("app.models.schemas")
    schemas_module.Question = FakeQuestion
    schemas_module.QuestionAudio = FakeQuestionAudio
    sys.modules.setdefault("app", app_module)
    sys.modules.setdefault("app.models", models_module)
    sys.modules["app.models.schemas"] = schemas_module

    spec = importlib.util.spec_from_file_location("speakege_demo_bank_for_audio", DEMO_BANK_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {DEMO_BANK_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def public_path_to_file(public_path: str) -> str:
    if not public_path.startswith("/audio/"):
        raise ValueError(f"Unexpected public audio path: {public_path}")
    return str(Path("frontend/public") / public_path.lstrip("/"))


def normalise_tts_text(text: str) -> str:
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
    text = re.sub(r"\n\s*\n+", ". ", text)
    text = re.sub(r"\n", ". ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\.\s*\.", ".", text)
    return text


def add_entry(entries: list[dict], *, question_id: str | None, task_type: str, role: str, path: str, text: str):
    entries.append({
        "question_id": question_id,
        "task_type": task_type,
        "role": role,
        "voice": "bm_fable",
        "speed": 0.8,
        "public_path": path,
        "file_path": public_path_to_file(path),
        "text": normalise_tts_text(text),
    })


def main():
    bank = load_demo_bank()
    entries: list[dict] = []

    add_entry(
        entries,
        question_id=None,
        task_type="common",
        role="start_speaking",
        path="/audio/ege/common/start_speaking.mp3",
        text="Now start speaking, please.",
    )
    add_entry(
        entries,
        question_id=None,
        task_type="common",
        role="start_reading",
        path="/audio/ege/common/start_reading.mp3",
        text="Now start reading aloud, please.",
    )
    add_entry(
        entries,
        question_id=None,
        task_type="common",
        role="interview_end",
        path="/audio/ege/common/interview_end.mp3",
        text="Thank you very much for your interview.",
    )
    add_entry(
        entries,
        question_id=None,
        task_type="task1",
        role="intro",
        path="/audio/ege/task1/intro.mp3",
        text=(
            "Task 1. You are going to read the text aloud. "
            "You have one and a half minutes to read the text silently, "
            "then be ready to read it aloud. Remember that you will not have "
            "more than one and a half minutes for reading aloud."
        ),
    )

    for question in bank.ALL_CURATED_QUESTIONS:
        audio = question.audio
        if not audio:
            continue

        if question.task_type == "task1":
            # All Task 1 variants share one instruction and one start cue.
            continue

        if question.task_type == "task2":
            if audio.intro:
                add_entry(
                    entries,
                    question_id=question.id,
                    task_type="task2",
                    role="intro",
                    path=audio.intro,
                    text=question.prompt_text,
                )
            for index, cue_path in enumerate(audio.question_cues, start=1):
                prompt = question.task2_prompts[index - 1]
                add_entry(
                    entries,
                    question_id=question.id,
                    task_type="task2",
                    role=f"q{index}",
                    path=cue_path,
                    text=f"Question {index}. Ask about {prompt}.",
                )

        elif question.task_type == "task3":
            if audio.intro:
                add_entry(
                    entries,
                    question_id=question.id,
                    task_type="task3",
                    role="intro",
                    path=audio.intro,
                    text=question.interviewer_intro or "Task 3. You are going to give an interview.",
                )
            for index, cue_path in enumerate(audio.question_cues, start=1):
                interview_question = question.interview_questions[index - 1]
                add_entry(
                    entries,
                    question_id=question.id,
                    task_type="task3",
                    role=f"q{index}",
                    path=cue_path,
                    text=f"Question {index}. {interview_question}",
                )

        elif question.task_type == "task4":
            if audio.intro:
                add_entry(
                    entries,
                    question_id=question.id,
                    task_type="task4",
                    role="intro",
                    path=audio.intro,
                    text=question.prompt_text,
                )

    # Deduplicate by output path so common files are generated once.
    unique_entries: dict[str, dict] = {}
    for entry in entries:
        unique_entries[entry["file_path"]] = entry

    ordered_entries = sorted(unique_entries.values(), key=lambda item: item["file_path"])
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(ordered_entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {MANIFEST_PATH.relative_to(ROOT)} with {len(ordered_entries)} audio files")


if __name__ == "__main__":
    main()
