# Docker-Based Processing Pipeline Dashboard

## 1. Project Overview

This project is a web-based dashboard for submitting files to various processing pipelines that run inside Docker containers. It features a modern single-page application (SPA) interface built with Vite and vanilla JavaScript, allowing users to upload files, select a processing pipeline, and monitor job progress.

The backend is a refactored Flask application that handles file uploads, manages jobs in a persistent SQLite database, and orchestrates Docker container execution using the `docker-py` library.

---

## 2. Core Features

*   **Modern SPA Frontend:** A fluid dashboard interface powered by Vite for a fast development experience and an optimized production build.
*   **Persistent Job-Queue:** Jobs are stored in an SQLite database, so they are not lost on server restart.
*   **Dynamic Pipeline Discovery:** The backend automatically discovers and lists available pipelines from the project's `/pipelines` directory.
*   **Containerized Processing:** Each pipeline runs in a Docker container, ensuring a consistent and isolated execution environment.

---

## 3. How to Run the Project

### Prerequisites

*   **Python 3:** Ensure you have Python 3 installed.
*   **Node.js and npm:** Required for the frontend.
*   **Docker:** The application requires Docker to run the processing pipelines.

### Docker without `sudo` (Recommended)

To run Docker commands without `sudo`, you should add your user to the `docker` group:
```bash
sudo usermod -aG docker ${USER}
```
You will need to log out and log back in for this change to take effect.

### Easy Setup with `setup.sh`

For a quick start, you can use the provided setup script. This script will install all dependencies, build the pipeline images, and build the frontend for production.

```bash
./setup.sh
```

After the script finishes, you can run the application in production mode with `python run.py`.

### Manual Installation

If you prefer to install the components manually, follow these steps:

1.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Install frontend dependencies:**
    ```bash
    npm install --prefix dashboard-ui
    ```
3.  **Build the Pipeline Images:**
    The application expects that the Docker images for the pipelines have been pre-built. You need to build an image for each pipeline defined in the `/pipelines` directory. For example:
    ```bash
    docker build -t word-counter-image ./pipelines/word-counter
    ```

---

## 4. Running the Application

There are two ways to run the application:

### Production Mode

In this mode, the Flask server serves the optimized frontend build.

1.  **Build the frontend:**
    ```bash
    npm run build --prefix dashboard-ui
    ```
2.  **Run the Flask server:**
    ```bash
    python run.py
    ```

### Development Mode

For development, you should run the Flask backend and the Vite dev server separately. This provides hot-reloading for the frontend.

1.  **Run the Flask backend:**
    ```bash
    python run.py
    ```
2.  **In a separate terminal, run the Vite dev server:**
    ```bash
    npm run dev --prefix dashboard-ui
    ```
    The Vite server will proxy API requests to the Flask backend (by default on port 5000). You will need to add a `vite.config.js` to configure the proxy.

---

## 5. Project Structure

The project is organized into a clean, separated backend and frontend structure.

```
/
├── backend/              # All Python/Flask backend code
├── dashboard-ui/         # All frontend assets (JS, CSS, etc.)
│   ├── src/              # Frontend source code
│   └── package.json      # Frontend dependencies
├── pipelines/            # Houses all available processing pipelines
├── uploads/              # Temporary storage for user-uploaded files
├── run.py                # Script to run the Flask server
└── README.md             # This file
```
