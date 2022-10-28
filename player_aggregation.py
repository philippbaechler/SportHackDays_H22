import faust

kafka_brokers = ['86.119.35.55:9092']

app = faust.App('test-app', broker=kafka_brokers)


class PlayerPosition(faust.Record, validation=True, serializer='json'):
    time: str
    team: int
    number: int
    x: float
    y: float
    EventTimestamp: int


rawPlayerPositionTopic = app.topic('testTopic', value_type=PlayerPosition)


new_row = {"time":0}


@app.agent(rawPlayerPositionTopic)
async def process(positions):
    global new_row
    async for position in positions:
        if position.time != new_row["time"]:
            print(new_row)
            new_row = {"time": position.time}
        
        player_id = str(position.team) + "_" + str(position.number)
        new_row[player_id] = {"x":{position.x}, "y":{position.y}}


app.main()
