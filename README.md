# NAIRO

NAIRO is a Python-based AI assistant with a modular "senses" architecture. It's designed to be a calm, professional, and proactive assistant, similar to J.A.R.V.I.S. The core of the application orchestrates different sense modules, which provide various functionalities. The initial implementation includes a web-based chat interface and a Discord bot. The AI's personality is configured to be similar to J.A.R.V.I.S. from the Iron Man movies—calm, professional, and proactive.

## Features

*   **Modular "Senses" Architecture:** Easily extendable with new functionalities by adding new "sense" modules.
*   **Dynamic Model Switching:** Automatically switches between the Gemini API and a local model based on internet connectivity.
*   **Web Interface:** A simple web-based chat interface to interact with the AI.
*   **Discord Bot:** A Discord bot that responds to messages in a server.
*   **Asynchronous Core:** Built with `asyncio` for efficient handling of concurrent operations.
*   **Configurable:** Most settings can be configured in the `config.py` file.

## Getting Started

### Prerequisites

*   Python 3.x
*   An environment with the packages from `requirements.txt` installed.

### Installation

1.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration:**
    *   Create a `.env` file in the project root.
    *   Add your Gemini API key to the `.env` file:
        ```
        GEMINI_API_KEY="YOUR_API_KEY_HERE"
        ```
    *   To use the Discord sense, add your Discord bot token to the `.env` file:
        ```
        DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
        ```

### Running the Application

To run the application, execute the main script:

```bash
python src/main.py
```

By default, this will start the web interface, which can be accessed at `http://localhost:5000`.

## Development Conventions

*   **Modular Architecture:** The project is structured around "senses," which are self-contained modules for different functionalities. New features should be implemented as new sense modules.
*   **Configuration:** All configuration is managed in the `config.py` file. Secrets and environment-specific settings are loaded from a `.env` file.
*   **Logging:** The project uses Python's built-in `logging` module. A custom logger is configured in `src/utils/logger_config.py`.
*   **AI Personality:** The AI's personality is defined by the system message in `src/core/model_manager.py`. This should be maintained to ensure a consistent user experience.
*   **Asynchronous Code:** The project heavily relies on `asyncio` for concurrent operations. New code should be written in an asynchronous style where appropriate.