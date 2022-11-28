import faust

kafka_brokers = ['86.119.35.55:9092']

app = faust.App('Ausloesung1-app', broker=kafka_brokers)

AusloesungSummaryTopic = app.topic("AusloesungSummary")
AusloesungTopic = app.topic('AusloesungTopic')


@app.agent(AusloesungSummaryTopic)
async def process(summaries):
    async for summary in summaries:
        if summary['team_0']['CoG'] == 1 and \
            summary['team_0']['Ball_possession'] == 1 and \
            summary['team_0']['pass_x_distance'] >= 6:
            await AusloesungTopic.send(value={'time': summary['time'], 'Trigger': "Team 0"})

        if summary['team_1']['CoG'] == 1 and \
            summary['team_1']['Ball_possession'] == 1 and \
            summary['team_1']['pass_x_distance'] <= -6:
            await AusloesungTopic.send(value={'time': summary['time'], 'Trigger': "Team 1"})

app.main()
