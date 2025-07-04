import threading
import time
import requests
import logging
from datetime import datetime
from config import GPO_CLOUD_API_URL, GPO_ORGANIZATION_API_KEY

logger = logging.getLogger("GPO Local Brain Scheduler")

class LocalBrainScheduler:
    def __init__(self, process_document_callback, update_linguists_callback, organization_id, shutdown_event):
        self.process_document_callback = process_document_callback
        self.update_linguists_callback = update_linguists_callback
        self.organization_id = organization_id
        self.shutdown_event = shutdown_event
        self.poll_interval = 60  # seconds
        self.linguist_sync_interval = 60 * 60 * 12  # 12 hours
        self.linguist_profiles = []
        self.last_linguist_sync = 0

    def poll_cloud_gpo(self):
        """Poll the Cloud GPO for new analysis requests."""
        try:
            headers = {"X-API-Key": GPO_ORGANIZATION_API_KEY}
            # MOCKED: Replace with real endpoint in production
            resp = requests.get(f"{GPO_CLOUD_API_URL}/api/local-brain-requests/{self.organization_id}", headers=headers, timeout=10)
            resp.raise_for_status()
            requests_list = resp.json().get("requests", [])
            for req in requests_list:
                req_id = req["local_analysis_request_id"]
                file_path = req["file_path"]
                content_type = req["content_type"]
                # Immediately update status to 'Processing Local Analysis'
                self.update_status(req_id, "Processing Local Analysis")
                self.process_document_callback(file_path, req_id, self.organization_id, content_type, self.linguist_profiles)
        except Exception as e:
            logger.error(f"Polling error: {e}")
            self.report_error(None, self.organization_id, "Polling Error", str(e))

    def update_status(self, local_analysis_request_id, status):
        try:
            headers = {"X-API-Key": GPO_ORGANIZATION_API_KEY}
            payload = {"local_analysis_request_id": local_analysis_request_id, "local_analysis_status": status, "timestamp": datetime.utcnow().isoformat() + "Z"}
            requests.post(f"{GPO_CLOUD_API_URL}/api/local-analysis-results", json=payload, headers=headers, timeout=10)
        except Exception as e:
            logger.error(f"Status update error: {e}")

    def report_error(self, local_analysis_request_id, organization_id, error_type, error_message):
        try:
            headers = {"X-API-Key": GPO_ORGANIZATION_API_KEY}
            payload = {
                "local_analysis_request_id": local_analysis_request_id,
                "organization_id": organization_id,
                "error_type": error_type,
                "error_message": error_message,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            requests.post(f"{GPO_CLOUD_API_URL}/api/local-brain-errors", json=payload, headers=headers, timeout=10)
        except Exception as e:
            logger.error(f"Error reporting failed: {e}")

    def sync_linguist_profiles(self):
        try:
            headers = {"X-API-Key": GPO_ORGANIZATION_API_KEY}
            resp = requests.get(f"{GPO_CLOUD_API_URL}/api/organization-linguists/{self.organization_id}", headers=headers, timeout=10)
            resp.raise_for_status()
            self.linguist_profiles = resp.json().get("linguists", [])
            self.update_linguists_callback(self.linguist_profiles)
            logger.info("Linguist profiles updated.")
        except Exception as e:
            logger.error(f"Linguist sync error: {e}")
            self.report_error(None, self.organization_id, "Linguist Sync Error", str(e))

    def run(self):
        logger.info("Starting Local Brain Scheduler service loop.")
        while not self.shutdown_event.is_set():
            now = time.time()
            # Poll for new requests
            self.poll_cloud_gpo()
            # Sync linguist profiles every 12 hours
            if now - self.last_linguist_sync > self.linguist_sync_interval:
                self.sync_linguist_profiles()
                self.last_linguist_sync = now
            # Sleep for poll interval or until shutdown
            self.shutdown_event.wait(self.poll_interval)
        logger.info("Scheduler shutting down gracefully.") 