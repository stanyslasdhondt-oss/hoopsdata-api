# HoopsData API

FastAPI backend for HoopsData: manages basketball matches and their video uploads.

## Install

```bash
git clone <url>
cd hoopsdata-api
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

Create a `.env` file at the root:

```
DATABASE_URL=sqlite:///./hoopsdata.db
APP_ENV=dev
CORS_ORIGINS=["http://localhost:5173"]
```

## Run

```bash
fastapi dev app/main.py
```

Interactive docs: http://127.0.0.1:8000/docs

## Test

```bash
pytest
```

## Note

Object storage is currently mocked: `/upload-url` and `/preview-url` return
placeholder URLs pointing to `fake-storage.local`. Cloudflare R2 will replace
`FakeStorage` in `app/storage.py` without any change to the routes.