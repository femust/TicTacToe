#!/usr/bin/python3
import numpy as np


def move_still_possible(S):
    return not (S[S == 0].size == 0)


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
        self.path = []
        self.path.append(root)
        self.states_in_given_depth = dict()
        for i in np.arange(9):
            self.states_in_given_depth[i] = []

    def move_at_random(self, S):
        xs, ys = np.where(S == 0)
        i = np.random.permutation(np.arange(xs.size))[0]
        S[xs[i], ys[i]] = -1
        return S

    def move_greedy(self, S):
        self.depth = self.depth + 1
        # node_to_append = State(S, self.current_node)
        # is_node_to_append_in_given_depth = False
        # for state_in_give_depth in self.states_in_given_depth[self.depth]:
        #     if np.all(node_to_append.id, state_in_give_depth.id):
        #         is_node_to_append_in_given_depth = True

        # if (not is_node_to_append_in_given_depth):
        #     self.states_in_given_depth[self.depth].append(node_to_append)

        # self.current_node = node_to_append
        # self.path.append(self.current_node)
        # take the action
        self.depth = self.depth + 1
        possible_id_states = self.generate_possible_id_states(S)
        for possible_id_state in possible_id_states:
            is_possible_state_in_depth = False
            for state_in_given_depth in self.states_in_given_depth[self.depth]:
                if np.all(possible_id_state == state_in_given_depth.id):
                    is_possible_state_in_depth = True
                    break
            if(not is_possible_state_in_depth):
                self.states_in_given_depth[self.depth].append(
                    State(possible_id_state))

        state_in_given_depth = None

        movement = self.states_in_given_depth[self.depth][0]
        first_element = True
        for state_in_given_depth in self.states_in_given_depth[self.depth]:
            to_consider = False
            for possible_id_state in possible_id_states:
                if (np.all(possible_id_state == state_in_given_depth.id)):
                    to_consider = True
                    if (first_element):
                        movement = state_in_given_depth
                        first_element = False
            if (to_consider):
                if (movement.value < state_in_given_depth.value):
                    movement = state_in_given_depth
        self.path.append(movement)
        S = np.copy(movement.id)
        return S

#    def add_state(self, state):
#         node_to_append = State(state, self.current_node)

#         self.depth = self.depth + 1

#         self.states_in_given_depth[self.depth] = [node_to_append]

#         self.current_node.children.append(node_to_append)
#         self.current_node = node_to_append

#     def pick(self):
#         self.current_node.generate_children()

#         self.depth = self.depth + 1
#         movement = self.current_node.children[0]
#         self.states_in_given_depth[self.depth] = []
#         for child in self.current_node.children:
#             if child not in self.states_in_given_depth[self.depth]:
#                 self.states_in_given_depth[self.depth].append(child)
#             if (child.value > movement.value):
#                 movement = child
#         return child.id

    def learn(self, who_won):
        if (who_won == 1 or who_won == 0):
            self.path[-1].value = 0
            self.update()
        if (who_won == -1):
            self.path[-1].value = 1
            self.update()

    def update(self):
        while (len(self.path) is not 2):
            s_prim = self.path.pop()
            s = self.path[-1]
            s.value = s.value + 0.2 * (s_prim.value - s.value)

    def reset(self):
        self.path = []
        self.path.append(self.root)
        self.depth = 0

    def generate_possible_id_states(self, S):
        possible_states = []
        xs, ys = np.where(S == 0)
        for x, y in zip(xs, ys):
            grid = np.copy(S)
            grid[x, y] = -1
            possible_states.append(grid)
        return possible_states


class State():
    def __init__(self, id):
        self.id = id
        self.children = []
        self.value = 0.1

    # def generate_possible_id_states(self, p=-1):
    #     possible_states = []
    #     xs, ys = np.where(self.id == 0)
    #     for x, y in zip(xs, ys):
    #         grid = np.copy(self.id)
    #         grid[x, y] = p
    #         possible_states.append(grid)
    #     return possible_states


if __name__ == '__main__':
    # initialize an empty tic tac toe board
    gameState = np.zeros((3, 3), dtype=int)
    init_state = State(gameState)
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
            else:
                # gameState = move_at_random(gameState, player)
                gameState = bot.move_greedy(gameState)
                pass

            # print current game state
            print_game_state(gameState)

            # evaluate current game state
            if move_was_winning_move(gameState, player):
                print('player %s wins after %d moves' % (name, mvcntr))
                noWinnerYet = False
                won = player

            # switch current player and increase move counter
            player *= -1
            mvcntr += 1

        if noWinnerYet:
            print('game ended in a draw')
            won = 0

        bot.learn(won)
        bot.reset()
