"""
Firebase Firestore client for storing traffic safety events.
"""
import logging
import os
from typing import Dict, Any, Optional

# Firebase Admin SDK
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logging.warning(
        "firebase-admin not installed. Run: pip install firebase-admin"
    )

from config import settings

logger = logging.getLogger(__name__)

# Global Firestore client
_db: Optional[Any] = None
_initialized = False


def initialize_firebase():
    """Initialize Firebase client (call once at startup)."""
    global _db, _initialized
    
    if _initialized:
        return
    
    if not FIREBASE_AVAILABLE:
        logger.warning("Firebase SDK not available. Events will NOT be sent to Firestore.")
        return
    
    # Check for configurable credentials path first
    firebase_creds = getattr(settings, 'USER_FIREBASE_CREDENTIALS', settings.FIREBASE_CREDENTIALS)
    
    if not os.path.exists(firebase_creds):
        logger.warning(
            f"Firebase credentials not found at {firebase_creds}. "
            "Events will NOT be sent to Firestore. "
            "See setup instructions in FIREBASE_SETUP.md"
        )
        return
    
    try:
        # Initialize Firebase app (only once)
        if not firebase_admin._apps:
            cred = credentials.Certificate(firebase_creds)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized successfully")
        
        _db = firestore.client()
        _initialized = True
        logger.info(f"Firestore client ready. Collection: {settings.FIREBASE_EVENT_COLLECTION}")
    
    except Exception as e:
        logger.exception(f"Failed to initialize Firebase: {e}")


def save_event(event_dict: Dict[str, Any]) -> bool:
    """
    Save a single event to Firestore.
    
    Args:
        event_dict: Event data dictionary (with 'id' field as document ID)
    
    Returns:
        True if saved successfully, False otherwise
    """
    if not _initialized or _db is None:
        return False
    
    try:
        doc_id = event_dict.get("id", "unknown")
        doc_ref = _db.collection(settings.FIREBASE_EVENT_COLLECTION).document(doc_id)
        doc_ref.set(event_dict)
        logger.debug(f"✓ Event {doc_id} saved to Firestore")
        return True
    
    except Exception as e:
        logger.error(f"Failed to save event to Firestore: {e}")
        return False


def get_recent_events(limit: int = 100) -> list:
    """
    Retrieve recent events from Firestore.
    
    Args:
        limit: Maximum number of events to retrieve
    
    Returns:
        List of event dictionaries
    """
    if not _initialized or _db is None:
        return []
    
    try:
        docs = (_db.collection(settings.FIREBASE_EVENT_COLLECTION)
                .order_by("time", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream())
        
        events = [doc.to_dict() for doc in docs]
        return events
    
    except Exception as e:
        logger.error(f"Failed to retrieve events from Firestore: {e}")
        return []
