#!/usr/bin/python3
import matplotlib.pyplot as plt
import numpy as np
import random


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
        self.be_explorer = False
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
            is_in_history, state = self.check_is_in_history(possible_state)
            if is_in_history:
                moves_to_consider.append(state)
            else:
                append_state = State(possible_state)
                self.states_in_given_depth_history[self.depth].append(
                    append_state)
                moves_to_consider.append(append_state)

        if (self.be_explorer):
            explore = self.is_time_for_exploration()
            if (explore):
                movement = random.choice(moves_to_consider)
            else:
                movement = self.find_the_best_move(moves_to_consider)
        else:
            movement = self.find_the_best_move(moves_to_consider)

        self.path.append(movement)

        return self.decode_state(movement.id)

    def find_the_best_move(self, moves_to_consider):
        movement = moves_to_consider[0]
        for move in moves_to_consider:
            if (movement.value < move.value):
                movement = move
        return movement

    def check_is_in_history(self, possible_state):
        is_in_history = False
        state_out = None
        for state in self.states_in_given_depth_history[self.depth]:
            if (possible_state == state.id):
                is_in_history = True
                state_out = state
                break
        return is_in_history, state_out

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

    def is_time_for_exploration(self):
        do_random = False
        dice = np.random.permutation(np.arange(10))[0]
        if (dice == 9):
            do_random = True
        return do_random


class State():
    def __init__(self, id):
        self.id = id
        self.value = 0.1


if __name__ == '__main__':
    HUMAN_PLAYER = 1  # assumption that the player has 1 symbol
    # initialize a move counter

    # initialize a flag that indicates whetehr or not game has ended

    player1 = Player("random", 1)
    player2 = Player("ai", -1)
    player1_loosing_curve = []
    player2_learning_curve = []
    drawing_curve = []

    number_of_games = 10000
    player1_wins = 0
    player2_wins = 0
    draws = 0

    for i in np.arange(1, number_of_games+1):
        # initialize an empty tic tac toe board
        #print("Bot vs human, game number: " + str(i))
        gameState = np.zeros((3, 3), dtype=int)
        noWinnerYet = True
        player = 1
        mvcntr = 1

        while move_still_possible(gameState) and noWinnerYet:
            # turn current player number into player symbol
            name = symbols[player]
            #print('%s moves' % name)

            # print current game state
            # print_game_state(gameState)
            # let current player move at random
            if (player == HUMAN_PLAYER):
                gameState = player1.make_move(gameState)
            else:
                gameState = player2.make_move(gameState)

            # evaluate current game state
            if move_was_winning_move(gameState, player):
                #print('player %s wins after %d moves' % (name, mvcntr))
                noWinnerYet = False
                who_won = player
                # print_game_state(gameState)
                break
            # switch current player and increase move counter
            player *= -1
            mvcntr += 1

        if noWinnerYet:
            #print('game ended in a draw')
            who_won = 0

        if (player2.type == "ai"):
            player2.bot.learn(who_won)
            player2.bot.reset_current_game()

        if (who_won == 1):
            player1_wins = player1_wins + 1
        if (who_won == -1):
            player2_wins = player2_wins + 1
        if (who_won == 0):
            draws = draws + 1

        if (i % 100 == 0):
            print("player 1: " + str(player1_wins / 100))
            print("player 2: " + str(player2_wins / 100))
            print("draws: " + str(draws / 100))
            player1_loosing_curve.append(player1_wins / 100)
            player2_learning_curve.append(player2_wins / 100)
            drawing_curve.append(draws / 100)
            player1_wins = 0
            player2_wins = 0
            draws = 0
plt.plot(player1_loosing_curve)
plt.title("Player 1 curve")
plt.show()

plt.title("Player 2 - AI curve")
plt.plot(player2_learning_curve)
plt.show()

plt.title("Drawing curve")
plt.plot(drawing_curve)
plt.show()
