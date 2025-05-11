# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Coord, Direction, \
    Action, MoveAction, GrowAction, GameBegin

from .internal_board import InternalBoard

import numpy as np

class Agent:
    """
    This class is the "entry point" for your agent, providing an interface to
    respond to various Freckers game events.
    """

    # Depth limit for the alpha-beta pruning algorithm
    MAX_DEPTH = 4


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
        # Call minimax with alpha-beta pruning here
        # best_action = self.minmax_decision(self._board, self.MAX_DEPTH)p
        best_action = self.alpha_beta_cutoff_search(self.MAX_DEPTH, **referee)
        return best_action
        """
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
        """
        # Our board will be updated by referee so no need to update it here


    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after a player has taken their
        turn. You should use it to update the agent's internal game state. 
        """

        # There are two possible action types: MOVE and GROW. Below we check
        # which type of action was played and print out the details of the
        # action for demonstration purposes. You should replace this with your
        # own logic to update your agent's internal game state representation.
        # Update the internal board with the move
        self._board.update(action)

        # Given code
        """
        match action:
            case MoveAction(coord, dirs):
                dirs_text = ", ".join([str(dir) for dir in dirs])
                print(f"Testing: {color} played MOVE action:")
                print(f"  Coord: {coord}")
                print(f"  Directions: {dirs_text}")

                


            case GrowAction():
                print(f"Testing: {color} played GROW action")
            case _:
                raise ValueError(f"Unknown action type: {action}")
        """




    def alpha_beta_cutoff_search(self, d, **referee: dict) -> Action:
        """
        Searches for the best possible action given the state of the game using the
        minimax with alpha-beta pruning algorithm. Cutoff is based on depth and presence of a terminal state.
        Evaluates each state using an evaluation function to choose the best action.

        Credit to AIMA textbook for the algorithm structure.
        """
        # Functions required for alpha-beta pruning
        def max_value(alpha, beta, depth, depth_counter):
            # Stop searching if we reach cutoff depth or terminal state
            if self._board.terminal_state() or cutoff_test(depth):
                depth_counter['depth'] = max(depth_counter['depth'], depth)
                return self._board.eval()
            # Best value for max at this node so gar
            # (Staring with the worst possible value)
            v = -np.inf
            # Look through all legal actions
            legal_actions = self._board.get_all_legal_actions(self._color)
            action_scores = {
                a: self._board.movement_progress_heuristic(a, self._color)
                for a in legal_actions
            }
            sorted_actions = sorted(legal_actions, key=lambda a: action_scores[a], reverse=True)

            for a in sorted_actions:
                # Apply action
                self._board.update(a)
                #print(f"{a} → {action_scores[a]}")
                action_bonus = action_scores[a] * 0.8
                # Call min_value function
                v = max(v, min_value(alpha, beta, depth + 1, depth_counter) + action_bonus)
                #v = max(v, min_value(alpha, beta, depth + 1, depth_counter))
                # Undo action
                self._board.undo_action()
                # Check for pruning
                if v >= beta:
                    return v
                # Update alpha (best value max has seen at this point)
                alpha = max(alpha, v)
            # Best value for max at this node
            return v

        def min_value(alpha, beta, depth, depth_counter):
            if self._board.terminal_state() or cutoff_test(depth):
                depth_counter['depth'] = max(depth_counter['depth'], depth)
                return self._board.eval()

            # Best value for min at this node so far
            v = np.inf
            legal_actions = self._board.get_all_legal_actions(self._color.opponent)
            action_scores = {
                a: self._board.movement_progress_heuristic(a, self._color.opponent)
                for a in legal_actions
            }
            sorted_actions = sorted(legal_actions, key=lambda a: action_scores[a], reverse=False)

            for a in sorted_actions:
                # Apply action
                self._board.update(a)
                #print(f"{a} → {action_scores[a]}")
                action_penalty = action_scores[a] * 1
                # Call max_value function
                v = min(v, max_value(alpha, beta, depth + 1, depth_counter) + action_penalty)
                # Undo action
                self._board.undo_action()
                # Check for pruning
                if v <= alpha:
                    return v
                # Update beta (best value min has seen at this point)
                beta = min(beta, v)

            # Best value for min at this node
            return v

        def cutoff_test(depth):
            """
            Returns True if the current depth is greater
            than the cutoff depth
            """
            return depth > d

        # Body of Alpha beta pruning algorithm
        # Best score for min on the path to state
        beta = np.inf
        # Best score max can achieve
        best_score = -np.inf
        # Best action for max
        best_action = None

        # If a solution is found what depth is it at?
        best_depth = np.inf



        # Look through all possible actions
        for action in self._board.get_all_legal_actions(self._color):
            # Apply action
            self._board.update(action)
            # Initialise depth counter for terminal state situation
            depth_counter = {'depth': 0}
            # Find V (resulting state's min_value)
            v = min_value(best_score, beta, 1, depth_counter)

            # Check if the action is a terminal state
            if self._board.terminal_state():
                # Check depth counter depth against best depth
                if depth_counter['depth'] < best_depth:
                    best_depth = depth_counter['depth']
                    best_score = v
                    best_action = action
                    self._board.undo_action()
                    continue

            # Undo action
            self._board.undo_action()

            # If this action is better than the best action so far
            if v > best_score:
                best_score = v
                best_action = action
            if best_action is None:
                print("[ERROR] No valid action found, defaulting to GROW")
                return GrowAction()
        # Return action with highest eval
        return best_action