import logging
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

from utils.logger_config import setup_logging
setup_logging(logging.DEBUG)

from core.models.switcher import get_model_response

log = logging.getLogger(__name__)
log.info("Starting Nairo Flask application...")

app = Flask(__name__, 
            template_folder='./core/web/templates',
            static_folder='./core/web/static'
            )


@app.route('/')
def index():
    log.debug("Serving the index page.")
    return render_template('index.html')


@app.route('/api/prompt', methods=['POST'])
def handle_prompt():
    try: 
        data = request.json
        if not data or 'prompt' not in data:
            log.warning("Received invalid prompt request.")
            return jsonify({"error": "Invalid request, 'prompt' missing."}), 400
        
        prompt = data['prompt']
        source = data.get('source', 'unknown')

        log.debug(f"Received prompt from source '{source}'")

        response = get_model_response(prompt)

        log.debug("Sending response back to client.")
        
        return jsonify({"response": response})

    except Exception as e:
        log.error(f"Error handling prompt: {e}", exc_info=True)
        return jsonify({"error": "An error occurred while processing the prompt."}), 500
    

if __name__ == '__main__':

    log.info("Test running Nairo Flask app on localhost:5000")
    app.run(host='0.0.0.0', port=5000)

