from datetime import datetime, timezone
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Gyul Days API")

class EntryCreate(BaseModel):
    content: str

class Entry(BaseModel):
    id: int
    content: str
    created_at: datetime

entries = []

@app.get("/")
def root():
    return {"message": "Gyul Days API is running"}

@app.post("/entries", response_model=Entry, status_code=201)
def create_entry(entry: EntryCreate):

    new_entry = Entry(
        id=len(entries) + 1,
        content=entry.content,
        created_at=datetime.now(timezone.utc),
    )

    entries.append(new_entry)

    return new_entry


@app.get("/entries", response_model=list[Entry])
def get_entries():
    return entries