import uuid
from sqlalchemy import Column, String, DateTime, func, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db import Base

class RiwayatKlasifikasi(Base):
    __tablename__ = "riwayat_klasifikasi"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)
    image_path = Column(String, nullable=False)
    predicted_class = Column(String, nullable=False) # partially_ripe, ripe, overripe
    confidence = Column(Float, nullable=False)
    model_used = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="history")