"""Unit tests for AWS S3 endpoints."""
import io


def test_s3_status_unconfigured(client):
    """Kiểm tra endpoint /s3/status phản hồi 200 ngay cả khi chưa kết nối AWS."""
    response = client.get("/s3/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "region" in data
    assert "credentials_provided" in data


def test_s3_upload_missing_bucket(client, monkeypatch):
    """Upload thất bại nếu S3_BUCKET_NAME rỗng."""
    from app.api import s3
    monkeypatch.setattr(s3, "S3_BUCKET_NAME", "")

    file_content = b"sample test file content"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    response = client.post("/s3/upload", files=files)
    assert response.status_code == 400
    assert "S3_BUCKET_NAME chưa được cấu hình" in response.json()["detail"]


def test_s3_upload_missing_credentials(client, monkeypatch):
    """Upload thất bại nếu credentials chưa được cung cấp."""
    from app.api import s3
    monkeypatch.setattr(s3, "S3_BUCKET_NAME", "my-test-bucket")
    monkeypatch.setattr(s3, "get_s3_client", lambda: None)

    file_content = b"sample test file content"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    response = client.post("/s3/upload", files=files)
    assert response.status_code == 503
    assert "AWS credentials" in response.json()["detail"]


def test_s3_upload_success_mock(client, monkeypatch):
    """Giả lập upload thành công khi có mock client."""
    from app.api import s3

    class MockS3Client:
        def upload_fileobj(self, fileobj, bucket, key):
            pass

    monkeypatch.setattr(s3, "S3_BUCKET_NAME", "my-test-bucket")
    monkeypatch.setattr(s3, "AWS_REGION", "ap-southeast-1")
    monkeypatch.setattr(s3, "get_s3_client", lambda: MockS3Client())

    file_content = b"hello from devops test"
    files = {"file": ("avatar.png", io.BytesIO(file_content), "image/png")}
    response = client.post("/s3/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "avatar.png"
    assert data["bucket"] == "my-test-bucket"
    assert "https://my-test-bucket.s3.ap-southeast-1.amazonaws.com/avatar.png" in data["url"]


def test_s3_list_files_mock(client, monkeypatch):
    """Giả lập lấy danh sách file thành công."""
    from app.api import s3

    class MockS3Client:
        def list_objects_v2(self, **kwargs):
            return {"Contents": [{"Key": "avatar.png"}, {"Key": "doc.pdf"}]}

    monkeypatch.setattr(s3, "S3_BUCKET_NAME", "my-test-bucket")
    monkeypatch.setattr(s3, "get_s3_client", lambda: MockS3Client())

    response = client.get("/s3/files")
    assert response.status_code == 200
    data = response.json()
    assert data["bucket"] == "my-test-bucket"
    assert data["file_count"] == 2
    assert "avatar.png" in data["files"]
