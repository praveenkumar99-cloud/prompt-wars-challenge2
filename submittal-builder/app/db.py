"""Database Access Layer (Firestore / In-Memory Fallback)"""
from datetime import datetime
from typing import Dict, Any, Optional
import logging
from .config import config

logger = logging.getLogger(__name__)

# Fallback in-memory store
_local_job_store = {}

def _get_firestore_client():
    if config.USE_GCP_SERVICES:
        try:
            from google.cloud import firestore
            return firestore.Client(project=config.GCP_PROJECT) if config.GCP_PROJECT else firestore.Client()
        except Exception as e:
            logger.warning(f"Failed to initialize Firestore: {e}")
    return None

def save_job(job_id: str, job_data: dict):
    """Save or update job data"""
    db = _get_firestore_client()
    if db:
        try:
            doc_ref = db.collection(config.GCP_FIRESTORE_COLLECTION).document(job_id)
            doc_ref.set(job_data, merge=True)
            return
        except Exception as e:
            logger.warning(f"Firestore save failed: {e}")
    
    # Fallback
    if job_id not in _local_job_store:
        _local_job_store[job_id] = {}
    _local_job_store[job_id].update(job_data)

def get_job(job_id: str) -> Optional[dict]:
    """Retrieve job data"""
    db = _get_firestore_client()
    if db:
        try:
            doc_ref = db.collection(config.GCP_FIRESTORE_COLLECTION).document(job_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            logger.warning(f"Firestore read failed: {e}")
            
    return _local_job_store.get(job_id)
