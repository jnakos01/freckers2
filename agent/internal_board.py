from typing import Any
from referee.game import PlayerColor, Coord, Direction, \
    Action, MoveAction, GrowAction, GameBegin, Board, IllegalActionException, constants
import numpy as np


class InternalBoard:
    def __init__(self, player_color: PlayerColor):
        self.board = Board()
        self.player_coords, self.enemy_coords = self.find_frog_coordinates(player_color)
        self.player_color = player_color

    def find_frog_coordinates(self, player_color: PlayerColor):
        # Find all frog positions for both RED and BLUE players
        red_frog_coords = []
        blue_frog_coords = []
        for coord, cell_state in self.board._state.items():
            if cell_state.state == PlayerColor.RED:
                red_frog_coords.append(coord)
            elif cell_state.state == PlayerColor.BLUE:
                blue_frog_coords.append(coord)

        return (red_frog_coords, blue_frog_coords) if player_color == PlayerColor.RED else (blue_frog_coords, red_frog_coords)

    def get_all_legal_actions(self, color: PlayerColor) -> list[Action]:
        """
        Returns all legal actions for the player whose turn it is.
        """
        all_actions = []

        frog_coords = self.player_coords if color == self.player_color else self.enemy_coords
        possible_directions = self.get_possible_directions(self.player_color)

        for coord in frog_coords:
            # Skip if frog is already in the final row
            if (color == PlayerColor.RED and coord.r == constants.BOARD_N - 1) or \
               (color == PlayerColor.BLUE and coord.r == 0):
                continue

            for direction in possible_directions:
                try:
                    move_action = MoveAction(coord, (direction,))
                    self.board._validate_move_action(move_action)
                    all_actions.append(move_action)

                    # Check for potential jump (coord + direction + direction)
                    try:
                        over = coord + direction
                        landing = over + direction
                    except ValueError:
                        continue  # Skip if out of bounds

                    if not self._coord_within_bounds(over) or not self._coord_within_bounds(landing):
                        continue

                    # If it's a jump (distance > 1), search for jump chains
                    if abs(landing.r - coord.r) > 1 or abs(landing.c - coord.c) > 1:
                        jump_sequences = self.get_jumps(landing, move_action, possible_directions)
                        for jump_sequence in jump_sequences:
                            jump_action = MoveAction(coord, tuple(jump_sequence))
                            try:
                                self.board._validate_move_action(jump_action)
                                all_actions.append(jump_action)
                            except IllegalActionException:
                                continue

                except IllegalActionException:
                    continue

        # Add GROW action at the end
        all_actions.append(GrowAction())

        # Debug print for jump actions
        """for action in all_actions:
            if isinstance(action, MoveAction) and len(action.directions) > 1:
                print(f"[DEBUG] Legal jump actions for {color.name}:")
                print(f"  - {action}")"""

        return all_actions

    def get_jumps(self, new_position: Coord, original_action: MoveAction,
                  possible_directions) -> list[tuple[Direction]]:
        """
        Returns a list of all possible jump sequences for the current player if a jump chain is possible
        """
        jumps = []
        visited = set()
        valid_dirs = []

        for d in possible_directions:
            try:
                if not self._coord_within_bounds(new_position + d):
                    continue
                over = new_position + d

                if not self._coord_within_bounds(over + d):
                    continue
                landing = over + d

                valid_dirs.append(d)
            except Exception:
                continue

        # Start recursive jump exploration
        self.explore_jumps(new_position, [], original_action, visited, jumps, valid_dirs)
        return jumps

    def explore_jumps(self, coord: Coord, current_chain: list[Direction], original_action: MoveAction,
        visited: set[Coord], jumps: list[tuple[Direction, ...]], possible_directions: list[Direction]) -> None:
        for direction in possible_directions:
            try:
                over = coord + direction
                landing = over + direction
            except ValueError:
                continue

            if not self._coord_within_bounds(over) or not self._coord_within_bounds(landing):
                continue

            # Valid jump: over has a frog (either color), landing has lily pad
            if self.board[over].state not in [PlayerColor.RED, PlayerColor.BLUE]:
                continue

            if self.board[landing].state != "LilyPad":
                continue

            # Avoid cycles
            if landing in visited:
                continue

            visited.add(landing)

            new_chain = (
                list(original_action.directions) + [direction]
                if not current_chain
                else current_chain + [direction]
            )

            jumps.append(tuple(new_chain))

            # Recursively search for more jumps
            self.explore_jumps(
                landing, new_chain, original_action, visited.copy(), jumps, possible_directions
            )

    def get_possible_directions(self, player_color: PlayerColor) -> list[Direction]:
        """
        Returns a list of all legal directions for the player whose turn it is.
        Does not validate the action.
        """
        possible_directions = []
        for direction in Direction:
            try:
                self.board._assert_direction_legal(direction, player_color)
                possible_directions.append(direction)
            except IllegalActionException:
                continue
        return possible_directions

    def update(self, action: Action) -> None:
        """
        Updates the internal board with the action played by the player.
        """
        try:
            self.board.apply_action(action)
        except IllegalActionException:
            raise ValueError("Illegal action encountered during apply_action")

        self.player_coords, self.enemy_coords = self.find_frog_coordinates(self.player_color)

    def undo_action(self):
        """ Undoes the previous action to the board """
        try:
            self.board.undo_action()
            self.player_coords, self.enemy_coords = self.find_frog_coordinates(self.player_color)
        except IndexError:
            raise ValueError("No actions to undo")

    def _coord_within_bounds(self, coord: Coord) -> bool:
        return 0 <= coord.r < constants.BOARD_N and 0 <= coord.c < constants.BOARD_N

    def terminal_state(self) -> bool:
        """
        Returns true if the game is over, false if the game is not over at the board's state.
        """
        return self.board.game_over

    def eval(self) -> float:
        """
        Returns the evaluation of the board state, positive if the player is winning,
        negative if the player is losing.

        Components:
        1. Sum of vertical distance to end of board for each player frog - that of the enemies
        """
        if self.terminal_state():
            if self.board.winner_color == self.player_color:
                return np.inf
            elif self.board.winner_color == self.player_color.opponent:
                return -np.inf

        score = 0

        # Vertical distance component
        score += 1 * self.vertical_distances()

        return score

    def vertical_distances(self):
        """
        Returns the first evaluation component:
        The sum of the distances to the end of the board for each player frog
        minus that of the enemies.
        """
        player_sum = 0
        enemy_sum = 0

        if self.player_color == PlayerColor.RED:
            for p_coord in self.player_coords:
                distance = abs(p_coord.r - (constants.BOARD_N - 1))
                player_sum += distance
            for e_coord in self.enemy_coords:
                distance = abs(e_coord.r)
                enemy_sum += distance

        elif self.player_color == PlayerColor.BLUE:
            for p_coord in self.player_coords:
                distance = abs(p_coord.r)
                player_sum += distance
            for e_coord in self.enemy_coords:
                distance = abs(e_coord.r - (constants.BOARD_N - 1))
                enemy_sum += distance

        return enemy_sum - player_sum

    def count_blocked_frogs(self, coords):
        # Count how many frogs have no legal moves
        count = 0
        directions = self.get_possible_directions(self.board.turn_color)
        for coord in coords:
            blocked = True
            for d in directions:
                try:
                    move = MoveAction(coord, (d,))
                    self.board._validate_move_action(move)
                    blocked = False
                    break
                except:
                    continue
            if blocked:
                count += 1
        return count

    # Uncomment the following methods if needed later

    def count_dominant_positions(self, coords):
        # Heuristic bonus for frogs close to the goal row
        score = 0
        N = constants.BOARD_N

        for coord in coords:
            if self.player_color == PlayerColor.RED:
                if coord.r == N - 1:
                    score += 3
                elif coord.r == N - 2:
                    score += 2
                elif coord.r == N - 3:
                    score += 1
            elif self.player_color == PlayerColor.BLUE:
                if coord.r == 0:
                    score += 3
                elif coord.r == 1:
                    score += 2
                elif coord.r == 2:
                    score += 1

        return score

    def count_left_behind(self, coords):
        # Penalty for frogs that remain far from the goal row
        score = 0
        N = constants.BOARD_N

        for coord in coords:
            if self.player_color == PlayerColor.RED:
                if coord.r == 0:
                    score -= 3
                elif coord.r == 1:
                    score -= 2
                elif coord.r == 2:
                    score -= 1
            elif self.player_color == PlayerColor.BLUE:
                if coord.r == N - 1:
                    score -= 3
                elif coord.r == N - 2:
                    score -= 2
                elif coord.r == N - 3:
                    score -= 1

        return score
    
    def count_jump_opportunities(self, coords: list[Coord], color: PlayerColor) -> int:
        """
        Returns the number of positions where a frog can initiate at least one jump.
        """
        jump_count = 0
        possible_directions = self.get_possible_directions(color)

        for coord in coords:
            for direction in possible_directions:
                try:
                    over = coord + direction
                    landing = over + direction
                except ValueError:
                    continue

                if not self._coord_within_bounds(over) or not self._coord_within_bounds(landing):
                    continue

                # Can jump if 'over' has any frog and 'landing' is a lily pad
                if self.board[over].state in [PlayerColor.RED, PlayerColor.BLUE] and \
                self.board[landing].state == "LilyPad":
                    jump_count += 1
                    break  # Count only one opportunity per frog
        return jump_count

    


