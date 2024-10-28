import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console

from shopipy.api import ShopifyAPI
from shopipy.config import ASSET_PATH, FILES_PATH, OrderVariant

console = Console()


class AssetOrganizer:
  """
  A class to organize assets based on order variants.
  """

  def __init__(
    self,
    orders: Optional[List[Dict[str, Any]]] = None,
    api: Optional[ShopifyAPI] = None,
  ) -> None:
    """
    Initialize the ImageOrganizer with orders and paths.

    :param orders: List of order dictionaries.
    :param api: Instance of ShopifyAPI to fetch orders.
    """
    if orders is None and api is not None:
      self.orders = api.extract_order_items()
    elif orders is not None:
      self.orders = orders
    else:
      raise ValueError("Either orders or api instance must be provided.")

    self.ASSET_PATH: Path = ASSET_PATH
    self.FILES_PATH: Path = FILES_PATH

  def map_variant_title(self, variant_title: str) -> Optional[str]:
    """
    Map variant titles from the order data to standard sizes.

    :param variant_title: The variant title from the order.
    :return: Mapped variant title or None if it should be skipped.
    """
    variant_title_map: Dict[str, Optional[str]] = {
      "Small": "5x7",
      "Medium": "8x10",
      "Large": "11x14",
      "$1.98": None,  # Skip this variant
    }
    return variant_title_map.get(variant_title, variant_title)

  def organize_images_by_variant(self) -> List[str]:
    """
    Organize images into folders based on their variant sizes.

    :return: List of missing image SKUs.
    """
    missing_skus: List[str] = []

    for variant in OrderVariant:
      # Folder location for the variant
      folder_path: Path = self.FILES_PATH / variant.value

      # Remove existing folder and its contents if it exists
      if folder_path.exists():
        shutil.rmtree(folder_path)

      # Create directory for the variant
      folder_path.mkdir(parents=True, exist_ok=True)

    for item in self.orders:
      sku: str = item["sku"]
      variant_title: str = item["variant"]
      quantity: int = item["quantity"]

      # Map variant titles to standard sizes
      variant_title = self.map_variant_title(variant_title)
      if variant_title is None:
        continue  # Skip this item

      # Use OrderVariant Enum for variant titles
      try:
        variant = OrderVariant(variant_title)
      except ValueError:
        # Log invalid variant title
        continue

      # Source file path for the SKU image
      source_image_file: Path = self.ASSET_PATH / variant.value / f"{sku}.jpg"

      # Destination folder path
      dest_folder: Path = self.FILES_PATH / variant.value

      if source_image_file.exists():
        for i in range(1, quantity + 1):
          dest_filename: str = (
            f"{sku}_{i}.jpg" if quantity > 1 else f"{sku}.jpg"
          )

          # Destination file path
          dest_image_file: Path = dest_folder / dest_filename
          try:
            shutil.copy(source_image_file, dest_image_file)
          except Exception as e:
            console.print_exception(f"Log copy failure: {e}")
            pass
      else:
        # Add the missing SKU to the list
        missing_skus.append(sku)

    return missing_skus, self.ASSET_PATH
