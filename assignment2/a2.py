# CMPUT 455 Assignment 2 starter code
# Implement the specified commands to complete the assignment
# Full assignment specification here: https://webdocs.cs.ualberta.ca/~mmueller/courses/cmput455/assignments/a2.html

import sys
import random
import time 
class CommandInterface:

    def __init__(self):
        # Define the string to function command mapping
        self.command_dict = {
            "help" : self.help,
            "game" : self.game,
            "show" : self.show,
            "play" : self.play,
            "legal" : self.legal,
            "genmove" : self.genmove,
            "winner" : self.winner,
            "timelimit" : self.timelimit,
            "solve" : self.solve
        }
        self.board = [[None]]
        self.player = 1
        self.starting_player = None
        self.default_time = 1
        self.timelimit_set = False
        self.current_time = 0
        self.transposition_table = {}  # Transposition table to store board states and results
    #===============================================================================================
    # VVVVVVVVVV START of PREDEFINED FUNCTIONS. DO NOT MODIFY. VVVVVVVVVV
    #===============================================================================================

    # Convert a raw string to a command and a list of arguments
    def process_command(self, str):
        str = str.lower().strip()
        command = str.split(" ")[0]
        args = [x for x in str.split(" ")[1:] if len(x) > 0]
        if command not in self.command_dict:
            print("? Uknown command.\nType 'help' to list known commands.", file=sys.stderr)
            print("= -1\n")
            return False
        try:
            return self.command_dict[command](args)
        except Exception as e:
            print("Command '" + str + "' failed with exception:", file=sys.stderr)
            print(e, file=sys.stderr)
            print("= -1\n")
            return False
        
    # Will continuously receive and execute commands
    # Commands should return True on success, and False on failure
    # Every command will print '= 1' or '= -1' at the end of execution to indicate success or failure respectively
    def main_loop(self):
        while True:
            str = input()
            if str.split(" ")[0] == "exit":
                print("= 1\n")
                return True
            if self.process_command(str):
                print("= 1\n")

    # Will make sure there are enough arguments, and that they are valid numbers
    # Not necessary for commands without arguments
    def arg_check(self, args, template):
        converted_args = []
        if len(args) < len(template.split(" ")):
            print("Not enough arguments.\nExpected arguments:", template, file=sys.stderr)
            print("Recieved arguments: ", end="", file=sys.stderr)
            for a in args:
                print(a, end=" ", file=sys.stderr)
            print(file=sys.stderr)
            return False
        for i, arg in enumerate(args):
            try:
                converted_args.append(int(arg))
            except ValueError:
                print("Argument '" + arg + "' cannot be interpreted as a number.\nExpected arguments:", template, file=sys.stderr)
                return False
        args = converted_args
        return True

    # List available commands
    def help(self, args):
        for command in self.command_dict:
            if command != "help":
                print(command)
        print("exit")
        return True

    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ END OF PREDEFINED FUNCTIONS. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================

    #===============================================================================================
    # VVVVVVVVVV START OF ASSIGNMENT 2 FUNCTIONS. ADD/REMOVE/MODIFY AS NEEDED. VVVVVVVV
    #===============================================================================================

    def game(self, args):
        if not self.arg_check(args, "n m"):
            return False
        n, m = [int(x) for x in args]
        if n < 0 or m < 0:
            print("Invalid board size:", n, m, file=sys.stderr)
            return False
        
        self.board = []
        for i in range(m):
            self.board.append([None]*n)
        self.player = 1
        return True
    
    def show(self, args):
        for row in self.board:
            for x in row:
                if x is None:
                    print(".", end="")
                else:
                    print(x, end="")
            print()                    
        return True

    def is_legal_reason(self, x, y, num):
        if self.board[y][x] is not None:
            return False, "occupied"
        
        consecutive = 0
        count = 0
        self.board[y][x] = num
        for row in range(len(self.board)):
            if self.board[row][x] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    return False, "three in a row"
            else:
                consecutive = 0
        too_many = count > len(self.board) // 2 + len(self.board) % 2
        
        consecutive = 0
        count = 0
        for col in range(len(self.board[0])):
            if self.board[y][col] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    return False, "three in a row"
            else:
                consecutive = 0
        if too_many or count > len(self.board[0]) // 2 + len(self.board[0]) % 2:
            self.board[y][x] = None
            return False, "too many " + str(num)

        self.board[y][x] = None
        return True, ""
    
    def is_legal(self, x, y, num):
        if self.board[y][x] is not None:
            return False
        
        consecutive = 0
        count = 0
        self.board[y][x] = num
        for row in range(len(self.board)):
            if self.board[row][x] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    return False
            else:
                consecutive = 0
        if count > len(self.board) // 2 + len(self.board) % 2:
            self.board[y][x] = None
            return False
        
        consecutive = 0
        count = 0
        for col in range(len(self.board[0])):
            if self.board[y][col] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    return False
            else:
                consecutive = 0
        if count > len(self.board[0]) // 2 + len(self.board[0]) % 2:
            self.board[y][x] = None
            return False

        self.board[y][x] = None
        return True
    
    def valid_move(self, x, y, num):
        return  x >= 0 and x < len(self.board[0]) and\
                y >= 0 and y < len(self.board) and\
                (num == 0 or num == 1) and\
                self.is_legal(x, y, num)

    def play(self, args):
        err = ""
        if len(args) != 3:
            print("= illegal move: " + " ".join(args) + " wrong number of arguments\n")
            return False
        try:
            x = int(args[0])
            y = int(args[1])
        except ValueError:
            print("= illegal move: " + " ".join(args) + " wrong coordinate\n")
            return False
        if  x < 0 or x >= len(self.board[0]) or y < 0 or y >= len(self.board):
            print("= illegal move: " + " ".join(args) + " wrong coordinate\n")
            return False
        if args[2] != '0' and args[2] != '1':
            print("= illegal move: " + " ".join(args) + " wrong number\n")
            return False
        num = int(args[2])
        legal, reason = self.is_legal_reason(x, y, num)
        if not legal:
            print("= illegal move: " + " ".join(args) + " " + reason + "\n")
            return False
        self.board[y][x] = num
        if self.player == 1:
            self.player = 2
        else:
            self.player = 1

        return True
    
    def legal(self, args):
        if not self.arg_check(args, "x y number"):
            return False
        x, y, num = [int(x) for x in args]
        if self.valid_move(x, y, num):
            print("yes")
        else:
            print("no")
        return True
    
    def get_legal_moves(self):
        moves = []
        for y in range(len(self.board)):
            for x in range(len(self.board[0])):
                for num in range(2):
                    if self.is_legal(x, y, num):
                        moves.append([str(x), str(y), str(num)])
        return moves

    def genmove(self, args):
        moves = self.get_legal_moves()
        if len(moves) == 0:
            print("resign")
        else:
            rand_move = moves[random.randint(0, len(moves) - 1)]
            self.play(rand_move)
            print(" ".join(map(str, rand_move)))  # Convert each part of rand_move to string
        return True

    def winner(self, args):
        if len(self.get_legal_moves()) == 0:
            if self.player == 1:
                print(2)
            else:
                print(1)
        else:
            print("unfinished")
        return True
    
    # new function to be implemented for assignment 2
    def timelimit(self, args):
        my_var = args[0]
        if my_var.isdigit():
            my_var = int(my_var)

        if isinstance(my_var, int):
            if(1 <= int(my_var) <= 100):
                self.timelimit_set = True
                self.default_time = my_var
        return True
    
    # new function to be implemented for assignment 2
    def solve(self, args):
        self.starting_player = self.player
        self.time_exceeded = False
        self.start_time = time.time()  # Start the timer
        best_move = None

        # Call the negamax function with alpha and beta initialized to -inf and +inf
        result = self.negamax(0, float('-inf'), float('inf'))

        if not self.time_exceeded:
            # If negamax found a winning strategy for the current player
            if result == 1:
                # Iterate through legal moves to find the specific best move
                for move in self.get_legal_moves():
                    self.play(move)
                    # Check if this move leads to a win
                    if -self.negamax(0, float('-inf'), float('inf')) == 1:
                        best_move = move
                    self.undo(move)

                # Output the result with the best move if found
                if best_move:
                    print(f"{self.player} {str(best_move[0])} {str(best_move[1])} {str(best_move[2])}")
                else:
                    print(str(self.player))  # Winner, but no specific move to suggest
            else:
                # No winning strategy for current player, opponent would win
                print(str(3 - self.player))
        else:
            # If the time limit was exceeded, print "unknown"
            print("unknown")

        return True

    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ END OF ASSIGNMENT 2 FUNCTIONS. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================


    def negamax(self, depth, alpha, beta):
        # Check for time limit
        if time.time() - self.start_time >= self.default_time:
            self.time_exceeded = True
            return 0  # Return a neutral value when time exceeds

        # Check for cached result
        board_hash = self.hash_board()
        if board_hash in self.transposition_table:
            return self.transposition_table[board_hash]  # Return stored evaluation

        if not self.get_legal_moves():
            return self.statically_evaluate()

        max_eval = float('-inf')

        # Iterate over all possible moves
        for move in self.get_legal_moves():
            self.play(move)
            eval = -self.negamax(depth + 1, -beta, -alpha)  # Recursive call with negation for opponent's turn
            self.undo(move)

            # Alpha-beta pruning
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if alpha >= beta:
                break  # Cut-off

        # Store the computed evaluation for this board state in the transposition table
        self.transposition_table[board_hash] = max_eval
        return max_eval

    def statically_evaluate(self):
        # Simply return 1 if the starting player wins, -1 if the starting player loses
        if self.starting_player == self.player:
            return -1  # Losing for the starting player
        return 1  # Winning for the starting player

    def undo(self, move):
        x, y, num = map(int, move)
        self.board[y][x] = None
        self.player = 3 - self.player  # Switch back to the other player

    def hash_board(self):
        return tuple(tuple(row) for row in self.board)

    def get_symmetric_moves(self, move):
        """Generate symmetrical moves to counter opponent's moves."""
        n, m = len(self.board[0]), len(self.board)
        x, y, num = map(int, move)

        # Assuming symmetry across the center lines (vertical, horizontal)
        symmetrical_moves = []
        if n > 1:
            symmetrical_moves.append((n - 1 - x, y, num))  # Mirror across vertical center
        if m > 1:
            symmetrical_moves.append((x, m - 1 - y, num))  # Mirror across horizontal center
        if n > 1 and m > 1:
            symmetrical_moves.append((n - 1 - x, m - 1 - y, num))  # Mirror across both axes

        # Filter out any moves that are already occupied or invalid
        return [move for move in symmetrical_moves if self.is_legal(move[0], move[1], move[2])]


if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()