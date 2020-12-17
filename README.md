# kalah-bot G25
A private repository for COMP34120 AI and Games First Semester Project: building a Kalah-playing bot.

## Running the java engine
In the working directory of the project, try running:
```
java -jar ./kalah/ManKalah.jar "java -jar ./kalah/MKRefAgent.jar" "java -jar ./kalah/JimmyPlayer.jar"
```
or:
```
java -jar ./kalah/ManKalah.jar "java -jar ./kalah/MKRefAgent.jar" "nc localhost 12345"
```

## Running the submission
first, unzip the archive.
```
unzip g25.zip -d .
```
activate the virtualenv included in the archive
```
source activate kalahenv/bin/activate
```
start hosting the agent
```
python3 -m kalah_python.host_minimax_agent
```
