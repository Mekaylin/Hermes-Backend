from fastapi import APIRouter, HTTPException, Form
from typing import Optional
from ..background_client import get_background_client

router = APIRouter(prefix='/background', tags=['Background Responses'])


@router.post('/start')
async def start_background(model: str = Form('o3'), input_text: str = Form(...)):
    try:
        client = get_background_client()
        resp = client.create_background_response(model=model, input_text=input_text)
        return {'status': 'ok', 'response': resp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/status/{resp_id}')
async def get_status(resp_id: str):
    try:
        client = get_background_client()
        resp = client.retrieve(resp_id)
        return {'status': 'ok', 'response': resp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/cancel')
async def cancel(resp_id: str = Form(...)):
    try:
        client = get_background_client()
        resp = client.cancel(resp_id)
        return {'status': 'ok', 'response': resp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
