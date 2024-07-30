#!/bin/bash

DEFAULT_HOST="127.0.0.1"
DEFAULT_PORT="4002"

usage() {
    echo "Usage: $0 --exercise_folder <folder> [--host <host>] [--port <port>]"
    exit 1
}

HOST=""
PORT=""
EXERCISE_FOLDER=""

while [ "$#" -gt 0 ]; do
    case "$1" in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --exercise_folder)
            EXERCISE_FOLDER="$2"
            shift 2
            ;;
        *)
            usage
            ;;
    esac
done

if [ -z "$EXERCISE_FOLDER" ]; then
    echo "Error: --exercise_folder argument is required."
    usage
fi


HOST=${HOST:-$DEFAULT_HOST}
PORT=${PORT:-$DEFAULT_PORT}

echo "EXERCISE_FOLDER: $EXERCISE_FOLDER"
echo "HOST: $HOST"
echo "PORT: $PORT"

source venv/bin/activate
EXERCISE_FOLDER="$EXERCISE_FOLDER" fastapi run main.py --host "$HOST" --port "$PORT"
