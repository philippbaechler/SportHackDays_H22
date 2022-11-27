import json
import numpy as np
from pymongo import MongoClient
from kafka import KafkaConsumer

group_id = "line-detection-visualization"
consumer = KafkaConsumer(bootstrap_servers='86.119.35.55',
                         auto_offset_reset='earliest',
                         group_id=group_id)
consumer.subscribe('ShowLineTime')

# Connect to Mongo DB
CONNECTION_STRING = "mongodb+srv://dartfish:615sZKN7UxYIKsXj@michacluster.gpmb4ck.mongodb.net/dartfish"
# Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
client = MongoClient(CONNECTION_STRING)
db = client["dartfish"]
col = db["lines"]
# delete everything first
x = col.delete_many({})
print("Everything deleted")
dummy = {}
dummy["id"] = 0
col.insert_one(dummy)

print("Start polling...")
while True:
    # try:
    """ Kafka read message """
    records = consumer.poll(10.0, update_offsets=True)

    for topic_data, consumer_records in records.items():
        for consumer_record in consumer_records:
            msg_json = json.loads(consumer_record.value.decode('utf-8'))
            response = {}
            response["id"] = 0
            response["offset"] = consumer_record.offset
            response["time"] = msg_json["time"]
            response["team_0_current_line_time"] = msg_json["team_0"]["current_line_time"]
            response["team_0_current_line"] = msg_json["team_0"]["line"]
            response["team_0_current_players"] = str(msg_json["team_0"]["players"])
            response["team_0_total_line_game_time_l1"] = msg_json["team_0"]["total_line_game_time"][0]
            response["team_0_total_line_game_time_l2"] = msg_json["team_0"]["total_line_game_time"][1]
            response["team_0_total_line_game_time_l3"] = msg_json["team_0"]["total_line_game_time"][2]
            response["team_1_current_line_time"] = msg_json["team_1"]["current_line_time"]
            response["team_1_current_line"] = msg_json["team_1"]["line"]
            response["team_1_current_players"] = str(msg_json["team_1"]["players"])
            response["team_1_total_line_game_time_l1"] = msg_json["team_1"]["total_line_game_time"][0]
            response["team_1_total_line_game_time_l2"] = msg_json["team_1"]["total_line_game_time"][1]
            response["team_1_total_line_game_time_l3"] = msg_json["team_1"]["total_line_game_time"][2]
            #col.insert_one(response)
            x = col.replace_one({"id": 0}, response)
            print(response)


