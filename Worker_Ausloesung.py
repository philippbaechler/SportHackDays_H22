import faust

kafka_brokers = ['86.119.35.55:9092']

app = faust.App('calculate-EB-app', broker=kafka_brokers)

AusloesungSummaryTopic = app.topic("AusloesungSummary")
AusloesungTopic = app.topic('AusloesungTopic')


@app.agent(AusloesungSummaryTopic)
async def process(summaries):
    async for summary in summaries:
        if summary['team_0']['COG'] == 1 and summary['team_0']['Ball_possession'] == 1 and summary['team_0']['Ball_position'] == 1:
            auslösung_0 = 'YES'
        else:
            auslösung_0 = "NO"
        if summary['team_1']['COG'] == 1 and summary['team_1']['Ball_possession'] == 1 and summary['team_1']['Ball_position'] == 1:
            auslösung_1 = 'YES'
        else:
            auslösung_1 = "NO"
        await AusloesungTopic.send(value={'time': box['time'], 'team_0': {'Auslösung': auslösung_0},
                                                'team_1': {'Auslösung': auslösung_1}})

app.main()
