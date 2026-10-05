# LearnSight AI

LearnSight AI is an AI-assisted early screening platform for potential learning difficulties, including dyslexia and dysgraphia. It is a research/demo prototype, **not a clinical diagnostic tool**.

## Quick start (Windows)

```powershell
# Backend
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The backend API documentation is at `http://localhost:8000/docs`.

Demo login: `admin@learnsight.demo` / `DemoPass123!`

## Architecture

- `frontend/` React + Vite single page application
- `backend/` FastAPI, SQLAlchemy, JWT security, report, OCR/NLP/ML services
- `backend/data/learnsight.db` generated SQLite demo database (or configure MySQL via `DATABASE_URL`)
- `models/` reserved for trained serialized ML/CNN models
- `training/` reproducible ML training/evaluation scripts

## OCR and ML

Tesseract is optional: install it and set `TESSERACT_CMD` in `.env`. The OCR endpoint supplies a helpful error when it is unavailable. The prediction service contains calibrated deterministic demo scoring that is immediately functional; it will load joblib models from `MODEL_DIR` when supplied. Use the training scripts with ethically sourced, consented and clinically reviewed data before any research use.

## Key endpoints

`POST /api/auth/register`, `POST /api/auth/login`, `GET/POST /api/students`, `POST /api/assessments`, `POST /api/upload/handwriting`, `GET /api/dashboard/statistics`, `GET /api/reports/{assessment_id}`.

## Safety and limitations

Scores indicate potential indicators only. Results require professional interpretation and must not be used as a medical diagnosis, admission decision, or to label a child. Demo records are synthetic.
