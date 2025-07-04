import sys
import logging
import threading
from config import GPO_CLOUD_API_URL, GPO_ORGANIZATION_API_KEY
from document_processor import extract_text
import ai_analyzer
from scheduler import LocalBrainScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GPO Local Brain")

# Global cache for linguist profiles
global_linguist_profiles = []

def update_linguists(profiles):
    global global_linguist_profiles
    global_linguist_profiles = profiles

def process_document_locally(file_path, local_analysis_request_id, organization_id, content_type, linguist_profiles=None):
    logger.info(f"Processing document: {file_path}")
    text, error = extract_text(file_path)
    if not text:
        status = "Error in Local Analysis (Text Extraction Failed)"
        payload = {
            "local_analysis_request_id": local_analysis_request_id,
            "local_analysis_status": status,
            "ai_analysis_timestamp": None
        }
        headers = {"X-API-Key": GPO_ORGANIZATION_API_KEY}
        try:
            import requests
            from datetime import datetime
            payload["ai_analysis_timestamp"] = datetime.utcnow().isoformat() + "Z"
            requests.post(f"{GPO_CLOUD_API_URL}/api/local-analysis-results", json=payload, headers=headers, timeout=10)
            logger.info(f"Status update sent to Cloud GPO.")
        except Exception as e:
            logger.error(f"Failed to send status update: {e}")
        return None, error
    # Use latest linguist profiles
    blueprint = ai_analyzer.analyze_document(text, linguist_profiles or global_linguist_profiles, content_type)
    send_blueprint_to_cloud(local_analysis_request_id, blueprint)
    return text, None

def send_blueprint_to_cloud(local_analysis_request_id, blueprint):
    from datetime import datetime
    import requests
    payload = {"local_analysis_request_id": local_analysis_request_id, "local_analysis_status": "Analysis Complete"}
    payload.update(blueprint)
    payload["ai_analysis_timestamp"] = datetime.utcnow().isoformat() + "Z"
    headers = {"X-API-Key": GPO_ORGANIZATION_API_KEY}
    try:
        resp = requests.post(f"{GPO_CLOUD_API_URL}/api/local-analysis-results", json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        logger.info(f"Blueprint sent to Cloud GPO: {resp.status_code}")
    except Exception as e:
        logger.error(f"Failed to send blueprint: {e}")

def main_service(organization_id):
    shutdown_event = threading.Event()
    scheduler = LocalBrainScheduler(
        process_document_callback=process_document_locally,
        update_linguists_callback=update_linguists,
        organization_id=organization_id,
        shutdown_event=shutdown_event
    )
    try:
        scheduler.run()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal. Exiting...")
        shutdown_event.set()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <organization_id>")
        sys.exit(1)
    organization_id = sys.argv[1]
    main_service(organization_id) 