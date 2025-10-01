from fastapi import APIRouter, Query
from typing import List
from ..services.predictor import generate_recommendations

router = APIRouter()


@router.get("")
async def recommendations(category: str = Query('crypto')) -> List[dict]:
    """Return top recommendations for a given category."""
    recs = await generate_recommendations(category)
    return recs
