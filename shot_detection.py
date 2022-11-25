import faust
import math
from datetime import datetime

kafka_brokers = ['86.119.35.55:9092']

app = faust.App('shot-detection-app', broker=kafka_brokers)


ballSpeedAndDirectionTopic = app.topic('ballSpeedAndDirection')
straightLineTopic = app.topic('straightLine')


MINIMAL_SHOT_SAMPLES = 10
MAX_ANGLE_DIFFERENCE = 3


def calculate_angle_difference(last_angle, current_angle):
    angle_diff = abs(current_angle - last_angle)
    if angle_diff > 180:
        angle_diff = 360 - angle_diff
    return round(angle_diff, 2)


last_messages = []

@app.agent(ballSpeedAndDirectionTopic)
async def process(messages):
    global last_messages
    async for message in messages:
        if len(last_messages) == 0:
            last_messages.append(message)
        else:
            angle_diff = calculate_angle_difference(message["direction"], last_messages[-1]["direction"])
            if angle_diff <= MAX_ANGLE_DIFFERENCE:
                last_messages.append(message)
            else:
                if len(last_messages) >= MINIMAL_SHOT_SAMPLES:
                    await straightLineTopic.send(value={"time": message["time"], "lineLength": len(last_messages)})
                last_messages = []
                last_messages.append(message)

        


app.main()