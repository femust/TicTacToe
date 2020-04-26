#!/usr/bin/python3
import numpy as np


def move_still_possible(S):
    return not (S[S == 0].size == 0)


def move_at_random(S, p):
    xs, ys = np.where(S == 0)

    i = np.random.permutation(np.arange(xs.size))[0]

    S[xs[i], ys[i]] = p

    return S


def human_move(S, p):
    xs, ys = np.where(S == 0)
    correct_move = False
    while (not correct_move):
        print("Where to place x? [0..2]")
        x = int(input("Pick x: "))
        y = int(input("Pick y: "))
        if (x in xs and y in ys and S[x, y] == 0):
            correct_move = True
            S[x, y] = p
        else:
            print("Incorrect move!")
    return S


def move_was_winning_move(S, p):
    if np.max((np.sum(S, axis=0)) * p) == 3:
        return True

    if np.max((np.sum(S, axis=1)) * p) == 3:
        return True

    if (np.sum(np.diag(S)) * p) == 3:
        return True

    if (np.sum(np.diag(np.rot90(S))) * p) == 3:
        return True

    return False


# python dictionary to map integers (1, -1, 0) to characters ('x', 'o', ' ')
symbols = {1: 'x',
           -1: 'o',
           0: ' '}


# print game state matrix using characters
def print_game_state(S):
    B = np.copy(S).astype(object)
    for n in [-1, 0, 1]:
        B[B == n] = symbols[n]
    print(B)


class Bot():
    def __init__(self, root):
        self.root = root
        self.current_node = root
        self.depth = 0
        self.elements_in_given_depth = {self.depth: [root]}

    def add_state(self, state):
        node_to_append = State(state, self.current_node)

        self.depth = self.depth + 1
        self.elements_in_given_depth[self.depth] = [node_to_append]

        self.current_node.children.append(node_to_append)
        self.current_node = node_to_append

    def pick(self):
        self.current_node.generate_children()

        self.depth = self.depth + 1
        movement = self.current_node.children[0]
        self.elements_in_given_depth[self.depth] = []
        for child in self.current_node.children:
            if child not in self.elements_in_given_depth[self.depth]:
                self.elements_in_given_depth[self.depth].append(child)
            if (child.value > movement.value):
                movement = child
        return child.id

    def learn(self, who_won):
        if (who_won == 1 or who_won == 0):
            self.current_node.value = 0
            self.update(self.current_node)
        if (who_won == -1):
            self.current_node.value = 1
            self.update(self.current_node)

    def update(self, from_node):
        while (from_node != self.root):
            from_node.parent.value = from_node.parent.value + \
                0.2 * (from_node.value - from_node.parent.value)

    def reset(self):
        self.current_node = self.root


class State():
    def __init__(self, id, parent):
        self.id = id
        self.parent = parent
        self.children = []
        self.value = 0.1

    def generate_children(self, p=-1):
        xs, ys = np.where(self.id == 0)
        for x, y in zip(xs, ys):
            grid = np.copy(self.id)
            grid[x, y] = p
            self.children.append(State(grid, self.id))
        for child in self.children:
            print(child.id)


if __name__ == '__main__':
    # initialize an empty tic tac toe board
    gameState = np.zeros((3, 3), dtype=int)
    init_state = State(gameState, None)
    bot = Bot(init_state)
    HUMAN_PLAYER = 1  # const, assumption that the player has 1 symbol

    for i in np.arange(10):
        print("Bot vs human, game number: " + str(i))
        gameState = np.zeros((3, 3), dtype=int)
        # initialize the player who moves first (either +1 or -1)
        player = 1

        # initialize a move counter
        mvcntr = 1

        # initialize a flag that indicates whetehr or not game has ended
        noWinnerYet = True

        while move_still_possible(gameState) and noWinnerYet:
            # turn current player number into player symbol
            name = symbols[player]
            print('%s moves' % name)

            # let current player move at random
            if (player == HUMAN_PLAYER):
                gameState = human_move(gameState, player)
                bot.add_state(gameState)
            else:
                #gameState = move_at_random(gameState, player)
                gameState = bot.pick()
                pass

            # print current game state
            print_game_state(gameState)

            # evaluate current game state
            if move_was_winning_move(gameState, player):
                print('player %s wins after %d moves' % (name, mvcntr))
                won = player

            # switch current player and increase move counter
            player *= -1
            mvcntr += 1

        if noWinnerYet:
            print('game ended in a draw')
            won = 0

        bot.learn(won)
