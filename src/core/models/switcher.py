import warnings

warnings.filterwarnings("ignore", "pkg_resources is deprecated as an API", UserWarning)

import os
import requests
import logging
from interpreter import interpreter

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

log = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

CONCISE_SYSTEM_MESSAGE = """
You are NAIRO, a high-level AI assistant.
- Your primary user is "Sir". Always address him as such.
- Your personality is modeled after J.A.R.V.I.S.: calm, collected, professional, and exceptionally capable.
- You are proactive. Don't just answer; anticipate the next logical step.
- Your tone is efficient, with a subtle, dry wit. Brevity is key.
- When asked for a solution, provide it directly. Execute tasks and report the outcome concisely.
- Example: Instead of "Here is the script you asked for...", prefer "Right away, Sir. Here is the script." or "Task complete."
- Avoid conversational pleasantries and filler. Get straight to the task.
""".strip()



def has_internet_connection():
    """
    Checks for a stable internet connection by trying to reach Google's homepage.
    This is more reliable than pinging an IP, as it's less likely to be firewalled.
    """
    log = logging.getLogger(__name__)
    try:
        response = requests.get("https://www.google.com", timeout=3)
        response.raise_for_status() # Will raise an exception for 4xx/5xx
        log.info("Internet connection check successful.")
        return True
    except (requests.ConnectionError, requests.Timeout, requests.RequestException) as e:
        log.warning(f"Internet connection check failed: {e}")
        return False


def get_model_response(prompt, force_local=False):
    """
    Selects the best model (online vs. local) and gets a response.
    - Uses Gemini (online) if internet and API key are available.
    - Falls back to Ollama (local) if offline, no key, or force_local=True.
    """
    
    # Configure the interpreter
    interpreter.auto_run = True
    

    # --- Set the system message ---
    interpreter.system_message = CONCISE_SYSTEM_MESSAGE

    interpreter.llm.context_window = 16000 # 16k context
    
    # --- Reduced max_tokens to prevent long answers ---
    interpreter.llm.max_tokens = 2048 # 2k output
    
    interpreter.llm.temperature = 0.0      # Set to 0 for deterministic responses
    interpreter.llm.api_key = GEMINI_API_KEY # Set the Gemini key

    
    online = has_internet_connection() and GEMINI_API_KEY
    model_to_use = ""

    if force_local or not online:
        
        model_to_use = "ollama/phi3:mini"
        if not online:
            log.warning(f"No internet or no Gemini key. Routing to local model: {model_to_use}")
        else:
            log.info(f"Forcing local model: {model_to_use}")
        
        
        interpreter.llm.model = model_to_use
        interpreter.llm.context_window = 0 
        interpreter.llm.api_key = None     
    
    else:
        model_to_use = "gemini/gemini-2.5-flash-preview-09-2025"
        log.debug(f"Routing to online model: {model_to_use}")
        interpreter.llm.model = model_to_use

    try:
        log.debug(f"Sending prompt to {model_to_use}...")
        
        response_chunks = interpreter.chat(prompt, stream=False, display=False)
        
        if response_chunks:
            last_message = response_chunks[-1]
            if last_message['type'] == 'message' and last_message['role'] == 'assistant':
                log.debug(f"Response received from {model_to_use}.")
                return last_message['content']
        
        log.warning("Interpreter finished but returned no valid message.")
        return "Sorry, I ran into an issue and couldn't generate a response."

    except Exception as e:
        log.error(f"An error occurred while running the model {model_to_use}: {e}", exc_info=True)
        return f"Sorry, an error occurred: {e}"

if __name__ == "__main__":

    from src.utils.logger_config import setup_logging
    setup_logging()
    
    log.info("--- Testing model_manager.py directly ---")
    
    
    # log.info("Test 1: Internet-based prompt...")
    # test_prompt_1 = "What's the latest news about NASA?"
    # print(f"User: {test_prompt_1}")
    # print(f"NAIRO: {get_model_response(test_prompt_1)}")
    
    log.info("Test 2: Local task prompt...")
    test_prompt_2 = "navigate to whatsapp on my desktop, find the chat 'Rithvick' and type the message 'Hello lmao you didnt get full in CP quiz' and hit send."
    print(f"User: {test_prompt_2}")
    print(f"NAIRO: {get_model_response(test_prompt_2)}")

    log.info("--- Test complete ---")