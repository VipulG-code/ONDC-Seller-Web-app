# 🛒 ONDC Seller Web App
A web-based application for sellers to manage their listings on the **Open Network for Digital Commerce (ONDC)**. Built with Python and Flask, this app provides a foundational backend system for seller onboarding, product uploads, and database management.

## 🔗 Live Repository
[GitHub Repository Link](https://github.com/VipulG-code/ONDC-Seller-Web-app)

## 📌 Features
- Seller account setup and session management
- Product listings and uploads
- SQLite-based database with SQLAlchemy ORM
- Secure configuration with environment variable support
- Modular Flask app structure
- Image upload functionality (up to 16MB)

## 🚀 Technologies Used
- **Python 3**
- **Flask**
- **SQLAlchemy**
- **SQLite**
- **Replit deployment support** (via `.replit` and `pyproject.toml`)

## 🗂️ Project Structure
```
ONDCSellerPlatform/
├── app.py                  # Entry point for creating Flask app
├── main.py                 # Run script for the server
├── config.py               # Configuration settings (dev & prod)
├── pyproject.toml          # Dependencies and metadata
├── uv.lock                 # Replit environment lock file
├── .replit                 # Replit project config
├── /app/static/uploads     # Upload folder for product images
├── /app/templates          # (Expected) HTML templates for UI
├── /app/models             # (Expected) DB Models
├── /app/routes             # (Expected) Flask route files
└── /app/                   # Application package
```

Getting Started
Setup Instructions
Clone the Repository
git clone https://github.com/VipulG-code/ONDC-Seller-Web-app.git
cd ONDC-Seller-Web-app

Create Virtual Environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install Dependencies
pip install -r requirements.txt

Run the App
python main.py
The server will run on http://0.0.0.0:5000.

## 🛡️ Configuration
You can configure the app using environment variables or directly in config.py.

## Author
Vipul Ghodake

##📃 License
This project is licensed under the MIT License. See LICENSE for details.
