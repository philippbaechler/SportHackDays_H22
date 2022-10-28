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


rawPlayerPositionTopic = app.topic('rawInputTopic', value_type=PlayerPosition)
playerPositionGroupedTopic = app.topic('playerPositionGroupedByTime')


new_row = {
    "time": 0,
    "teams": {
        "team_0": {
            # "24": {"x": 2, "y":4},
            # "8": {"x": 1, "y":5},
            # "64": {"x": 1, "y":5}
        },
        "team_1": {
            # "30": {"x": 2, "y":4},
            # "8": {"x": 1, "y":5}
        }
    }
}


@app.agent(rawPlayerPositionTopic)
async def process(positions):
    global new_row
    async for position in positions:
        if position.time != new_row["time"]:
            print(new_row)
            await playerPositionGroupedTopic.send(value=new_row)
            new_row = {"time":position.time, "teams":{"team_0":{},"team_1":{}}}

        new_row["teams"]["team_"+str(position.team)][str(position.number)] = {"x":position.x, "y":position.y}


app.main()


