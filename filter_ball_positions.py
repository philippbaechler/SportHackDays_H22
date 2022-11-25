import faust
import math
from datetime import datetime

kafka_brokers = ['86.119.35.55:9092']

app = faust.App('ball-position-filter', broker=kafka_brokers)


ballPositionTopic = app.topic('rawInputBallTopic')
filteredInputBallTopic = app.topic('filteredInputBallTopic')


FILTER_LENGTH = 5


def get_filtered_position(positions):
    avg_x = 0
    avg_y = 0
    for pos in positions:
        avg_x += float(pos["x"])
        avg_y += float(pos["y"])
    avg_x /= len(positions)
    avg_y /= len(positions)

    return {"time": positions[2]["time"], "x": round(avg_x, 6), "y": round(avg_y, 6)}

last_positions = []


@app.agent(ballPositionTopic)
async def process(positions):
    global last_positions
    async for position in positions:
        if len(last_positions) < FILTER_LENGTH:
            last_positions.append(position)
        else:
            last_positions[1:FILTER_LENGTH] = last_positions[0:(FILTER_LENGTH-1)]
            last_positions[0] = position

        if len(last_positions) == FILTER_LENGTH:
            #print(get_filtered_position(last_positions))
            await filteredInputBallTopic.send(value=get_filtered_position(last_positions))


app.main()
