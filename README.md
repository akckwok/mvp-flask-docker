# Docker-Based Processing Pipeline Dashboard

## 1. Project Overview

This project is a web-based dashboard for submitting files to various processing pipelines that run inside Docker containers. It features a modern single-page application (SPA) interface that allows users to upload a file, select an available processing pipeline, and monitor the job's progress in real-time.

The backend is a lightweight Flask server responsible for handling file uploads, managing jobs, and orchestrating Docker container execution. The frontend is built with vanilla JavaScript, emphasizing a modular, component-based structure without the need for a heavy framework.

---

## 2. Core Features

*   **Single-Page Application (SPA):** A fluid dashboard interface with client-side routing for a seamless user experience without page reloads.
*   **Drag-and-Drop File Uploads:** An intuitive interface for selecting and uploading files.
*   **Dynamic Status Cards:** Real-time feedback for each job, showing the current status (e.g., Awaiting Selection, Processing, Complete).
*   **Simulated Log Output:** A log viewer on each status card provides mock output from the backend process, simulating a real data pipeline.
*   **Dynamic Pipeline Discovery:** The backend automatically discovers and lists available pipelines from the project's `/pipelines` directory.
*   **Containerized Processing:** Each pipeline is defined by a simple `Dockerfile`, ensuring a consistent and isolated execution environment.

---

## 3. How to Run the Project

Follow these steps to get the application running on your local machine.

### Prerequisites

*   **Python 3:** Ensure you have Python 3 installed. You can check with `python3 --version`.
*   **Docker:** The application requires Docker to build and run the processing pipelines. Make sure the Docker daemon is running. You can check by running `docker ps`.

### Installation & Setup

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install Python dependencies:**
    This project uses Flask as its web server. Install it using the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

1.  **Start the server:**
    Run the `server.py` script from the root of the project.
    ```bash
    python3 server.py
    ```
    When the server starts, it will automatically build the Docker images for all pipelines found in the `/pipelines` directory. You should see output indicating that the images are being built.

2.  **Access the dashboard:**
    Open your web browser and navigate to:
    [http://localhost:5000](http://localhost:5000)

---

## 4. Project Structure

The project is organized into a few key directories:

```
/
├── dashboard-ui/         # Contains all frontend assets (HTML, CSS, JS)
│   ├── public/           # Main index.html and styles
│   └── src/              # JavaScript source code (components, pages)
├── pipelines/            # Houses all available processing pipelines
│   ├── word-counter/     # An example pipeline
│   └── video-converter/  # Another example pipeline
├── uploads/              # Temporary storage for user-uploaded files
├── server.py             # The main Flask web server
└── README.md             # This file
```

---

## 5. Adding a New Pipeline

The application is designed to make adding new pipelines simple.

1.  **Create a new directory** inside the `/pipelines` folder. The name of this directory will be used as the pipeline's unique identifier (e.g., `/pipelines/my-new-pipeline`).

2.  **Add a `Dockerfile`** to your new directory. This file defines the environment for your pipeline.

3.  **Add a processing script** (e.g., `process.sh`, `process.py`). This script will be executed by the `CMD` instruction in your `Dockerfile`.

4.  **That's it!** The next time you start the server with `python3 server.py`, it will automatically:
    *   Discover your new pipeline.
    *   Build a Docker image for it (e.g., `my-new-pipeline-image`).
    *   List it as an option in the dropdown menu on the dashboard.
```
