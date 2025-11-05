# 🤖 Automated Game Platform Orchestrator

This repository contains the core agents and orchestration logic for the automated game creation and marketing pipeline. The primary scheduling file is `orchestrator.py`.

## 🛠️ Project Setup

### 1. Dependency Management (Using uv)

We use `uv` for ultra-fast dependency management and virtual environment handling.

* **Install uv:** Ensure `uv` is installed on your system: `pip install uv`.
* **Create Virtual Environment:** Create the `.venv` folder: `uv venv`.
* **Activate Environment:**
    * **Windows:** `.venv\Scripts\activate` 
    * **Linux/macOS:** `source .venv/bin/activate`
* **Install Dependencies:** Install all necessary packages: `uv add -r requirements.txt`.

### 2. Configuration Files

Configuration settings are isolated into two files: one for secrets (`.env`) and one for MySQL connection details (`config.py`).

#### A. Secrets (`.env`)

Create a file named `.env` in the root directory to store sensitive API keys. This file **must not** be committed to Git.

```

# .env file (DO NOT COMMIT)

# API key for the Payment Service (e.g., Stripe, OpenAI)

OPENAI_API_KEY = ''
STRIPE\_API\_KEY="sk\_live\_XXXXXXXXXXXXXXXXXXXXXX"

# Placeholder for any other sensitive keys

EXTERNAL\_SERVICE\_API\_KEY="XYZ123ABC"

````

#### B. MySQL Configuration (`config.py`)

Create a file named `config.ini` for database connection details.

```
HOST = 127.0.0.1
DATABASE = game_platform_db
USER = db_user
PASSWORD = strong_db_password
PORT = 3306
````

## ✅ Running Tests

Tests are run using `pytest` for real database calls.

  * **Install Pytest:** Ensure `pytest` are installed use `uv sync`.
  * **Run All Tests:** Execute `pytest -v` from the project root.
  * **Fix Pytest Warning:** The `pytest.ini` file is configured to suppress the `__init__` constructor warning.

## ⏰ Scheduling the Orchestrator (Windows Task Scheduler)

The `orchestrator.py` script must be scheduled to run every 24 hours using the Python interpreter inside your `.venv`.

**1. Create a New Task:**

  * Open **Task Scheduler** (search for it in the Start Menu).
  * In the Actions pane, click **"Create Basic Task."**

**2. Set Trigger (Every 24 Hours):**

  * **Trigger:** Select **Daily**.
  * **Recur every:** `1` day.

**3. Set Action (The Program):**

  * **Action:** Select **"Start a program."**
  * **Program/Script:** Provide the **full path** to your virtual environment's Python interpreter.
      * *Example:* `C:\Users\YourName\projects\game-platform\.venv\Scripts\python.exe`
  * **Add arguments (optional):** Provide the **full path** to your `orchestrator.py` script.
      * *Example:* `C:\Users\YourName\projects\game-platform\orchestrator.py`
  * **Start in (optional):** Set the working directory to the project root (recommended for logger and config file path resolution).
      * *Example:* `C:\Users\YourName\projects\game-platform\`

**4. Finalize:** Complete the task creation wizard. The script will now execute every 24 hours using the isolated environment.

```
```