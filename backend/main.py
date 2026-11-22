"""Điểm vào của máy chủ. Chạy từ thư mục gốc:  uvicorn backend.main:app --reload"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.app.core import config
from backend.app.routers.detection.router import router as detection_router

app = FastAPI(title="ITS Group 9 API", description="Nhận diện phương tiện ưu tiên")

app.include_router(detection_router)

# Phục vụ giao diện (phải đặt sau các route /api để không che chúng)
app.mount("/", StaticFiles(directory=config.FRONTEND_DIR, html=True), name="frontend")
