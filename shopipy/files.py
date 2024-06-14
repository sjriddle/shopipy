import os
from typing import Dict, List

import img2pdf
from rich import print

from shopipy.base import ASSET_PATH, PDF_PATH


# Function to create a PDF from images
def create_pdf(image_files: list, pdf_path: str = PDF_PATH) -> None:
    if not image_files:
        print("[yellow][-] No images found to create PDF[/yellow]")
        exit(0)
    print("[green][+] Creating PDF from image files[/green]")

    with open(PDF_PATH, "wb+") as f:
        f.write(img2pdf.convert(image_files))

    if os.path.exists(PDF_PATH):
        print(f"[green][+] PDF created at: {PDF_PATH}[/green]")


def aggregate_image_files(orders: List[Dict]) -> Dict:
    print("[green][+] Aggregating image files[/green]")

    image_files = []
    missing_images = []

    for item in orders:
        sku = item["sku"]
        variant_title = item["variant"]
        quantity = item["quantity"]

        if variant_title == "Small":
            variant_title = "8x10"

        # Folder path for the variant
        variant_folder = os.path.join(ASSET_PATH, variant_title)

        # File path for the SKU image
        image_file = os.path.join(variant_folder, f"{sku}.jpg")
        if os.path.exists(image_file):
            image_files.extend([image_file] * quantity)
        else:
            missing_images.append(image_file)

        if not image_files:
            print("[red][-] No image files found[/red]")
            exit(0)
        if missing_images:
            print("[yellow][-] Missing images:[/yellow]")
            for image in missing_images:
                print(f"  - {image}")
    return {"found": image_files, "missing": missing_images}
