from pathlib import Path
from typing import Any, Dict, List, Union

import typer
from dotenv import dotenv_values, find_dotenv, load_dotenv, set_key, unset_key
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated

from shopipy.api import ShopifyAPI
from shopipy.assets import AssetOrganizer
from shopipy.config import OrderVariant
from shopipy.pdf import PDFGenerator

app = typer.Typer(
  rich_markup_mode="rich", no_args_is_help=True, name="shopipy"
)
# Sub-commands for files and orders
files_cmd = typer.Typer(rich_markup_mode="rich", no_args_is_help=True)
app.add_typer(files_cmd, name="files", help="Manage files and directories")

orders_cmd = typer.Typer(rich_markup_mode="rich", no_args_is_help=True)
app.add_typer(orders_cmd, name="orders", help="List or create new orders")

config_cmd = typer.Typer(rich_markup_mode="rich", no_args_is_help=True)
app.add_typer(config_cmd, name="config", help="Configure application settings")

console = Console()

# Instantiate API
shopify_api = ShopifyAPI()

# Load environment variables
dotenv_path = find_dotenv()
if not dotenv_path:
  dotenv_path = Path(".env")
  dotenv_path.touch()  # Create an empty .env file
else:
  dotenv_path = Path(dotenv_path)
load_dotenv(dotenv_path)


@files_cmd.command(name="pdf", help="Generate a PDF from open orders")
def generate_pdf() -> None:
  """
  Generate a PDF from open orders.
  """
  # Create an instance of PDFGenerator
  pdfr = PDFGenerator(api=shopify_api)
  with console.status("Generating PDF...", spinner="aesthetic"):
    try:
      assets_info: Dict[str, List[Path]] = pdfr.aggregate_image_files()
      items_found: List[Path] = assets_info["found"]
      items_missing: List[Any] = assets_info.get("missing", [])

      # Create PDF from images
      pdfr.create_pdf(items_found)

      console.print(
        f"\n:white_check_mark: [bold]PDF generated successfully in folder: {pdfr.PDF_PATH}[/bold]"
      )

      # Print missing SKUs if any
      if items_missing:
        console.print(
          f":mag_right: [bold]Missing items in folder: {pdfr.ASSET_PATH}[/bold]"
        )
        for sku in items_missing:
          console.print(sku, style="yellow")

    except Exception as e:
      console.print(f":x: Failed to generate PDF: {e}")


@orders_cmd.command(name="list", help="List all open orders from Shopify")
def list_orders() -> None:
  """
  List all open orders from Shopify.
  """
  with console.status(
    "[bold]Retrieving Shopify Orders[/bold]", spinner="aesthetic"
  ):
    orders = shopify_api.extract_order_items()

  total: int = len(orders)
  console.print(
    f":white_check_mark: [bold]Found [cyan]{total}[/cyan] open orders[/bold]\n"
  )

  # Create and display the orders table
  shopify_api.create_order_table(orders)


@files_cmd.command(
  name="add", help="Add order item to the latest PDF", no_args_is_help=True
)
def add_order_item(
  sku: Annotated[
    str,
    typer.Option(
      prompt=":keycap_#: Enter the Item SKU", help="Enter the Item SKU"
    ),
  ],
  variant: Annotated[
    OrderVariant,
    typer.Option(
      prompt=True, show_choices=True, help="Select the Variant Size"
    ),
  ],
  quantity: Annotated[
    int, typer.Option(prompt=True, help="Enter the Quantity")
  ],
) -> None:
  """
  Add an order item to the latest PDF.
  """
  if quantity <= 0:
    console.print(":x: Quantity must be a positive integer.")
    raise typer.Exit(code=1)

  # Create an instance of PDFGenerator
  pdf_generator = PDFGenerator(orders=[], api=None)

  # Create the order item
  order_item = {"sku": sku, "variant": variant.value, "quantity": quantity}

  # Append the new order item
  pdf_generator.orders.append(order_item)

  try:
    # Aggregate images for the new order item
    images_info = pdf_generator.aggregate_image_files()
    image_files = images_info["found"]

    if image_files:
      # Append the new images to the most recent PDF
      for image_file in image_files:
        pdf_generator.append_image_to_pdf(image_file)
      console.print(
        ":white_check_mark: [bold]Order item added and PDF updated.[/bold]"
      )
    else:
      console.print(
        ":x: [red]No images found for the provided SKU and variant.[/red]"
      )
  except Exception as e:
    console.print(f":x: Failed to add order item: {e}")


