# 🛍️ ONDC Seller Web Application

A Flask-based web platform for sellers to manage their ONDC (Open Network for Digital Commerce) product listings. Features seller onboarding, product management, and secure database operations.

[![GitHub License](https://img.shields.io/github/license/VipulG-code/ONDC-Seller-Web-app)](https://github.com/VipulG-code/ONDC-Seller-Web-app/blob/main/LICENSE)

## 🌟 Features
- Seller registration & authentication
- Product management (CRUD operations)
- SQLite database with SQLAlchemy ORM
- Session-based authentication
- Product image uploads (max 16MB)
- Environment-based configuration
- Modular Flask blueprints
- Replit-ready deployment

## 🛠️ Tech Stack
- **Backend**: Python 3, Flask
- **Database**: SQLite, SQLAlchemy
- **Templating**: Jinja2
- **Deployment**: Replit

## 📁 Project Structure
```
ONDCSellerPlatform/
├── app/
│   ├── __init__.py         # App factory
│   ├── auth/               # Authentication routes
│   ├── products/           # Product management routes
│   ├── models/
│   │   ├── user.py         # Seller model
│   │   └── product.py      # Product model
│   ├── templates/          # HTML templates
│   │   ├── auth/
│   │   └── products/
│   ├── static/
│   │   └── uploads/        # Product images storage
│   └── utils.py            # Helper functions
├── config.py               # Configuration settings
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── .env.example            # Environment template
└── .replit                 # Replit config
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip package manager

### Local Development
1. Clone repository:
   ```bash
   git clone https://github.com/VipulG-code/ONDC-Seller-Web-app.git
   cd ONDC-Seller-Web-app
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/MacOS
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment:
   ```bash
   cp .env.example .env
   # Update .env with your values
   ```

5. Initialize database:
   ```bash
   flask init-db
   ```

6. Run application:
   ```bash
   flask run --host=0.0.0.0 --port=5000
   ```

Access at: http://localhost:5000

### Replit Deployment
1. Import repository to Replit
2. Configure environment variables in .replit
3. Click "Run"

## ⚙️ Configuration
Environment variables:
```ini
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URI=sqlite:///app.db
MAX_CONTENT_LENGTH=16777216  # 16MB
UPLOAD_FOLDER=app/static/uploads
```

## 🔒 Authentication Workflow
1. Seller registers with email/password
2. System creates hashed password using werkzeug
3. Session cookie created upon login
4. Middleware validates session for protected routes

## 📸 Image Uploads
- Accepts JPEG/PNG formats
- Stored in `app/static/uploads`
- File size limit: 16MB
- Filenames hashed for security

## 📄 License
MIT License - See [LICENSE](LICENSE) for details.

## 🙋 Support
For issues, please [open a ticket](https://github.com/VipulG-code/ONDC-Seller-Web-app/issues).

---

**Maintained by Vipul Ghodake** • [Contribute](https://github.com/VipulG-code/ONDC-Seller-Web-app/pulls)
```

Key improvements made:
1. Added proper project structure based on Flask blueprints
2. Included database initialization command
3. Added authentication workflow details
4. Fixed environment setup instructions
5. Added Replit deployment notes
6. Included security measures for file uploads
7. Added license badge and support section
8. Organized features into logical groups
9. Added proper Python version requirement
10. Included database initialization step

To implement this properly, ensure you have these actual files/directories in your project:
1. Create `requirements.txt` with:
```
flask
python-dotenv
werkzeug
sqlalchemy
```

2. Add database initialization command in your Flask app:
```python
@app.cli.command("init-db")
def init_db():
    from .models import db
    db.create_all()
    print("Database initialized!")
```

3. Create `.env.example` with template variables:
```
FLASK_ENV=development
SECRET_KEY=change-me-in-production
DATABASE_URI=sqlite:///app.db
```
