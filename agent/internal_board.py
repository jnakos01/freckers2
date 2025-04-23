import copy

from referee.game import PlayerColor, Coord


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