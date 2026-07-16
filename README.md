# FastAPI Hello API

A lightweight, modern FastAPI application designed for quick deployment on Render. It exposes a simple API that returns `"Hello"` and a health check endpoint.

## Features

- **FastAPI**: Modern, fast (high-performance), web framework for building APIs with Python.
- **Render Ready**: Pre-configured for easy deployment on Render as a Web Service.
- **CORS Enabled**: Configured to allow cross-origin requests.
- **Health Check Endpoint**: `/health` for monitoring service status.

---

## Local Development

### Prerequisites

- Python 3.8+
- Git

### Running Locally

1. **Clone the repository** (if you have already pushed it to GitHub):
   ```bash
   git clone <your-repo-url>
   cd fastapi-hello-app
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**:
   - **Windows**:
     ```powershell
     .venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**:
   ```bash
   python main.py
   ```
   Or run using Uvicorn directly:
   ```bash
   uvicorn main:app --reload
   ```

6. **Test the API**:
   Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. You should see:
   ```json
   {"message": "Hello"}
   ```

   You can also access the interactive API documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## Deploying to Render

To deploy this API to [Render](https://render.com/), follow these steps:

1. **Push the repository to GitHub** (see the next section if you haven't done this yet).
2. Go to your **Render Dashboard** and click **New > Web Service**.
3. Connect your GitHub account and select the **fastapi-hello-app** repository.
4. Configure the service:
   - **Language**: `Python`
   - **Branch**: `main`
   - **Region**: Select a region close to your users.
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     uvicorn main:app --host 0.0.0.0 --port $PORT
     ```
5. Click **Create Web Service**. Render will build and deploy your FastAPI application.
