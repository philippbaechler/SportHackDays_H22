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


@app.agent(rawPlayerPositionTopic)
async def process(positions):
    async for position in positions:
        print(f'{position.time} Position for {position.number}')
        print(f'-> team: {position.team} / number: {position.number} / x:{position.x} / y:{position.y}')
        print(70*"-")


app.main()
