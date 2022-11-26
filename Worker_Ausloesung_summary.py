import faust

kafka_brokers = ['86.119.35.55:9092']

app = faust.App(
    "Auslösung-app",
    broker="kafka_brokers",
    topic_allow_declare=False,
    topic_disable_leader=True,
    consumer_auto_offset_reset="latest",
)
#input topics
centerOfGravityTopic = app.topic("centerOfGravity")
filteredInputBallTopic = app.topic("filteredInputBallTopic")
#output topic
AusloesungSummaryTopic = app.topic("AusloesungSummary")

COG_0 = 0
COG_1 = 0


@app.agent(centerOfGravityTopic)
async def helper_func(stream):
    global COG_0, COG_1
    async for streams in stream:
        if streams['team']['team_0']['x'] >= 0:
            COG_0 = 1
        else:
            COG_0 = 0
        if streams['team']['team_1']['x'] > 0:
            COG_1 = 1
        else:
            COG_1 = 0

@app.agent(filteredInputBallTopic)
async def main_func(stream):
    global COG_0, COG_1
    async for streams in stream:
        if -0.1 <= streams['x'] >= 0.1:
            Ball_position_0 = 1
        else:
            Ball_position_0 = 0
        if -0.1 <= streams['x'] >= 0.1:
            Ball_position_1 = 1
        else:
            Ball_position_1 = 0
        await AusloesungSummaryTopic.send(value={'time': box['time'], 'team_0': {'COG': COG_0,
                                                                            'Ball_position': Ball_position_0},
                                                                'team_1': {'COG': COG_1,
                                                                            'Ball_position': Ball_position_1}})
app.main()
