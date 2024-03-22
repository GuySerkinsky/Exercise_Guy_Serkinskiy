 from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import requests

import httpx
import asyncio

app = FastAPI()

class StartGameRequest(BaseModel):
    target_url: str
    pong_delay: int

next_server_url = None
pong_time_ms = 1000  # Default value; can be updated via start command
game_active = False

@app.post("/start/")
async def start_game(request: StartGameRequest, background_tasks: BackgroundTasks):
    global next_server_url, pong_time_ms, game_active
    next_server_url = request.target_url
    pong_time_ms = request.pong_delay
    game_active = True
    print(f"Game started: will ping {next_server_url} every {pong_time_ms} ms")

    # Send the initial ping to kickstart the ping-pong exchange
    background_tasks.add_task(send_ping)

    return {"message": "Game started"}

@app.post("/ping/")
async def receive_ping():
    print("Received ping, sending pong...")
    # Here, you'd send a pong back to the original sender (which could be determined from the request data or headers)
    # For simplicity, I'm assuming the original sender is always the server on port 8000
    try:
        response = requests.post("http://localhost:8000/pong/")
        if response.status_code == 200:
            print("Pong sent successfully")
        else:
            print("Failed to send pong")
    except Exception as e:
        print(f"Error sending pong: {e}")
        
@app.post("/pong/")
async def receive_pong(background_tasks: BackgroundTasks):
    print("Received pong, scheduling next ping...")
    if game_active:
        background_tasks.add_task(send_ping)


async def send_ping():
    if game_active:
        await asyncio.sleep(pong_time_ms / 1000)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                print(f"Sending ping to {next_server_url}...")
                response = await client.post(next_server_url + "/ping/")
                response.raise_for_status()
                print(f"Ping sent successfully to {next_server_url}")
        except Exception as e:
            print(f"Error sending ping to {next_server_url}: {e}")

@app.post("/stop/")
async def stop_game():
    global game_active
    game_active = False
    print("Game stopped.")
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
    print("Game resumed, sending ping...")
    # Immediately kickstart the ping process again
    background_tasks.add_task(send_ping)
    return {"message": "Game resumed"}