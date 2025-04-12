# Streamlit Web Application

A simple web application built with Streamlit that includes user authentication and management.

## Features

- User authentication with login/logout functionality
- Admin panel for user management
- Two sections with different content
- Persistent user data stored in SQLite database
- Password hashing for security

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:
   ```bash
   streamlit run app.py
   ```
2. Access the application at http://localhost:8501
3. Login with default admin credentials:
   - Username: admin
   - Password: admin123

## Admin Features

- Create new users
- Update user passwords
- Manage user privileges

## Security

- Passwords are hashed using SHA-256
- User sessions are managed using Streamlit's session state
- Admin privileges are required for user management

## Project Structure

- `app.py`: Main application file
- `users.db`: SQLite database for user data
- `requirements.txt`: Project dependencies
- `README.md`: Project documentation 