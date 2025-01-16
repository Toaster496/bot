import requests
from bs4 import BeautifulSoup
from ebaysdk.trading import Connection as Trading
import g4f
import json
import time

# AliExpress Scraping
def scrape_aliexpress_product(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to retrieve the page")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract product details (change according to the page structure)
    title = soup.find("h1", {"class": "product-title"}).text.strip()
    price = soup.find("span", {"class": "product-price-value"}).text.strip()
    description = soup.find("div", {"class": "product-description"}).text.strip()
    images = [img['src'] for img in soup.find_all('img', {"class": "product-image"})]

    return {
        "title": title,
        "price": price,
        "description": description,
        "images": images
    }

# eBay API Setup
def create_ebay_listing(title, description, price, images):
    api = Trading(appid='YourAppID', devid='YourDevID', certid='YourCertID', token='YourAuthToken', config_file=None)
    
    item = {
        "Title": title,
        "Description": description,
        "PrimaryCategory": {"CategoryID": 12345},  # Use an appropriate category ID
        "StartPrice": price,
        "Currency": "USD",
        "ConditionID": 1000,  # Condition for new item
        "Country": "US",
        "Location": "US",
        "ShippingDetails": {"ShippingServiceOptions": {"ShippingService": "USPSMediaMail", "ShippingServiceCost": 2.5}},
        "PictureDetails": {"PictureURL": images[0]},  # Use the first image from AliExpress
        "Quantity": 1,
        "ListingDuration": "GTC",
        "PaymentMethods": "PayPal",
        "PayPalEmailAddress": "your-paypal@example.com",
    }
    
    response = api.execute('AddFixedPriceItem', item)
    if response.reply.Ack == 'Success':
        print(f"Successfully listed item: {title}")
    else:
        print(f"Error: {response.reply.Errors.LongMessage}")

# GPT-4 Free Integration (for title and description enhancement)
def generate_gpt4_content(title, description):
    # Use g4f (GPT-4 Free) for enhancing title and description
    prompt = f"Enhance the following eBay product listing. Make the title more engaging and create a persuasive product description:\n\nTitle: {title}\nDescription: {description}"

    # Call g4f API to get enhanced content
    response = g4f.ChatCompletion.create(
        model="gpt-4",  # Use GPT-4 model
        messages=[
            {"role": "system", "content": "You are an eBay listing optimization assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract enhanced title and description
    enhanced_title = response['choices'][0]['message']['content'].split('\n')[0]  # Get the enhanced title
    enhanced_description = '\n'.join(response['choices'][0]['message']['content'].split('\n')[1:])  # Get the enhanced description
    
    return enhanced_title, enhanced_description

# Main Function to Scrape, Enhance, and List Products
def main():
    # URL of the AliExpress product
    product_url = 'https://www.aliexpress.com/item/1234567890.html'
    
    # Scrape the product details from AliExpress
    product_data = scrape_aliexpress_product(product_url)
    if not product_data:
        print("Error: Could not retrieve product data.")
        return
    
    # Use GPT-4 to enhance the title and description
    enhanced_title, enhanced_description = generate_gpt4_content(product_data["title"], product_data["description"])
    
    # Create the eBay listing
    create_ebay_listing(enhanced_title, enhanced_description, product_data["price"], product_data["images"])

# Run the bot
if __name__ == "__main__":
    while True:
        main()
        time.sleep(3600)  # Run the bot every hour (or change the interval as needed)
