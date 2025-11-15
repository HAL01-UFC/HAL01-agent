# HAL01-agent
POC of the HAL01 conversational agent, for use in the UFC ecosystem.

## Installation

1. Clone the repository:
   ```bash
   https://github.com/HAL01-UFC/HAL01-agent.git
   cd HAL01-agent
   ```

2. Install dependencies:
   
   With `uv` (recommended for faster installation):
   ```bash
   # Install uv if you don't have it
   pip install uv
   
   # Create and activate a virtual environment
   uv venv

   # TO ACTIVATE:
   # On Windows
   .venv\Scripts\activate
   # On Mac/Linux
   source .venv/bin/activate
   
   # Install dependencies from pyproject.toml
   uv pip install -e .
   ```

   to add a new dependency:
    ```bash
      uv add dependency
      ```

3. Set up environment variables (create a `.env` file with the following variables):
   ```
    no variables yet =)
   ```

4. Run the application:

    api
    ```bash
    uv run uvicorn app.main:app --reload --port 3000
    ```
    cli
    ```bash
    python -m app.main
    ```



## API Endpoints

### Chat Endpoints

- `POST /api/agent`: Generate AI responses to user messages
