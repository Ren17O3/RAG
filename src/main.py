from fastapi import FastAPI

from src.api.reset import router as reset_router
from src.api.document import router as doc_router

app = FastAPI()

app.include_router(reset_router, prefix="/api", tags=["reset"])
app.include_router(doc_router, prefix="/api", tags=["documents"])
