from typing import Dict, List

import requests
from rich import print

from shopipy.base import ACCESS_TOKEN, API_VERSION, SHOP_URL


def get_open_orders() -> Dict[str, List[Dict[str, str]]]:
    print("[green][+] Retrieving open orders[/green]")
    HEADERS = {"X-Shopify-Access-Token": ACCESS_TOKEN}
    # Perform the GET request to get orders
    response = requests.get(
        f"{SHOP_URL}/api/{API_VERSION}/orders.json?status=unfulfilled",
        headers=HEADERS,
    )

    # Check if the request was successful
    if response.status_code != 200:
        print(
            "[red] [-] API Call Failed\n[/red]",
            f"  - Status Code:   {response.status_code}\n"
            f"  - Error Message: {response.text}",
        )
        exit()

    orders = response.json().get("orders", [])

    # Create a dictionary to store SKU quantities and their variant titles
    sku_dict: dict = {}
    if orders:
        print(f"[green][+] Found {len(orders)} open orders[/green]")

    else:
        print("[yellow][-] No open orders found[/yellow]")
        exit(0)

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
