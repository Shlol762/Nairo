import asyncio
import logging
import aiohttp
from interpreter import interpreter
import config

log = logging.getLogger(__name__)

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

# This event will be used to signal the online status across the application
IS_ONLINE = asyncio.Event()

def initialize_model_manager():
    """
    Initializes the interpreter with settings from the config file.
    """
    log.info("Initializing Model Manager...")
    interpreter.auto_run = config.INTERPRETER_AUTO_RUN
    interpreter.system_message = CONCISE_SYSTEM_MESSAGE
    interpreter.llm.context_window = 16000  # 16k context
    interpreter.llm.max_tokens = 2048  # 2k output
    interpreter.llm.temperature = 0.0
    interpreter.llm.api_key = config.GEMINI_API_KEY # Using GEMINI_API_KEY from config
    log.info("Model Manager initialized.")

async def has_internet_connection_async():
    """
    Checks for a stable internet connection asynchronously using aiohttp.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.google.com", timeout=3) as response:
                response.raise_for_status()
                return True
    except Exception as e:
        log.warning(f"Async internet connection check failed: {e}")
        return False

async def check_internet_periodically(shutdown_event: asyncio.Event):
    """
    Periodically checks for internet connection and sets the IS_ONLINE event.
    """
    while not shutdown_event.is_set():
        if await has_internet_connection_async():
            if not IS_ONLINE.is_set():
                log.info("Internet connection established. NAIRO is online.")
                IS_ONLINE.set()
        else:
            if IS_ONLINE.is_set():
                log.warning("Internet connection lost. NAIRO is offline.")
                IS_ONLINE.clear()
        
        try:
            # Wait for the specified interval or until shutdown is triggered
            await asyncio.wait_for(shutdown_event.wait(), timeout=config.INTERNET_CHECK_INTERVAL_SECONDS)
            # If wait() completes, it means the event was set, so we break
            break
        except asyncio.TimeoutError:
            # This is the normal path, continue the loop
            pass

async def get_model_response(prompt: str, force_local: bool = False):
    """
    Selects the best model (online vs. local) and gets a response asynchronously.
    The blocking `interpreter.chat()` call is run in a separate thread.
    """
    online = IS_ONLINE.is_set() and config.GEMINI_API_KEY
    model_to_use = ""

    if force_local or not online:
        model_to_use = "ollama/phi3:mini"
        if not online:
            log.warning(f"No internet or no API key. Routing to local model: {model_to_use}")
        else:
            log.info(f"Forcing local model: {model_to_use}")
        
        interpreter.llm.model = model_to_use
        interpreter.llm.context_window = 0
        interpreter.llm.api_key = None
    else:
        model_to_use = config.MODEL_NAME
        log.debug(f"Routing to online model: {model_to_use}")
        interpreter.llm.model = model_to_use
        interpreter.llm.api_key = config.GEMINI_API_KEY

    try:
        log.debug(f"Sending prompt to {model_to_use}...")
        
        # Run the blocking `interpreter.chat` in a separate thread
        loop = asyncio.get_running_loop()
        response_chunks = await loop.run_in_executor(
            None,  # Use the default thread pool executor
            lambda: interpreter.chat(prompt, stream=False, display=False)
        )
        
        if response_chunks:
            last_message = response_chunks[-1]
            if last_message.get('type') == 'message' and last_message.get('role') == 'assistant':
                log.debug(f"Response received from {model_to_use}.")
                return last_message.get('content', "No content in message.")
        
        log.warning("Interpreter finished but returned no valid message.")
        return "Sorry, I ran into an issue and couldn't generate a response."

    except Exception as e:
        log.error(f"An error occurred while running the model {model_to_use}: {e}", exc_info=True)
        return f"Sorry, an error occurred: {e}"

if __name__ == "__main__":
    # This part is for direct testing and will not run in the main application
    async def main_test():
        from src.utils.logger_config import setup_logging
        setup_logging()
        
        initialize_model_manager()
        
        # Start the internet checker as a background task for the test
        shutdown_flag = asyncio.Event()
        checker_task = asyncio.create_task(check_internet_periodically(shutdown_flag))

        log.info("--- Testing model_manager.py directly ---")
        
        # Wait a moment for the first internet check
        await asyncio.sleep(2)

        log.info("Test 1: Internet-based prompt...")
        test_prompt_1 = "What's the latest news about NASA?"
        print(f"User: {test_prompt_1}")
        response = await get_model_response(test_prompt_1)
        print(f"NAIRO: {response}")
        
        log.info("Test 2: Local task prompt (forced)...")
        test_prompt_2 = "List files in the current directory."
        print(f"User: {test_prompt_2}")
        response = await get_model_response(test_prompt_2, force_local=True)
        print(f"NAIRO: {response}")

        log.info("--- Test complete ---")
        shutdown_flag.set()
        await checker_task

    asyncio.run(main_test())