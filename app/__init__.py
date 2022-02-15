from flask import Flask
from environs import Env
from .controller import alpha

env = Env()
env.read_env()

app = Flask(__name__)

@app.get("/leads")
def list():
    return alpha.list_top_leads()