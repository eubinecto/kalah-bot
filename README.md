# kalah-bot G25
A private repository for COMP34120 AI and Games First Semester Project: building a Kalah-playing bot.

## Running the java engine
In the working directory of the project, try running:
```
java -jar ./kalah/ManKalah.jar "java -jar ./kalah/MKRefAgent.jar" "java -jar ./kalah/JimmyPlayer.jar"
```
or:
```
java -jar ./kalah/ManKalah.jar "java -jar ./kalah/MKRefAgent.jar" "nc localhost 12346"
```

## Running the submission
first, unzip the archive.
```
unzip g25.zip -d ./
```

start hosting the agent.
If you want the agent to listen to server forever even after a game ends,
set `--run_forever` to True.
```
python3 -m kalah_python.host_minimax_agent --host=localhost --port=12345 --listen_forever=True
```
