from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routers import auth, notes, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="notes-rbac", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(notes.router)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
