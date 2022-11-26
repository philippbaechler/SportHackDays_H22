import faust

kafka_brokers = ['86.119.35.55:9092']

app = faust.App('search-sequence-app', broker=kafka_brokers)

AusloesungTopic = app.topic('AusloesungTopic')
search_sequenceTopic = app.topic("search_sequence")


@app.agent(AusloesungTopic)
async def process(sequences):
    async for sequence in sequences:
        if sequence['team_0']['Auslösung'] == "YES":
            print(sequence['time'])
        elif sequence['team_1']['Auslösung'] == "YES":
            print(sequence['time'])
app.main()