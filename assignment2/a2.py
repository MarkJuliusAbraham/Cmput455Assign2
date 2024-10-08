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
        self.winning_move = None

        self.hashtable = {}
        self.current_time = 0

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
            rand_move = moves[random.randint(0, len(moves)-1)]
            self.play(rand_move)
            print(" ".join(rand_move))
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
        
        self.hashtable = {}

        depth = 0
        self.starting_player = self.player
        #Boolean Negamax algorithm
        self.time_exceeded = False
        self.start_time = time.time()

        if self.negamax(depth):
            if self.time_exceeded == True:
                return True
            print(self.starting_player," ".join(self.winning_move))
        else:
            if self.starting_player == 1:
                print("2")
            else:
                print("1")

    #===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ END OF ASSIGNMENT 2 FUNCTIONS. ɅɅɅɅɅɅɅɅɅɅ
    #===============================================================================================

    def negamax(self,depth):
        last_move = None
        current_time = time.time()
        elasped_time = current_time-self.start_time
        if elasped_time >= self.default_time:
            if not self.time_exceeded:
                print("unknown")  # Time limit reached, returning without solving
                self.time_exceeded = True
            return False
        if(len(self.get_legal_moves()) == 0 ):
            return self.statically_evaluate()
        k = self.get_legal_moves()
        for move in k:
            self.play(move)
            last_move = move
            key = "".join(map(str, self.board))


            value = self.lookup_position()
            if (value != None):
                isWin = value
            else:
                isWin = not self.negamax(depth)
                self.hashtable[key] = isWin

            # if( key in self.hashtable):
            #     isWin = self.hashtable[key]
            # else:
            #     isWin = not self.negamax(depth) 
            #     self.hashtable[key] = isWin
            
            self.undo(move)
            if isWin:
                if depth == 0:
                    self.winning_move = last_move
                return True
        if depth == 0:
            self.winning_move = last_move
        return False
    

    def statically_evaluate(self):
    
        return False

    def transpose_and_hash(self, value):
        
        for _ in range(2):
            self.horizontal_flip()
            key = "".join(map(str, self.board))
            self.hashtable[key] = value
            self.vertical_flip()
            key = "".join(map(str, self.board))
            self.hashtable[key] = value

    def lookup_position(self):
        # Try to find the position in the hash table under any symmetry
        possible_keys = []
        
        self.horizontal_flip()
        possible_keys.append("".join(map(str, self.board)))  # Horizontal
        self.vertical_flip()
        possible_keys.append("".join(map(str, self.board)))  # Both flipped
        self.horizontal_flip()
        possible_keys.append("".join(map(str, self.board)))  # Vertical
        self.vertical_flip()
        possible_keys.append("".join(map(str, self.board)))  # Original

        # Check each possible key in the hashtable
        for key in possible_keys:
            if key in self.hashtable:
                return self.hashtable[key]

        return None


    def horizontal_flip(self):
        for row in self.board:
            row.reverse()
        return

    def vertical_flip(self):
        flipped_array = self.board[::-1]
        self.board = flipped_array
        return




    def undo(self, args):
        err = ""
        if len(args) != 3:
            return Exception
        try:
            x = int(args[0])
            y = int(args[1])
        except ValueError:
            return False
        if  x < 0 or x >= len(self.board[0]) or y < 0 or y >= len(self.board):
            return False
        
        self.board[y][x] = None
        if self.player == 1:
            self.player = 2
        else:
            self.player = 1
        return True

if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()