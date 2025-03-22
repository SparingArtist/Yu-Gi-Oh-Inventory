import pandas as pd
import requests

# Load Excel file
df = pd.read_excel("cards.xlsx")

# API Base URL
API_BASE = "https://db.ygoprodeck.com/api/v7/cardinfo.php?name="

# List to store full card data
cards_data = []

for _, row in df.iterrows():
    name = row["Card Name"]
    quantity = int(row["Quantity"]) if "Quantity" in row and not pd.isna(row["Quantity"]) else 1

    print(f"Fetching data for: {name} (x{quantity})...")

    # Format name for API request
    api_url = API_BASE + name.replace(" ", "%20")

    # API request
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and len(data['data']) > 0:
            card_info = data['data'][0]
            
            # Get PNG image if available
            png_image_url = None
            if 'card_images' in card_info:
                for image in card_info['card_images']:
                    if image['image_url'].endswith('.png'):
                        png_image_url = image['image_url']
                        break  # Stop once a PNG is found
            
            # Add to list
            cards_data.append({
                "Name": card_info.get("name", name),
                "Category": card_info.get("type", "Unknown"),
                "Typing": card_info.get("race", "N/A"),
                "Quantity": quantity,
                "Image URL": card_info['card_images'][0]['image_url'] if 'card_images' in card_info else None,
                "Description": card_info.get("desc", ""),
                "Attack": card_info.get("atk"),
                "Defense": card_info.get("def"),
                "Level": card_info.get("level"),
                "Race": card_info.get("race"),
                "Attribute": card_info.get("attribute")
            })
        else:
            print(f"⚠ No data found for: {name}")
    else:
        print(f"❌ Failed to fetch: {name} (Status Code: {response.status_code})")

# Convert list to DataFrame
updated_df = pd.DataFrame(cards_data)

# Save to Excel
updated_df.to_excel("updated_cards.xlsx", index=False)
print("✅ Updated Excel file saved as 'updated_cards.xlsx'")
