from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db

from src.conf import messages

router = APIRouter(tags=["utils"])


@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    Check the health of the database connection by executing a simple query.

    Args:
        db (AsyncSession): The database session dependency.

    Returns:
        dict: A message indicating the health of the database connection.

    Raises:
        HTTPException: If the database is not accessible or returns an error.
    """
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=messages.DATABASE_ERROR_CONFIG_MESSAGE,
            )
        return {"message": messages.HEALTHCHECKER_MESSAGE}
    
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=messages.DATABASE_ERROR_CONNECT_MESSAGE,
        )