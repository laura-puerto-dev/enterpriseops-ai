from fastapi import FastAPI

from enterpriseops_ai.api.routes import router as ai_router

app = FastAPI(
    title="EnterpriseOps AI",
    version="0.1.0",
)

app.include_router(ai_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
