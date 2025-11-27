import uuid
from sqlalchemy import String, Float, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from db.database import Base

class Request(Base):
    __tablename__ = "requests"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    input_type: Mapped[str] = mapped_column(String(10))
    input_value: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="received")
    stage: Mapped[str] = mapped_column(String(20), default="received")
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    parsed: Mapped["ParsedPrompt"] = relationship(back_populates="request", uselist=False, cascade="all, delete-orphan")
    result: Mapped["Result"] = relationship(back_populates="request", uselist=False, cascade="all, delete-orphan")

class ParsedPrompt(Base):
    __tablename__ = "request_parsed"
    request_id: Mapped[str] = mapped_column(String, ForeignKey("requests.id"), primary_key=True)
    json_prompt: Mapped[dict] = mapped_column(JSON)
    request: Mapped["Request"] = relationship(back_populates="parsed")

class Result(Base):
    __tablename__ = "results"
    request_id: Mapped[str] = mapped_column(String, ForeignKey("requests.id"), primary_key=True)
    analogs: Mapped[dict] = mapped_column(JSON)
    request: Mapped["Request"] = relationship(back_populates="result")

class SitesCache(Base):
    __tablename__ = "sites_cache"
    site_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    normalized_json_prompt: Mapped[dict] = mapped_column(JSON)
    embedding: Mapped[list | None] = mapped_column(JSON, nullable=True)
    analogs: Mapped[dict] = mapped_column(JSON)
    updated_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
