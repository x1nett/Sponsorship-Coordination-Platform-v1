# Sponsorship Influencer Coordination Platform

This platform allows sponsors and influencers to coordinate campaigns. Sponsors can create ad requests, and influencers can accept or negotiate these requests, facilitating seamless sponsorship deals.

## Features

- **Sponsor Campaign Management**: Sponsors can create and manage their advertising campaigns.
- **Influencer Coordination**: Influencers can browse campaigns, accept, or negotiate offers.
- **Secure Login**: Utilizes Flask-Login and bcrypt for secure user authentication.
- **Data Persistence**: Uses SQLAlchemy to manage and persist data.
- **Pagination**: Paginated data to efficiently display large sets of results.
- **Data Visualization**: Basic data visualization using Matplotlib.
- **Random Data Generation**: Faker is used to generate mock data for testing purposes.

## Tech Stack

- **Frontend**: HTML, Bootstrap
- **Backend**: Flask
- **Database**: Flask-SQLAlchemy (using SQLAlchemy ORM)
- **Authentication**: Flask-Login, Flask-Bcrypt
- **Visualization**: Matplotlib

## Prerequisites

Ensure you have the following installed:

- Python 3.x
- Virtual Environment (optional but recommended)

## Libraries Used

Install the following Python dependencies by running `pip install -r requirements.txt`:

- Faker==26.0.0
- Flask==3.0.3
- Flask_Bcrypt==1.0.1
- Flask_Login==0.6.3
- flask_sqlalchemy==3.1.1
- matplotlib==3.8.3
- python-dotenv==1.0.1
- SQLAlchemy==2.0.31

## Installation and Setup

1. Navigate to the project folder:

2. Create a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Run the application:

    ```bash
    python app.py
    ```

5. Open your browser and visit `http://127.0.0.1:5000` to view the platform.

## Configuration

The application uses environment variables for sensitive information. Create a `.env` file in the root directory and add the required configurations:

- `SECRET_KEY`: A secure random key for session management.
- `SQLALCHEMY_DATABASE_URI`: The path to your SQLite database file.
- `ADMIN_EMAIL`: The admin user's email.
- `ADMIN_PASSWORD`: The admin user's password.
