# 🎟️ TBS Box Office

**HackNight Submission — Open Source Contribution Project**  
*A Django-based event ticket booking system built for rapid development, modular extensibility, and community-driven innovation.*

---

## 🚀 Overview

**TBS Box Office** is a Django-powered ticket booking platform inspired by systems like *BookMyShow*.  
It provides a seamless interface for users to browse, book, and manage event tickets, while offering a powerful admin interface for event organizers and helps the admins traack each ticket's life cycle and get data on events and how theyre booked.

---

## 🧠 Core Objectives

- Deliver a functional, minimal, and scalable ticket booking system.  
- There is no payment gateway as it is free for the students having a USN and password.
- full fleged, robust, batteries included and ready to go website.

---

## ⚙️ Features (Baseline)

- User authentication (sign up, login, logout)
- Event listing and detailed event pages
- Ticket booking and cancellation workflow
- Admin dashboard for event and ticket management
- Modular design for easy extension and debugging

---

## 📁 Project Structure

├── events/ # Core Django app for event and ticket logic\
├── homepage/ # Landing page and general website routes\
├── new/ # Optional or in-progress modules\
├── static/ # Static assets (CSS, JS, images)\
├── templates/ # HTML templates\
├── db.sqlite3 # Default SQLite database (for dev)\
├── manage.py # Django project management script\
├── Pipfile / Pipfile.lock # Dependency management (Pipenv)\
├── README.md # Project documentation\
└── deleted_data.csv # Sample / archived data\


---

## Tech stack
*Python (Django)*, *HTML*, *CSS*, *JavaScript*

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

### 6. To access the Django Admin panel:
```bash
python manage.py createsuperuser
```

---

## Maintainer in charge: *Suraj Acharya*, Github: *SA-10125*

---

## How to Contribute
### 1. Fork the repository on GitHub.
### 2. Clone your forked repository:
### 3. Create a new branch for your feature or fix:
### 4. Make your changes and commit them with clear, descriptive messages:
### 5. Push your changes to your fork:
### 6. Open a Pull Request (PR) from your branch to the main branch of the original repository, describing your changes in detail.

---

##Please refer to CONTRIBUTING.md
