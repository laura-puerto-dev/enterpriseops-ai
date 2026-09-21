from contextvars import ContextVar

request_id_var: ContextVar[str | None] = ContextVar(
    "request_id",
    default=None,
)

agent_run_id_var: ContextVar[str | None] = ContextVar(
    "agent_run_id",
    default=None,
)
