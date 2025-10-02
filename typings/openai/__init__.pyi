from typing import Any, Dict, List, Optional

# Module-level convenience API key (some code sets openai.api_key = ...)
api_key: Optional[str]


class Model:
    @staticmethod
    def list(*args, **kwargs) -> Any: ...
    @staticmethod
    def create(*args, **kwargs) -> Any: ...


class ChatCompletion:
    @staticmethod
    def create(*args, **kwargs) -> Any: ...


class _ResponsesClient:
    def create(self, *args, **kwargs) -> Dict[str, Any]: ...
    def retrieve(self, id: str, *args, **kwargs) -> Dict[str, Any]: ...
    def cancel(self, id: str, *args, **kwargs) -> Dict[str, Any]: ...


class OpenAI:
    """Simple typing for the new OpenAI Python client surface used in this repo.

    Supports construction with `api_key=` and exposes a `.responses` client with
    methods `create`, `retrieve`, and `cancel` used by the background client.
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs: Any) -> None: ...

    @property
    def responses(self) -> _ResponsesClient: ...
    @property
    def chat(self) -> Any: ...
    @property
    def vector_stores(self) -> _VectorStoresClient: ...


# Historical top-level convenience variable often present in the openai package
chat: Any
vector_stores: Any


class _ChatCompletionCreateResult:
    choices: List[Dict[str, Any]]


class _ChatChoice:
    message: Dict[str, Any]


class _VectorStoresClient:
    def create(self, *args, **kwargs) -> Dict[str, Any]: ...
    class files:
        @staticmethod
        def upload_and_poll(*args, **kwargs) -> Dict[str, Any]: ...
    def search(self, *args, **kwargs) -> Dict[str, Any]: ...


# Common convenience attribute on the module-level client
vector_stores = _VectorStoresClient()

