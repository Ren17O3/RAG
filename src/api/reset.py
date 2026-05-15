import shutil
import os

from fastapi import APIRouter

router = APIRouter()


@router.delete("/reset-session")
async def reset_session(session_id: str):

    session_path = f"storage/sessions/{session_id}"

    if os.path.exists(session_path):

        shutil.rmtree(session_path)

    return {"status": "success", "message": "Session reset successfully."}
