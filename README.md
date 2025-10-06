# 🎟️ TBS Box Office

**HackNight Submission — Open Source Contribution Project**  
*A Django-based event ticket booking system built for rapid development, modular extensibility, and community-driven innovation.*

---

## 🚀 Overview

**TBS Box Office** is a Django-powered ticket booking platform inspired by systems like *BookMyShow*.  
It provides a seamless interface for users to browse, book, and manage event tickets, while offering a powerful admin interface for event organizers.

This repository has been restructured for **HackNight**, enabling open-source contributors to extend functionality, enhance security, and improve overall UX through well-scoped issues.

---

## 🧠 Core Objectives

- Deliver a functional, minimal, and scalable ticket booking system.  
- Encourage collaboration through clean code and modular design.  
- Provide contributors with issues spanning both **frontend** and **backend** domains.  
- Serve as an educational and open-source learning project built on Django.

---

## ⚙️ Features (Baseline)

- User authentication (sign up, login, logout)
- Event listing and detailed event pages
- Ticket booking and cancellation workflow
- Email notifications for tickets and cancellations
- Admin dashboard for event and ticket management
- Modular design for easy extension and debugging

---

## 📁 Project Structure

├── events/ # Core Django app for event and ticket logic
├── homepage/ # Landing page and general website routes
├── new/ # Optional or in-progress modules
├── static/ # Static assets (CSS, JS, images)
├── templates/ # HTML templates
├── db.sqlite3 # Default SQLite database (for dev)
├── manage.py # Django project management script
├── Pipfile / Pipfile.lock # Dependency management (Pipenv)
├── README.md # Project documentation
└── deleted_data.csv # Sample / archived data


---

## 🧰 Setup Guide

### 1. Clone the repository
```bash
git clone https://github.com/SA-10125/TBS-Box-Office-for-hacknight.git
cd TBS-Box-Office-for-hacknight
```
### 2. Set up a virtual environment (optional)
```bash
pip install pipenv
pipenv install
pipenv shell
```
### 🧩 Install Dependencies
After setting up and activating your virtual environment, install all project dependencies by running:
```bash
pip install -r requirements.txt
```
(If you face installation errors, upgrade pip first:
```bash
python -m pip install --upgrade pip
```
)
### 3. Run migrations.
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Start the server
```bash
python manage.py runserver
```
### 5. Access website
Visit http://127.0.0.1:8000/ in your browser.
