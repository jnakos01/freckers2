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
        possible_directions = self.get_possible_directions(self.board._turn_color)

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

                    # Check if it was a jump or normal move
                    new_coords = self.board._resolve_move_destination(move_action)

                    # If it's a jump (distance > 1), search for jump chains
                    if abs(new_coords.r - coord.r) > 1 or abs(new_coords.c - coord.c) > 1:
                        jump_sequences = self.get_jumps(new_coords, move_action, possible_directions)
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
        1. Vertical distances to the goal.
        2. Bonus for dominant positions.
        3. Penalty for frogs left behind.
        4. Penalty for blocked frogs.
        """
        if self.terminal_state():
            if self.board.winner_color == self.player_color:
                return np.inf
            elif self.board.winner_color == self.player_color.opponent:
                return -np.inf

        score = 0

        # Vertical distance component
        score += 1.0 * self.vertical_distances()

        # Bonus for dominant positions
        score += 2.0 * self.count_dominant_positions(self.player_coords, self.enemy_coords)

        # Penalty for frogs left behind
        score += 3.0 * self.count_left_behind(self.player_coords, self.enemy_coords)


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

    def count_blocked_frogs(self, player_coords, enemy_coords):
        # Net count of how many frogs have no legal moves. (Enemy - player counts)
        score = 0
        player_directions = self.get_possible_directions(self.board.turn_color)
        enemy_directions = self.get_possible_directions(self.board.turn_color.opponent)

        def is_blocked_frog(coord, directions):
            for d in directions:
                try:
                    over = coord + d
                    landing = over + d
                    if self._coord_within_bounds(over) and self._coord_within_bounds(landing):
                        # Jump Move
                        if self.board[over].state in [PlayerColor.RED, PlayerColor.BLUE] and \
                        self.board[landing].state == "LilyPad":
                            return False

                    # Normal Move
                    if self._coord_within_bounds(over):
                        if self.board[over].state == "LilyPad":
                            return False
                except ValueError:
                    continue
            return True

        # Count blocked player frogs
        for coord in player_coords:
            blocked = is_blocked_frog(coord, player_directions)
            if blocked:
                score -= 1

        # Count blocked enemy frogs
        for coord in enemy_coords:
            blocked = is_blocked_frog(coord, enemy_directions)
            if blocked:
                score += 1

        return score

    # Uncomment the following methods if needed later

    def count_dominant_positions(self, player_coords, enemy_coords):
        # Heuristic bonus for frogs close to the goal row
        score = 0
        N = constants.BOARD_N

        for coord in player_coords:
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

        for coord in enemy_coords:
            if self.player_color == PlayerColor.BLUE:
                if coord.r == N - 1:
                    score -= 3
                elif coord.r == N - 2:
                    score -= 2
                elif coord.r == N - 3:
                    score -= 1
            elif self.player_color == PlayerColor.RED:
                if coord.r == 0:
                    score -= 3
                elif coord.r == 1:
                    score -= 2
                elif coord.r == 2:
                    score -= 1

        return score

    def count_left_behind(self, player_coords, enemy_coords):
        # Penalty for frogs that remain far from the goal row
        score = 0
        N = constants.BOARD_N

        for coord in player_coords:
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

        for coord in enemy_coords:
            if self.player_color == PlayerColor.BLUE:
                if coord.r == 0:
                    score += 3
                elif coord.r == 1:
                    score += 2
                elif coord.r == 2:
                    score += 1
            elif self.player_color == PlayerColor.RED:
                if coord.r == N - 1:
                    score += 3
                elif coord.r == N - 2:
                    score += 2
                elif coord.r == N - 3:
                    score += 1



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
    
    def movement_progress_heuristic(self, action: Action, color: PlayerColor = None) -> float:
        if not isinstance(action, MoveAction):
            return 0  # Neutral for GROW or others

        if color is None:
            color = self.player_color

        start = action.coord
        current = start

        for d in action.directions:
            if len(action.directions) == 1:
                # Movimiento simple: solo avanzar una vez
                current = current + d
            else:
                # Salto: avanzar dos veces en esa dirección
                current = current + d + d

        # Calcular avance vertical neto
        if color == PlayerColor.RED:
            delta = current.r - start.r
        else:
            delta = start.r - current.r

        return delta if delta > 2 else 0
    
    def forward_progress_heuristic(self, action: Action, color: PlayerColor = None) -> float:
        if not isinstance(action, MoveAction):
            return 0 

        if color is None:
            color = self.player_color

        start = action.coord
        current = start

        for d in action.directions:
            current = current + d if len(action.directions) == 1 else current + d + d

        delta = current.r - start.r if color == PlayerColor.RED else start.r - current.r

        if delta <= 0:
            return 0

        N = constants.BOARD_N
        if (color == PlayerColor.RED and start.r >= N - 2) or \
        (color == PlayerColor.BLUE and start.r <= 1):
            return 0

        return 1 


    # DON'T USE YET AS CAN PROHIBIT FORWARD PROGRESS
    def max_vert_distance_between_frogs(self, player_coords: list[Coord], enemy_coords: list[Coord]) -> int:
        """
        Returns the maximum vertical distance between any two enemy frogs
        - that of the maximum vertical distance between any two player frogs.
        """

        player_min = min(coord.r for coord in player_coords)
        player_max = max(coord.r for coord in player_coords)
        player_dist = abs(player_max - player_min)

        enemy_min = min(coord.r for coord in enemy_coords)
        enemy_max = max(coord.r for coord in enemy_coords)
        enemy_dist = abs(enemy_max - enemy_min)
        return enemy_dist - player_dist





