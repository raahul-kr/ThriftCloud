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


def test_recommendation_lifecycle_actions() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@thriftcloud.dev", "password": "demo12345"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        recommendations_response = client.get("/api/v1/dashboard/recommendations", headers=headers)
        assert recommendations_response.status_code == 200
        recommendation_id = recommendations_response.json()["items"][0]["id"]

        acknowledge_response = client.patch(
            f"/api/v1/dashboard/recommendations/{recommendation_id}",
            headers=headers,
            json={"action": "acknowledge"},
        )
        assert acknowledge_response.status_code == 200
        acknowledge_payload = acknowledge_response.json()
        assert acknowledge_payload["message"] == "Recommendation acknowledged"
        assert acknowledge_payload["item"]["acknowledged_at"] is not None

        assign_response = client.patch(
            f"/api/v1/dashboard/recommendations/{recommendation_id}",
            headers=headers,
            json={"action": "assign_owner", "assigned_owner": "FinOps Team"},
        )
        assert assign_response.status_code == 200
        assert assign_response.json()["item"]["assigned_owner"] == "FinOps Team"

        dismiss_response = client.patch(
            f"/api/v1/dashboard/recommendations/{recommendation_id}",
            headers=headers,
            json={"action": "dismiss"},
        )
        assert dismiss_response.status_code == 200
        assert dismiss_response.json()["item"]["status"] == "dismissed"

        recommendations_after_dismiss = client.get("/api/v1/dashboard/recommendations", headers=headers)
        dismissed_ids = {item["id"] for item in recommendations_after_dismiss.json()["items"]}
        assert recommendation_id not in dismissed_ids


def test_viewer_cannot_assign_recommendation_owner() -> None:
    with TestClient(app) as client:
        admin_login = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@thriftcloud.dev", "password": "demo12345"},
        )
        admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
        recommendation_id = client.get("/api/v1/dashboard/recommendations", headers=admin_headers).json()["items"][0]["id"]

        viewer_login = client.post(
            "/api/v1/auth/login",
            json={"email": "viewer@thriftcloud.dev", "password": "demo12345"},
        )
        viewer_headers = {"Authorization": f"Bearer {viewer_login.json()['access_token']}"}

        assign_response = client.patch(
            f"/api/v1/dashboard/recommendations/{recommendation_id}",
            headers=viewer_headers,
            json={"action": "assign_owner", "assigned_owner": "Viewer Team"},
        )
        assert assign_response.status_code == 403


def test_forecast_and_anomaly_endpoints() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@thriftcloud.dev", "password": "demo12345"},
        )
        headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

        forecast_response = client.get("/api/v1/dashboard/forecast", headers=headers)
        assert forecast_response.status_code == 200
        forecast_payload = forecast_response.json()
        assert forecast_payload["history"]
        assert forecast_payload["forecast"]
        assert forecast_payload["method"] == "deterministic_trend_extrapolation"

        anomaly_response = client.get("/api/v1/dashboard/anomalies", headers=headers)
        assert anomaly_response.status_code == 200
        anomaly_payload = anomaly_response.json()
        assert "items" in anomaly_payload
        assert anomaly_payload["scanned_points"] >= 1
