from fastapi import APIRouter, Request, HTTPException, Body
import os
import subprocess

router = APIRouter(prefix="/admin", tags=["admin"])


def _is_local(request: Request) -> bool:
    client = request.client
    if not client:
        return False
    host = client.host
    return host.startswith('127.') or host == '::1' or host == 'localhost'


@router.post('/finbert/download')
async def download_finbert(request: Request, payload: dict = Body(default=None)):
    # If ADMIN_TOKEN is set, require it
    admin_token = os.getenv('ADMIN_TOKEN')
    if admin_token:
        header = request.headers.get('x-admin-token')
        if header != admin_token:
            raise HTTPException(status_code=403, detail='invalid admin token')
    else:
        # Only allow local requests when no admin token configured
        if not _is_local(request):
            raise HTTPException(status_code=403, detail='admin token required')

    # Accept body as JSON {"model":"ProsusAI/finbert"}
    model_name = None
    if payload and isinstance(payload, dict):
        model_name = payload.get('model')
    if not model_name:
        model_name = 'ProsusAI/finbert'
    script = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'fetch_finbert.py')
    script = os.path.abspath(script)
    try:
        # Run the script and capture output
        res = subprocess.run(['python3', script, '--model', model_name], check=False, capture_output=True, text=True)
        return {'ok': True, 'returncode': res.returncode, 'stdout': res.stdout, 'stderr': res.stderr}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
