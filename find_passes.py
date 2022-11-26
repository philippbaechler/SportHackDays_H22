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
                    "from_player": last_player_in_possession["player_number"],
                    "from_x": round(last_player_in_possession["position"]["x"], 2),
                    "from_y": round(last_player_in_possession["position"]["y"], 2),
                    "to_player": message["player_number"],
                    "to_x": round(message["position"]["x"], 2),
                    "to_y": round(message["position"]["y"], 2),
                    "d_x": round(message["position"]["x"]-last_player_in_possession["position"]["x"], 2),
                    "d_y": round(message["position"]["y"]-last_player_in_possession["position"]["y"], 2)
                })



app.main()




