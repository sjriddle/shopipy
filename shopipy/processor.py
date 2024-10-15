# shopipy/processor.py

import io
import logging
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

import img2pdf
import PyPDF2
from rich.logging import RichHandler

from shopipy.api import ShopifyAPI
from shopipy.config import (
  ASSET_PATH,
  FILES_PATH,
  PDF_DIR,
  PDF_PATH,
  OrderVariant,
)

# Configure logging
logging.basicConfig(
  level=logging.ERROR,
  format="%(message)s",
  datefmt="[%X]",
  handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)

log = logging.getLogger("rich")


class OrderProcessor:
  """
  A class to process orders, organize images, and generate PDFs.
  """

  def __init__(
    self,
    orders: Optional[List[Dict[str, Any]]] = None,
    api: Optional[ShopifyAPI] = None,
  ) -> None:
    """
    Initialize the OrderProcessor with orders and paths.

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
    self.PDF_DIR: Path = PDF_DIR
    self.PDF_PATH: Path = PDF_PATH

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

  def create_pdf(self, image_files: List[Path]) -> None:
    """
    Create a PDF from a list of image files.

    :param image_files: List of image file paths.
    """
    if not self.PDF_PATH:
      log.error("PDF path is incorrect: %s", self.PDF_PATH)
      raise ValueError("Invalid PDF path")
    if not image_files:
      log.warning("No images found to create PDF")
      return

    image_files_str: List[str] = [
      str(image_file) for image_file in image_files
    ]

    try:
      with open(self.PDF_PATH, "wb") as f:
        f.write(img2pdf.convert(image_files_str))
    except Exception as e:
      log.error("Failed to create PDF: %s", e)
      raise

    if self.PDF_PATH.exists():
      log.info("PDF created at: %s", self.PDF_PATH)
    else:
      log.error("Failed to create PDF at: %s", self.PDF_PATH)

  def organize_images_by_variant(self) -> None:
    """
    Organize images into folders based on their variant sizes.
    """
    for variant in OrderVariant:
      # Folder location for the variant
      folder_path: Path = self.FILES_PATH / variant.value

      # Remove existing folder and its contents if it exists
      if folder_path.exists():
        log.info("Cleaning up existing files: %s", folder_path)
        shutil.rmtree(folder_path)

      # Create directory for the variant
      log.info("Creating folder: %s", folder_path)
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
        log.error("Invalid variant title: %s", variant_title)
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
            log.info("Copied %s to %s", source_image_file, dest_image_file)
          except Exception as e:
            log.error("Failed to copy image: %s", e)
      else:
        log.warning("Image file not found: %s", source_image_file)

  def aggregate_image_files(self) -> Dict[str, List[Path]]:
    """
    Aggregate image files from orders.

    :return: Dictionary containing lists of found and missing image files.
    """
    image_files: List[Path] = []
    missing_images: List[Path] = []

    for item in self.orders:
      sku: str = item["sku"]
      variant_title: str = item["variant"]
      quantity: int = item["quantity"]

      # Map variant titles
      variant_title = self.map_variant_title(variant_title)
      if variant_title is None:
        continue  # Skip this item

      # Use OrderVariant Enum for variant titles
      try:
        variant = OrderVariant(variant_title)
      except ValueError:
        log.error("Invalid variant title: %s", variant_title)
        continue

      # File path for the SKU image
      image_file: Path = self.ASSET_PATH / variant.value / f"{sku}.jpg"
      if image_file.exists():
        log.info("Found %s", image_file)
        image_files.extend([image_file] * quantity)
      else:
        missing_images.append(image_file)

    if not image_files:
      log.error("No image files found")
      raise FileNotFoundError("No image files found")
    if missing_images:
      log.warning("Missing images:")
      for i, image in enumerate(missing_images, 1):
        log.warning("  %d: %s", i, image)
    return {"found": image_files, "missing": missing_images}

  def get_most_recent_pdf(self) -> Optional[Path]:
    """
    Get the most recent PDF file from the PDF directory.

    :return: Path to the most recent PDF file or None if none found.
    """
    pdf_files: List[Path] = [
      f for f in self.PDF_DIR.iterdir() if f.is_file() and f.suffix == ".pdf"
    ]

    if not pdf_files:
      log.warning("No PDF files found")
      return None

    pdf_files.sort(key=lambda x: x.stat().st_mtime)
    most_recent_pdf: Path = pdf_files[-1]
    log.info("Most recent PDF: %s", most_recent_pdf.name)
    return most_recent_pdf

  def append_image_to_pdf(self, image_path: Path) -> None:
    """
    Append an image to the most recent PDF in the PDF directory.

    :param image_path: Path to the image file to append.
    """
    pdf_path: Optional[Path] = self.get_most_recent_pdf()
    if not pdf_path:
      log.error("Unable to find recent PDF in directory: %s", self.PDF_DIR)
      return

    if not image_path.exists():
      log.error("Image file not found: %s", image_path)
      return

    try:
      # Read the existing PDF
      with open(pdf_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        writer = PyPDF2.PdfWriter()

        # Copy pages from reader to writer
        for page in reader.pages:
          writer.add_page(page)

        # Convert image to PDF and add to writer
        image_pdf_bytes = PyPDF2.convert(str(image_path))
        image_pdf_reader = PyPDF2.PdfReader(io.BytesIO(image_pdf_bytes))
        for page in image_pdf_reader.pages:
          writer.add_page(page)

        # Write the updated PDF
        new_pdf_path: Path = pdf_path.with_name(pdf_path.stem + "_updated.pdf")
        with open(new_pdf_path, "wb") as new_pdf_file:
          writer.write(new_pdf_file)
    except Exception as e:
      log.error("Failed to append image to PDF: %s", e)
      return

    if new_pdf_path.exists():
      log.info("Updated PDF created at: %s", new_pdf_path)
    else:
      log.error("Failed to create updated PDF")

  def process_orders(self) -> None:
    """
    Process the orders by organizing images, aggregating them, and creating a PDF.
    """
    # Organize images by variant
    self.organize_images_by_variant()

    # Aggregate image files
    images_info: Dict[str, List[Path]] = self.aggregate_image_files()
    image_files: List[Path] = images_info["found"]

    # Create PDF from images
    self.create_pdf(image_files)

    # Optionally, append an image to the most recent PDF
    # image_to_append = Path('/path/to/image.jpg')
    # self.append_image_to_pdf(image_to_append)
