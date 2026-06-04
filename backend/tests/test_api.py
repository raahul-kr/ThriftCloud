from fastapi.testclient import TestClient

from app.main import app


def test_login_and_fetch_dashboard_summary() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@thriftcloud.dev", "password": "demo12345"},
        )

        assert login_response.status_code == 200
        payload = login_response.json()
        assert "access_token" in payload

        dashboard_response = client.get(
            "/api/v1/dashboard/summary",
            headers={"Authorization": f"Bearer {payload['access_token']}"},
        )

        assert dashboard_response.status_code == 200
        dashboard = dashboard_response.json()
        assert dashboard["finops_score"] >= 0
        assert dashboard["providers"]
        assert dashboard["active_rule_count"] >= 4
        assert dashboard["recommendations"]

        recommendation_response = client.get(
            "/api/v1/dashboard/recommendations",
            headers={"Authorization": f"Bearer {payload['access_token']}"},
        )
        assert recommendation_response.status_code == 200
        recommendation_payload = recommendation_response.json()
        assert recommendation_payload["total_open"] >= 1
        assert recommendation_payload["active_rule_count"] >= 4
        assert recommendation_payload["items"]
