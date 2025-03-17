# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import requests
import os
from bson.json_util import dumps

app = Flask(__name__)

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["rental_db"]
listings_collection = db["listings"]

# API Key của Mapbox
MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoicGhvbmdkZCIsImEiOiJjbTg4Z25ocnAwMTgzMmlwcHU4N3hobmo5In0.hna31Ganho4KuG5Ml5fw1g"

def geocode_address(address):
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{requests.utils.quote(address)}.json?access_token={MAPBOX_ACCESS_TOKEN}"
    response = requests.get(url)
    data = response.json()
    if "features" in data and len(data["features"]) > 0:
        coordinates = data["features"][0]["geometry"]["coordinates"]
        return coordinates[1], coordinates[0]  # Trả về latitude, longitude
    return None, None

@app.route("/api/listings", methods=["GET"])
def home():
    return app.send_static_file("index.html")

@app.route("/get_listings", methods=["GET"])
def get_listings():
    # Lấy tham số tìm kiếm từ query string
    longitude = request.args.get("longitude", type=float)
    latitude = request.args.get("latitude", type=float)

    query = {}
    if longitude and latitude:
        # Tìm các nhà trọ trong phạm vi 10km từ vị trí tìm kiếm
        query = {
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "$maxDistance": 10000  # 10km
                }
            }
        }

    # Lấy danh sách nhà trọ từ MongoDB
    listings = list(listings_collection.find(query, {"_id": 0}))
    return jsonify(listings)

@app.route("/add_listing", methods=["POST"])
def add_listing():
    data = request.json
    title = data.get("title")
    address = data.get("address")
    price = data.get("price")
    image_url = data.get("image_url")
    video_url = data.get("video_url")
    
    # Xác định tọa độ từ địa chỉ
    latitude, longitude = geocode_address(address)
    
    listing = {
        "title": title,
        "address": address,
        "price": price,
        "latitude": latitude,
        "longitude": longitude,
        "image_url": image_url,
        "video_url": video_url,
        "location": {
            "type": "Point",
            "coordinates": [longitude, latitude]
        }
    }
    
    listings_collection.insert_one(listing)
    return jsonify({"success": True, "message": "Nhà trọ đã được thêm!"})

if __name__ == "__main__":
    app.run(debug=True, port=5001)