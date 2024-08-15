import requests
from collections import defaultdict
from rich import print
from rich.table import Table
from shopipy.base import ACCESS_TOKEN, API_VERSION, SHOP_URL


def fetch_open_orders(additional_items=None):
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

    # Dictionary to hold the aggregate data
    aggregates = defaultdict(lambda: {"variant": "", "quantity": 0})

    if not orders:
        print(":warning: [bold] No open orders found[/bold]")
        return []

    # Iterate through each order and their line items
    for order in orders:
        for line_item in order.get('line_items', []):
            sku = line_item.get('sku')
            variant_title = line_item.get('variant_title')
            quantity = line_item.get('quantity', 0)

            if sku and variant_title:
                aggregates[sku]['variant'] = variant_title
                aggregates[sku]['quantity'] += quantity

    # Process additional items if provided
    if additional_items:
        for item in additional_items:
            add_sku = item.get('sku')
            add_variant = item.get('variant')
            add_quantity = item.get('quantity', 0)

            if add_sku and add_variant:
                aggregates[add_sku]['variant'] = add_variant
                aggregates[add_sku]['quantity'] += add_quantity
            else:
                aggregates[add_sku] = {
                    'variant': add_variant,
                    'quantity': add_quantity
                }

    # Prepare the results
    results = [{"sku": s, **details} for s, details in aggregates.items()]

    return results


def yield_orders(orders: list=None):
    for order in orders:
        yield order


def create_order_table(orders: list=None):
    table = Table(title="Open Orders", highlight=True, show_lines=True)
    table.add_column("SKU", style="cyan")
    table.add_column("Variant", style="magenta")
    table.add_column("Quantity", style="green")

    for order in orders:
        table.add_row(
            order["sku"], order["variant"], str(order["quantity"])
        )

    return table
