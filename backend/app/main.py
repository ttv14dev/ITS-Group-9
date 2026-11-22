from fastapi import FastAPI

from app.routers.detection.image_detection import router as image_router

app = FastAPI(
    title="ITS Group 9 API",
    description="Vehicle Detection System"
)

# Kết nối API nhận diện phương tiện
app.include_router(
    image_router,
    prefix="/api/detect",
    tags=["Detection"]
)


@app.get("/")
def home():
    return {
        "message": "ITS Group 9 API is running"
    }