# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Coord, Direction, \
    Action, MoveAction, GrowAction, GameBegin, Board

from .internal_board import InternalBoard

import numpy as np

class Agent:
    """
    This class is the "entry point" for your agent, providing an interface to
    respond to various Freckers game events.
    """
    # Node access constants for node tuple
    # Credit: Canvas robot-search strategy example
    COORDINATES = 0
    CELL_STATE = 1
    PARENT = 2
    ACTION = 3
    DEPTH = 4
    CHILDREN = 5


    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        Any setup and/or precomputation should be done here.
        """
        self._color = color
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as RED")
            case PlayerColor.BLUE:
                print("Testing: I am playing as BLUE")

        # Construct initial board representation
        self._board = InternalBoard(color)



    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 
        """

        # Implement minimax with alpha-beta pruning here



        # Below we have hardcoded two actions to be played depending on whether
        # the agent is playing as BLUE or RED. Obviously this won't work beyond
        # the initial moves of the game, so you should use some game playing
        # technique(s) to determine the best action to take.
        match self._color:
            case PlayerColor.RED:
                print("Testing: RED is playing a MOVE action")
                return MoveAction(
                    Coord(0, 3),
                    [Direction.Down]
                )
            case PlayerColor.BLUE:
                print("Testing: BLUE is playing a GROW action")
                return GrowAction()

        # Our board will be updated by referee


    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after a player has taken their
        turn. You should use it to update the agent's internal game state. 
        """

        # There are two possible action types: MOVE and GROW. Below we check
        # which type of action was played and print out the details of the
        # action for demonstration purposes. You should replace this with your
        # own logic to update your agent's internal game state representation.
        match action:
            case MoveAction(coord, dirs):
                dirs_text = ", ".join([str(dir) for dir in dirs])
                print(f"Testing: {color} played MOVE action:")
                print(f"  Coord: {coord}")
                print(f"  Directions: {dirs_text}")

                # Update the internal board with the move
                self._board.update(action)


            case GrowAction():
                print(f"Testing: {color} played GROW action")
            case _:
                raise ValueError(f"Unknown action type: {action}")



    def alpha_beta_cutoff_search(self, d = 4, **referee: dict) -> Action:
        """
        Searches for the best possible action given the state of the game using the
        minimax with alpha-beta pruning algorithm. Cutoff is based on depth and presence of a terminal state.
        Evaluates each state using an evaluation function to choose the best action.

        Credit to AIMA textbook for the algorithm structure.
        """

        # Functions required for alpha-beta pruning
        def max_value(alpha, beta, depth):
            pass

        def min_value(alpha, beta, depth):
            pass

        def cutoff_test(depth):
            """
            Returns True if the current depth is greater
            than the cutoff depth or if the state is terminal.
            """
            return depth > d or self._board.terminal_state()

        # Body of Alpha beta pruning algorithm
        beta = np.inf
        best_score = -np.inf
        best_action = None

        # Look through all possible actions
        for action in self._board.get_possible_actions():



