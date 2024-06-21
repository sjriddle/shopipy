import requests
from rich import print
from shopipy.base import ACCESS_TOKEN, API_VERSION, SHOP_URL
from rich.table import Table


def fetch_open_orders() -> dict:
    HEADERS = {"X-Shopify-Access-Token": ACCESS_TOKEN}
    # Perform the GET request to get orders
    response = requests.get(
        f"{SHOP_URL}/api/{API_VERSION}/orders.json?status=unfulfilled&limit=250",
        headers=HEADERS,
    )

    # Check if the request was successful
    if response.status_code != 200:
        print(
            ":x: [red] API Call Failed\n[/red]",
            f"  - Status Code:   {response.status_code}\n"
            f"  - Error Message: {response.text}",
        )
        exit()

    orders = response.json().get("orders", [])

    # Create a dictionary to store SKU quantities and their variant titles
    sku_dict: dict = {}
    if not orders:
        print(":warning: [bold] No open orders found[/bold]")
        return {"results": []}
        

    # Iterate through all orders and their line items
    for order in orders:
        for line_item in order.get("line_items", []):
            sku = line_item.get("sku")
            variant_title = line_item.get("variant_title")
            quantity = line_item.get("quantity")

            if sku and variant_title:
                if sku in sku_dict:
                    sku_dict[sku]["quantity"] += quantity
                else:
                    sku_dict[sku] = {
                        "variant": variant_title,
                        "quantity": quantity,
                    }

    # Prepare the results
    results = {
        "results": [
            {"sku": sku, **details} for sku, details in sku_dict.items()
        ]
    }

    # Reuturn the resulting dictionary
    return results
    
    
def yield_orders():
    orders = fetch_open_orders()["results"]
    for order in orders:
        yield order
        


def create_order_table(orders: list = None):
    table = Table(title="Open Orders", highlight=True, show_lines=True)
    table.add_column("SKU", style="cyan")
    table.add_column("Variant", style="magenta")
    table.add_column("Quantity", style="green")

    for order in fetch_open_orders()["results"]:
        table.add_row(
            order["sku"], order["variant"], str(order["quantity"])
        )

    return table
