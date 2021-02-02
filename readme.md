# kalah-bot G25
A private repository for COMP34120 AI and Games First Semester Project: building a Kalah-playing bot.

Eu-Bin Kim
Stefan Ciocate			
Ilia Plavnik
Paul Stefanescu


## Running the submission

### dependencies (the agent server can't run without them)
First, please make sure to install the following libraries:
```
pip3 install transitions
pip3 install overrides
pip3 install numpy
```


### hosting the minimax agent
> Note: the python version we use is python3.

after the libraries are installed, unzip the archive:
```
tar -xzvf g25.tar.gz
```

this will unpack `kalah_python`. 

now without changing the directory, you can start hosting our minimax agent by running:
```
python3 -m kalah_python.host_minimax_agent --host=localhost --port=12345 --listen_forever=True
```
> This will start a server that waits for the netcat command as listed in the java command example.
> If --listen_forever is set to True, the server will continue to run and await new games until you 'control-c' it (This allows you to start it up once and call as many java commands as you want)
> If --listen_forever is set to True, the server will stop after playing one game.
> Remember that you can change the port as you wish
> Note: the server can be run using &, otherwise you will need another terminal for the java commands