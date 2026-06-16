from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from database.connection import get_db
from database.models import Alert, Asset, Base


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()


@pytest.fixture
def client(db_session, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("app.main.init_db", lambda: None)

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@patch("app.api.routes.events.EventsJob")
def test_post_events_run_returns_zero_when_no_events(mock_job_cls: MagicMock, client: TestClient) -> None:
    mock_job_cls.return_value.run.return_value = None

    response = client.post("/events/run")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["message"] is None
    assert payload["events"] == 0


@patch("app.api.routes.events.EventsJob")
def test_post_events_run_returns_message_and_count(mock_job_cls: MagicMock, client: TestClient) -> None:
    mock_job_cls.return_value.run.return_value = (
        "<b>Alerta — Eventos</b>\n\n"
        "• PETR4 anunciou dividendos de R$ 1,25 por ação.\n"
        "  Data-base: 15/08/2026 | Pagamento: 30/08/2026\n"
        "• VALE3 anunciou JCP de R$ 0,80 por ação.\n"
        "  Data-base: 10/08/2026 | Pagamento: 25/08/2026"
    )

    response = client.post("/events/run")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["events"] == 2
    assert "PETR4" in payload["message"]


def test_get_alerts_filters_by_event_alert_type(client: TestClient, db_session) -> None:
    asset = Asset(ticker="PETR4", asset_type="stock")
    db_session.add(asset)
    db_session.flush()

    db_session.add_all(
        [
            Alert(
                asset_id=asset.id,
                alert_type="dividend",
                title="Dividendo PETR4",
                content="conteudo dividend",
                fingerprint="f1",
                created_at=datetime(2026, 6, 16, tzinfo=timezone.utc),
            ),
            Alert(
                asset_id=asset.id,
                alert_type="jcp",
                title="JCP PETR4",
                content="conteudo jcp",
                fingerprint="f2",
                created_at=datetime(2026, 6, 15, tzinfo=timezone.utc),
            ),
            Alert(
                asset_id=asset.id,
                alert_type="price_highlight",
                title="Destaque PETR4",
                content="conteudo preco",
                created_at=datetime(2026, 6, 14, tzinfo=timezone.utc),
            ),
        ]
    )
    db_session.commit()

    response = client.get("/alerts", params={"alert_type": "dividend", "limit": 10})

    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["alert_type"] == "dividend"
    assert items[0]["ticker"] == "PETR4"
    assert items[0]["fingerprint"] == "f1"
