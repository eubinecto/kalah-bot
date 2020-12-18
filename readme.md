# kalah-bot G25
A private repository for COMP34120 AI and Games First Semester Project: building a Kalah-playing bot.


## Running the submission

### dependencies
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
unzip g25.zip -d ./
```

this will unpack `kalah_python`. 

now, you can start hosting our minimax agent by running:
```
python3 -m kalah_python.host_minimax_agent --host=localhost --port=12345 --listen_forever=True
```
> Note: If you want the agent to listen to server again, set `--listen_forever` to True. 
> this will reset the game and start playing the game again.

