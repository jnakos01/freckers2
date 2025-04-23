import copy

from referee.game import PlayerColor, Coord


class InternalBoard:
    def __init__(self, board, player_color: PlayerColor):
        self.board = copy.deepcopy(board)
        self.player_coords, self.enemy_coords = find_frog_coordinates(board, player_color)






''' Finds and returns the coordinates of the frogs for both players as two separate lists.'''
def find_frog_coordinates(board, player_color: PlayerColor):
    player_frog_coords = []
    enemy_frog_coords = []
    # Stores all player frog coordinates
    if player_color == PlayerColor.RED:
        for coord in board.items():
            if coord.color == PlayerColor.RED:
                player_frog_coords.append(coord)

            elif coord.color == PlayerColor.BLUE:
                enemy_frog_coords.append(coord)

    # Stores all enemy frog coordinates
    elif player_color == PlayerColor.BLUE:
        for coord in board.items():
            if coord.color == PlayerColor.BLUE:
                player_frog_coords.append(coord)

            elif coord.color == PlayerColor.RED:
                enemy_frog_coords.append(coord)

    return player_frog_coords, enemy_frog_coords