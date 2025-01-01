from api import ShopifyAPI
from assets import AssetOrganizer
from rich import print

# Instantiate API
shopify_api = ShopifyAPI()

orders = shopify_api.fetch_open_orders()
print(orders)
