from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import httpx
import asyncio

from enum import Enum

app = FastAPI()

class StartGameRequest(BaseModel):
    target_url: str
    pong_delay: int

class ResponseData(BaseModel):
    response_url: str
    

next_server_url = None
pong_time_ms = 1000  # Default value; can be updated via start command
game_active = True

@app.post("/start/")
async def start_game(request: StartGameRequest, background_tasks: BackgroundTasks):
    global next_server_url, pong_time_ms, game_active, server_state
    next_server_url = request.target_url
    pong_time_ms = request.pong_delay
    game_active = True
    background_tasks.add_task(send_ping)
    return {"message": "Game started"}

@app.post("/ping/")
async def receive_ping(responsedata: ResponseData, background_tasks: BackgroundTasks):
    global next_server_url, server_state
    server_state = ServerState.Ping
    next_server_url = responsedata.response_url
    print("Received ping, scheduling next ping...")
    try:
        background_tasks.add_task(send_ping)
    except Exception as e:
        print(f"Error sending ping: {e}")
    return {"message": 200}


async def send_ping():
    global game_active, next_server_url
    if game_active:
        await asyncio.sleep(pong_time_ms / 1000)
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                if '8000' in next_server_url:
                    response_server_url = 'http://localhost:8001'
                else:
                    response_server_url = 'http://localhost:8000'
                responsedata = ResponseData(response_url=response_server_url)
                # Convert the Pydantic model to a dictionary
                response_data_dict = responsedata.dict()
                response = await client.post(f"{next_server_url}/ping/", json=response_data_dict)
                response.raise_for_status()
                print(f"Ping sent successfully to {next_server_url}")
            except Exception as e:
                print(f"Error sending ping: {e}")

@app.post("/stop/")
async def stop_game():
    global game_active
    game_active = False
    return {"message": "Game stopped"}

@app.post("/pause/")
async def pause_game():
    global game_active
    game_active = False
    return {"message": "Game paused"}

@app.post("/resume/")
async def resume_game(background_tasks: BackgroundTasks):
    global game_active
    game_active = True
    background_tasks.add_task(send_ping)
    return {"message": "Game resumed"}
