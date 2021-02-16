SnakeNEAT

Genetic Breeding Neural Network capable of playing Snake through NEAT. The Snake game and the model visualization is built using PyGame.

The Snake is bred through natural selection of the most fit Snake in each generation. The fitness is determined by time alive along with its score. The Snake is rewarded more heavily for eating apples than surviving. The Snake is also punished for only staying alive and not eating apples through a "starvation" score.

The network is fed 24 inputs: N, NE, E, SE, S, SW, W, NW euclidean distance from the snakes head and the wall, its tail, and the apple. These inputs are then used to determine 4 outputs: move left, move right, move up, move down.

After 1000 generations of natural selection, the model can consistently score 10+.
