import faust
import math
from datetime import datetime

kafka_brokers = ['86.119.35.55:9092']

app = faust.App('find-ball-possession-app', broker=kafka_brokers)

last_player_in_possession = {}

ballPositionTopic = app.topic('ballPossession')
passCollectionTopic = app.topic('passCollection')


@app.agent(ballPositionTopic)
async def process(messages):
    global last_player_in_possession
    async for message in messages:
        if message["possession"] == "False":
            last_player_in_possession = message
        elif "possession" in last_player_in_possession:
            if last_player_in_possession["team"] == message["team"]:
                await passCollectionTopic.send(value={
                    "time": message["time"],
                    "team": message["team"],
                    "from": {
                        "player_number": last_player_in_possession["player_number"],
                        "x": last_player_in_possession["position"]["x"],
                        "y": last_player_in_possession["position"]["y"]
                        },
                    "to": {
                        "player_number": message["player_number"],
                        "x": message["position"]["x"],
                        "y": message["position"]["y"]
                        }
                })



app.main()




