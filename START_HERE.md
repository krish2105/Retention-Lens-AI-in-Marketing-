# FIRST RUN — RetentionLens

**What is ready:** real folder structure, course file, independently usable Work prompts, architecture/research specifications, synthetic CSV, FastAPI+SQLite review endpoints, a functional Next.js dashboard with persistent theme choice, demo domain calculation and Python unit tests.
**What is NOT ready:** customer-ready feature set, ML/DL artifacts, downloaded source datasets, reliable third-party API integration, authenticated multi-tenancy, subscriptions or production deployment.

## Run
```bash
cd services/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
In a **second terminal**:
```bash
cd apps/web
npm install
npm run dev
```
Visit `http://localhost:3000`. If API base URL differs, set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `apps/web/.env.local`.

## Use ChatGPT Work — fresh session, no inherited memory
1. Open project folder as a repo or upload the unzipped folder to your Work environment.
2. Paste **all** of `prompts/00_MASTER_WORK_PROMPT.md`.
3. Ask it to perform only Milestone 0: audit the tree, run tests, verify source-of-truth, write `project/CURRENT_STATE.md` and a reviewed backlog.
4. Continue using the narrower phase prompts in `prompts/`.
5. Before ending every Work session, require it to update `project/CURRENT_STATE.md`, `project/SESSION_LOG.md`, `project/DECISIONS.md`, `project/NEXT_ACTIONS.md` and `project/BLOCKERS.md`.

## Important time and scope constraint
The five projects **share 20 hours/week**. This project receives **4 hours/week under a balanced plan** unless you deliberately change the allocation. From Oct 22 through Nov 9 there are about 2.7 weeks, approximately 54 hours across all five. Read `docs/ROADMAP.md` before promising five fully built products by Nov 10.

## Safety / ownership
The outline is supplied for private course planning. Do not commit it to a public git repository without permission. Demo records are **synthetic** and not proof of business impact. Review `docs/DATA_AND_RESEARCH.md` before real data ingestion.
