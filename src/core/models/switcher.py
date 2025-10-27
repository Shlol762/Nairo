import os
import subprocess
import requests
from dotenv import load_dotenv
from interpreter import interpreter


load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))


print("")
