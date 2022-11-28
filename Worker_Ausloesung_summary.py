import faust

kafka_brokers = ['86.119.35.55:9092']

app = faust.App("Ausloesung-app", broker=kafka_brokers)

#input topics
centerOfGravityTopic = app.topic("centerOfGravity")
filteredInputBallTopic = app.topic("filteredInputBallTopic")
passCollectionTopic = app.topic("passCollection")
#output topic
AusloesungSummaryTopic = app.topic("AusloesungSummary")


CoG_0 = 0
CoG_1 = 0


@app.agent(centerOfGravityTopic)
async def helper_func1(stream):
    global CoG_0, CoG_1
    async for streams in stream:
        if streams['teams']['team_0']['x'] <= 0:
            CoG_0 = 1
        else:
            CoG_0 = 0
        if streams['teams']['team_1']['x'] >= 0:
            CoG_1 = 1
        else:
            CoG_1 = 0


@app.agent(passCollectionTopic)
async def helper_func(stream):
    global CoG_0, CoG_1
    async for streams in stream:
        Ball_possession_0 = 0
        Ball_possession_1 = 0
        pass_x_distance_0 = 0
        pass_x_distance_1 = 0
        if streams['team'] == 0:
            Ball_possession_0 = 1
            pass_x_distance_0 = streams["d_x"]
        if streams['team'] == 1:
            Ball_possession_1 = 1
            pass_x_distance_1 = streams["d_x"]

        await AusloesungSummaryTopic.send(value={
                                    'time': streams['time'], 
                                    'team_0': {
                                        'CoG': CoG_0,
                                        'Ball_possession': Ball_possession_0,
                                        'pass_x_distance': pass_x_distance_0},
                                    'team_1': {
                                        'CoG': CoG_1,
                                        'Ball_possession': Ball_possession_1,
                                        'pass_x_distance': pass_x_distance_0}})



app.main()
