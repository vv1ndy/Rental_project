# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, send_from_directory
from pymongo import MongoClient
import requests
import os
from bson.json_util import dumps

app = Flask(__name__, static_folder="static", template_folder="templates")

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

@app.route("/")
def home():
    return render_template("index.html")  # Trả về trang chủ

@app.route("/get_listings", methods=["GET"])
def get_listings():
    try:
        listings = list(listings_collection.find({}, {"_id": 0}))  # Lấy danh sách nhà trọ từ MongoDB
        return jsonify(listings)
    except Exception as e:
        print("Lỗi khi lấy danh sách nhà trọ:", e)
        return jsonify({"error": "Lỗi khi lấy danh sách nhà trọ"}), 500

@app.route("/add_listing", methods=["GET", "POST"])
def add_listing():
    print("⚡ Nhận request:", request.method)  # Debug request method
    if request.method == "POST":
        try:
            data = request.json
            title = data.get('title')
            address = data.get('address')
            price = data.get('price')
            image_url = data.get('image_url')
            description = data.get('description')

            # Xác định tọa độ từ địa chỉ
            latitude, longitude = geocode_address(address)

            # Kiểm tra các trường bắt buộc
            if not all([title, address, price, image_url, description, latitude, longitude]):
                return jsonify({"success": False, "message": "Thiếu thông tin bắt buộc"}), 400

            # Lưu thông tin nhà trọ vào MongoDB
            listing = {
                "title": title,
                "address": address,
                "price": price,
                "image_url": image_url,
                "description": description,
                "latitude": latitude,
                "longitude": longitude,
                "location": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                }
            }
            listings_collection.insert_one(listing)

            return jsonify({"success": True, "message": "Nhà trọ đã được thêm thành công!"}), 201
        except Exception as e:
            print("Lỗi khi thêm nhà trọ:", str(e))
            return jsonify({"success": False, "message": "Đã xảy ra lỗi khi thêm nhà trọ"}), 500

    # Nếu là GET, trả về giao diện thêm nhà trọ
    return render_template("add_listing.html")

# Serve static files (CSS, JS, images)
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
