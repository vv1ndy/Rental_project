# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import requests
import os

app = Flask(__name__)

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["rental_db"]
listings_collection = db["listings"]

# API Key của Mapbox
MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoicGhvbmdkZCIsImEiOiJjbTg4Z25ocnAwMTgzMmlwcHU4N3hobmo5In0.hna31Ganho4KuG5Ml5fw1g"

def geocode_address(address):
    """ Chuyển địa chỉ thành tọa độ bằng Mapbox API """
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{requests.utils.quote(address)}.json?access_token={MAPBOX_ACCESS_TOKEN}"
    response = requests.get(url)
    data = response.json()
    if "features" in data and len(data["features"]) > 0:
        coordinates = data["features"][0]["geometry"]["coordinates"]
        return coordinates[1], coordinates[0]  # Latitude, Longitude
    return None, None

@app.route("/")
def home():
    """ Hiển thị trang chủ """
    return render_template("index.html")

@app.route("/get_listings", methods=["GET"])
def get_listings():
    """ Lấy danh sách nhà trọ từ MongoDB """
    listings = list(listings_collection.find({}, {"_id": 0}))  # Đọc từ `listings_collection`
    return jsonify(listings)

@app.route("/add_listing", methods=["POST"])
def add_listing():
    """ Thêm nhà trọ vào database """
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
        "video_url": video_url
    }

    listings_collection.insert_one(listing)
    return jsonify({"message": "Nhà trọ đã được thêm!"})

if __name__ == "__main__":
    app.run(debug=True, port=5001)
