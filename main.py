# Entry point — kept at root so `uvicorn main:app` and test imports continue to work.
# All application logic lives inside the `app/` package.
from app.main import app  # noqa: F401
from app.core.database import cart  # noqa: F401
