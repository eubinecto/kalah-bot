# kalah-bot G25
A private repository for COMP34120 AI and Games First Semester Project: building a Kalah-playing bot.


## Running the code
In the working directory of the project, try running:
```
java -jar ./kalah/ManKalah.jar "java -jar ./kalah/MKRefAgent.jar" "java -jar ./kalah/JimmyPlayer.jar"

```

or:
```
java -jar ./kalah/ManKalah.jar "java -jar ./kalah/MKRefAgent.jar" "nc localhost 12345"

```

and the program should output something like:
```
0  --  7  7  7  7  7  7  7
7  7  7  7  7  7  7  --  0
Move: South - 1
0  --  7  7  7  7  7  7  7
0  8  8  8  8  8  8  --  1
Move: Swap
Move: North - 1
1  --  8  8  8  8  8  8  0
0  8  8  8  8  8  8  --  1
Move: North - 2
2  --  9  9  9  9  9  0  0
1  9  8  8  8  8  8  --  1
Move: South - 4
2  --  9  9  9  10  10  1  1
1  9  8  0  9  9  9  --  2
Move: North - 1
2  --  9  9  9  10  10  2  0
1  9  8  0  9  9  9  --  2
Move: South - 3
2  --  9  9  9  10  11  3  1
1  9  0  1  10  10  10  --  3
Move: North - 1
2  --  9  9  9  10  11  4  0
1  9  0  1  10  10  10  --  3
Move: South - 6
2  --  10  10  10  11  12  5  1
2  9  0  1  10  0  11  --  4
Move: North - 1
2  --  10  10  10  11  12  6  0
2  9  0  1  10  0  11  --  4
Move: South - 5
2  --  11  11  11  12  13  7  1
2  9  0  1  0  1  12  --  5
Move: North - 1
2  --  11  11  11  12  13  8  0
2  9  0  1  0  1  12  --  5
Move: South - 4
2  --  11  11  11  12  0  8  0
2  9  0  0  0  1  12  --  19
Move: North - 4
17  --  12  12  12  0  0  8  0
3  10  1  1  1  2  0  --  19
Move: South - 6
17  --  12  12  12  0  0  8  0
3  10  1  1  1  0  1  --  20
Move: South - 7
17  --  12  12  12  0  0  8  0
3  10  1  1  1  0  0  --  21
Move: South - 5
17  --  12  12  12  0  0  0  0
3  10  1  1  0  0  0  --  30
Move: North - 7
21  --  0  12  12  0  1  1  1
4  11  2  0  1  1  1  --  30
Move: South - 7
21  --  0  12  12  0  1  1  1
4  11  2  0  1  1  0  --  31
Move: South - 3
21  --  0  12  12  0  1  1  1
4  11  0  1  2  1  0  --  31
Move: North - 3
23  --  0  12  12  0  0  1  1
4  11  0  0  2  1  0  --  31
Move: South - 5
23  --  0  12  12  0  0  1  0
4  11  0  0  0  2  0  --  33
Move: North - 2
23  --  0  12  12  0  1  0  0
4  11  0  0  0  2  0  --  33
Move: South - 6
23  --  0  12  12  0  1  0  0
4  11  0  0  0  0  1  --  34
Move: South - 7
23  --  0  12  12  0  1  0  0
4  11  0  0  0  0  0  --  35
Move: South - 1
23  --  0  12  12  0  0  0  0
0  12  1  1  0  0  0  --  37
Move: North - 5
26  --  1  13  0  0  0  0  1
1  13  2  2  1  0  1  --  37
Move: South - 7
26  --  1  13  0  0  0  0  1
1  13  2  2  1  0  0  --  38
Move: South - 1
26  --  1  13  0  0  0  0  1
0  14  2  2  1  0  0  --  38
Move: North - 1
26  --  1  13  0  0  0  1  0
0  14  2  2  1  0  0  --  38
Move: South - 4
26  --  1  13  0  0  0  0  0
0  14  2  0  2  0  0  --  40
Move: North - 7
27  --  0  13  0  0  0  0  0
0  14  2  0  2  0  0  --  40
Move: North - 6
30  --  1  0  0  0  1  1  1
1  15  3  0  3  1  1  --  40
Move: South - 7
30  --  1  0  0  0  1  1  1
1  15  3  0  3  1  0  --  41
Move: South - 2
30  --  2  0  1  1  2  2  2
2  0  4  1  4  2  1  --  44
Move: North - 1
30  --  2  0  1  1  3  3  0
2  0  4  1  4  2  1  --  44
Move: South - 7
30  --  2  0  1  1  3  3  0
2  0  4  1  4  2  0  --  45
Move: South - 6
30  --  2  0  1  1  3  3  0
2  0  4  1  4  0  1  --  46
Move: South - 7
30  --  2  0  1  1  3  3  0
2  0  4  1  4  0  0  --  47
Move: South - 5
30  --  2  0  1  1  3  3  1
2  0  4  1  0  1  1  --  48
Move: North - 1
30  --  2  0  1  1  3  4  0
2  0  4  1  0  1  1  --  48
Move: South - 1
30  --  2  0  1  1  3  4  0
0  1  5  1  0  1  1  --  48
Move: North - 2
32  --  2  0  2  2  4  0  0
0  0  5  1  0  1  1  --  48
Move: South - 4
32  --  2  0  2  2  0  0  0
0  0  5  0  0  1  1  --  53
Move: North - 4
32  --  2  1  3  0  0  0  0
0  0  5  0  0  1  1  --  53
Move: South - 7
32  --  2  1  3  0  0  0  0
0  0  5  0  0  1  0  --  54
Move: South - 3
32  --  2  1  3  0  0  0  0
0  0  0  1  1  2  1  --  55
Move: South - 7
32  --  2  1  3  0  0  0  0
0  0  0  1  1  2  0  --  56
Move: South - 4
32  --  2  1  3  0  0  0  0
0  0  0  0  2  2  0  --  56
Move: North - 5
33  --  3  2  0  0  0  0  0
0  0  0  0  2  2  0  --  56
Move: North - 6
34  --  4  0  0  0  0  0  0
0  0  0  0  2  2  0  --  56
Move: North - 7
35  --  0  0  0  0  0  0  0
0  0  0  0  0  0  0  --  63

WINNER: Player 2 (java -jar ./kalah/JimmyPlayer.jar)
SCORE: 28

Player 2 (java -jar ./kalah/JimmyPlayer.jar): 30 moves, 99 milliseconds per move
Player 1 (java -jar ./kalah/MKRefAgent.jar): 22 moves, 0 milliseconds per move

0 0
1 99

```


