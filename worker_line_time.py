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
last_line_team_0 = -1
last_line_team_1 = -1
last_line_time_team_0 = None
last_line_time_team_1 = None
t0_last_line_chg = None
t0_current_line_time = None
t1_last_line_chg = None
t1_current_line_time = None
current_timestamp = None
t0_total_line_game_time = [0, 0, 0]
t1_total_line_game_time = [0, 0, 0]
t0_current_line_game_time = 0
t1_current_line_game_time = 0


# define function
def get_line_weights(current_players, lines, goalkeeper):
    line_weights = []
    current_players = np.array(current_players)
    current_players = current_players[current_players != goalkeeper]
    for line in lines:
        line_weights.append(np.sum([1 for player in current_players if player in line]) / len(current_players))
    return line_weights


# kafka stuff
@app.agent(playerPositionGroupedByTimeTopic)  # function executes when changes in topic
async def process(message):  # message is data from topis playerPositionGroupedByTime

    # set global variable (to store them out of the function)
    global last_line_team_0, last_line_team_1, last_players_team_0, last_players_team_1, last_line_time_team_0, last_line_time_team_1
    global t0_last_line_chg, t0_current_line_time, t1_last_line_chg, t1_current_line_time, current_timestamp, t0_total_line_game_time, t1_total_line_game_time
    global t0_current_line_game_time, t1_current_line_game_time

    # anync needed because of faust
    async for msg in message:
        eventExists = False
        msg_json = msg

        current_players_team_0 = [int(x) for x in list(msg_json["teams"]["team_0"].keys())]
        current_players_team_1 = [int(x) for x in list(msg_json["teams"]["team_1"].keys())]

        """ Preprocessing """
        # Filter out junk data
        if msg_json["time"] == 0 or len(current_players_team_0) < 6 or len(current_players_team_1) < 6:
            continue

        # Initialize line change timestamp
        current_timestamp = datetime.strptime(msg_json["time"], '%Y-%m-%d %H:%M:%S.%f%z')
        if t0_last_line_chg == None or t1_last_line_chg == None:
            t0_last_line_chg = current_timestamp
            t1_last_line_chg = current_timestamp

        """ Player changed """
        # New player
        for player in current_players_team_0:
            if player not in last_players_team_0:
                # print(current_timestamp, "Player", player, " has joined Team 0", consumer_record.offset)
                eventExists = True
        for player in current_players_team_1:
            if player not in last_players_team_1:
                # print(current_timestamp, "Player", player, " has joined Team 1", consumer_record.offset)
                eventExists = True

        # Player has left the field
        for player in last_players_team_0:
            if player not in current_players_team_0:
                # print(current_timestamp, "Player", player, " has left Team 0", consumer_record.offset)
                eventExists = True
        for player in last_players_team_1:
            if player not in current_players_team_1:
                # print(current_timestamp, "Player", player, " has left Team 1", consumer_record.offset)
                eventExists = True

        """ Line detection """
        # Line detection
        current_line_weights_team_0 = get_line_weights(current_players=current_players_team_0, lines=t0_lines,
                                                       goalkeeper=t0_goalkeeper)
        current_line_weights_team_1 = get_line_weights(current_players=current_players_team_1, lines=t1_lines,
                                                       goalkeeper=t1_goalkeeper)

        current_line_team_0 = np.argmax(current_line_weights_team_0)
        current_line_team_1 = np.argmax(current_line_weights_team_1)

        t0_current_line_time = (current_timestamp - t0_last_line_chg).seconds
        t1_current_line_time = (current_timestamp - t1_last_line_chg).seconds

        # Line change team 0
        if current_line_team_0 != last_line_team_0:
            #print(current_timestamp, "Team 0 has switched from", line_names[last_line_team_0], "to", line_names[current_line_team_0], consumer_record.offset)
            t0_last_line_chg = current_timestamp
            t0_current_line_game_time = 0
            eventExists = True

        # Line change team 1
        if current_line_team_1 != last_line_team_1:
            #print(current_timestamp, "Team 1 has switched from", line_names[last_line_team_1], "to", line_names[current_line_team_1], consumer_record.offset)
            t1_last_line_chg = current_timestamp
            t1_current_line_game_time = 0
            eventExists = True

        # execute when min. 1 second has passed
        if last_line_time_team_0 != t0_current_line_time or last_line_time_team_1 != t1_current_line_time:
            t0_total_line_game_time[current_line_team_0] += 1
            t1_total_line_game_time[current_line_team_1] += 1
            t0_current_line_game_time += 1
            t1_current_line_game_time += 1
            eventExists = True

        if eventExists:
            #print("Players Team 0:", sorted(current_players_team_0), ", line time:", t0_current_line_time)
            #print("Players Team 1:", sorted(current_players_team_1), ", line time:", t1_current_line_time)
            # Prepare JSON message
            response_msg= {}
            response_team_0 = {}
            response_team_1 = {}
            response_msg["time"] = str(current_timestamp)
            response_team_0["players"] = sorted(current_players_team_0)
            response_team_0["line"] = line_names[last_line_team_0]
            response_team_0["current_line_time"] = t0_current_line_game_time
            response_team_0["total_line_game_time"] = t0_total_line_game_time
            response_team_1["players"] = sorted(current_players_team_1)
            response_team_1["line"] = line_names[last_line_team_1]
            response_team_1["current_line_time"] = t1_current_line_game_time
            response_team_1["total_line_game_time"] = t1_total_line_game_time
            response_msg["team_0"] = response_team_0
            response_msg["team_1"] = response_team_1
            print(response_msg)
            await ShowLineTimeTopic.send(value=response_msg)

        # Set variables for next iteration
        last_players_team_0 = current_players_team_0
        last_players_team_1 = current_players_team_1
        last_line_team_0 = current_line_team_0
        last_line_team_1 = current_line_team_1
        last_line_time_team_0 = t0_current_line_time
        last_line_time_team_1 = t1_current_line_time        


app.main()