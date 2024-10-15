# shopipy/api.py

import logging
from typing import Any, Dict, List, Optional

import requests
from requests.exceptions import RequestException
from rich import print
from rich.logging import RichHandler
from rich.table import Table

from shopipy.config import ACCESS_TOKEN, API_VERSION, SHOP_URL

logging.basicConfig(
  level="ERROR",
  format="%(message)s",
  datefmt="[%X]",
  handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)

log = logging.getLogger("rich")


class ShopifyAPI:
  """
  A class to interact with the Shopify API.
  """

  def __init__(self) -> None:
    """
    Initialize the ShopifyAPI with authentication details.
    """
    self.access_token: str = ACCESS_TOKEN
    self.shop_url: str = SHOP_URL
    self.api_version: str = API_VERSION
    self.headers: Dict[str, str] = {
      "X-Shopify-Access-Token": self.access_token
    }

  def fetch_open_orders(self) -> List[Dict[str, Any]]:
    """
    Fetch open (unfulfilled) orders from Shopify.

    :return: List of order dictionaries.
    """
    url: str = f"{self.shop_url}/api/{self.api_version}/orders.json"
    params: Dict[str, Any] = {
      "status": "open",
      "fulfillment_status": "unfulfilled",
      "financial_status": "paid",
      "limit": 250,
    }

    try:
      response = requests.get(url, headers=self.headers, params=params)
      response.raise_for_status()
    except RequestException as e:
      log.error("API Call Failed: %s", e)
      return []

    orders: List[Dict[str, Any]] = response.json().get("orders", [])
    if not orders:
      log.info("No open orders found")
      return []

    return orders

  def extract_order_items(self) -> List[Dict[str, Any]]:
    """
    Extract SKU, variant, and quantity from open orders.

    :return: List of dictionaries containing SKU, variant, and quantity.
    """
    orders: List[Dict[str, Any]] = self.fetch_open_orders()
    sku_dict: Dict[str, Dict[str, Any]] = {}

    for order in orders:
      for line_item in order.get("line_items", []):
        sku: Optional[str] = line_item.get("sku")
        variant_title: Optional[str] = line_item.get("variant_title")
        quantity: Optional[int] = line_item.get("quantity")

        if sku and variant_title and quantity:
          if sku in sku_dict:
            sku_dict[sku]["quantity"] += quantity
          else:
            sku_dict[sku] = {
              "variant": variant_title,
              "quantity": quantity,
            }

    results: List[Dict[str, Any]] = [
      {"sku": sku, **details} for sku, details in sku_dict.items()
    ]

    return results

  def create_order_table(
    self, orders: Optional[List[Dict[str, Any]]] = None
  ) -> None:
    """
    Create a table of open orders using the Rich library.

    :param orders: List of order dictionaries.
    """
    if orders is None:
      orders = self.extract_order_items()

    table = Table(title="Open Orders", highlight=True, show_lines=True)
    table.add_column("SKU", style="cyan")
    table.add_column("Variant", style="magenta")
    table.add_column("Quantity", style="green")

    for order in orders:
      table.add_row(order["sku"], order["variant"], str(order["quantity"]))

    print(table)
