import faust

kafka_brokers = ['86.119.35.55:9092']

#every app needs own name
app = faust.App('calculate-EB-app', broker=kafka_brokers)

teamBoundingBoxTopic = app.topic('teamBoundingBox')
teamBoundingBoxAreaTopic = app.topic('teamBoundingBoxArea')


def EnclosingBox_Length(x_min, x_max, y_min, y_max):
    x_length = x_max - x_min
    y_length = y_max - y_min
    return x_length, y_length

def EnclosingBox_Area(x_length, y_length):
    area = x_length * y_length
    return area


@app.agent(teamBoundingBoxTopic)
async def process(boxes):
    async for box in boxes:
        x_max = box['team_0']['x_max']
        x_min = box['team_0']['x_min']
        y_max = box['team_0']['y_max']
        y_min = box['team_0']['y_min']
        x_length_team_0, y_length_team_0 = EnclosingBox_Length(x_max, x_min, y_max, y_min)
        area_team_0 = EnclosingBox_Area(x_length_team_0, y_length_team_0)
        x_max = box['team_1']['x_max']
        x_min = box['team_1']['x_min']
        y_max = box['team_1']['y_max']
        y_min = box['team_1']['y_min']
        x_length_team_1, y_length_team_1 = EnclosingBox_Length(x_max, x_min, y_max, y_min)
        area_team_1 = EnclosingBox_Area(x_length_team_1, y_length_team_1)
        await teamBoundingBoxAreaTopic.send(value={'time': box['time'], 'team_0': {'area': area_team_0,
                                                                                   'x_length': x_length_team_0,
                                                                                   'y_length': y_length_team_0},
                                                                        'team_1': {'area': area_team_1,
                                                                                   'x_length': x_length_team_1,
                                                                                   'y_length': y_length_team_1}})
app.main()
