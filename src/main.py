import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import logging
import signal
import importlib
from typing import Set, Dict

import config
from utils.logger_config import setup_logging
from core.model_manager import initialize_model_manager, check_internet_periodically, get_model_response
from senses._base import SenseModule

# Setup logging as early as possible
setup_logging()
log = logging.getLogger(__name__)

# --- Globals for managing tasks and shutdown ---
running_tasks: Set[asyncio.Task] = set()
shutdown_event = asyncio.Event()

def handle_task_completion(task: asyncio.Task):
    """Callback to handle task completion, logging exceptions."""
    try:
        # This will re-raise the exception if the task failed
        task.result()
        log.info(f"Task {task.get_name()} finished successfully.")
    except asyncio.CancelledError:
        log.warning(f"Task {task.get_name()} was cancelled.")
    except Exception:
        log.exception(f"Task {task.get_name()} failed with an exception:")
    
    running_tasks.discard(task)

async def main():
    """Main entry point for the NAIRO application."""
    log.info("--- Starting NAIRO ---")

    # Initialize core components
    initialize_model_manager()

    # --- Start background tasks ---
    log.info("Starting background tasks...")
    
    # 1. Internet Checker
    internet_checker_task = asyncio.create_task(check_internet_periodically(shutdown_event))
    internet_checker_task.set_name("InternetChecker")
    internet_checker_task.add_done_callback(handle_task_completion)
    running_tasks.add(internet_checker_task)

    # --- Dynamically load and start Senses ---
    log.info(f"Loading enabled senses: {config.ENABLED_SENSES}")
    sense_classes: Dict[str, SenseModule] = {}
    for sense_name in config.ENABLED_SENSES:
        try:
            module_path = f"senses.{sense_name}"
            sense_module = importlib.import_module(module_path)
            
            # Convention: Class name is CamelCase version of module name + "Sense"
            # e.g., 'web' -> 'WebSense'
            class_name = f"{sense_name.capitalize()}Sense"
            sense_class = getattr(sense_module, class_name)
            
            sense_instance = sense_class(get_model_response, shutdown_event)
            
            # Inject logger into the sense instance
            sense_instance.logger = logging.getLogger(f"sense.{sense_name}")

            sense_task = asyncio.create_task(sense_instance.start())
            sense_task.set_name(f"Sense:{sense_name}")
            sense_task.add_done_callback(handle_task_completion)
            running_tasks.add(sense_task)
            
            sense_classes[sense_name] = sense_instance
            log.info(f"Successfully loaded and started '{sense_name}' sense.")

        except (ImportError, AttributeError) as e:
            log.error(f"Failed to load sense '{sense_name}': {e}", exc_info=True)

    if not sense_classes:
        log.warning("No senses were loaded. The application will have no functionality.")

    # --- Wait for shutdown signal ---
    await shutdown_event.wait()

    # --- Graceful Shutdown ---
    log.info("Shutdown signal received. Cleaning up...")

    # Stop senses (optional, if they have a stop method)
    for name, sense in sense_classes.items():
        if hasattr(sense, 'stop') and asyncio.iscoroutinefunction(sense.stop):
            try:
                log.info(f"Stopping sense '{name}'...")
                await sense.stop()
            except Exception:
                log.exception(f"Error while stopping sense '{name}':")

    # Cancel all running tasks
    for task in list(running_tasks):
        task.cancel()
    
    # Wait for all tasks to finish cancelling
    if running_tasks:
        await asyncio.gather(*running_tasks, return_exceptions=True)

    log.info("--- NAIRO has shut down ---")

def signal_handler(sig, frame):
    """Signal handler to initiate graceful shutdown."""
    log.info(f"Received signal {sig}. Initiating shutdown...")
    shutdown_event.set()

if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # This is caught to prevent the asyncio default message on Ctrl+C
        log.info("Shutdown initiated by KeyboardInterrupt.")
    except Exception:
        log.critical("A critical error occurred in the main application loop.", exc_info=True)

