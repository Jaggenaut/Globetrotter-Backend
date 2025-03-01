# Globetrotter

Globetrotter, a full-stack web app where users get cryptic clues about a famous place and must guess which destination it refers to. Once they guess, they’ll unlock fun facts, trivia, and surprises about the destination!

# FastAPI Deployment Guide

## Prerequisites

Ensure you have the following installed:

- Python 3.8+
- Virtualenv (optional but recommended)
- PostgreSQL or any other database (if applicable)
- Git
- Uvicorn (for running the FastAPI server)

## Deployment Steps

### 1. Clone the Repository

```sh
git clone <repository_url>
cd <project_directory>
```

### 2. Create and Activate a Virtual Environment (Optional but Recommended)

```sh
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```sh
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file and configure your environment variables:

```
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### 5. Start the FastAPI Server

```sh
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Test the API

Open a browser or use `curl`/Postman to test the API at:

```
http://127.0.0.1:8000/docs
```

## Conclusion

This guide covers the basic steps to deploy a FastAPI application. You may need to customize it based on your specific project requirements.
