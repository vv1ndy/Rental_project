from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
import os

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/rental_db"
mongo = PyMongo(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_listing', methods=['POST'])
def add_listing():
    data = request.json
    listing = {
        "title": data.get("title"),
        "address": data.get("address"),
        "price": data.get("price"),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude")
    }
    listing_id = mongo.db.listings.insert_one(listing).inserted_id
    return jsonify({"message": "Listing added", "id": str(listing_id)})

@app.route('/get_listings', methods=['GET'])
def get_listings():
    listings = mongo.db.listings.find()
    listings_list = []
    for listing in listings:
        listings_list.append({
            "id": str(listing["_id"]),
            "title": listing["title"],
            "address": listing["address"],
            "price": listing["price"],
            "latitude": listing["latitude"],
            "longitude": listing["longitude"]
        })
    return jsonify(listings_list)

if __name__ == '__main__':
    app.run(debug=True)

