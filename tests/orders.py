from shopipy.orders import fetch_open_orders
from rich import print

def main():
    print("Fetching open orders from Shopify")
    orders = fetch_open_orders(additional_items=[{"sku": "SO303MD", "variant": "8x10", "quantity": 2}])
    print(orders)

                
    # print(orders)    
if __name__ == "__main__":
    main()
