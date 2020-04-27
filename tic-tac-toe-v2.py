#!/usr/bin/python3
import numpy as np


def move_still_possible(S):
    return not (S[S == 0].size == 0)


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


class Player():
    def __init__(self, type, player):
        self.type = type
        self.player = player
        if not self.type in ["manual", "random", "ai"]:
            raise NameError
        if self.type == "ai":
            self.bot = Bot()

    def make_move(self, S):
        if self.type == "random":
            return self.move_at_random(S)
        if self.type == "manual":
            return self.manual_move(S)
        if self.type == "ai":
            return self.bot_move(S)

    def move_at_random(self, S):
        xs, ys = np.where(S == 0)
        i = np.random.permutation(np.arange(xs.size))[0]
        S[xs[i], ys[i]] = self.player
        return S

    def manual_move(self, S):
        xs, ys = np.where(S == 0)
        correct_move = False
        while (not correct_move):
            print("Where to place x? [0..2]")
            x = int(input("Pick x: "))
            y = int(input("Pick y: "))
            if (x in xs and y in ys and S[x, y] == 0):
                correct_move = True
                S[x, y] = self.player
            else:
                print("Incorrect move!")
        return S

    def bot_move(self, S):
        return self.bot.move(S)


class Bot():
    def __init__(self):
        self.depth = 0
        self.path = []
        self.states_in_given_depth_history = dict()
        for i in np.arange(9):
            self.states_in_given_depth_history[i] = []

    def encode_state(self, S):
        return np.array2string(S, separator=',').replace("[", "").replace("]", "").replace("\n", "").replace(" ", "")

    def decode_state(self, S):
        return np.fromstring(S, dtype="int", sep=",").reshape(3, 3)

    def move(self, S):
        # we're assuming that the bot plays always second for simplicity
        self.depth = self.depth + 2
        possible_states = self.generate_possible_id_states(S)

        moves_to_consider = []
        for possible_state in possible_states:
            if possible_state in self.states_in_given_depth_history[self.depth]:
                moves_to_consider.append(
                    self.states_in_given_depth_history[self.depth].index(possible_state))
            else:
                append_state = State(possible_state)
                self.states_in_given_depth_history[self.depth].append(
                    append_state)
                moves_to_consider.append(append_state)

        movement = moves_to_consider[0]

        for move in moves_to_consider:
            if (movement.value < move.value):
                movement = move

        self.path.append(movement)

        return self.decode_state(movement.id)

    def generate_possible_id_states(self, S):
        possible_states = []
        xs, ys = np.where(S == 0)
        for x, y in zip(xs, ys):
            grid = np.copy(S)
            grid[x, y] = -1
            possible_states.append(self.encode_state(grid))
        return possible_states

    def learn(self, who_won):
        if (who_won == 1 or who_won == 0):
            self.path[-1].value = 0
        if (who_won == -1):
            self.path[-1].value = 1
        self.update()

    def update(self):
        while (len(self.path) is not 1):
            s_prim = self.path[-1]
            s = self.path[-2]
            s.value = s.value + 0.2 * (s_prim.value - s.value)
            self.path.pop()

    def reset_current_game(self):
        self.path = []
        self.depth = 0


class State():
    def __init__(self, id):
        self.id = id
        self.value = 0.1


if __name__ == '__main__':
    # initialize an empty tic tac toe board
    gameState = np.zeros((3, 3), dtype=int)

    # initialize the player who moves first (either +1 or -1)
    player = 1

    HUMAN_PLAYER = 1  # assumption that the player has 1 symbol
    # initialize a move counter
    mvcntr = 1

    # initialize a flag that indicates whetehr or not game has ended
    noWinnerYet = True

    player1 = Player("manual", 1)
    player2 = Player("ai", -1)

    while move_still_possible(gameState) and noWinnerYet:
        # turn current player number into player symbol
        name = symbols[player]
        print('%s moves' % name)

        # let current player move at random
        if (player == HUMAN_PLAYER):
            gameState = player1.make_move(gameState)
        else:
            gameState = player2.make_move(gameState)

        # print current game state
        print_game_state(gameState)

        # evaluate current game state
        if move_was_winning_move(gameState, player):
            print('player %s wins after %d moves' % (name, mvcntr))
            noWinnerYet = False
            who_won = player
            break
        # switch current player and increase move counter
        player *= -1
        mvcntr += 1

    if noWinnerYet:
        print('game ended in a draw')

if (player2.type == "ai"):
    player2.bot.learn(who_won)
    player2.bot.reset_current_game()
