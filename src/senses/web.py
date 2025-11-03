import asyncio
from quart import Quart, render_template, request, jsonify
from hypercorn.config import Config
from hypercorn.asyncio import serve

from senses._base import SenseModule

quart_app = Quart(__name__, template_folder='../web/templates', static_folder='../web/static')

class WebSense(SenseModule):
    def __init__(self, model_responder, shutdown_event):
        super().__init__(model_responder, shutdown_event)
        self.hypercorn_task = None

    @quart_app.route('/')
    async def index():
        return await render_template('index.html')

    @quart_app.route('/chat', methods=['POST'])
    async def chat():
        data = await request.get_json()
        user_input = data.get('message')
        if not user_input:
            return jsonify({"error": "No message provided"}), 400
        
        # Since model_responder is part of the sense instance, 
        # we need a way to access it from the Quart route.
        # A simple way is to store it on the app object.
        response = await quart_app.config['model_responder'](user_input)
        return jsonify({"response": response})

    async def start(self):
        quart_app.config['model_responder'] = self.model_responder
        config = Config()
        config.bind = ["localhost:5000"]
        
        self.logger.info("Starting Quart Web Sense")
        self.hypercorn_task = asyncio.create_task(
            serve(quart_app, config, shutdown_trigger=self.shutdown_event.wait)
        )
        await self.hypercorn_task

    async def stop(self):
        self.logger.info("Stopping Quart Web Sense")
        # The shutdown_trigger in serve handles this.
        # No explicit stop needed for the server itself if using the trigger.
        pass
