import os
from typing import Any, Dict
from openai import OpenAI


class BackgroundClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            raise RuntimeError('OPENAI_API_KEY not set')
        self.client = OpenAI(api_key=self.api_key)

    def create_background_response(self, model: str, input_text: str, **kwargs) -> Dict[str, Any]:
        # Per docs, background requires store=True
        payload = {'model': model, 'input': input_text, 'background': True, 'store': True}
        payload.update(kwargs)
        return self.client.responses.create(**payload)

    def retrieve(self, resp_id: str) -> Dict[str, Any]:
        return self.client.responses.retrieve(resp_id)

    def cancel(self, resp_id: str) -> Dict[str, Any]:
        return self.client.responses.cancel(resp_id)


_bg_client: BackgroundClient | None = None


def get_background_client() -> BackgroundClient:
    global _bg_client
    if _bg_client is None:
        _bg_client = BackgroundClient()
    return _bg_client
