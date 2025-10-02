from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import os
from ..semantic_search import get_semantic_client

router = APIRouter(prefix="/semantic", tags=["Semantic Retrieval"])


@router.post('/vector-store/create')
async def create_vector_store(name: str = Form(...)):
    try:
        client = get_semantic_client()
        vs = client.create_vector_store(name=name)
        return {"status": "ok", "vector_store": vs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/vector-store/upload')
async def upload_file(vector_store_id: str = Form(...), file: UploadFile = File(...)):
    try:
        client = get_semantic_client()
        # save to temp
        import tempfile
        suffix = os.path.splitext(file.filename)[1] if file.filename else '.txt'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp.flush()
            res = client.upload_file_to_store(vector_store_id=vector_store_id, file_path=tmp.name)
        return {"status": "ok", "result": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/search')
async def search(vector_store_id: str = Form(...), query: str = Form(...), max_results: Optional[int] = Form(10)):
    try:
        client = get_semantic_client()
        res = client.search(vector_store_id=vector_store_id, query=query, max_results=max_results)
        return {"status": "ok", "results": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/synthesize')
async def synthesize(vector_store_id: str = Form(...), query: str = Form(...)):
    try:
        client = get_semantic_client()
        res = client.search(vector_store_id=vector_store_id, query=query)
        # format results
        formatted = ''
        for item in getattr(res, 'data', []) or []:
            formatted += f"<result file_id='{getattr(item, 'file_id', '')}' filename='{getattr(item, 'filename', '')}'>"
            for part in getattr(item, 'content', []):
                formatted += getattr(part, 'text', '')
            formatted += '</result>'

        answer = client.synthesize_with_model(formatted, query)
        return {"status": "ok", "answer": answer, "sources": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
