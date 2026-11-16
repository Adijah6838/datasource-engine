import os

def create_mock_file(filename, content, is_json=False):
    os.makedirs("data/samples", exist_ok=True)
    path = f"data/samples/{filename}"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

def test_idempotency_and_validation(client):
    # 1. Create a mock CSV with 2 valid and 1 invalid record
    csv_content = "id,name\n1,Alice\n2,Bob\n,MissingID"
    path = create_mock_file("test_users.csv", csv_content)

    # 2. Register Source
    res = client.post("/sources/", json={
        "name": "Test Source", 
        "source_type": "csv", 
        "config": {"path": path, "id_field": "id"}
    })
    assert res.status_code == 200
    source_id = res.json()["id"]

    # 3. Trigger Job
    res = client.post("/jobs/", json={"source_id": source_id})
    assert res.status_code == 200
    job_id = res.json()["id"]

    # 4. Wait a moment for background task (FastAPI TestClient runs it synchronously)
    # 5. Check Job status
    res = client.get(f"/jobs/{job_id}")
    job = res.json()
    assert job["status"] == "completed"
    assert job["total_processed"] == 2  # Alice, Bob
    assert job["total_rejected"] == 1   # MissingID

    # 6. Trigger the SAME job again to test idempotency
    res = client.post("/jobs/", json={"source_id": source_id})
    job2_id = res.json()["id"]
    
    res = client.get(f"/jobs/{job2_id}")
    job2 = res.json()
    assert job2["status"] == "completed"
    assert job2["total_processed"] == 0  # No duplicates added!

def test_json_parsing(client):
    json_content = '[{"order_id": "1001"}, {"order_id": "1002"}]'
    path = create_mock_file("test_orders.json", json_content, is_json=True)

    res = client.post("/sources/", json={
        "name": "Test JSON", 
        "source_type": "json", 
        "config": {"path": path, "id_field": "order_id"}
    })
    source_id = res.json()["id"]

    res = client.post("/jobs/", json={"source_id": source_id})
    job_id = res.json()["id"]

    res = client.get(f"/jobs/{job_id}")
    assert res.json()["total_processed"] == 2