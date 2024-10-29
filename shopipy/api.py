from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

import requests
from requests.exceptions import RequestException
from rich.console import Console
from rich.table import Table

from shopipy.config import ACCESS_TOKEN, API_VERSION, SHOP_URL

console = Console()


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

  def get_order_count(self) -> int:
    """
    Fetch the total number of open (unfulfilled) orders.

    :return: Total count of orders.
    """
    url: str = f"{self.shop_url}/api/{self.api_version}/orders/count.json"
    params: Dict[str, Any] = {
      "status": "open",
      "fulfillment_status": "unfulfilled",
    }

    try:
      response = requests.get(url, headers=self.headers, params=params)
      response.raise_for_status()
    except RequestException as e:
      console.print_exception(f"[bold red]API Call Failed:[/bold red] {e}")
      return 0

    count = response.json().get("count", 0)
    return count

  def fetch_open_orders(self) -> List[Dict[str, Any]]:
    """
    Fetch all open (unfulfilled) orders from Shopify using pagination.

    :return: List of order dictionaries.
    """
    total_orders = self.get_order_count()
    if total_orders == 0:
      console.print(":x: No open orders found")
      return []

    url: str = f"{self.shop_url}/api/{self.api_version}/orders.json"
    params: Dict[str, Any] = {
      "status": "open",
      "fulfillment_status": "unfulfilled",
      "limit": 250,
    }

    orders: List[Dict[str, Any]] = []
    fetched_orders = 0

    while True:
      try:
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
      except RequestException as e:
        console.print_exception(f"[bold red]API Call Failed:[/bold red] {e}")
        break

      current_orders = response.json().get("orders", [])
      orders.extend(current_orders)
      fetched_orders += len(current_orders)

      # Check if all orders have been fetched
      if fetched_orders >= total_orders:
        break

      # Check for 'Link' header for pagination
      link_header = response.headers.get("Link", "")
      if 'rel="next"' not in link_header:
        # No more pages to fetch
        break

      # Extract 'page_info' for the next page
      next_page_info = self.extract_next_page_info(link_header)
      if not next_page_info:
        break

      # Update params for the next request
      params = {
        "page_info": next_page_info,
        "limit": 250,
      }

    return orders

  def extract_next_page_info(self, link_header: str) -> Optional[str]:
    """
    Extracts the 'page_info' parameter from the Link header for pagination.

    :param link_header: The 'Link' header string from the response.
    :return: The 'page_info' parameter string or None if not found.
    """
    links = link_header.split(",")
    for link in links:
      segments = link.strip().split(";")
      if len(segments) < 2:
        continue
      link_part = segments[0].strip("<>")
      rel_part = segments[1].strip()
      if rel_part == 'rel="next"':
        # Parse the URL to extract 'page_info'
        parsed_url = urlparse(link_part)
        query_params = parse_qs(parsed_url.query)
        page_info = query_params.get("page_info", [None])[0]
        return page_info
    return None

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

    table = Table(
      title="[bold]Unfulfilled Orders[/bold]",
    )
    table.add_column("SKU", style="cyan")
    table.add_column("Variant", style="magenta")
    table.add_column("Quantity", style="green")

    for order in orders:
      table.add_row(order["sku"], order["variant"], str(order["quantity"]))

    console.print(table)
