# Rental_project
Đồ án 1 của mình
# Rental Project

## Mô tả
Dự án này là một website tìm nhà trọ cho sinh viên, cho phép sinh viên xem danh sách nhà trọ và chủ nhà đăng tin cho thuê. Hệ thống sử dụng Flask làm backend, MongoDB làm cơ sở dữ liệu, và Mapbox API để hiển thị bản đồ.

## Cấu trúc thư mục
```
/rental_project
│── /templates
│   ├── index.html        # Giao diện chính hiển thị danh sách nhà trọ
│   ├── add_listing.html  # Form để chủ nhà đăng tin
│── /static
│   ├── /css
│   │   ├── style.css     # CSS cho giao diện
│   ├── /js
│   │   ├── script.js     # JavaScript để gọi API và hiển thị bản đồ với Mapbox
│── app.py                # Flask backend
│── requirements.txt       # Danh sách thư viện cần cài đặt
│── config.py              # Cấu hình Flask và MongoDB
│── README.md              # Hướng dẫn cài đặt và chạy dự án
```

## Cài đặt
### 1. Cài đặt môi trường
Yêu cầu Python 3.8+ và MongoDB.
```bash
python -m venv venv
source venv/bin/activate  # Trên macOS/Linux
venv\Scripts\activate     # Trên Windows
pip install -r requirements.txt
```

### 2. Cấu hình môi trường
Tạo file `.env` và thêm thông tin kết nối MongoDB:
```
MONGO_URI=mongodb://localhost:27017/rental_db
```

### 3. Chạy ứng dụng
```bash
python app.py
```
Ứng dụng sẽ chạy tại `http://127.0.0.1:5000`

## Tính năng
- Sinh viên có thể tìm kiếm, xem danh sách nhà trọ.
- Chủ nhà có thể đăng ký, đăng tin cho thuê.
- Tích hợp Mapbox API để hiển thị vị trí nhà trọ.

## Liên hệ
Nếu có bất kỳ vấn đề gì, vui lòng liên hệ qua email: phong150403@gmail.com


# Rental_project
