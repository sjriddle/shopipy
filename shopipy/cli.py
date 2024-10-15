import logging
import time

import typer
from rich.console import Console
from rich.logging import RichHandler
from typing_extensions import Annotated

# Import from the shopipy package
from shopipy.api import ShopifyAPI
from shopipy.config import OrderVariant
from shopipy.processor import OrderProcessor

logging.basicConfig(
  level="NOTSET",
  format="%(message)s",
  datefmt="[%X]",
  handlers=[RichHandler(rich_tracebacks=True)],
)

log = logging.getLogger("rich")

app = typer.Typer(
  rich_markup_mode="rich", no_args_is_help=True, name="shopipy"
)

# Sub-commands for files and orders
files_cmd = typer.Typer(rich_markup_mode="rich", no_args_is_help=True)
app.add_typer(files_cmd, name="files", help="Manage files and directories")

orders_cmd = typer.Typer(rich_markup_mode="rich", no_args_is_help=True)
app.add_typer(orders_cmd, name="orders", help="List or create new orders")

console = Console()

# Instantiate ShopifyAPI
shopify_api = ShopifyAPI()


@orders_cmd.command(name="pdf", help="Generate a PDF from open orders")
def generate_pdf() -> None:
  """
  Generate a PDF from open orders.
  """
  # Create an instance of OrderProcessor
  processor = OrderProcessor(api=shopify_api)
  try:
    processor.process_orders()
    logging.info(":white_check_mark: [bold]PDF generated successfully.[/bold]")
  except Exception as e:
    logging.error("Failed to generate PDF: %s", e)
    logging.info(f":x: [red]Failed to generate PDF: {e}[/red]")


@orders_cmd.command(name="list", help="List all open orders from Shopify")
def list_orders(
  no_progress: Annotated[
    bool, typer.Option("--no-progress", "-n", help="Disable progress bar.")
  ] = False,
) -> None:
  """
  List all open orders from Shopify.
  """
  progress_label = console.print(
    ":scroll: [green bold]Retrieving Shopify Orders[/green bold]"
  )
  orders = shopify_api.extract_order_items()

  if not no_progress and orders:
    with typer.progressbar(
      orders, fill_char="█", label=progress_label, length=len(orders)
    ) as progress:
      for _ in progress:
        # Simulate processing time
        time.sleep(0.01)
  else:
    console.print(
      ":scroll: [green bold]Retrieving Shopify Orders[/green bold]"
    )

  total: int = len(orders)
  console.print(
    f":white_check_mark: [bold]Found [cyan]{total}[/cyan] open orders[/bold]\n"
  )

  # Create and display the orders table
  shopify_api.create_order_table(orders)


@orders_cmd.command(name="add", help="Add order item to the latest PDF")
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
    log.error("Quantity must be a positive integer.")
    raise typer.Exit(code=1)

  # Create an instance of OrderProcessor
  processor = OrderProcessor(api=shopify_api)

  # Create the order item
  order_item = {"sku": sku, "variant": variant.value, "quantity": quantity}

  # Append the new order item
  processor.orders.append(order_item)

  try:
    # Process the new order item (e.g., aggregate images and append to PDF)
    images_info = processor.aggregate_image_files()
    image_files = images_info["found"]

    if image_files:
      # Append the new images to the most recent PDF
      for image_file in image_files:
        processor.append_image_to_pdf(image_file)
      console.print(
        ":white_check_mark: [bold]Order item added and PDF updated.[/bold]"
      )
    else:
      console.print(
        ":x: [red]No images found for the provided SKU and variant.[/red]"
      )
  except Exception as e:
    log.error("Failed to add order item: %s", e)


@files_cmd.command(
  "create", help="Create directories for storing images and PDFs"
)
def create_folders() -> None:
  """
  Create directories for storing images and PDFs.
  """
  # Create an instance of OrderProcessor
  processor = OrderProcessor(api=shopify_api)
  try:
    processor.organize_images_by_variant()
    console.print(
      ":white_check_mark: [bold]Directories created successfully.[/bold]"
    )
  except Exception as e:
    log.error("Failed to create directories: %s", e)
