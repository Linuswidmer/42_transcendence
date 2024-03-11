import random

def create_tournament_tree(players):
    # Randomly shuffle the players
    random.shuffle(players)

    # Pair the players into matches
    matches = [(players[i], players[i + 1]) for i in range(0, len(players), 2)]

    return matches