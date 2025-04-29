import copy
from typing import Any

from referee.game import PlayerColor, Coord, Direction, \
    Action, MoveAction, GrowAction, GameBegin, Board, IllegalActionException



class InternalBoard:
    def __init__(self, board, player_color: PlayerColor):
        self.board = copy.deepcopy(board)
        self.player_coords, self.enemy_coords = find_frog_coordinates(board, player_color)
        # Set the first player to move to be red
        self.player_turn = PlayerColor.RED


''' Finds and returns the coordinates of the frogs for both players as two separate lists.
    With the player's frogs being first'''
def find_frog_coordinates(board, player_color: PlayerColor):
    red_frog_coords = []
    blue_frog_coords = []
    # Stores all player frog coordinates
    for coord, cell_state in board._state.items():
        if cell_state == PlayerColor.RED:
            red_frog_coords.append(coord)
        elif cell_state == PlayerColor.BLUE:
                blue_frog_coords.append(coord)

    if player_color == PlayerColor.RED:
        return red_frog_coords, blue_frog_coords

    else:
        # If the player is blue, return the coordinates in reverse order
        return blue_frog_coords, red_frog_coords



"""
Returns all legal actions for the player whose turn it is.
"""
def get_all_legal_actions(self) -> list[Action]:
    all_actions = [GrowAction()]

    # Add grow action as it is always available

    # Get all possible moves for each player frog
    for coord in self.player_coords:
        # Get all possible directions for the current frog
        possible_directions = self.board.get_possible_directions(self.player_turn)
        # Create a move action for each possible direction if valid
        for direction in possible_directions:
            try:
                # Find new position for single step move
                move_action = MoveAction(coord, tuple(direction,))
                self.board._validate_move_action(move_action)
                all_actions.append(move_action)

                # If the move was a jump check for jump chains
                new_position = coord + direction
                # If the move was a jump, check for jump chains
                if abs(new_position.r - coord.r) > 1 or abs(new_position.c - coord.c) > 1:
                    # Returns all possible jump sequences if available
                    jump_sequences = self.board.get_jumps(new_position, move_action, possible_directions)
                    # If there are jump sequences, create actions and add them to the list
                    if len(jump_sequences) > 0:
                        # Add all jump sequences to the list of actions
                        for jump_sequence in jump_sequences:
                            jump_action = MoveAction(coord, tuple(jump_sequence))
                            # Validate the jump action
                            self.board._validate_move_action(jump_action)
                            all_actions.append(jump_action)

                # Skip if action is illegal
            except IllegalActionException:
                pass

    # Return all legal actions
    return all_actions


# Returns a list of all possible direction tuples for the current player if a jump chain
# is possible
def get_jumps(self, new_position: Coord, original_action: MoveAction,
              possible_directions) -> list[tuple[Direction]]:
    """
    Returns a list of all possible jump sequences for the current player.
    """
    jumps = []

    visited = set()

    self.board.explore_jumps(new_position, [], original_action, visited, jumps, possible_directions)

    return jumps


# Recursively explores all possible jump sequences for the current player
def explore_jumps(self, coord: Coord, current_chain: list[Direction], original_action: MoveAction,
    visited: set[Coord],
    jumps: list[tuple[Direction, ...]], possible_directions: list[Direction] = None,
    ) -> None:

    for direction in possible_directions:
        try:
            # Create a jump move
            over = coord + direction
            landing = over + direction

            # Avoid cycles
            if landing in visited:
                continue

            # Check if the jump is valid
            if (self.board._cell_occupied_by_player(over) and self.board._cell_empty(landing)
            ):
                # Add the landing to visited to prevent revisiting
                visited.add(landing)

                # We have a jump, if the chain is empty we had our first jump
                if not current_chain:
                    # Add the first jump to the chain
                    new_chain = list(original_action.directions) + [direction]
                else:
                    # Add the current direction to the chain
                    new_chain = current_chain + [direction]

                jumps.append(tuple(new_chain))

                # Explore further jumps from the new landing
                self.board.explore_jumps(
                    landing, new_chain, original_action, visited.copy(), jumps, possible_directions
                )

        except IllegalActionException:
            continue


"""
Returns a list of all legal directions for the player who's turn it is.
Does not validate the action.
"""
def get_possible_directions(self, player_color: PlayerColor) -> list[Direction]:
    possible_directions = []
    for direction in Direction:
        try:
            # Check if the direction is legal for the player colour
            self.board._assert_direction_legal(direction, player_color)
            possible_directions.append(direction)
        # Skip moves out of the board or illegal moves
        except IllegalActionException:
            continue
    return possible_directions

