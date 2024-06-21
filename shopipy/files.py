import os
from os import listdir
from os.path import isfile, join
import img2pdf
from datetime import datetime
from rich import print
from rich.panel import Panel
from shopipy.base import ASSET_PATH, PDF_PATH, PDF_DIR


# Function to create a PDF from images
def create_pdf(image_files: list, pdf_path: str = PDF_PATH) -> None:
    if not pdf_path:
        print(f":x: PDF path is incorrect: [bold] {pdf_path} [/bold]")
        exit(0)
    if not image_files:
        print(":warning: [bold] No images found to create PDF[/bold]")
        exit(0)
    print(":white_check_mark: [bold] Creating PDF from image files[/bold]")

    with open(PDF_PATH, "wb+") as f:
        f.write(img2pdf.convert(image_files))

    if os.path.exists(PDF_PATH):
        print(f":white_check_mark: PDF created at: [bold]{PDF_PATH}[/bold]")
    else:
        print(":x: [red] PDF path does not exist[/red]")


def aggregate_image_files(orders: list) -> dict:
    print(":white_check_mark: [bold] Aggregating image files[/bold]")

    image_files = []
    missing_images = []

    for item in orders:
        sku = item["sku"]
        variant_title = item["variant"]
        quantity = item["quantity"]

        if variant_title == "Small":
            variant_title = "5x7"

        # Folder path for the variant
        variant_folder = os.path.join(ASSET_PATH, variant_title)

        # File path for the SKU image
        image_file = os.path.join(variant_folder, f"{sku}.jpg")
        if os.path.exists(image_file):
            print(f'[green]HIT {image_file}[/green]')
            image_files.extend([image_file] * quantity)
        else:
            missing_images.append(image_file)

    if not image_files:
        print(":x: [bold cyan] No image files found[/bold]")
        exit(0)
    if missing_images:
        print(":magnifying_glass_tilted_left: [bold] Missing images:[/bold]")
        for i, image in enumerate(missing_images):
            print(f"  {i+1}:{image}")
    return {"found": image_files, "missing": missing_images}



def get_most_recent_pdf(pdf_dir: str = PDF_DIR) -> str:
    pdf_files = [f for f in listdir(pdf_dir) if isfile(join(pdf_dir, f)) and f.endswith('.pdf')]

    if not pdf_files:
        print(f":x: [bold] No PDF files found [/bold]")
        return None

    pdf_files.sort(key=lambda x: datetime.fromtimestamp(int(x.rstrip('.pdf').split('_')[-1])))
    most_recent_pdf = pdf_files[-1]
    print(f":white_check_mark: Most recent PDF: [bold]{most_recent_pdf}[/bold]")
    return os.path.join(pdf_dir, most_recent_pdf)

def append_image_to_pdf(sku: str, image_path: str, pdf_dir: str = PDF_DIR):
    pdf_path = get_most_recent_pdf(sku, pdf_dir)
    if not pdf_path:
        print(f":x: Unable to find recent PDF for SKU: [bold]{sku}[/bold]")
        return

    if not os.path.exists(image_path):
        print(f":x: Image file not found: [bold]{image_path}[/bold]")
        return

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    image_pdf_path = image_path.replace('.jpg', '_temp.pdf')
    with open(image_pdf_path, "wb") as f:
        f.write(img2pdf.convert(image_path))

    image_reader = PdfReader(image_pdf_path)
    writer.add_page(image_reader.pages[0])

    new_pdf_path = pdf_path.replace('.pdf', '_updated.pdf')
    with open(new_pdf_path, "wb") as f:
        writer.write(f)

    os.remove(image_pdf_path)

    if os.path.exists(new_pdf_path):
        print(f":white_check_mark: Updated PDF created at: [bold]{new_pdf_path}[/bold]")
    else:
        print(":x: [red]Failed to create updated PDF[/red]")
