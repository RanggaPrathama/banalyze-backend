from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.logging import logger
from app.core.dependencies import get_current_user
from app.db import get_db
from app.modules.history_classify.history_classify_schema import HistoryClassifyResponse, HistoryClassifyRequest
from app.modules.history_classify.history_classify_service import HistoryClassifyService
from app.utils.responses import SuccessResponse, success_response


router = APIRouter()


@router.get("", response_model=SuccessResponse[list[HistoryClassifyResponse]])
async def get_all_history(
    page: int = Query(default=1, ge=1),
    paginate: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    order_by: str = Query(default="createdAt"),
    order_type: str = Query(default="DESC", pattern="^(ASC|DESC|asc|desc)$"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = HistoryClassifyService(db)
    histories, total = await service.get_all_history(
        user_id=current_user.id,
        page=page,
        paginate=paginate,
        search=search,
        order_by=order_by,
        order_type=order_type,
    )

    return success_response(
        data=[
            HistoryClassifyResponse(
                id=str(h.id),
                user_id=str(h.user_id),
                title=h.title,
                image_path=h.image_path,
                predicted_class=h.predicted_class,
                confidence=h.confidence,
                model_used=h.model_used,
                created_at=h.created_at,
                updated_at=h.updated_at,
            )
            for h in histories
        ],
        message="History retrieved successfully.",
    )



@router.post("", response_model=SuccessResponse[HistoryClassifyResponse], status_code=status.HTTP_201_CREATED)
async def create_history(
    file: UploadFile = File(...),
    body: HistoryClassifyRequest = Depends(HistoryClassifyRequest.as_form),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
   try:
        logger.info(f"Creating history classify for user_id={current_user.id} with predicted_class={body.predicted_class}")
        logger.debug(f"Received file: filename={file.filename}, content_type={file.content_type}")
        logger.debug(f"Request body: predicted_class={body.predicted_class}, confidence={body.confidence}, model_used={body.model_used}")
        service = HistoryClassifyService(db)
        history = await service.create_history(
            user_id=str(current_user.id),
            image_file=file,
            predicted_class=body.predicted_class,
            confidence=body.confidence,
            model_used=body.model_used,
        )
        logger.info(f"History classify created successfully for user_id={current_user.id} with predicted_class={body.predicted_class}")
        return success_response(
            data=HistoryClassifyResponse(
                id=str(history.id),
                user_id=str(history.user_id),
                title=history.title,
                image_path=history.image_path,
                predicted_class=history.predicted_class,
                confidence=history.confidence,
                model_used=history.model_used,
                created_at=history.created_at,
                updated_at=history.updated_at,
            ),
            message="History created successfully.",
        )
   except Exception as e:
          logger.error(f"Error creating history classify for user_id={current_user.id}: {e}")
          raise e


@router.get("/{history_id}", response_model=SuccessResponse[HistoryClassifyResponse])
async def get_history_by_id(
    history_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = HistoryClassifyService(db)
    history = await service.get_history_by_id(history_id=history_id, user_id=str(current_user.id))

    if not history:
        raise HTTPException(status_code=404, detail="History not found.")

    return success_response(
        data=HistoryClassifyResponse(
            id=str(history.id),
            user_id=str(history.user_id),
            title=history.title,
            image_path=history.image_path,
            predicted_class=history.predicted_class,
            confidence=history.confidence,
            model_used=history.model_used,
            created_at=history.created_at,
            updated_at=history.updated_at,
        ),
        message="History retrieved successfully.",
    )