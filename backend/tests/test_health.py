import asyncio
import os
import sys
import pytest

from fastapi.testclient import TestClient

# Ensure project root is on path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import simple_main
app = simple_main.app


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    r = client.get('/health')
    assert r.status_code == 200
    data = r.json()
    assert 'status' in data
    assert data['status'] == 'healthy'
    assert 'redis' in data
