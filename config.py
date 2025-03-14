import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
    MONGO_URI = "mongodb://localhost:27017/rental_db"
    MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoicGhvbmdkZCIsImEiOiJjbTg4Z25ocnAwMTgzMmlwcHU4N3hobmo5In0.hna31Ganho4KuG5Ml5fw1g"
