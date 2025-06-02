from fastapi import FastAPI
from backend.api import router as api_router

app = FastAPI(title="CV Management API", version="1.0.0")
app.include_router(api_router, prefix="/api", tags=["cv_management"])

@app.get("/")
async def root():
    return {"message": "Welcome to the CV Management API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="localhost", port=8000, log_level="info", reload=True)
    # ^ use string if you still want reload and want to avoid warning
