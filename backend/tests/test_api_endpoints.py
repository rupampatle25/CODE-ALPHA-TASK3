import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.database import Base, engine
from app.models.models import User, MusicProject, GenerationJob, GeneratedAsset, UsageRecord

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield

def test_health_and_root():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["service"] == "Sargam AI API"

        h_res = client.get("/health")
        assert h_res.status_code == 200
        assert h_res.json()["status"] == "healthy"

def test_auth_workflow():
    with TestClient(app) as client:
        email = "producer@example.com"
        # Register
        reg_res = client.post("/api/auth/register", json={
            "email": email,
            "name": "Alex Producer",
            "password": "strongPassword123!"
        })
        assert reg_res.status_code in (201, 400)

        # Login
        login_res = client.post("/api/auth/login", json={
            "email": email,
            "password": "strongPassword123!"
        })
        assert login_res.status_code == 200
        token_data = login_res.json()
        assert "access_token" in token_data
        token = token_data["access_token"]

        # Verify current user
        me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 200
        assert me_res.json()["email"] == email
        assert me_res.json()["credits_balance"] >= 0

def test_billing_plans():
    with TestClient(app) as client:
        res = client.get("/api/billing/plans")
        assert res.status_code == 200
        plans = res.json()
        assert len(plans) == 3
        plan_ids = [p["id"] for p in plans]
        assert "free" in plan_ids
        assert "creator" in plan_ids
        assert "pro" in plan_ids
