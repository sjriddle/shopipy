import typer
from rich import print

from shopipy.files import aggregate_image_files, create_pdf
from shopipy.orders import get_open_orders

app = typer.Typer(
    rich_markup_mode="rich", no_args_is_help=True, name="shopipy"
)
orders_cmd = typer.Typer(rich_markup_mode="rich", no_args_is_help=True)

orders = app.add_typer(
    orders_cmd, name="orders", help="List or create new orders"
)


@orders_cmd.command(name="pdf")
def generate_pdf() -> None:  # pragma: no cover
    """
    Generates a PDF from open orders with assets
    """
    results = get_open_orders()
    image_files = aggregate_image_files(results["results"])
    create_pdf(image_files["found"])


@orders_cmd.command(name="list", help="List all open orders from Shopify")
def list_orders() -> None:
    from rich.console import Console
    from rich.table import Table

    """
    List all orders in the database
    """
    print("[green][+] Listing all orders[/green]")
    results = get_open_orders()["results"]
    table = Table(title="Open Orders")
    table.add_column("SKU", style="cyan")
    table.add_column("Variant", style="magenta")
    table.add_column("Quantity", style="green")

    for result in results:
        table.add_row(
            result["sku"], result["variant"], str(result["quantity"])
        )

    console = Console()
    console.print(table)


@orders_cmd.command(
    name="add", help="Add order to the latest pdf or generate new PDF"
)
def add_order() -> None:
    print("[red][-] Not implemented yet[/red]")
