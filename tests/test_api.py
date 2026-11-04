def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_read_analysis(client):
    payload = {
        "dataset_name": "quarterly-sales",
        "records": [
            {"region": "North", "revenue": 100},
            {"region": "South", "revenue": 500},
            {"region": "West", "revenue": 150},
        ],
    }
    created = client.post("/api/v1/analyses", json=payload)
    assert created.status_code == 201
    body = created.json()
    assert body["record_count"] == 3
    assert body["result"]["numeric_metrics"][0]["field"] == "revenue"
    assert body["result"]["numeric_metrics"][0]["average"] == 250
    assert body["result"]["llm_enhanced"] is False

    fetched = client.get(f"/api/v1/analyses/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["dataset_name"] == "quarterly-sales"


def test_invalid_empty_records(client):
    response = client.post("/api/v1/analyses", json={"dataset_name": "empty", "records": []})
    assert response.status_code == 422


def test_missing_analysis(client):
    response = client.get("/api/v1/analyses/9999")
    assert response.status_code == 404


def test_upload_csv_creates_analysis(client):
    response = client.post(
        "/api/v1/analyses/upload",
        files={
            "file": (
                "sales.csv",
                b"product,revenue,quantity\nLaptop,1299.99,2\nMouse,29.99,5\n",
                "text/csv",
            )
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["dataset_name"] == "sales.csv"
    assert data["record_count"] == 2
    assert data["result"]["record_count"] == 2

    metrics = {metric["field"]: metric for metric in data["result"]["numeric_metrics"]}
    assert metrics["revenue"]["total"] == 1329.98
    assert metrics["quantity"]["total"] == 7


def test_upload_csv_rejects_unsupported_file_type(client):
    response = client.post(
        "/api/v1/analyses/upload",
        files={"file": ("sales.txt", b"some content", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only CSV files are supported."


def test_upload_csv_rejects_invalid_csv(client):
    response = client.post(
        "/api/v1/analyses/upload",
        files={"file": ("sales.csv", b"", "text/csv")},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "The uploaded CSV file is empty."
