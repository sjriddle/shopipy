import os
from datetime import datetime
from enum import Enum
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# Application information
APP_NAME = "shopipy"

# Shopify API credentials and configuration
ACCESS_TOKEN = os.getenv("ADMIN_API_KEY")
SHOP_NAME = os.getenv("STORE_NAME")
API_VERSION = os.getenv(
  "API_VERSION", "2024-04"
)  # Use a default API version if not set

# Get the current user's home directory
HOME_DIR = Path.home()

# Paths configuration
ASSET_PATH = Path(os.getenv("ASSET_PATH", HOME_DIR / "assets"))
FILES_PATH = Path(os.getenv("FILES_PATH", HOME_DIR / "files"))
PDF_DIR = Path(os.getenv("PDF_DIR", HOME_DIR / "Documents" / "prints"))

# Ensure essential environment variables are set
REQUIRED_ENV_VARS = {
  "ADMIN_API_KEY": ACCESS_TOKEN,
  "STORE_NAME": SHOP_NAME,
  # ASSET_PATH and FILES_PATH have default values now
}

missing_vars = [var for var, value in REQUIRED_ENV_VARS.items() if not value]
if missing_vars:
  raise EnvironmentError(
    f"Missing required environment variables: {', '.join(missing_vars)}"
  )

# Construct PDF_PATH with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
PDF_PATH = PDF_DIR / f"ph_{timestamp}.pdf"

# Construct the Shopify shop URL
SHOP_URL = f"https://{SHOP_NAME}.myshopify.com/admin"


# Define the OrderVariant Enum (ensure it's only defined here and imported elsewhere)
class OrderVariant(Enum):
  SMALL = "5x7"
  MEDIUM = "8x10"
  LARGE = "11x14"
  XLARGE = "16x20"
  XXLARGE = "18x24"
  XXXLARGE = "24x36"
  XXXXLARGE = "30x40"
