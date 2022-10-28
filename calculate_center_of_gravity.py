import faust

kafka_brokers = ['86.119.35.55:9092']

app = faust.App('center-of-gravity-app', broker=kafka_brokers)


playerPositionGroupedTopic = app.topic('playerPositionGroupedByTime')
centerOfGravityTopic = app.topic('centerOfGravity')


new_msg = {
    "time": 0,
    "teams": {
        "team_0": {},
        "team_1": {}
    }
}


def calculate_center_of_gravity(team_player_pos):
    x_list = [team_player_pos[element]["x"] for element in team_player_pos]
    y_list = [team_player_pos[element]["y"] for element in team_player_pos]
    return sum(x_list)/len(x_list), sum(y_list)/len(y_list)


@app.agent(playerPositionGroupedTopic)
async def process(positions):
    global new_msg
    async for position in positions:
        if len(position["teams"]["team_0"]) >= 3:
            x,y = calculate_center_of_gravity(position["teams"]["team_0"])
            new_msg["teams"]["team_0"]["x"] = x
            new_msg["teams"]["team_0"]["y"] = y
        if len(position["teams"]["team_1"]) >= 3:
            x,y = calculate_center_of_gravity(position["teams"]["team_1"])
            new_msg["teams"]["team_1"]["x"] = x
            new_msg["teams"]["team_1"]["y"] = y
        if len(new_msg["teams"]["team_0"]) > 0 or len(new_msg["teams"]["team_1"]) > 0:
            new_msg["time"] = position["time"]
            await centerOfGravityTopic.send(value=new_msg)


app.main()
