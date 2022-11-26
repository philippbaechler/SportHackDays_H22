#!/bin/bash


OUTPUT_PID_FILE=running.pid
OUTPUT_PID_PATH=.
PYTHON_EXE="python3"
WORKER_1="player_aggregation.py"
WORKER_1_ARGUMENTS="$WORKER_1 worker -l info --web-port=6066"
WORKER_2="calculate_center_of_gravity.py"
WORKER_2_ARGUMENTS="$WORKER_2 worker -l info --web-port=6067"
WORKER_3="find_team_bbox.py"
WORKER_3_ARGUMENTS="$WORKER_3 worker -l info --web-port=6068"
WORKER_4="filter_ball_positions.py"
WORKER_4_ARGUMENTS="$WORKER_4 worker -l info --web-port=6069"
WORKER_5="calculate_ball_v_and_dir.py"
WORKER_5_ARGUMENTS="$WORKER_5 worker -l info --web-port=6070"
WORKER_6="shot_detection.py"
WORKER_6_ARGUMENTS="$WORKER_6 worker -l info --web-port=6071"
WORKER_7="find_ball_possession.py"
WORKER_7_ARGUMENTS="$WORKER_7 worker -l info --web-port=6072"
WORKER_8="find_passes.py"
WORKER_8_ARGUMENTS="$WORKER_8 worker -l info --web-port=6073"


if [[ $# -gt 0 ]]; then
    PYTHON_EXE="$1"
fi


if [ ! -e "$OUTPUT_PID_PATH/$OUTPUT_PID_FILE" ]; then
    echo "Starting all python workers!"
    "$PYTHON_EXE" ./$WORKER_1_ARGUMENTS & echo $! > "$OUTPUT_PID_PATH/$OUTPUT_PID_FILE"
    "$PYTHON_EXE" ./$WORKER_2_ARGUMENTS & echo $! >> "$OUTPUT_PID_PATH/$OUTPUT_PID_FILE"
    "$PYTHON_EXE" ./$WORKER_3_ARGUMENTS & echo $! >> "$OUTPUT_PID_PATH/$OUTPUT_PID_FILE"
    "$PYTHON_EXE" ./$WORKER_4_ARGUMENTS & echo $! >> "$OUTPUT_PID_PATH/$OUTPUT_PID_FILE"
    "$PYTHON_EXE" ./$WORKER_5_ARGUMENTS & echo $! >> "$OUTPUT_PID_PATH/$OUTPUT_PID_FILE"
    "$PYTHON_EXE" ./$WORKER_6_ARGUMENTS & echo $! >> "$OUTPUT_PID_PATH/$OUTPUT_PID_FILE"
    "$PYTHON_EXE" ./$WORKER_7_ARGUMENTS & echo $! >> "$OUTPUT_PID_PATH/$OUTPUT_PID_FILE"
    "$PYTHON_EXE" ./$WORKER_8_ARGUMENTS & echo $! >> "$OUTPUT_PID_PATH/$OUTPUT_PID_FILE"
    
else
    echo "Stopping all python workers!"

    kill $(pgrep -f $WORKER_1)
    kill $(pgrep -f $WORKER_2)
    kill $(pgrep -f $WORKER_3)
    kill $(pgrep -f $WORKER_4)
    kill $(pgrep -f $WORKER_5)
    kill $(pgrep -f $WORKER_6)
    kill $(pgrep -f $WORKER_7)
    kill $(pgrep -f $WORKER_8)

    rm "$OUTPUT_PID_PATH/$OUTPUT_PID_FILE"
fi
