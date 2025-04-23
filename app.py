# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for, flash
from pymongo import MongoClient
import requests
import os
from bson.json_util import dumps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = 'your-secret-key-here'  # Thay đổi thành key bí mật của bạn

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["rental_db"]
listings_collection = db["listings"]
users_collection = db["users"]

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
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = request.form.get("remember")

        # Kiểm tra email và mật khẩu có được nhập không
        if not email or not password:
            flash("Vui lòng nhập đầy đủ email và mật khẩu", "error")
            return redirect(url_for("login"))

        # Tìm user trong database
        user = users_collection.find_one({"email": email})
        
        if user:
            # Kiểm tra mật khẩu
            if check_password_hash(user["password"], password):
                # Kiểm tra tài khoản có bị khóa không
                if user.get("is_locked", False):
                    flash("Tài khoản của bạn đã bị khóa. Vui lòng liên hệ quản trị viên.", "error")
                    return redirect(url_for("login"))
                
                # Kiểm tra tài khoản có bị vô hiệu hóa không
                if user.get("is_disabled", False):
                    flash("Tài khoản của bạn đã bị vô hiệu hóa.", "error")
                    return redirect(url_for("login"))
                
                # Đăng nhập thành công
                session["user_id"] = str(user["_id"])
                session["user_name"] = user["name"]
                session["user_email"] = user["email"]
                session["user_role"] = user.get("role", "user")
                
                # Cập nhật thời gian đăng nhập cuối
                users_collection.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"last_login": datetime.now()}}
                )
                
                if remember:
                    session.permanent = True
                
                flash("Đăng nhập thành công!", "success")
                return redirect(url_for("home"))
            else:
                # Tăng số lần đăng nhập sai
                users_collection.update_one(
                    {"_id": user["_id"]},
                    {"$inc": {"failed_login_attempts": 1}}
                )
                
                # Kiểm tra số lần đăng nhập sai
                user = users_collection.find_one({"_id": user["_id"]})
                if user.get("failed_login_attempts", 0) >= 5:
                    # Khóa tài khoản sau 5 lần đăng nhập sai
                    users_collection.update_one(
                        {"_id": user["_id"]},
                        {"$set": {"is_locked": True}}
                    )
                    flash("Tài khoản của bạn đã bị khóa do đăng nhập sai quá nhiều lần. Vui lòng liên hệ quản trị viên.", "error")
                else:
                    flash("Mật khẩu không đúng. Bạn còn " + str(5 - user.get("failed_login_attempts", 0)) + " lần thử.", "error")
        else:
            flash("Email không tồn tại trong hệ thống", "error")
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Lấy thông tin từ form
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        terms = request.form.get("terms")

        # Kiểm tra các trường bắt buộc
        if not all([name, email, phone, password, confirm_password]):
            flash("Vui lòng điền đầy đủ thông tin", "error")
            return redirect(url_for("register"))

        # Kiểm tra email đã tồn tại chưa
        if users_collection.find_one({"email": email}):
            flash("Email đã được sử dụng", "error")
            return redirect(url_for("register"))
        
        # Kiểm tra mật khẩu
        if password != confirm_password:
            flash("Mật khẩu không trùng khớp", "error")
            return redirect(url_for("register"))
        
        # Kiểm tra điều khoản
        if not terms:
            flash("Bạn cần đồng ý với điều khoản sử dụng", "error")
            return redirect(url_for("register"))

        # Kiểm tra độ dài mật khẩu
        if len(password) < 6:
            flash("Mật khẩu phải có ít nhất 6 ký tự", "error")
            return redirect(url_for("register"))

        # Tạo user mới với thông tin đầy đủ
        user = {
            "name": name,
            "email": email,
            "phone": phone,
            "password": generate_password_hash(password),
            "created_at": datetime.now(),
            "role": "user",
            "is_locked": False,
            "is_disabled": False,
            "failed_login_attempts": 0,
            "last_login": None,
            "profile": {
                "avatar": None,
                "address": None,
                "bio": None
            },
            "settings": {
                "email_notifications": True,
                "sms_notifications": True
            }
        }
        
        try:
            # Thêm user vào MongoDB
            result = users_collection.insert_one(user)
            
            if result.inserted_id:
                flash("Đăng ký thành công! Vui lòng đăng nhập.", "success")
                return redirect(url_for("login"))
            else:
                flash("Đã xảy ra lỗi khi đăng ký. Vui lòng thử lại.", "error")
        except Exception as e:
            flash(f"Lỗi hệ thống: {str(e)}", "error")
    
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Đã đăng xuất thành công", "success")
    return redirect(url_for("home"))

# Kiểm tra đăng nhập cho các route cần xác thực
def login_required(f):
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Vui lòng đăng nhập để tiếp tục", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route("/get_listings", methods=["GET"])
def get_listings():
    try:
        listings = list(listings_collection.find({}, {"_id": 0}))
        return jsonify(listings)
    except Exception as e:
        print("Lỗi khi lấy danh sách nhà trọ:", e)
        return jsonify({"error": "Lỗi khi lấy danh sách nhà trọ"}), 500

@app.route("/add_listing", methods=["GET", "POST"])
@login_required
def add_listing():
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
                },
                "user_id": session["user_id"],
                "created_at": datetime.now()
            }
            listings_collection.insert_one(listing)

            return jsonify({"success": True, "message": "Nhà trọ đã được thêm thành công!"}), 201
        except Exception as e:
            print("Lỗi khi thêm nhà trọ:", str(e))
            return jsonify({"success": False, "message": "Đã xảy ra lỗi khi thêm nhà trọ"}), 500

    return render_template("add_listing.html")

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
