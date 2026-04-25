

import math
import random
from datetime import datetime, timezone
from typing import Optional, Tuple, List
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import cast, String, func, asc, desc
from app.models.history_classify import RiwayatKlasifikasi
from app.modules.file_uploads import FileUploadService
from app.modules.history_classify.history_classify_schema import HistoryClassifyResponse

_ORDER_BY_MAP = {
    "createdAt": RiwayatKlasifikasi.created_at,
    "updatedAt": RiwayatKlasifikasi.updated_at,
    "title": RiwayatKlasifikasi.title,
    "predictedClass": RiwayatKlasifikasi.predicted_class,
    "confidence": RiwayatKlasifikasi.confidence,
    "modelUsed": RiwayatKlasifikasi.model_used,
}


class HistoryClassifyService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.file_upload_service = FileUploadService()

    def generate_title(self, dt: Optional[datetime] = None) -> str:
        """Generate a human-friendly scan title based on the time of day."""
        now = dt or datetime.now(timezone.utc)
        hour = now.hour

        if 5 <= hour < 12:
            period = "Morning"
        elif 12 <= hour < 18:
            period = "Afternoon"
        else:
            period = "Evening"

        number = random.randint(1000, 9999)
        return f"Scan {period} #{number}"

    async def get_all_history(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        user_id: Optional[str] = None,
        page: int = 1,
        paginate: int = 20,
        search: Optional[str] = None,
        order_by: str = "createdAt",
        order_type: str = "DESC",
        no_pagination: bool = False,
    ) -> Tuple[List[RiwayatKlasifikasi], int]:
        sort_column = _ORDER_BY_MAP.get(order_by, RiwayatKlasifikasi.created_at)
        sort_direction = desc(sort_column) if order_type.upper() == "DESC" else asc(sort_column)

        base_query = select(RiwayatKlasifikasi)

        if user_id:
            base_query = base_query.where(
                cast(RiwayatKlasifikasi.user_id, String) == str(user_id)
            )

        if search:
            clean_search = search.strip()
            search_term = f"%{clean_search}%"
            class_search_term = f"{clean_search.replace(' ', '_')}%"
            base_query = base_query.where(
                RiwayatKlasifikasi.title.ilike(search_term)
                | RiwayatKlasifikasi.predicted_class.ilike(class_search_term)
            )

        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                base_query = base_query.where(RiwayatKlasifikasi.created_at >= start_dt)
            except ValueError:
                pass  # Invalid date format, ignore the filter

        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                base_query = base_query.where(RiwayatKlasifikasi.created_at <= end_dt)
            except ValueError:
                pass  # Invalid date format, ignore the filter
        if start_date and end_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                if start_dt > end_dt:
                    # Swap if start date is greater than end date
                    start_dt, end_dt = end_dt, start_dt
                base_query = base_query.where(
                    RiwayatKlasifikasi.created_at.between(start_dt, end_dt)
                )
            except ValueError:
                pass  # Invalid date format, ignore the filter
        
        print(f"Debug base_query: {base_query}")
        count_result = await self.db.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = count_result.scalar_one()

        if no_pagination:
            result = await self.db.execute(base_query.order_by(sort_direction))
        else:
            offset = (page - 1) * paginate
            result = await self.db.execute(
                base_query.order_by(sort_direction).offset(offset).limit(paginate)
            )
        items = result.scalars().all()
        # keluarkan datanya untuk debug
        
        # Generator fix: Hilangkan tanda kurung bulat di dalam list
        # print(f"Debug items: {[HistoryClassifyResponse(id=str(item.id), user_id=str(item.user_id), title=item.title, image_path=item.image_path, predicted_class=item.predicted_class, confidence=item.confidence, model_used=item.model_used, created_at=item.created_at, updated_at=item.updated_at) for item in items]}")
        
        return items, total

    async def get_history_by_id(self, history_id: str, user_id: Optional[str] = None) -> Optional[RiwayatKlasifikasi]:
        query = select(RiwayatKlasifikasi).where(
            cast(RiwayatKlasifikasi.id, String) == str(history_id)
        )
        if user_id:
            query = query.where(cast(RiwayatKlasifikasi.user_id, String) == str(user_id))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create_history(
        self,
        user_id: str,
        image_file: UploadFile,
        predicted_class: str,
        confidence: float,
        model_used: str,
    ) -> RiwayatKlasifikasi:
        folder = f"history_classify/{predicted_class}"
        image_url = await self.file_upload_service.upload_image(image_file, folder=folder)

        title = self.generate_title()
        new_history = RiwayatKlasifikasi(
            user_id=user_id,
            title=title,
            image_path=image_url,
            predicted_class=predicted_class,
            confidence=confidence,
            model_used=model_used,
        )
        self.db.add(new_history)
        await self.db.commit()
        await self.db.refresh(new_history)
        return new_history
