import os
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)


# ---------------------------------------------------------------------------
# ORM
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


class ItemModel(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(500), default="")


Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ItemCreate(BaseModel):
    title: str
    description: str = ""


class ItemRead(BaseModel):
    id: int
    title: str
    description: str

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="DocketLite API", version="0.1.0")


@app.get("/health")
def health():
    """Liveness + optional DB reachability check."""
    result = {"status": "ok"}
    if os.getenv("DATABASE_URL"):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            result["db"] = "ok"
        except Exception as exc:  # noqa: BLE001
            result["db"] = f"unreachable: {exc}"
    return result


@app.get("/items", response_model=List[ItemRead])
def list_items():
    """Return all items."""
    with Session(engine) as session:
        return session.query(ItemModel).all()


@app.post("/items", response_model=ItemRead, status_code=201)
def create_item(payload: ItemCreate):
    """Create a new item."""
    if not payload.title.strip():
        raise HTTPException(status_code=422, detail="title must not be blank")
    with Session(engine) as session:
        item = ItemModel(title=payload.title.strip(), description=payload.description)
        session.add(item)
        session.commit()
        session.refresh(item)
        return item
@app.get("/version")
def version():
    """Return the release tag baked into the image."""
    return {"version": os.getenv("APP_VERSION", "dev")}
