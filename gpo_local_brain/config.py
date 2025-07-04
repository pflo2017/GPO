import os
from dotenv import load_dotenv

load_dotenv()

GPO_CLOUD_API_URL = os.getenv("GPO_CLOUD_API_URL")
GPO_ORGANIZATION_API_KEY = os.getenv("GPO_ORGANIZATION_API_KEY") 