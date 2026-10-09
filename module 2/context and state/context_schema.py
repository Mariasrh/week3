from pydantic import BaseModel
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

class UserContext(BaseModel):
    user_id: str = "USR-9982"
    role: str = "customer"  # "customer" or "staff"
    preferred_language: str = "Spanish"

@tool
def get_user_context(config: RunnableConfig) -> str:
    """Retrieves immutable context information about the user (ID, role, language)."""
    context: UserContext = config.get("configurable", {}).get("context", UserContext())
    return (
        f"User ID: {context.user_id}, "
        f"Role: {context.role}, "
        f"Preferred Language: {context.preferred_language}"
    )