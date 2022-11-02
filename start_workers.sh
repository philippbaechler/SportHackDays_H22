#!/bin/bash


OUTPUT_PID_FILE=running.pid
OUTPUT_PID_PATH=.
PYTHON_EXE="python3"
WORKER_1="player_aggregation.py"
WORKER_1_ARGUMENTS="$WORKER_1 worker -l info --web-port=6066"
WORKER_2="calculate_center_of_gravity.py"
WORKER_2_ARGUMENTS="$WORKER_2 worker -l info --web-port=6067"


if [[ $# -gt 0 ]]; then
    PYTHON_EXE="$1"
fi


if [ ! -e "$OUTPUT_PID_PATH/$OUTPUT_PID_FILE" ]; then
    echo "Starting all python workers!"
    "$PYTHON_EXE" ./$WORKER_1_ARGUMENTS & echo $! > "$OUTPUT_PID_PATH/$OUTPUT_PID_FILE"
    "$PYTHON_EXE" ./$WORKER_2_ARGUMENTS & echo $! >> "$OUTPUT_PID_PATH/$OUTPUT_PID_FILE"
else
    echo "Stopping all python workers!"

    kill $(pgrep -f $WORKER_1)
    kill $(pgrep -f $WORKER_2)

    rm "$OUTPUT_PID_PATH/$OUTPUT_PID_FILE"
fi
