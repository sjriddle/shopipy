import logging
import typer
import time
from enum import Enum
from rich.logging import RichHandler
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.spinner import Spinner
from shopipy.files import aggregate_image_files, create_pdf
from shopipy.orders import fetch_open_orders, yield_orders, create_order_table
from typing_extensions import Annotated


class OrderVariant(str, Enum):
    sm = "5x7"
    md = "8x10"
    lg = "11x14"
    ps = "16x20"
    pm = "18x24"
    pl = "24x36"
    xl = "30x40"
    

app = typer.Typer(
    rich_markup_mode="rich", no_args_is_help=True, name="shopipy"
)
orders_cmd = typer.Typer(
    rich_markup_mode="rich", no_args_is_help=True
)

orders = app.add_typer(
    orders_cmd, name="orders", help="List or create new orders"
)

console = Console()

@orders_cmd.command(name="pdf")
def generate_pdf() -> None:  
    results = fetch_open_orders()
    image_files = aggregate_image_files(results["results"])
    create_pdf(image_files["found"])


@orders_cmd.command(name="list", help="List all open orders from Shopify")
def list_orders(no_progress: Annotated[bool, typer.Option("--no-progress", "-n", help="Say hi formally.")] = False) -> None:
    """
    List all orders in the database
    """
    progress_label = console.print(":scroll: [green bold] Retrieving Shiopify Orders[/green bold]", new_line_start=True)
    total: int = 0
    with typer.progressbar(
        yield_orders(),
        fill_char='█',
        label=progress_label,
        length=100
    ) as progress:
        for order in progress:
            # Sleep for processing time
            time.sleep(0.01)
            total += 1
    
    console.print(f":white_check_mark: [bold] Found [cyan]{total}[/cyan] open orders[/bold] \n")
    console.print(create_order_table())


@orders_cmd.command(name="add", help="Add order to the latest PDF")
def add_order_item(
    sku: Annotated[str, typer.Option(prompt=":keycap_#: Enter the Item SKU", help="Enter the Item SKU")],    
    variant: Annotated[OrderVariant, typer.Option(prompt=True, show_choices=True, help="Select the Variant Size")],    
    quantity: Annotated[str, typer.Option(prompt=True, help="Enter the Quantity")],    
) -> None:
    results = fetch_open_orders()["results"]
    results.extend([{"sku": sku, "variant": variant.value, "quantity": quantity}])
    print(len(results))
    print(results)
    print(variant)
    # image_files = aggregate_image_files(results)
    console.print(sku, variant.value, quantity)
