from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php?name="

@app.route("/", methods=["GET", "POST"])
def index():
    card_data = None
    error = None

    if request.method == "POST":
        card_name = request.form.get("card_name")
        response = requests.get(API_URL + card_name)

        if response.status_code == 200:
            data = response.json()
            if "data" in data:
                card = data["data"][0]
                card_data = {
                    "name": card.get("name"),
                    "type": card.get("type"),
                    "attribute": card.get("attribute", "N/A"),
                    "level": card.get("level", "N/A"),
                    "race": card.get("race", "N/A"),
                    "atk": card.get("atk", "N/A"),
                    "def": card.get("def", "N/A"),
                    "desc": card.get("desc", "N/A"),
                    "image": card["card_images"][0]["image_url"]
                }
            else:
                error = "Card not found!"
        else:
            error = "Error fetching card data!"

    return render_template("index.html", card=card_data, error=error)

if __name__ == "__main__":
    app.run(debug=True)
