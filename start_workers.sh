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
    
else
    echo "Stopping all python workers!"

    kill $(pgrep -f $WORKER_1)
    kill $(pgrep -f $WORKER_2)
    kill $(pgrep -f $WORKER_3)
    kill $(pgrep -f $WORKER_4)
    kill $(pgrep -f $WORKER_5)

    rm "$OUTPUT_PID_PATH/$OUTPUT_PID_FILE"
fi
