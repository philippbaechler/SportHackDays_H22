import faust

kafka_brokers = ['86.119.35.55:9092']

app = faust.App('compare-EB-app', broker=kafka_brokers)

teamBoundingBoxAreaTopic = app.topic('teamBoundingBoxArea')
teamBoundingBoxAreaCompareTopic = app.topic('teamBoundingBoxAreaCompare')

last_EB = {}

@app.agent(teamBoundingBoxAreaTopic)
async def process(boxes):
    global last_EB
    async for box in boxes:
        if 'time' in last_EB:
            change_team_0 = box['team_0']['area'] - last_EB['team_0']['area']
            percentage_team_0 = (box['team_0']['area'] / last_EB['team_0']['area'])*100
            if change_team_0 < 0:
                change_team_0 = 0
            elif change_team_0 == 0:
                change_team_0 = 1
            elif change_team_0 > 0:
                change_team_0 = 2
            change_team_1 = box['team_1']['area'] - last_EB['team_1']['area']
            percentage_team_1 = (box['team_1']['area'] / last_EB['team_1']['area']) * 100
            if change_team_1 < 0:
                change_team_1 = 0
            elif change_team_1 == 0:
                change_team_1 = 1
            elif change_team_1 > 0:
                change_team_1 = 2
            await teamBoundingBoxAreaCompareTopic.send(value={'time': box['time'], 'team_0': {'Change': change_team_0,
                                                                                   'Percentage change': percentage_team_0},
                                                                        'team_1': {'Change': change_team_1,
                                                                                   'Percentage change': percentage_team_1}})
        last_EB = box
app.main()