import boto3
import uuid
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from botocore.exceptions import ClientError

router = APIRouter(prefix="/files", tags=["files"])

# Config từ environment variables
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "fastapi-app-files-nhatnt29")
S3_REGION = os.getenv("AWS_REGION", "ap-southeast-2")

s3_client = boto3.client("s3", region_name=S3_REGION)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Tạo unique filename
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"

        # Upload lên S3
        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET,
            unique_filename,
            ExtraArgs={"ContentType": file.content_type}
        )

        # Trả về URL
        file_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{unique_filename}"

        return {
            "message": "File uploaded successfully",
            "filename": unique_filename,
            "original_filename": file.filename,
            "url": file_url
        }
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_files():
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET)
        files = []
        for obj in response.get("Contents", []):
            files.append({
                "filename": obj["Key"],
                "size": obj["Size"],
                "last_modified": str(obj["LastModified"])
            })
        return {"files": files, "count": len(files)}
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))
