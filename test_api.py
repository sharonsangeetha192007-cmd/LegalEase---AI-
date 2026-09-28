from fastapi.testclient import TestClient

import backend.routes as routes
from backend.main import app


class FakeGenerator:
    model = "test-model"

    def generate_document(self, **kwargs):
        return "# Test Agreement\n\nThis is a mocked document."


def test_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_generate(monkeypatch):
    monkeypatch.setattr(routes, "GeminiDocumentGenerator", FakeGenerator)

    client = TestClient(app)
    response = client.post(
        "/generate",
        json={
            "document_type": "NDA",
            "parties": "A (Discloser), B (Recipient)",
            "terms": "Confidentiality; 15 day termination",
            "effective_date": "2026-09-27",
            "jurisdiction": "India",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["model"] == "test-model"
    assert "Test Agreement" in body["content"]


def test_generate_validation():
    client = TestClient(app)
    response = client.post(
        "/generate",
        json={
            "document_type": "",
            "parties": "A",
            "terms": "B",
            "effective_date": "2026-09-27",
        },
    )
    assert response.status_code == 422
