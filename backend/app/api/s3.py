"""AWS S3 Cloud Storage Router."""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, status

from app.config.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    S3_BUCKET_NAME,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/s3", tags=["s3"])


def get_s3_client():
    """Khởi tạo S3 Client qua boto3 nếu đã cấu hình access key."""
    if not (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY):
        return None
    try:
        import boto3
        return boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        )
    except Exception as exc:
        logger.warning(f"Không thể khởi tạo boto3 S3 client: {exc}")
        return None


@router.get("/status", summary="Kiểm tra trạng thái kết nối AWS S3")
def get_s3_status():
    """Kiểm tra cấu hình biến môi trường AWS S3."""
    is_configured = bool(AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and S3_BUCKET_NAME)
    return {
        "status": "connected" if is_configured else "not_configured",
        "bucket_name": S3_BUCKET_NAME or "Not configured",
        "region": AWS_REGION,
        "credentials_provided": bool(AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY),
    }


@router.post("/upload", status_code=status.HTTP_201_CREATED, summary="Tải file lên AWS S3 Bucket")
async def upload_file_to_s3(file: UploadFile = File(...)):
    """Upload một tập tin lên AWS S3 Bucket đã cấu hình."""
    if not S3_BUCKET_NAME:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Biến môi trường S3_BUCKET_NAME chưa được cấu hình",
        )

    s3_client = get_s3_client()
    if not s3_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY) chưa sẵn sàng",
        )

    try:
        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET_NAME,
            file.filename,
        )
        file_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file.filename}"
        return {
            "message": "Upload file thành công lên AWS S3",
            "bucket": S3_BUCKET_NAME,
            "filename": file.filename,
            "url": file_url,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi upload lên S3: {str(exc)}",
        )


@router.get("/files", summary="Liệt kê danh sách file trên AWS S3")
def list_s3_files(prefix: Optional[str] = ""):
    """Liệt kê danh sách object key trong AWS S3 Bucket."""
    if not S3_BUCKET_NAME:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Biến môi trường S3_BUCKET_NAME chưa được cấu hình",
        )

    s3_client = get_s3_client()
    if not s3_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AWS credentials chưa sẵn sàng",
        )

    try:
        kwargs = {"Bucket": S3_BUCKET_NAME}
        if prefix:
            kwargs["Prefix"] = prefix
        response = s3_client.list_objects_v2(**kwargs)
        contents = response.get("Contents", [])
        files = [item["Key"] for item in contents]
        return {
            "bucket": S3_BUCKET_NAME,
            "file_count": len(files),
            "files": files,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi truy vấn S3 Bucket: {str(exc)}",
        )
