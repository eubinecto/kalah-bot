# arguments to be provided
HOST=localhost
PORT=12346
MKREF_PATH=./kalah/MKRefAgent.jar
python3 -m kalah_python.host_g25_agent --host=$HOST --port=$PORT & sleep 0.5
java -jar ./kalah/ManKalah.jar "nc $HOST $PORT" "java -jar $MKREF_PATH"
sleep 0.5 && python3 -m kalah_python.host_g25_agent --host=$HOST --port=$PORT & sleep 0.5
java -jar ./kalah/ManKalah.jar "java -jar $MKREF_PATH" "nc $HOST $PORT"