import asyncio
import discord
import config
from senses._base import SenseModule

class DiscordSense(SenseModule):
    def __init__(self, model_responder, shutdown_event):
        super().__init__(model_responder, shutdown_event)
        # We'll use an intents object to declare what events our bot wants to receive.
        # This is now a required practice for discord.py.
        intents = discord.Intents.default()
        intents.messages = True  # Enable message-related events
        intents.message_content = True # Enable message content intent
        self.client = discord.Client(intents=intents)
        self.token = config.DISCORD_BOT_TOKEN # We will need to add this to our config

        # --- Event Handlers ---
        @self.client.event
        async def on_ready():
            """Called when the bot successfully connects to Discord."""
            self.logger.info(f'Logged in as {self.client.user}')

        @self.client.event
        async def on_message(message):
            """Called every time a message is received."""
            # Ignore messages from the bot itself to prevent loops
            if message.author == self.client.user:
                return

            # For simplicity, let's have the bot respond to any message in a channel it's in.
            # We can make this more specific later (e.g., mentions only).
            self.logger.info(f"Received message on Discord: \"{message.content}\"")
            
            # Get the AI's response
            ai_response = await self.model_responder(message.content)
            
            # Send the response back to the channel
            await message.channel.send(ai_response)

    async def start(self):
        """Starts the Discord bot."""
        self.logger.info("Starting Discord Sense...")
        if not self.token:
            self.logger.error("Discord bot token is not configured. The Discord sense will not start.")
            return
        
        try:
            # The `start` method of the client is blocking, so we run it as a task.
            await self.client.start(self.token)
        except discord.LoginFailure:
            self.logger.error("Failed to log in to Discord. Please check your bot token.")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred in the Discord sense: {e}", exc_info=True)
        finally:
            self.logger.info("Discord sense has stopped.")

    async def stop(self):
        """Stops the Discord bot."""
        self.logger.info("Stopping Discord Sense...")
        if self.client.is_running():
            await self.client.close()