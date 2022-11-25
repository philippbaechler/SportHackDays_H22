import faust
import math
from datetime import datetime

kafka_brokers = ['86.119.35.55:9092']

app = faust.App('ball-v-and-dir-app', broker=kafka_brokers)


ballPositionTopic = app.topic('filteredInputBallTopic')
ballSpeedAndDirectionTopic = app.topic('ballSpeedAndDirection')


last_position = {
    "time": "2022-08-21 10:30:43.696+0100",
    "x": 0,
    "y": 0,
}

def calculate_direction(dx, dy):
    if dx > 0 and dy > 0:
        return round(math.degrees(math.atan(dy/dx)), 2)
    elif dx < 0 and dy > 0:
        return round(90 + (math.degrees(math.atan(dy/dx)) + 90),2)
    elif dx < 0 and dy < 0:
        return round(180 + math.degrees(math.atan(dy/dx)), 2)
    elif dx > 0 and dy < 0:
        return round(270 + (math.degrees(math.atan(dy/dx)) + 90),2)
    elif dx == 0 and dy == 0:
        return 0
    elif dx == 0 and dy > 0:
        return 90
    elif dx < 0 and dy == 0:
        return 180
    elif dx == 0 and dy < 0:
        return 270


@app.agent(ballPositionTopic)
async def process(positions):
    global last_position
    async for position in positions:
        dx = float(position["x"])-float(last_position["x"])
        dy = float(position["y"])-float(last_position["y"])
        distance_m = math.sqrt(dx**2 + dy**2)

        current_time = datetime.strptime(position["time"], '%Y-%m-%d %H:%M:%S.%f%z')
        last_time = datetime.strptime(last_position["time"], '%Y-%m-%d %H:%M:%S.%f%z')
        time_passed = current_time-last_time
        time_passed_s = time_passed.microseconds/10**6
        
        velocity_m_per_s = round(distance_m / time_passed_s, 2) if time_passed_s else 0
            
        direction_deg = 0
        if dx != 0:
            direction_deg = round(math.degrees(math.atan(dy/dx)), 2)

        await ballSpeedAndDirectionTopic.send(value={"time": position["time"], "velocity": velocity_m_per_s, "direction": calculate_direction(dx, dy)})

        last_position = position


app.main()
