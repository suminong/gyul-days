from fastapi import FastAPI

from app.routers import auth, entries, users

app = FastAPI(title="Gyul Days API")


app.include_router(entries.router)
app.include_router(users.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "Gyul Days API is running"}