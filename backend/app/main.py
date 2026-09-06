from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, entries, spaces, users

app = FastAPI(title="Gyul Days API")


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