@files_cmd.command("create", help="Create folders of assets based on variant.")
def create_folders(
  filepath: Annotated[
    str,
    typer.Option(
      prompt=False, help="Enter alternative location to create folders."
    ),
  ] = "",
) -> None:
  """
  Create directories for storing assets.
  """
  # Create an instance of AssetOrganizer
  asset_organizer = AssetOrganizer(api=shopify_api)
  try:
    missing_skus, asset_path = asset_organizer.organize_images_by_variant()
    console.print(
      ":white_check_mark: [bold]Folders created successfully with assets.[/bold]"
    )

    # Print missing SKUs if any
    if missing_skus:
      console.print(
        f":mag_right: [bold]Missing items in folder: {asset_path}[/bold]"
      )
      for sku in missing_skus:
        console.print(sku, style="yellow")
  except Exception as e:
    console.print(f":x: Failed to create directories: {e}")


# Configuration Commands
@config_cmd.command("set", help="Set a configuration value")
def set_config(
  key: Annotated[
    str,
    typer.Option(
      prompt=True,
      help="Configuration key to set (ADMIN_API_KEY, ASSET_PATH, FILES_PATH, PDF_PATH, STORE_NAME):",
      show_choices=True,
    ),
  ],
  value: Annotated[
    str,
    typer.Option(prompt=True, help="Value to set for the configuration key"),
  ],
) -> None:
  """
  Set a configuration value in the .env file.
  """
  valid_keys = [
    "ADMIN_API_KEY",
    "ASSET_PATH",
    "FILES_PATH",
    "PDF_PATH",
    "STORE_NAME",
  ]
  if key not in valid_keys:
    console.print(f":x: Invalid configuration key: {key}")
    console.print(f"Valid keys are: {', '.join(valid_keys)}")
    raise typer.Exit(code=1)

  set_key(str(dotenv_path), key, value)
  console.print(
    f":white_check_mark: Set [bold]{key}[/bold] to [cyan]{value}[/cyan]"
  )


@config_cmd.command("unset", help="Unset a configuration value")
def unset_config(
  key: Annotated[
    str,
    typer.Option(
      prompt=True,
      help="Configuration key to unset (ADMIN_API_KEY, ASSET_PATH, FILES_PATH, PDF_PATH, STORE_NAME):",
      show_choices=True,
    ),
  ],
) -> None:
  """
  Unset (remove) a configuration value from the .env file.
  """
  valid_keys = [
    "ADMIN_API_KEY",
    "ASSET_PATH",
    "FILES_PATH",
    "PDF_PATH",
    "STORE_NAME",
  ]
  if key not in valid_keys:
    console.print(f":x: Invalid configuration key: {key}")
    console.print(f"Valid keys are: {', '.join(valid_keys)}")
    raise typer.Exit(code=1)

  unset_key(str(dotenv_path), key)
  console.print(f":white_check_mark: Unset [bold]{key}[/bold]")


@config_cmd.command("show", help="Show current configuration values")
def show_config() -> None:
  """
  Show the current configuration values from the .env file.
  """
  config = dotenv_values(dotenv_path)
  table = Table(
    title="Current Configuration",
    show_header=True,
    header_style="bold magenta",
  )
  table.add_column("Key", style="cyan")
  table.add_column("Value", style="green")

  valid_keys = [
    "ADMIN_API_KEY",
    "ASSET_PATH",
    "FILES_PATH",
    "PDF_PATH",
    "STORE_NAME",
  ]
  for key in valid_keys:
    value = config.get(key, "[red]Not Set[/red]")
    if (
      key in ["ADMIN_API_KEY", "STORE_NAME"] and value != "[red]Not Set[/red]"
    ):
      value = f"{value[:4]}****{value[-4:]}"  # Mask the API key
    table.add_row(key, value)

  console.print(table)
