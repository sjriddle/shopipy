import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

# Application information
NAME = "shopipy"

# Shopify API credentials
ACCESS_TOKEN = os.getenv("ADMIN_API_KEY", "")
SHOP_NAME = os.getenv("STORE_NAME", "")
ASSET_PATH = os.getenv("ASSET_PATH", "")
PDF_DIR = os.getenv("PDF_PATH", "/Users/peechcraft/Documents/prints")
PDF_PATH = os.path.join(
    PDF_DIR,
    f"ph_{int(datetime.now().replace(microsecond=0).timestamp())}.pdf",
)
API_VERSION = "2024-04"
SHOP_URL = f"https://{SHOP_NAME}.myshopify.com/admin"
