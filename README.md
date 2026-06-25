## Project paths used in commands

Most commands below assume the repo is here:

```bash
~/projects/speakege
```

If your local path is different, replace it.

---

## Backend: first setup after clone / after `git clean -fdx`

```bash
cd ~/projects/speakege/backend

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create `backend/.env` if missing:

```bash
cat > .env <<'EOF'
APP_NAME=speakege
DATABASE_URL=postgresql://speakege_user:ENCODED_PASSWORD@HOST:5432/speakege
JWT_SECRET=PASTE_RANDOM_SECRET_HERE

FRONTEND_URL=http://localhost:3000

GROQ_API_KEY=your_groq_key_here
OPENAI_API_KEY=your_openai_key_here
EOF
```

For local SQLite instead of PostgreSQL:

```env
DATABASE_URL=sqlite:///./local.db
```

Generate a JWT secret:

```bash
openssl rand -hex 32
```

or:

```bash
python - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
```

If PostgreSQL password has special characters, URL-encode it:

```bash
python - <<'PY'
from urllib.parse import quote
password = input("Password: ")
print(quote(password, safe=""))
PY
```

---

## Backend: migrations

Run from `backend/` with venv activated:

```bash
cd ~/projects/speakege/backend
source .venv/bin/activate

alembic upgrade head
```

Check current migration:

```bash
alembic current
```

Check migration heads:

```bash
alembic heads
```

---

## Backend: run dev server

```bash
cd ~/projects/speakege/backend
source .venv/bin/activate

uvicorn main:app --reload --reload-dir app --reload-dir providers
```

Health check:

```bash
curl http://localhost:8000/api/health
```

---

## Frontend: first setup after clone / after `git clean -fdx`

```bash
cd ~/projects/speakege/frontend

npm ci
```

Create `frontend/.env.local` if missing:

```bash
cat > .env.local <<'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000/api
EOF
```

---

## Frontend: run dev server

```bash
cd ~/projects/speakege/frontend

npm run dev
```

Open:

```text
http://localhost:3000
```

---

## Validation checks

Backend syntax check without creating `__pycache__`:

```bash
cd ~/projects/speakege

python - <<'PY'
from pathlib import Path
import ast

for path in [*Path('backend/app').rglob('*.py'), *Path('backend/providers').rglob('*.py'), *Path('backend/alembic').rglob('*.py'), Path('backend/main.py')]:
    ast.parse(path.read_text(encoding='utf-8'), filename=str(path))

print('backend syntax ast-ok')
PY
```

Frontend checks:

```bash
cd ~/projects/speakege/frontend

npm run lint
npx tsc --noEmit
npm run build
```

---

## Auth test commands

Register:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

Login:

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

User endpoint:

```bash
TOKEN="PASTE_TOKEN_HERE"

curl http://localhost:8000/api/auth/user \
  -H "Authorization: Bearer $TOKEN"
```

---

## Attempts/history test commands

History:

```bash
TOKEN="PASTE_TOKEN_HERE"

curl http://localhost:8000/api/attempts/history \
  -H "Authorization: Bearer $TOKEN"
```

Submission by id:

```bash
curl http://localhost:8000/api/submissions/PASTE_SUBMISSION_ID_HERE
```

---

## Billing/credits commands

Public credit config:

```bash
curl http://localhost:8000/api/billing/public
```

Check latest credit ledger entries:

```bash
cd ~/projects/speakege/backend
source .venv/bin/activate

python - <<'PY'
from sqlalchemy import text
from app.database import engine

with engine.connect() as conn:
    rows = conn.execute(text("""
        SELECT user_id, amount, reason, attempt_id, created_at
        FROM credit_ledger
        ORDER BY created_at DESC
        LIMIT 10
    """)).fetchall()

for row in rows:
    print(row)
PY
```

---

## Manual credit grant script

Use this before real payments exist.

Run from `backend/`:

```bash
cd ~/projects/speakege/backend
source .venv/bin/activate

python scripts/grant_credits.py user@example.com 100 manual_test_grant
```

Arguments:

```text
email   — user email
amount  — positive number of credits to add
reason  — optional ledger reason, default manual_grant
```

Example:

```bash
python scripts/grant_credits.py student@example.com 40 manual_grant
```

The script prints:

```text
User
User ID
Ledger ID
Reason
Granted amount
Balance before -> after
```

It rejects zero and negative amounts.

---

## Evaluate endpoint test

Guest / legacy-style test with `question_id`:

```bash
curl -X POST http://localhost:8000/api/evaluate \
  -F "audio=@samples/audio/task2_clinic_4_of_4.mp3;type=audio/mpeg" \
  -F "question_id=demo_task2_clinic_001"
```

Authenticated test:

```bash
TOKEN="PASTE_TOKEN_HERE"

curl -X POST http://localhost:8000/api/evaluate \
  -H "Authorization: Bearer $TOKEN" \
  -F "audio=@samples/audio/task2_clinic_4_of_4.mp3;type=audio/mpeg" \
  -F "question_id=demo_task2_clinic_001"
```

---

## PostgreSQL inspection commands

Latest attempts:

```bash
cd ~/projects/speakege/backend
source .venv/bin/activate

python - <<'PY'
from sqlalchemy import text
from app.database import engine

with engine.connect() as conn:
    rows = conn.execute(text("""
        SELECT id, user_id, guest_id, task_type, status, total_score, max_score, credit_cost, source, created_at
        FROM attempts
        ORDER BY created_at DESC
        LIMIT 5
    """)).fetchall()

for row in rows:
    print(row)
PY
```

Tables in current DB:

```bash
cd ~/projects/speakege/backend
source .venv/bin/activate

python - <<'PY'
from sqlalchemy import text
from app.database import engine

with engine.connect() as conn:
    rows = conn.execute(text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)).fetchall()

for row in rows:
    print(row[0])
PY
```


---

## Questions table and seed commands

Demo questions are seeded from `backend/app/questions/demo_bank.py` into the DB-backed `questions` table.

Run after migrations:

```bash
cd ~/projects/speakege/backend
source .venv/bin/activate

python scripts/seed_demo_questions.py
```

Check seeded questions:

```bash
cd ~/projects/speakege/backend
source .venv/bin/activate

python - <<'PYCODE'
from sqlalchemy import text
from app.database import engine

with engine.connect() as conn:
    rows = conn.execute(text("""
        SELECT id, task_type, is_demo, is_active, position
        FROM questions
        ORDER BY position, task_type
    """)).fetchall()

for row in rows:
    print(row)
PYCODE
```

Test question endpoint:

```bash
curl http://localhost:8000/api/questions/demo/task2
```

---

## Static audio prompt paths

Static audio lives in:

```text
frontend/public/audio/ege/
```

Example browser URL:

```text
http://localhost:3000/audio/ege/task3/variant01/q1.mp3
```

---

## Git hygiene

Do not commit:

```text
backend/.env
frontend/.env.local
backend/venv
backend/.venv
__pycache__
*.pyc
backend/local.db
*.sqlite
*.sqlite3
node_modules
.next
```

Avoid `git add -A` while generated files are present. Prefer selective `git add`.

Remove tracked Python generated files from Git:

```bash
git ls-files -z \
  | grep -zE '(^|/)(venv|\.venv|__pycache__)(/|$)|\.py[cod]$' \
  | xargs -0 git rm -r --cached -q --ignore-unmatch
```

Then:

```bash
git add .gitignore
git commit -m "Remove generated Python files from git"
```
