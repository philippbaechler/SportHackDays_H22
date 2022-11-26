import faust
import math
from datetime import datetime

kafka_brokers = ['86.119.35.55:9092']

app = faust.App('find-ball-possession-app', broker=kafka_brokers)


ballPositionTopic = app.topic('filteredInputBallTopic')
playerPositionGroupedTopic = app.topic('playerPositionGroupedByTime')
ballPossessionTopic = app.topic('ballPossession')


current_ball_position = {}
current_player_in_possession = {}


def calculate_distances(position):
    distances = {"team_0":{}, "team_1":{}}

    for player_pos in position["teams"]["team_0"]:
        dx = position["teams"]["team_0"][player_pos]["x"] - current_ball_position["x"]
        dy = position["teams"]["team_0"][player_pos]["y"] - current_ball_position["y"]
        distance = math.sqrt(dx**2 + dy**2)
        distances["team_0"][player_pos] = distance

    for player_pos in position["teams"]["team_1"]:
        dx = position["teams"]["team_1"][player_pos]["x"] - current_ball_position["x"]
        dy = position["teams"]["team_1"][player_pos]["y"] - current_ball_position["y"]
        distance = math.sqrt(dx**2 + dy**2)
        distances["team_1"][player_pos] = distance
    
    return distances


def find_shortest_distance(distances):
    shortest_distance = {"team": -1, "player_number": -1, "distance": 1000}

    for player in distances["team_0"]:
        if distances["team_0"][player] < shortest_distance["distance"]:
            shortest_distance = {"team": 0, "player_number": player, "distance": distances["team_0"][player]}

    for player in distances["team_1"]:
        if distances["team_1"][player] < shortest_distance["distance"]:
            shortest_distance = {"team": 1, "player_number": player, "distance": distances["team_1"][player]}

    return shortest_distance


@app.agent(ballPositionTopic)
async def helper_func(positions):
    global current_ball_position
    async for position in positions:
        current_ball_position = position


@app.agent(playerPositionGroupedTopic)
async def process(positions):
    global current_ball_position, current_player_in_possession
    async for position in positions:
        if "time" in current_ball_position:
            distances = calculate_distances(position)
            shortest_distance = find_shortest_distance(distances)
            
            if shortest_distance["distance"] < 2:
                if current_player_in_possession != {"team": shortest_distance["team"], "player_number": shortest_distance["player_number"]}:
                    if current_player_in_possession != {}:
                        new_message={
                                 "time": position["time"],
                                 "team": current_player_in_possession["team"], 
                                 "player_number": current_player_in_possession["player_number"],
                                 "possesion": "False",
                                 "position": {"x": current_ball_position["x"], "y": current_ball_position["y"]}}
                        await ballPossessionTopic.send(value=new_message)
                    current_player_in_possession = {"team": shortest_distance["team"], "player_number": shortest_distance["player_number"]}
                    new_message={
                                 "time": position["time"],
                                 "team": current_player_in_possession["team"], 
                                 "player_number": current_player_in_possession["player_number"],
                                 "possesion": "True",
                                 "position": {"x": current_ball_position["x"], "y": current_ball_position["y"]}}
                    await ballPossessionTopic.send(value=new_message)
            elif current_player_in_possession != {}:
                new_message={    
                             "time": position["time"],
                             "team": current_player_in_possession["team"], 
                             "player_number": current_player_in_possession["player_number"],
                             "possesion": "False",
                             "position": {"x": current_ball_position["x"], "y": current_ball_position["y"]}}
                await ballPossessionTopic.send(value=new_message)
                current_player_in_possession = {}


app.main()


