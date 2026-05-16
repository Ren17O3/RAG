from fastapi import FastAPI
from src.api.ingest import router as ingest_router
from src.api.query import router as query_router
from src.api.reset import router as reset_router
from src.api.document import router as doc_router

app = FastAPI()

app.include_router(ingest_router, prefix="/api", tags=["ingestion"])
app.include_router(query_router, prefix="/api", tags=["query"])
app.include_router(reset_router, prefix="/api", tags=["reset"])
app.include_router(doc_router, prefix="/api", tags=["documents"])
