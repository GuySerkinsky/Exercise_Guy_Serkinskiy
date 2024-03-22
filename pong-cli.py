import argparse
import requests

server_url_1 = "http://localhost:8000"
server_url_2 = "http://localhost:8001"

def start_game(pong_time_ms):
    data = {
        "target_url": server_url_2,  # This should match the Pydantic model field
        "pong_delay": pong_time_ms   # This should match the Pydantic model field
    }
    response = requests.post(f"{server_url_1}/start/", json=data)
    if response.status_code == 200:
        print("Game started")
    else:
        print(f"Failed to start the game. Status Code: {response.status_code}")

def pause_game():
    requests.post(f"{server_url_1}/pause/")
    requests.post(f"{server_url_2}/pause/")
    print("Game paused")

def resume_game():
    requests.post(f"{server_url_1}/resume/")
    requests.post(f"{server_url_2}/resume/")
    print("Game resumed")

def stop_game():
    requests.post(f"{server_url_1}/stop/")
    requests.post(f"{server_url_2}/stop/")
    print("Game stopped")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pong Game CLI')
    subparsers = parser.add_subparsers(dest='command')

    start_parser = subparsers.add_parser('start')
    start_parser.add_argument('pong_time_ms', type=int)

    subparsers.add_parser('pause')
    subparsers.add_parser('resume')
    subparsers.add_parser('stop')

    args = parser.parse_args()

    if args.command == 'start':
        start_game(args.pong_time_ms)
    elif args.command == 'pause':
        pause_game()
    elif args.command == 'resume':
        resume_game()
    elif args.command == 'stop':
        stop_game()