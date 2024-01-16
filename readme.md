# Grocery Store - Online Store Web Application

This is a web application developed using Flask, Python, HTML, CSS, Jinja2, SQLite and API. The application simulates an online store where users can browse products, add them to their cart, and place orders.

## Features

- Browse and search for products by name, section, category, manufacturing date, and price.
- Add products to the cart and proceed to checkout.
- Admin dashboard for managing products, sections, and categories.
- User authentication and session management.
- User-friendly interface with responsive design.

## Technologies Used

- Python
- Flask
- HTML
- CSS (Bootstrap for styling)
- Jinja2 templating engine
- SQLAlchemy (SQLite for database)
- DateTimePicker for date selection

## Getting Started

1. Create and activate Virtual Environment: Open terminal or cmd . Navigate to the root directory of the project and type the following   commands . 
        `python -m venv venv`  :To create the virtual environment 
        `venv\Scripts\activate` :To activate the virtual environment. (in windows)
2. Install dependencies: `pip install -r requirements.txt`
3. Create the database: `flask db init && flask db migrate && flask db upgrade`
4. Run the application: `python app.py` or `flask run`
5. Open your browser and navigate to `http://localhost:8080` to access the application.


# Folder Structure

- `__pycache__`: Directory containing Python bytecode files for the application
- `instance`: Directory where your SQLite database file grocery.sqlite3 is located.
- `templates`: Directory holding HTML templates for various views of your application.
- `api.py`: Python script for API-related functionalities.
- `api.yaml` : API specification file in YAML format.
- `app.py` : Main Python script to run your Flask application.
- `readme.md` :  Documentation file describing your project.
- `requirements.txt` : File listing the required Python packages for your application.


```
├── APPDEVPROJECT1(1)
│   ├──__pycache__
│   |        └── app.cpython-310.pyc
│   |
│   ├── instance
│   |      └── grocery.sqlite3
│   |
│   | 
│   ├──  templates
│   |       ├── admin.html
│   |       ├── admindashboard.html
│   |       ├── adminlogin.html
│   |       ├── base.html
│   |       ├── edit_product.html
│   |       ├── home.html
│   |       ├── payment.html
│   |       ├── product.html
│   |       ├── productform.html 
│   |       ├── register_page.html
│   |       ├── sectioncreate.html
│   |       ├── sectionedit.html
│   |       ├── store.html
|   |       ├── user_login.html
│   |       └── userprofile.html 
│   ├── api.py
│   | 
│   ├── api.json
│   |
│   ├── api.yaml
│   |
│   ├──app.py     
│   │       
│   ├──readme.md    
│   |
│   └── requirements.txt
|

```


