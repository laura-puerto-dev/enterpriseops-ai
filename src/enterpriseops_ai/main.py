from fastapi import FastAPI

app = FastAPI(
    title="EnterpriseOps AI",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
