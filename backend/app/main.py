from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.db import engine, Base
from app.api import users, s3, files


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tạo tables tự động khi ứng dụng khởi động
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Could not connect to database at startup: {e}")
    yield


app = FastAPI(
    title="User Management API",
    description="API quản lý người dùng với CI/CD Pipeline GitHub Actions & AWS S3/EC2",
    version="1.0.0",
    lifespan=lifespan,
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký router
app.include_router(users.router)
app.include_router(s3.router)
app.include_router(files.router)


@app.get("/", tags=["root"])
def read_root():
    return {"message": "User Management API đang hoạt động", "docs": "/docs"}


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint cho Docker HEALTHCHECK và Zero-downtime Blue/Green deployment"""
    return {
        "status": "healthy",
        "service": "user-management-api",
        "version": "1.0.0"
    }
