from typing import Any

from referee.game import PlayerColor, Coord, Direction, \
    Action, MoveAction, GrowAction, GameBegin, Board, IllegalActionException, constants



class InternalBoard:
    def __init__(self, player_color: PlayerColor):
        self.board = Board()
        self.player_coords, self.enemy_coords = self.find_frog_coordinates(player_color)
        # Which player are we playing as
        self.player_color = player_color


    def find_frog_coordinates(self, player_color: PlayerColor):
        """
        Finds and returns the coordinates of the frogs for both players as two separate lists.
        With the player's frogs being first
        """
        red_frog_coords = []
        blue_frog_coords = []
        # Stores all player frog coordinates
        for coord, cell_state in self.board._state.items():
            if cell_state == PlayerColor.RED:
                red_frog_coords.append(coord)
            elif cell_state == PlayerColor.BLUE:
                    blue_frog_coords.append(coord)

        if player_color == PlayerColor.RED:
            return red_frog_coords, blue_frog_coords

        else:
            # If the player is blue, return the coordinates in reverse order
            return blue_frog_coords, red_frog_coords




    def get_all_legal_actions(self) -> list[Action]:
        """
        Returns all legal actions for the player whose turn it is.
        """

        # List to store all legal actions
        all_actions = [GrowAction()]

        # Add grow action as it is always available

        # Get all possible moves for each player frog
        for coord in self.player_coords:
            # Get all possible directions for the current frog
            possible_directions = self.get_possible_directions(self.board.current_player_color)
            # Create a move action for each possible direction if valid
            for direction in possible_directions:
                try:
                    # Find new position for single step move
                    move_action = MoveAction(coord, (direction,))
                    self.board._validate_move_action(move_action)
                    all_actions.append(move_action)

                    # If the move was a jump check for jump chains
                    new_position = coord + direction
                    # If the move was a jump, check for jump chains
                    if abs(new_position.r - coord.r) > 1 or abs(new_position.c - coord.c) > 1:
                        # Returns all possible jump sequences if available
                        jump_sequences = self.get_jumps(new_position, move_action, possible_directions)
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



    def get_jumps(self, new_position: Coord, original_action: MoveAction,
                  possible_directions) -> list[tuple[Direction]]:
        """
        Returns a list of all possible jump sequences for the current player if a jump chain is possible
        """
        jumps = []

        visited = set()

        self.explore_jumps(new_position, [], original_action, visited, jumps, possible_directions)

        return jumps


    # Recursively explores all possible jump sequences for the current player
    def explore_jumps(self, coord: Coord, current_chain: list[Direction], original_action: MoveAction,
        visited: set[Coord], jumps: list[tuple[Direction, ...]], possible_directions: list[Direction] = None,
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
                if self.board._cell_occupied_by_player(over) and self.board._cell_empty(landing):
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
                    self.explore_jumps(
                        landing, new_chain, original_action, visited.copy(), jumps, possible_directions
                    )

            except IllegalActionException:
                continue



    def get_possible_directions(self, player_color: PlayerColor) -> list[Direction]:
        """
        Returns a list of all legal directions for the player who's turn it is.
        Does not validate the action.
        """
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


    def update(self, action: Action) -> None:
        """
        Updates the internal board with the action played by the player.
        """
        match action:
            case MoveAction():
                # Update the board with the move
                try:
                    self.board.apply_action(action)
                except IllegalActionException:
                    raise ValueError("Illegal action encountered during apply_action")
            # Update the board with the Grow action
            case GrowAction():
                try:
                    self.board.apply_action(action)
                except IllegalActionException:
                    raise ValueError("Illegal action encountered during apply_action")


    def undo_action(self):
        """ Undoes the previous action to the board """
        try:
            # Undo the last action applied to the board
            self.board.undo_action()
        except IndexError:
            raise ValueError("No actions to undo")



    def terminal_state(self) -> bool:
        """
        Returns true if the game is over, false if the game is not over at the board's state.
        """
        if self.board.game_over:
            return True
        else:
            return False


    def eval(self) -> float:
        """
        Returns the evaluation of the board state, positive if the player is winning,
        negative if the player is losing.

        Components:
        1. Sum of vertical distance to end of board for each player frog - that of the enemies
        """

        return self.vertical_distances()


    def vertical_distances(self):
        """
        Returns the first evaluation component:
        The sum of the distances to the end of the board for each player frog
        - that of the enemies.
        """
        player_sum = 0
        enemy_sum = 0

        # Component 1
        # Calculate the distance to the end of the board for each player frog
        if self.player_color == PlayerColor.RED:
            for p_coord in self.player_coords:
                # Distance to end of board (-7)
                distance = abs(p_coord.r - (constants.BOARD_N - 1))
                player_sum += distance
            # Sum up enemy frog distances (blue)
            for e_coord in self.enemy_coords:
                # Distance to other end of board
                distance = abs(e_coord.r)
                enemy_sum += distance

        elif self.player_color == PlayerColor.BLUE:
            for p_coord in self.player_coords:
                # Distance to other end of board (-7)
                distance = abs(p_coord.r)
                player_sum += distance
            # Sum up enemy frog distances (red)
            for e_coord in self.enemy_coords:
                # Distance to end of board
                distance = abs(e_coord.r - (constants.BOARD_N - 1))
                enemy_sum += distance


        # Return the difference enemy sum and player sum
        # As higher values are best for the player
        return enemy_sum - player_sum

