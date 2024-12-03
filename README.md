# 🛒 E-Commerce Web Application

Welcome to the E-Commerce Web Application! This project is a fully functional e-commerce platform built with Flask and SQLAlchemy. It includes features such as user registration, product management, shopping cart, order processing, and an admin dashboard.

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- User Registration and Authentication
- Product Management
- Shopping Cart
- Order Processing
- Admin Dashboard
- Inventory Management
- Reviews and Ratings

## 🛠️ Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/ecommerce-app.git
    cd ecommerce-app
    ```

2. **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the database:**
    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

5. **Run the application:**
    ```bash
    flask run
    ```

## 🚀 Usage

- **Home Page:** Browse products, search, and filter by categories.
- **Product Page:** View product details and add to cart.
- **Cart:** View and manage items in your cart.
- **Checkout:** Place orders and provide shipping information.
- **Admin Dashboard:** Manage products, users, orders, and inventory.

## 📂 Project Structure

```plaintext
.
├── src/
│   ├── app.py              # Main application file
│   ├── models.py           # Database models
│   ├── forms.py            # Flask-WTF forms
│   ├── restoreDatabase.py  # Script to restore the database
│   ├── templates/          # HTML templates
│   └── static/             # Static files (CSS, JS, images)
├── requirements.txt        # Python dependencies
└── README.md               # Project README

```

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

Fork the repository.
Create a new branch (git checkout -b feature-branch).
Make your changes.
Commit your changes (git commit -m 'Add new feature').
Push to the branch (git push origin feature-branch).
Open a pull request.

## 📜 License 
This project is licensed under the MIT License. See the LICENSE file for details.

Made with ❤️ by Heanan Brody Bird
