# Contributing to Smart Crop Care Assistant

First off, thank you for considering contributing to this project! This guide will help you get your development environment set up and running.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

*   **Python** (version 3.9 or higher)
*   **Git** for version control
*   **VS Code** (or your preferred code editor)

## Setup Instructions

Follow these steps to get the application running on your local machine.

### 1. Clone the Repository

Open your terminal, navigate to the directory where you want to store the project, and clone the repository:

```bash
git clone <your-repository-url>
cd smart_agriculture_app
```

### 2. Create and Activate a Virtual Environment

It is highly recommended to use a virtual environment to manage project dependencies and avoid conflicts with other Python projects.

**On Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS and Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

After activation, you should see `(venv)` at the beginning of your terminal prompt.

### 3. Install Dependencies

Install all the required Python packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

This command will install Flask, SQLAlchemy, and all other necessary libraries for the project.

### 4. Configure Environment Variables

The application uses environment variables for configuration. These are stored in a `.env` file.

1.  **Create the `.env` file** by making a copy of the example file:

    **On Windows:**

    ```bash
    copy .env.example .env
    ```

    **On macOS and Linux:**

    ```bash
    cp .env.example .env
    ```

2.  **Review the `.env` file:** Open the newly created `.env` file in your editor. The default settings are configured for local development using an SQLite database, so you may not need to change anything to get started.

    Key variables include:
    *   `SECRET_KEY`: A secret key for session management. A default is provided.
    *   `DATABASE_URL`: Defaults to `sqlite:///smart_agriculture.db`, which will create a local database file.
    *   `PLANTNET_API_KEY`: An optional key for the plant identification feature. The app will function without it, but this feature will be disabled.

### 5. Set Up the Database

The application uses Flask-Migrate to manage database schema changes.

1.  **Apply Database Migrations:** Run the following command to create the database and apply all migrations:

    ```bash
    flask db upgrade
    ```

2.  **Populate Initial Data:** To get started with some sample data (like crop types and disease information), run the population script:

    ```bash
    python populate_crop_data.py
    ```

### 6. (Optional) Create a Test User

To make testing easier, you can create a pre-configured test user with sample farms and crops:

```bash
python create_test_user.py
```

### 7. Run the Application

You are now ready to run the application!

```bash
python run.py
```

The application will start, and you can access it by opening your web browser and navigating to:

**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

You can log in with the test user credentials created in the previous step or register a new user.

---

Happy coding, and we look forward to your contributions!
