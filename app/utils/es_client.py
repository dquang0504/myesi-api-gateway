# app/utils/es_client.py
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, TransportError
from app.core.config import settings
import logging

logger = logging.getLogger("es_client")

# Initialize Elasticsearch client
es = Elasticsearch([settings.ELASTICSEARCH_URL])

def ensure_connection() -> bool:
    """
    Ensure Elasticsearch is reachable.
    """
    try:
        if es.ping():
            logger.info("✅ Connected to Elasticsearch")
            return True
        else:
            logger.warning("⚠️ Elasticsearch ping returned False")
            return False
    except (ConnectionError, TransportError) as e:
        logger.exception("❌ Elasticsearch connection error: %s", e)
        return False


def index_audit(data: dict, index_name: str = "api_gateway_audit"):
    """
    Store audit log or request info into Elasticsearch.
    """
    try:
        if not ensure_connection():
            logger.warning("⚠️ Skipping audit — Elasticsearch not available")
            return None

        doc = {
            **data,
            "timestamp": datetime.utcnow().isoformat()
        }

        res = es.index(index=index_name, document=doc)
        logger.info(f"📜 Audit indexed in {index_name}: {res.get('result', 'unknown')}")
        return res

    except Exception as e:
        logger.exception("❌ Failed to index audit log: %s", e)
        return None
