from flask import Flask, render_template, request, jsonify
import pandas as pd
import requests

app = Flask(__name__)

# Load card data from updated_cards.xlsx
def load_card_data():
    try:
        df = pd.read_excel("updated_cards.xlsx")
        return df.to_dict(orient="records")  # Convert to list of dictionaries
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return []

# Fetch card details from YGOPRODECK API
def fetch_card_details(card_name):
    api_url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?name={card_name}"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        if "data" in data:
            return data["data"][0]  # Return first matching card
    return None

# Initial load of card data
cards = load_card_data()

@app.route("/")
def home():
    return render_template("index.html", cards=cards)

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "No search query provided"}), 400
    
    # Find matching cards
    results = [card for card in cards if query.lower() in card["Card Name"].lower()]
    
    # If no results, try fetching from API
    if not results:
        api_card = fetch_card_details(query)
        if api_card:
            results = [api_card]
    
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
