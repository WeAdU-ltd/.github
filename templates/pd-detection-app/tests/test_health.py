from pd_detection.app import create_app


def test_health() -> None:
    app = create_app()
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    body = response.get_json()
    assert body is not None
    assert body["status"] == "ok"
    assert body["service"] == "pd-detection"
