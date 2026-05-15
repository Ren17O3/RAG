import os
import shutil
import time

BASE_PATH = "storage/sessions"

MAX_AGE_HOURS = 48


def cleanup_old_sessions():

    now = time.time()

    max_age_seconds = MAX_AGE_HOURS * 3600

    if not os.path.exists(BASE_PATH):
        return

    for session_id in os.listdir(BASE_PATH):

        session_path = os.path.join(BASE_PATH, session_id)

        if not os.path.isdir(session_path):
            continue

        modified_time = os.path.getmtime(session_path)

        age = now - modified_time

        if age > max_age_seconds:

            shutil.rmtree(session_path, ignore_errors=True)
