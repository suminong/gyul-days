from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, entries, spaces, users
from pathlib import Path
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Gyul Days API")
BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

UPLOAD_DIR = (
    BASE_DIR / "uploads"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


app.mount(
    "/uploads",
    StaticFiles(
        directory=str(
            UPLOAD_DIR
        )
    ),
    name="uploads",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_methods=[
        "GET",
        "POST",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
    ],
)


app.include_router(entries.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(spaces.router)

@app.get("/")
def root():
    return {"message": "Gyul Days API is running"}