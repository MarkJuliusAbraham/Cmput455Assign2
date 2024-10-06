# CMPUT 455 Assignment 1 starter code
# Implement the specified commands to complete the assignment
# Full assignment specification here: https://webdocs.cs.ualberta.ca/~mmueller/courses/cmput455/assignments/a1.html

import sys
import random
class CommandInterface:
    # The following is already defined and does not need modification
    # However, you may change or add to this code as you see fit, e.g. adding class variables to init

    

    def __init__(self):
        # Define the string to function command mapping
        self.command_dict = {
            "help" : self.help,
            "game" : self.game,
            "show" : self.show,
            "play" : self.play,
            "legal" : self.legal,
            "genmove" : self.genmove,
            "winner" : self.winner
        }
        self.board = None
        self.max_x = None
        self.max_y = None
        self.current_player = 0
        self.status = None

    

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
    # Commands will automatically print '= 1' at the end of execution on success
    def main_loop(self):
        while True:
            str = input()
            if str.split(" ")[0] == "exit":
                print("= 1\n")
                return True
            if self.process_command(str):
                print("= 1\n")

    # List available commands
    def help(self, args):
        for command in self.command_dict:
            if command != "help":
                print(command)
        print("exit")
        return True

    #======================================================================================
    # End of predefined functionality. You will need to implement the following functions.
    # Arguments are given as a list of strings
    # We will only test error handling of the play command
    #======================================================================================

    def game(self, args):

        if len(args) != 2 or not args[0].isdigit() or not args[1].isdigit():
            print("Invalid arguments for game")
            return False
        self.max_x = int(args[0])
        self.max_y = int(args[1])

        if not (1 <= self.max_x <= 20) or not (1 <= self.max_y <= 20):
            print("Invalid dimensions: n and m must be between 1 and 20")
            return False

        # 2d array
        # self.board = [['.' for _ in range(self.x)] for _ in range(self.y)]

        self.board = []
        for _ in range(self.max_x+1):
            self.board.append("#")

        for _ in range(self.max_y):
            self.board.append('#')
            for _ in range(self.max_x):
                self.board.append('.')

        for _ in range(self.max_x+1):
            self.board.append("#")

        self.current_player = 0
        return True
                
    def show(self, args):

        if(self.board == None):
            print("game is not initialized")
            return False
            #if necessary to create a default state for the game
            #self.game(['3','3']) 
        pos = 0
        for item in self.board:
            
            if item != "#":
                print(item,end="")
            if (pos%( self.max_x+1)) == 0:
                print("\n",end="")
            pos += 1
        
        print('\n')
        return True
    
    def play(self, args):

        if( self.legalChecks(args,shouldPrint=True) == False ):
            return False
        #math to place in a 1d array with borders

        x = int(args[0])
        y = int(args[1])
        digit = args[2]
        pos_in_1d_array = (self.max_x+1)*(y+1)+(x+1)

        self.board[pos_in_1d_array] = digit
        self.current_player += 1
        return True
    
    def legal(self, args):
        if self.legalChecks(args,shouldPrint=False)== True:
            print("Yes")
            return True
        else:
            print("No")
            return False
        
    def genmove(self, args):
        moves = self.collectLegalMoves()
        if len(moves) == 0:
            print("resign")
            return False
        else:
            random_play = random.choice(moves)
            print("@", *random_play,sep =' ')
            self.play(random_play)
            return True 

    def winner(self, args):
        moves = self.collectLegalMoves()
        if len(moves) == 0:
            print(1+((self.current_player % 2)==0))
        else:
            print("unfinished")
        return True
    
    #======================================================================================
    # End of functions requiring implementation
    #======================================================================================

    def legalChecks(self,args,shouldPrint):

        x = int(args[0])
        y = int(args[1])
        digit = args[2]

        if len(args) != 3:
            if(shouldPrint):
                print("Illegal move: " + " ".join(args) + " wrong number of arguments")
            return False
        
        if ( not args[0].isdigit() or not args[1].isdigit() or not args[2].isdigit()):
            if(shouldPrint):
                print("Illegal move: " + " ".join(args) + " wrong coordinate")
            return False
        
        if( not(0 <= x <= self.max_x-1) or not(0 <= y <= self.max_y-1)):
            if(shouldPrint):
                print("Illegal move: " + " ".join(args) + " wrong coordinate")
            return False

        if(digit != '0' and digit != '1'):
            if(shouldPrint):
                print("Illegal move: " + " ".join(args) + " wrong number")
            return False
        
        pos_in_1d_array = (self.max_x+1)*(y+1)+(x+1)

        if(self.board[pos_in_1d_array] != '.'):
            if(shouldPrint):
                print("illegal move: " + " ".join(args) + " occupied")
            return False
        
        #neighbour testing
        if not (self.neighbour_test(x,y,digit)):
            if(shouldPrint):
                print("Illegal move: " + " ".join(args) + " three in a row")
            return False

        #balancing case
        if not (self.isBalanced(x,y,digit)):
            if(shouldPrint):
                print("Illegal move: " + " ".join(args) + " too many " + str(digit))
            return False

        return True
        
    def neighbour_test(self, x, y, digit):
        """
            Args: 
                x: x position relative to the board 
                y: y position relative to the board
                digit: the digit to be placed
            Returns:
                bool: True if the digit has no similar neighbors that creates a 3-of-the-same block. False otherwise.
        """

        x_offset_var = (x+1)

        pos_in_1d_array = (self.max_x+1)*(y+1)+x_offset_var
        
        #do row check

        #check if left is the same as digit

        if(self.board[pos_in_1d_array-1] == digit):
            #check if right is also the same OR the twice-left is the same
            if(self.board[pos_in_1d_array+1]==digit or self.board[pos_in_1d_array-2]==digit):
                return False
        elif(self.board[pos_in_1d_array+1]==digit and self.board[pos_in_1d_array+2]==digit):
            return False

    
        #do column check

        clamped_value = None
        if(self.board[pos_in_1d_array+(self.max_x+1)*(-1)] == digit):
            #check if right is also the same OR the twice-left is the same
            if(self.board[pos_in_1d_array+(self.max_x+1)*(1)] == digit):
                return False

            clamped_value = pos_in_1d_array+(self.max_x+1)*(-2)
            if(clamped_value < 0):
                clamped_value = 0
            
            if(self.board[clamped_value]==digit):
                return False
        elif(self.board[pos_in_1d_array + (self.max_x+1)*(1)] == digit):
            clamped_value = pos_in_1d_array + (self.max_x+1)*(2)
            if(clamped_value > len(self.board)-1):
                clamped_value = len(self.board)-1

            if(self.board[clamped_value] == digit):
                return False
        
        return True

    def isBalanced(self, x, y, digit):

        amount_to_skip = self.max_x + 1
        
        max_entry = int(( self.max_x + self.max_x % 2 ) / 2)
        row_count = 1
        column_count = 1

        #increments the column count for any same digit found in the column
        for i in range(self.max_y):
            column_count += (digit == self.board[(amount_to_skip)*(i+1)+(x+1)])

        #increments the row count for any same digit found in the row
        for i in range(self.max_x):
            row_count += (digit == self.board[(amount_to_skip)*(y+1)+(i+1)])

        #if either row or column exceeds max entry, isBalanced returns false
        if (column_count > max_entry) or (row_count > max_entry):
            return False

        return True

    def collectLegalMoves(self):
        move = []
        xpos = 0
        ypos = 0
        max = self.max_x*self.max_y
        for pos_1darray in range(max):
            xpos = pos_1darray % self.max_x
            ypos = pos_1darray // self.max_x
            args = [str(xpos), str(ypos), str(0)]
            if self.legalChecks(args, shouldPrint=False) == True:
                move.append(args)
            args = [str(xpos), str(ypos), str(1)]
            if self.legalChecks(args, shouldPrint=False) == True:
                move.append(args)
        
        return move


if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()