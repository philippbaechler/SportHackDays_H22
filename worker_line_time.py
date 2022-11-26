import json
import numpy as np
from datetime import datetime
import faust

kafka_brokers = ['86.119.35.55:9092']

app = faust.App('line_app', broker=kafka_brokers)  # name of the app

playerPositionGroupedByTimeTopic = app.topic('playerPositionGroupedByTime')  # get data from topic
ShowLineTimeTopic = app.topic('ShowLineTime')  # send data to topic

# constants
t0_goalkeeper = 30
t0_line1 = [6, 11, 12, 24, 99]
t0_line2 = [8, 14, 19, 21, 23]
t0_line3 = [2, 5, 9, 17, 37]
t0_lines = [t0_line1, t0_line2, t0_line3]
t1_goalkeeper = 67
t1_line1 = [3, 8, 15, 16, 68]
t1_line2 = [13, 14, 28, 81, 90]
t1_line3 = [4, 11, 18, 24, 73]
t1_lines = [t1_line1, t1_line2, t1_line3]
line_names = ["Line 1", "Line 2", "Line 3"]

# initialize global variable
last_players_team_0 = []
last_players_team_1 = []
last_line_team_0 = 0
last_line_team_1 = 0

# define function
def get_line_weights(current_players, lines, goalkeeper):
    line_weights = []
    current_players = np.array(current_players)
    current_players = current_players[current_players != goalkeeper]
    for line in lines:
        line_weights.append(np.sum([1 for player in current_players if player in line])/len(current_players))
    return line_weights

# kafka stuff
@app.agent(playerPositionGroupedByTimeTopic)  # function executes when changes in topic
async def process(message):  # all data topic -> message

    # set global variable
    global last_line_team_0, last_line_team_1, last_players_team_0, last_players_team_1

    for idx, msg in enumerate(message):    
        eventExists = False
        msg_json = json.loads(msg.value)
        
        current_players_team_0 = [int(x) for x in list(msg_json["teams"]["team_0"].keys())]
        current_players_team_1 = [int(x) for x in list(msg_json["teams"]["team_1"].keys())]

    # Filter out junk data
        if msg_json["time"] == 0 or len(current_players_team_0) < 6 or len(current_players_team_1) < 6:
            continue
            
        # Player joins field
        for player in current_players_team_0:
            if player not in last_players_team_0:
                print(msg_json["time"], "Player", player, " has joined Team 0", msg.offset)
                eventExists = True
        for player in current_players_team_1:
            if player not in last_players_team_1:
                print(msg_json["time"], "Player", player, " has joined Team 1", msg.offset)    
                eventExists = True

        # Player leaves field
        for player in last_players_team_0:
            if player not in current_players_team_0:
                print(msg_json["time"], "Player", player, " has left Team 0", msg.offset)
                eventExists = True
        for player in last_players_team_1:
            if player not in current_players_team_1:
                print(msg_json["time"], "Player", player, " has left Team 1", msg.offset)
                eventExists = True

        # Line detection
        current_line_weights_team_0 = get_line_weights(current_players=current_players_team_0, 
                                                        lines=t0_lines, goalkeeper=t0_goalkeeper)
        current_line_weights_team_1 = get_line_weights(current_players=current_players_team_1, 
                                                        lines=t1_lines, goalkeeper=t1_goalkeeper)
        current_line_team_0 = np.argmax(current_line_weights_team_0)
        current_line_team_1 = np.argmax(current_line_weights_team_1)   
        if current_line_team_0 != last_line_team_0:
            print(msg_json["time"], "Team 0 has switched from", line_names[last_line_team_0], "to", line_names[current_line_team_0], msg.offset)
            eventExists = True
        if current_line_team_1 != last_line_team_1:
            print(msg_json["time"], "Team 1 has switched from", line_names[last_line_team_1], "to", line_names[current_line_team_1], msg.offset)
            eventExists = True        
        
        if eventExists:
            print("Players Team 0:", sorted(current_players_team_0))
            print("Players Team 1:", sorted(current_players_team_1))

        # Set variables for next iteration
        last_players_team_0 = current_players_team_0
        last_players_team_1 = current_players_team_1
        last_line_team_0 = current_line_team_0
        last_line_team_1 = current_line_team_1

        await ShowLineTimeTopic.send(value={'time': msg_json['time']})

app.main()