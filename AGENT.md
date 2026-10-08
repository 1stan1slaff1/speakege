# SpeakEGE — agent context

Web app for Russian students preparing for the English EGE oral exam.
Simulates the exam, records/uploads audio, transcribes via Groq Whisper,
grades via OpenAI GPT-4o-mini with FIPI-style rubrics, feedback in Russian.
Auth (JWT), credits, history, question bank. Payments not yet implemented.

If this file conflicts with code, code wins — then update this file.

## Stack

- Backend: FastAPI in `backend/app`, AI providers in `backend/providers`
  (`transcription/` = Groq Whisper, `grading/` = GPT-4o-mini).
- Frontend: Next.js + React 19 in `frontend/src`.
- DB: PostgreSQL on a VPS. Dev backend connects through an SSH tunnel
  (`ssh -N -L 15432:127.0.0.1:5432 speakegedb`, `DATABASE_URL` in
  `backend/.env`). SQLite is only an optional fallback, not the dev setup.
- Migrations: Alembic. Questions/topics use seeds, not migrations
  (see below).

## Exam format (ЕГЭ 2022+)

| Task | Type | Timing | Max |
|---|---|---|---|
| task1 | read text aloud | 90s prep + 90s | 1 |
| task2 | ask 4 questions (advertisement) | 90s prep + 4x20s | 4 |
| task3 | interview, 5 answers | 5x40s | 5 |
| task4 | voice message, project photos | 150s prep + 180s | 10 |

Total 20. Task1 text is read by the student, never voiced.

## Question bank

- Source of truth: `backend/app/questions/demo_bank.py` — 80 questions
  (20 per task). IDs: `demo_*_001` (first per task), `curated_*_NNN`.
- After ANY bank change: re-run `backend/scripts/seed_demo_questions.py`
  (no Alembic needed) + restart backend. Otherwise the app serves stale DB rows.
- Audio paths come from `Question.audio` (`intro`, `start_cue`,
  `question_cues`, `end`).
- Exam page has a hardcoded fallback (`DEMO_QUESTIONS`) used only when the
  backend question fails to load; its audio paths must match variant01.

## Grading

- Rubrics: `backend/app/rubrics/task1.py` … `task4.py`.
- Evaluate endpoint: `backend/app/api/routes/evaluate.py`.
- Credits (source of truth): `backend/app/billing/credits.py` —
  task1=2, task2=4, task3=5, task4=8; new registered users get 40 free.
  Frontend displays costs from `/api/billing/public`, mirror defaults in
  `frontend/src/config/billing.ts`.

## Prompt audio (current state)

- Baseline: `frontend/public/audio/ege/` — 244 Kokoro mp3
  (`bm_fable`, speed 0.8). Manifest `content/ege_audio_manifest.json`,
  builder `tools/build_ege_audio_manifest.py`.
- OpenAI replacement test: `frontend/public/audio/ege_openai_test/`,
  model `gpt-4o-mini-tts`, voice `fable`, speed 1.0.
  - `tools/generate_openai_audio_variant_b.py` — chunked + concatenated.
    REJECTED: seams are audible.
  - `tools/generate_openai_audio_variant_a.py` — one TTS call per file.
    CHOSEN. Flags: `--variants-per-task N`, `--start-variant M`.
    Dry-run by default; `--generate` spends real money (~$18.7/1M chars).
  - Voice/instructions change ONLY in the script
    (`--voice`, `--instructions` / `DEFAULT_INSTRUCTIONS`).
- Test split in `demo_bank.py` (`audio_root_for_variant`):
  variants 1-2 -> `ege_openai_test`, 3+ -> `ege`.
- Roles: agent runs dry-runs only (no API key, no billing).
  The USER runs `--generate` locally (key in `backend/.env`).

## Pending work (update as it moves)

1. User generates variant-A test (variants 1-2, 28 files, ~$0.08),
   listens in the app, approves quality.
2. User generates the rest (3-20, 220 files, ~$0.62).
3. Migrate `ege_openai_test/` -> `ege/`, remove the test split so all
   variants use OpenAI audio, re-seed, commit.

## Key frontend files

- `frontend/src/app/exam/[taskId]/page.tsx` — exam flow.
- `frontend/src/app/practice/page.tsx` — filter via `?task_type=taskN`.
- `frontend/src/app/learn/` + `frontend/src/config/learn.ts` — materials,
  slugs match `material_url` in `backend/app/feedback/error_topics.py`.
- `frontend/src/config/auth.ts` — token key `speakege_access_token`.

## Workflow with the user

- AI edits `/home/user/speakege`; user downloads the workspace,
  copies needed files from `~/Downloads/speakege` to `~/projects/speakege`
  with `\cp -f`; `mkdir -p` for new dirs.
- Machine uses `python3`, never `python`. Quote `[bracket]` paths in shell.
- Replies in Russian, concise, exact commands, no "changed files" section.
- Selective `git add`, short commit messages. Never commit:
  `.env` files, venvs, `__pycache__`, `*.pyc`, `*.sqlite*`,
  `node_modules`, `.next`.
- README stays minimal: dev commands + short descriptions only.
- Update THIS file when: a user-facing feature is added/changed, a pending
  decision is made, audio/bank/billing logic changes, or this workflow changes.

## Intentional non-features

- Failed attempts are NOT stored (do not re-add).
- Task4 images are SVG placeholders (no real DB-backed images yet).
- No Task1 pronunciation scoring yet.
