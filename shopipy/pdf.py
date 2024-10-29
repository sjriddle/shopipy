import io
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import img2pdf
import PyPDF2
from rich.console import Console

from shopipy.api import ShopifyAPI
from shopipy.config import ASSET_PATH, PDF_DIR, PDF_PATH, OrderVariant

console = Console()


class PDFGenerator:
  """
  A class to generate and manipulate PDFs from images.
  """

  def __init__(
    self,
    orders: Optional[List[Dict[str, Any]]] = None,
    api: Optional[ShopifyAPI] = None,
  ) -> None:
    """
    Initialize the PDFGenerator with orders and paths.

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

  def aggregate_image_files(self) -> Dict[str, List[Path]]:
    """
    Aggregate image files from orders.

    :return: Dictionary containing lists of found and missing image files.
    """
    image_files: List[Path] = []
    missing_sku: List[Path] = []

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
        console.print(f":x: Invalid variant title: {variant_title}")
        continue

      # File path for the SKU image
      image_file: Path = self.ASSET_PATH / variant.value / f"{sku}.jpg"
      if image_file.exists():
        image_files.extend([image_file] * quantity)
      else:
        missing_sku.append(sku)

    if not image_files:
      raise FileNotFoundError("No image files found")

    return {"found": image_files, "missing": missing_sku}

  def create_pdf(self, image_files: List[Path]) -> None:
    """
    Create a PDF from a list of image files.

    :param image_files: List of image file paths.
    """
    if not self.PDF_PATH:
      raise ValueError("Invalid PDF path")
    if not image_files:
      console.print(
        f":x: No images found at location [cyan]{ASSET_PATH}[/cyan] to create PDF"
      )
      return

    image_files_str: List[str] = [
      str(image_file) for image_file in image_files
    ]

    try:
      with open(self.PDF_PATH, "wb") as f:
        f.write(img2pdf.convert(image_files_str))
    except Exception as e:
      console.print_exception(f":x: Failed to create PDF: {e}")
      raise

  def get_most_recent_pdf(self) -> Optional[Path]:
    """
    Get the most recent PDF file from the PDF directory.

    :return: Path to the most recent PDF file or None if none found.
    """
    pdf_files: List[Path] = [
      f for f in self.PDF_DIR.iterdir() if f.is_file() and f.suffix == ".pdf"
    ]

    if not pdf_files:
      return None

    pdf_files.sort(key=lambda x: x.stat().st_mtime)
    most_recent_pdf: Path = pdf_files[-1]
    console.print(f":paperclip: Most recent PDF: {most_recent_pdf.name}")
    return most_recent_pdf

  def append_image_to_pdf(self, image_path: Path) -> None:
    """
    Append an image to the most recent PDF in the PDF directory.

    :param image_path: Path to the image file to append.
    """
    pdf_path: Optional[Path] = self.get_most_recent_pdf()
    if not pdf_path:
      console.print(
        f":x: Unable to find recent PDF in directory: {self.PDF_DIR}",
      )
      return

    if not image_path.exists():
      console.print(f":x: Image file not found: {image_path}")
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
        image_pdf_bytes = img2pdf.convert(str(image_path))
        image_pdf_reader = PyPDF2.PdfReader(io.BytesIO(image_pdf_bytes))
        for page in image_pdf_reader.pages:
          writer.add_page(page)

        # Write the updated PDF
        new_pdf_path: Path = pdf_path.with_name(f"{pdf_path.stem}_updated.pdf")
        with open(new_pdf_path, "wb") as new_pdf_file:
          writer.write(new_pdf_file)
      console.print(
        f":white_check_mark: Updated PDF created at: {new_pdf_path}"
      )
    except Exception as e:
      console.print(f":x: Failed to append image to PDF: {e}")

  def process_pdf(self) -> None:
    """
    Aggregate images and create a PDF.
    """
    images_info: Dict[str, List[Any]] = self.aggregate_image_files()
    image_files: List[Any] = images_info["found"]

    # Create PDF from images
    self.create_pdf(image_files)
