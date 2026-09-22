from fastapi import FastAPI

from enterpriseops_ai.api.routes import router as ai_router
from enterpriseops_ai.observability.logging import configure_logging
from enterpriseops_ai.observability.middleware import request_context_middleware

configure_logging()
app = FastAPI(
    title="EnterpriseOps AI",
    version="0.1.0",
)

app.middleware("http")(request_context_middleware)

app.include_router(ai_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
