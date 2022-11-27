import faust

kafka_brokers = ['86.119.35.55:9092']

app = faust.App(
    "Ausloesung-app",
    broker=kafka_brokers)

#input topics
centerOfGravityTopic = app.topic("centerOfGravity")
filteredInputBallTopic = app.topic("filteredInputBallTopic")
passCollectionTopic = app.topic("passCollection")
#output topic
AusloesungSummaryTopic = app.topic("AusloesungSummary")

COG_0 = 0
COG_1 = 0
Ball_possession_0 = 0
Ball_possession_1 = 0

@app.agent(centerOfGravityTopic)
async def helper_func(stream):
    global COG_0, COG_1
    async for streams in stream:
        if streams['teams']['team_0']['x'] <= 0:
            COG_0 = 1
        else:
            COG_0 = 0
        if streams['teams']['team_1']['x'] >= 0:
            COG_1 = 1
        else:
            COG_1 = 0

@app.agent(passCollectionTopic)
async def helper_func(stream):
    global Ball_possession_0, Ball_possession_1
    async for streams in stream:
        if streams['team'] == 0:
            Ball_possession_0 = 1
        else:
            Ball_possession_0 = 0
        if streams['team'] == 1:
            Ball_possession_1 = 1
        else:
            Ball_possession_1 = 0

@app.agent(filteredInputBallTopic)
async def main_func(stream):
#    global COG_0, COG_1
    async for streams in stream:
        Ball_position_0 = 1
        Ball_position_1 = 1
#        if -0.5 <= streams['x'] <= 0.5:
#            Ball_position_0 = 1
#        else:
#            Ball_position_0 = 0
#        if -0.5 <= streams['x'] <= 0.5:
#            Ball_position_1 = 1
#        else:
#            Ball_position_1 = 0
        await AusloesungSummaryTopic.send(value={'time': streams['time'], 'team_0': {'COG': COG_0,
                                                                            'Ball_position': Ball_position_0,
                                                                            'Ball_possession': Ball_possession_0},
                                                                            'team_1': {'COG': COG_1,
                                                                            'Ball_position': Ball_position_1,
                                                                            'Ball_possession': Ball_possession_1}})
app.main()
