import boto3
import uuid
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".env"))

router = APIRouter(prefix="/files", tags=["files"])

# Config từ environment variables
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "fastapi-app-files-nhatnt29")
S3_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")


def get_s3():
    """Lazy-init boto3 client với credentials đọc trực tiếp từ env tại runtime."""
    key_id = os.getenv("AWS_ACCESS_KEY_ID", "")
    secret = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    region = os.getenv("AWS_REGION", "ap-southeast-2")
    kwargs = {"region_name": region}
    if key_id and secret:
        kwargs["aws_access_key_id"] = key_id
        kwargs["aws_secret_access_key"] = secret
    return boto3.client("s3", **kwargs)


def get_bucket():
    """Đọc tên bucket tại runtime."""
    return os.getenv("S3_BUCKET_NAME", "fastapi-app-files-nhatnt29")


def get_region():
    """Đọc region tại runtime."""
    return os.getenv("AWS_REGION", "ap-southeast-2")


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    bucket = get_bucket()
    region = get_region()
    try:
        # Tạo unique filename
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"

        # Upload lên S3
        s3 = get_s3()
        s3.upload_fileobj(
            file.file,
            bucket,
            unique_filename,
            ExtraArgs={"ContentType": file.content_type}
        )

        # Trả về URL
        file_url = f"https://{bucket}.s3.{region}.amazonaws.com/{unique_filename}"

        return {
            "message": "File uploaded successfully",
            "filename": unique_filename,
            "original_filename": file.filename,
            "url": file_url,
            "bucket": bucket,
        }
    except NoCredentialsError:
        raise HTTPException(
            status_code=503,
            detail="AWS credentials chưa được cấu hình. Kiểm tra AWS_ACCESS_KEY_ID và AWS_SECRET_ACCESS_KEY."
        )
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_files():
    bucket = get_bucket()
    try:
        s3 = get_s3()
        response = s3.list_objects_v2(Bucket=bucket)
        files = []
        for obj in response.get("Contents", []):
            files.append({
                "filename": obj["Key"],
                "size": obj["Size"],
                "last_modified": str(obj["LastModified"])
            })
        return {"files": files, "count": len(files), "bucket": bucket}
    except NoCredentialsError:
        raise HTTPException(
            status_code=503,
            detail="AWS credentials chưa được cấu hình. Kiểm tra AWS_ACCESS_KEY_ID và AWS_SECRET_ACCESS_KEY."
        )
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))
