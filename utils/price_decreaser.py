import random

def price_decreaser(price):
    print(price)
    try:
        # Remove the dollar sign and comma
        price_value = float(price.replace('$', '').replace(',', ''))
        print(price_value)
        
        # Decrease by a random amount between 0.01 and 0.05
        decrease_amount = random.uniform(0.01, 0.05)
        new_price_value = price_value - decrease_amount
        
        # Format the new price to two decimal places
        new_price = f"{new_price_value:.2f}"
        return new_price
    except Exception as e:
        print(f"Error decreasing price: {e}")
        return price