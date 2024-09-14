import os
import time
from typing import Dict, Any
from itsdangerous import TimestampSigner, BadSignature, SignatureExpired


SECRET_KEY = os.getenv('CONTRACT_ANALYSIS_LLM_SECRET')

if not SECRET_KEY:
    raise ValueError('The environment variable CONTRACT_ANALYSIS_LLM_SECRET is not set. Set it to a secure key first.')

SESSION_EXPIRATION = 30 * 60  # Sessions expire after 30 minutes

signer = TimestampSigner(SECRET_KEY)
session_store: Dict[str, Dict[str, Any]] = {}


def create_session() -> str:
    session_id = signer.sign("session").decode()
    session_store[session_id] = {"created_at": time.time(), "data": {}}
    return session_id


def get_session(session_id: str) -> Dict[str, Any]:
    try:
        signer.unsign(session_id, max_age=SESSION_EXPIRATION)
        session = session_store.get(session_id)
        if session and time.time() - session["created_at"] < SESSION_EXPIRATION:
            return session["data"]
        else:
            # Session expired or does not exist
            session_store.pop(session_id, None)
            return {}
    except (BadSignature, SignatureExpired):
        # Invalid or expired session
        session_store.pop(session_id, None)
        return {}


def set_session_data(session_id: str, key: str, value: Any):
    session_data = get_session(session_id)
    session_data[key] = value
    session_store[session_id]["data"] = session_data
