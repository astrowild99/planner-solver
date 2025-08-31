"""
This creates the asgi service using FastAPI to communicate with the outside world

the apis are not the only way that the system communicates, as you can also listen to
messages exchanged via the rabbitmq server
"""
import datetime

from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def health_check():
    return {
        "status": "[OK]",
        "server_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }