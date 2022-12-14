import faust

kafka_brokers = ['86.119.35.55:9092']

app = faust.App('find-team-bbox-app', broker=kafka_brokers)


playerPositionGroupedTopic = app.topic('playerPositionGroupedByTime')
teamBoundingBoxTopic = app.topic('teamBoundingBox')


def find_team_bounding_box(team_player_pos):
    x_list = [team_player_pos[element]["x"] for element in team_player_pos]
    y_list = [team_player_pos[element]["y"] for element in team_player_pos]
    return min(x_list), max(x_list), min(y_list), max(y_list)

def get_field_players(all_teams):
    field_players_0 = all_teams["team_0"]
    field_players_1 = all_teams["team_1"]
    if "30" in field_players_0:
        del field_players_0["30"]
    if "67" in field_players_1:
        del field_players_1["67"]
    return field_players_0, field_players_1


@app.agent(playerPositionGroupedTopic)
async def process(positions):
    new_msg = {}
    async for position in positions:
        field_players_0, field_players_1 = get_field_players(position["teams"])

        if len(field_players_0) >= 3:
            min_x, max_x, min_y, max_y = find_team_bounding_box(field_players_0)
            new_msg["team_0"] = {"x_min": min_x, "x_max": max_x, "y_min": min_y, "y_max": max_y}
        if len(field_players_1) >= 3:
            min_x, max_x, min_y, max_y = find_team_bounding_box(field_players_1)
            new_msg["team_1"] = {"x_min": min_x, "x_max": max_x, "y_min": min_y, "y_max": max_y}
        if ("team_0" in new_msg) or ("team_1" in new_msg):
            new_msg["time"] = position["time"]
            await teamBoundingBoxTopic.send(value=new_msg)


app.main()
