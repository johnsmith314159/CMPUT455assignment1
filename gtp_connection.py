"""
gtp_connection.py
Module for playing games of Go using GoTextProtocol

Parts of this code were originally based on the gtp module 
in the Deep-Go project by Isaac Henrion and Amos Storkey 
at the University of Edinburgh.
"""
import traceback
from sys import stdin, stdout, stderr
from board_util import (
    GoBoardUtil,
    BLACK,
    WHITE,
    EMPTY,
    BORDER,
    PASS,
    MAXSIZE,
    coord_to_point,
)
import numpy as np
import re


class GtpConnection:
    def __init__(self, go_engine, board, debug_mode=False):
        """
        Manage a GTP connection for a Go-playing engine

        Parameters
        ----------
        go_engine:
            a program that can reply to a set of GTP commandsbelow
        board: 
            Represents the current board state.
        """
        self._debug_mode = debug_mode
        self.go_engine = go_engine
        self.board = board
        self.commands = {
            "protocol_version": self.protocol_version_cmd,
            "quit": self.quit_cmd,
            "name": self.name_cmd,
            "boardsize": self.boardsize_cmd,
            "showboard": self.showboard_cmd,
            "clear_board": self.clear_board_cmd,
            "komi": self.komi_cmd,
            "version": self.version_cmd,
            "known_command": self.known_command_cmd,
            "genmove": self.genmove_cmd,
            "list_commands": self.list_commands_cmd,
            "play": self.play_cmd,
            "legal_moves": self.legal_moves_cmd,
            "gogui-rules_game_id": self.gogui_rules_game_id_cmd,
            "gogui-rules_board_size": self.gogui_rules_board_size_cmd,
            "gogui-rules_legal_moves": self.gogui_rules_legal_moves_cmd,
            "gogui-rules_side_to_move": self.gogui_rules_side_to_move_cmd,
            "gogui-rules_board": self.gogui_rules_board_cmd,
            "gogui-rules_final_result": self.gogui_rules_final_result_cmd,
            "gogui-analyze_commands": self.gogui_analyze_cmd
        }

        # used for argument checking
        # values: (required number of arguments,
        #          error message on argnum failure)
        self.argmap = {
            "boardsize": (1, "Usage: boardsize INT"),
            "komi": (1, "Usage: komi FLOAT"),
            "known_command": (1, "Usage: known_command CMD_NAME"),
            "genmove": (1, "Usage: genmove {w,b}"),
            "play": (2, "Usage: play {b,w} MOVE"),
            "legal_moves": (1, "Usage: legal_moves {w,b}"),
        }

        self.gameOver = False
        self.win_color = -1

    def write(self, data):
        stdout.write(data)

    def flush(self):
        stdout.flush()

    def start_connection(self):
        """
        Start a GTP connection. 
        This function continuously monitors standard input for commands.
        """
        line = stdin.readline()
        while line:
            self.get_cmd(line)
            line = stdin.readline()

    def get_cmd(self, command):
        """
        Parse command string and execute it
        """
        if len(command.strip(" \r\t")) == 0:
            return
        if command[0] == "#":
            return
        # Strip leading numbers from regression tests
        if command[0].isdigit():
            command = re.sub("^\d+", "", command).lstrip()

        elements = command.split()
        if not elements:
            return
        command_name = elements[0]
        args = elements[1:]
        if self.has_arg_error(command_name, len(args)):
            return
        if command_name in self.commands:
            try:
                self.commands[command_name](args)
            except Exception as e:
                self.debug_msg("Error executing command {}\n".format(str(e)))
                self.debug_msg("Stack Trace:\n{}\n".format(traceback.format_exc()))
                raise e
        else:
            self.debug_msg("Unknown command: {}\n".format(command_name))
            self.error("Unknown command")
            stdout.flush()

    def has_arg_error(self, cmd, argnum):
        """
        Verify the number of arguments of cmd.
        argnum is the number of parsed arguments
        """
        if cmd in self.argmap and self.argmap[cmd][0] != argnum:
            self.error(self.argmap[cmd][1])
            return True
        return False

    def debug_msg(self, msg):
        """ Write msg to the debug stream """
        if self._debug_mode:
            stderr.write(msg)
            stderr.flush()

    def error(self, error_msg):
        """ Send error msg to stdout """
        stdout.write("? {}\n\n".format(error_msg))
        stdout.flush()

    def respond(self, response=""):
        """ Send response to stdout """
        stdout.write("= {}\n\n".format(response))
        stdout.flush()

    def reset(self, size):
        """
        Reset the board to empty board of given size
        """
        self.board.reset(size)
        self.gameOver = False
        self.win_color = -1

    def board2d(self):
        return str(GoBoardUtil.get_twoD_board(self.board))

    def protocol_version_cmd(self, args):
        """ Return the GTP protocol version being used (always 2) """
        self.respond("2")

    def quit_cmd(self, args):
        """ Quit game and exit the GTP interface """
        self.respond()
        exit()

    def name_cmd(self, args):
        """ Return the name of the Go engine """
        self.respond(self.go_engine.name)

    def version_cmd(self, args):
        """ Return the version of the  Go engine """
        self.respond(self.go_engine.version)

    def clear_board_cmd(self, args):
        """ clear the board """
        self.reset(self.board.size)
        self.respond()

    def boardsize_cmd(self, args):
        """
        Reset the game with new boardsize args[0]
        """
        self.reset(int(args[0]))
        self.respond()

        """
    ==========================================================================
    Assignment 1 - game-specific commands start here
    ==========================================================================
    """

    def gogui_analyze_cmd(self, args):
        """ We already implemented this function for Assignment 1 """
        self.respond("pstring/Legal Moves For ToPlay/gogui-rules_legal_moves\n"
                     "pstring/Side to Play/gogui-rules_side_to_move\n"
                     "pstring/Final Result/gogui-rules_final_result\n"
                     "pstring/Board Size/gogui-rules_board_size\n"
                     "pstring/Rules GameID/gogui-rules_game_id\n"
                     "pstring/Show Board/gogui-rules_board\n"
                     )

    def gogui_rules_game_id_cmd(self, args):
        """ We already implemented this function for Assignment 1 """
        self.respond("Gomoku")

    def gogui_rules_board_size_cmd(self, args):
        """ We already implemented this function for Assignment 1 """
        self.respond(str(self.board.size))

    def gogui_rules_legal_moves_cmd(self, args):
        """ Implement this function for Assignment 1 """

        # board_color = args[0].lower()
        # color = color_to_int(board_color)

        self.check_result([])
        
        if self.gameOver:
            self.respond()
        else:

            moves = self.board.get_empty_points()

            gtp_moves = []
            for move in moves:
                coords = point_to_coord(move, self.board.size)
                gtp_moves.append(format_point(coords).lower())
            sorted_moves = " ".join(sorted(gtp_moves))
            self.respond(sorted_moves)

        return

    def gogui_rules_side_to_move_cmd(self, args):
        """ We already implemented this function for Assignment 1 """
        color = "black" if self.board.current_player == BLACK else "white"
        self.respond(color)

    def gogui_rules_board_cmd(self, args):
        """ We already implemented this function for Assignment 1 """
        size = self.board.size
        str = ''
        for row in range(size-1, -1, -1):
            start = self.board.row_start(row + 1)
            for i in range(size):
                #str += '.'
                point = self.board.board[start + i]
                if point == BLACK:
                    str += 'X'
                elif point == WHITE:
                    str += 'O'
                elif point == EMPTY:
                    str += '.'
                else:
                    assert False
            str += '\n'
        self.respond(str)
            
    def gogui_rules_final_result_cmd(self, args):
        """ Implement this function for Assignment 1 """
        #unknow=0
        #final_check=False
        #test_list=[]
        #while final_check == False:
        #find first stone color on the board
        wincheck=0


        first_stone_point=0
        color_list=[]
        for i in range((self.board.size+1)*(self.board.size+1)-1):
            color_list.append(self.board.get_color(i))#return [3,3,3,3,0,0,0,0....]

        ##################################CHECK BLACK##############################
        #print(color_list)
        for i in color_list:
            #first_stone_point+=1
                #if i==1 or i==2:
            if i == 1:
                color_check=i
                break
            first_stone_point+=1
        
        final_list = self.board.connected_component(first_stone_point)
        #print(first_stone_point)
        #print(final_list)
        #print(final_list[1])

        #check row 5
        #print(final_list)
        row_check=0
        match_row_black=0
        for i in final_list:
            if i == True:
                match_row_black+=1
            elif i == False:
                if match_row_black>=5:
                    #self.respond('black wins')
                    row_check=1
                    #print('rowb')
                    break
                else:
                    match_row_black=0

            #check col 5
        match_col_black=0
        col_check=0
        #print(self.board.size)
        #print(self.board.size+1)
        #while True:
        for i in range(len(final_list)):
            if final_list[i]==True and col_check != 1:
                checkpoint=i

                for j in range(checkpoint,len(final_list),+(self.board.size+1)):
                    if final_list[j]==True:
                        match_col_black+=1
                        #print('THIS IS MATCH FOUND')
                        #print(j)

            elif final_list[i] == False:
                if match_col_black >= 5:
                            #self.respond('black wins')
                    col_check=1
                    #print('colb')
                    break
                else:
                    match_col_black=0
            #else:
                #break


        final_list_dia=self.board.connected_component_dia(first_stone_point)

        #print(final_list_dia)
        #dia forward +2, backward+0
        dia_f_check=0
        match_dia_black_forward=0
        for i in range(len(final_list_dia)):
            if final_list_dia[i]==True and dia_f_check!=1:
                checkpoint=i
                for j in range(checkpoint,len(final_list_dia),+(self.board.size+2)):
                    if final_list_dia[j] == True:
                        match_dia_black_forward+=1
                #print(i)
                #print('THIS IS TRUE')
            elif final_list_dia[i]==False:
                #print(i)
                #print('THIS IS FALSE')
                if match_dia_black_forward>=5:
                    #self.respond('black wins')
                    dia_f_check=1
                    #print('diaFb')
                    break
                else:
                    match_dia_black_forward=0

        dia_b_check=0
        match_dia_black_backward=0
        for i in range(len(final_list_dia)):
            if final_list_dia[i]==True and dia_b_check!=1:
                checkpoint=i
                for j in range(checkpoint,len(final_list),+(self.board.size)):
                    if final_list_dia[j]==True:
                        match_dia_black_backward+=1
            elif final_list_dia[i]==False:
                if match_dia_black_backward>=5:
                        #self.respond('black wins')
                    dia_b_check=1
                    #print('diaBb')
                    break
                else:
                    match_dia_black_backward=0


        #if match_col_black<5 and match_row_black<5 and match_dia_black_forward<5 and match_dia_black_backward<5:
            #self.respond('unknown')
        if dia_b_check==1 or dia_f_check==1 or row_check==1 or col_check==1:
            wincheck=1
            self.respond('black')
            self.gameOver=True
            self.win_color=1
            return



        ###########################CHECK WHITE###################################
        first_stone_point=0

        for i in color_list:
            if i == 2:
                color_check=i
                break
            first_stone_point+=1
        #print(first_stone_point)
        
        final_list = self.board.connected_component(first_stone_point)
        #print(final_list)

        #check row 5
        row_check=0
        match_row_white=0
        for i in final_list:
            if i == True:
                match_row_white+=1
            elif i == False:
                if match_row_white>=5:
                    row_check=1
                    #print('row')
                    break
                else:
                    match_row_white=0


        match_col_white=0
        col_check=0
        for i in range(len(final_list)):
            if final_list[i]==True and col_check != 1:
                checkpoint=i
                for j in range(checkpoint,len(final_list),+(self.board.size+1)):
                    if final_list[j]==True:
                        match_col_white+=1

            elif final_list[i] == False:
                if match_col_white >= 5:
                    col_check=1
                    #print('col')
                    break
                else:
                    match_col_white=0
            #else:
                #break


        final_list_dia=self.board.connected_component_dia(first_stone_point)


        dia_f_check=0
        match_dia_white_forward=0
        for i in range(len(final_list_dia)):
            if final_list_dia[i]==True and dia_f_check!=1:
                checkpoint=i
                for j in range(checkpoint,len(final_list_dia),+(self.board.size+2)):
                    if final_list_dia[j] == True:
                        match_dia_white_forward+=1
            elif final_list_dia[i]==False:
                if match_dia_white_forward>=5:
                    dia_f_check=1
                    #print('diaF')
                    break
                else:
                    match_dia_white_forward=0


        dia_b_check=0
        match_dia_white_backward=0
        for i in range(len(final_list_dia)):
            if final_list_dia[i]==True and dia_b_check!=1:
                checkpoint=i
                for j in range(checkpoint,len(final_list),+(self.board.size)):
                    if final_list_dia[j]==True:
                        match_dia_white_backward+=1
            elif final_list_dia[i]==False:
                if match_dia_white_backward>=5:
                    dia_b_check=1
                    #print('diaB')
                    break
                else:
                    match_dia_white_backward=0

        if dia_b_check==1 or dia_f_check==1 or row_check==1 or col_check==1:
            wincheck=1
            self.respond('white')
            self.gameOver=True
            self.win_color=2
            return

        check_empty=self.board.get_empty_points()

        if len(check_empty)==0:
            self.respond('draw')
            self.win_color=3
            self.gameOver=True
        elif wincheck!=1:
            self.respond('unknown')

    def play_cmd(self, args):
        """ Modify this function for Assignment 1 """
        """
        play a move args[1] for given color args[0] in {'b','w'}
        """
        try:
            board_color = args[0].lower()
            board_move = args[1]
            color = color_to_int(board_color)

            #Test if b or w was entered.
            if board_color != 'b' and board_color!= 'w':
                self.respond("illegal move: \"{}\" wrong color".format(board_color))
                return
            

            #Test if the color entered is the color to play.
            # if color != self.board.current_player:
            #     self.respond(
            #         "illegal move. \"{}\" wrong color".format(board_color)
            #     )
            #     return

            #Test if move is on board.
            if (ord(board_move.lower()[0]) - ord('a')) > self.board.size or int(board_move[1:]) > self.board.size:
                self.respond("illegal move: \"{}\" wrong coordinate".format(board_move).lower())
                return
            if color == 3:
                self.respond("illegal move: \"{}\" wrong coordinate".format(args[1].lower()))
                return

            coord = move_to_coord(args[1], self.board.size)
            move = coord_to_point(coord[0], coord[1], self.board.size)

            #Code for passing
            # if args[1].lower() == "pass":
            #     self.board.play_move(PASS, color)
            #     self.board.current_player = GoBoardUtil.opponent(color)
            #     self.respond()
            #     return

            #Test if coordinate is occupied.
            if self.board.board[move] != EMPTY:
                self.respond("illegal move: \"{}\" occupied".format(board_move.lower()))
                return
            else:
                self.board.board[move] = color
                self.board.current_player = GoBoardUtil.opponent(color)
                self.respond()
                return

        except Exception as e:
            self.respond("Error: {}".format(str(e)))

    def genmove_cmd(self, args):
        """ Modify this function for Assignment 1 """
        """ generate a move for color args[0] in {'b','w'} """

        # should have winner color as int

        board_color = args[0].lower()
        color = color_to_int(board_color)

        self.check_result([])

        moves = self.board.get_empty_points()
        np.random.shuffle(moves)

        # move = self.go_engine.get_move(self.board, color)

        if not self.gameOver:
            move_coord = point_to_coord(moves[0], self.board.size)
            move_as_string = format_point(move_coord)
            # self.play_cmd([board_color, move_as_string])
            # self.board.board[moves[0]] = color
            # self.board.current_player = GoBoardUtil.opponent(color)
            self.respond(move_as_string.lower())
        elif self.win_color != -1 and self.win_color != color and self.win_color != 3:
            self.respond("resign")
        elif self.win_color == 3:
           self.respond("pass")
        else:
            self.respond()

    """
    ==========================================================================
    Assignment 1 - game-specific commands end here
    ==========================================================================
    """

    def showboard_cmd(self, args):
        self.respond("\n" + self.board2d())

    def komi_cmd(self, args):
        """
        Set the engine's komi to args[0]
        """
        self.go_engine.komi = float(args[0])
        self.respond()

    def known_command_cmd(self, args):
        """
        Check if command args[0] is known to the GTP interface
        """
        if args[0] in self.commands:
            self.respond("true")
        else:
            self.respond("false")

    def list_commands_cmd(self, args):
        """ list all supported GTP commands """
        self.respond(" ".join(list(self.commands.keys())))

    """ Assignment 1: ignore this command, implement 
        gogui_rules_legal_moves_cmd  above instead """
    def legal_moves_cmd(self, args):
        """
        List legal moves for color args[0] in {'b','w'}
        """
        board_color = args[0].lower()
        color = color_to_int(board_color)
        moves = GoBoardUtil.generate_legal_moves(self.board, color)
        gtp_moves = []
        for move in moves:
            coords = point_to_coord(move, self.board.size)
            gtp_moves.append(format_point(coords))
        sorted_moves = " ".join(sorted(gtp_moves))
        self.respond(sorted_moves)


    def check_result(self, args):
        """ Implement this function for Assignment 1 """
        #unknow=0
        #final_check=False
        #test_list=[]
        #while final_check == False:
        #find first stone color on the board
        wincheck=0


        first_stone_point=0
        color_list=[]
        for i in range((self.board.size+1)*(self.board.size+1)-1):
            color_list.append(self.board.get_color(i))#return [3,3,3,3,0,0,0,0....]

        ##################################CHECK BLACK##############################
        #print(color_list)
        for i in color_list:
            #first_stone_point+=1
                #if i==1 or i==2:
            if i == 1:
                color_check=i
                break
            first_stone_point+=1
        
        final_list = self.board.connected_component(first_stone_point)
        #print(first_stone_point)
        #print(final_list)
        #print(final_list[1])

        #check row 5
        #print(final_list)
        row_check=0
        match_row_black=0
        for i in final_list:
            if i == True:
                match_row_black+=1
            elif i == False:
                if match_row_black>=5:
                    #self.respond('black wins')
                    row_check=1
                    #print('rowb')
                    break
                else:
                    match_row_black=0

            #check col 5
        match_col_black=0
        col_check=0
        #print(self.board.size)
        #print(self.board.size+1)
        #while True:
        for i in range(len(final_list)):
            if final_list[i]==True and col_check != 1:
                checkpoint=i

                for j in range(checkpoint,len(final_list),+(self.board.size+1)):
                    if final_list[j]==True:
                        match_col_black+=1
                        #print('THIS IS MATCH FOUND')
                        #print(j)

            elif final_list[i] == False:
                if match_col_black >= 5:
                            #self.respond('black wins')
                    col_check=1
                    #print('colb')
                    break
                else:
                    match_col_black=0
            #else:
                #break


        final_list_dia=self.board.connected_component_dia(first_stone_point)

        #print(final_list_dia)
        #dia forward +2, backward+0
        dia_f_check=0
        match_dia_black_forward=0
        for i in range(len(final_list_dia)):
            if final_list_dia[i]==True and dia_f_check!=1:
                checkpoint=i
                for j in range(checkpoint,len(final_list_dia),+(self.board.size+2)):
                    if final_list_dia[j] == True:
                        match_dia_black_forward+=1
                #print(i)
                #print('THIS IS TRUE')
            elif final_list_dia[i]==False:
                #print(i)
                #print('THIS IS FALSE')
                if match_dia_black_forward>=5:
                    #self.respond('black wins')
                    dia_f_check=1
                    #print('diaFb')
                    break
                else:
                    match_dia_black_forward=0

        dia_b_check=0
        match_dia_black_backward=0
        for i in range(len(final_list_dia)):
            if final_list_dia[i]==True and dia_b_check!=1:
                checkpoint=i
                for j in range(checkpoint,len(final_list),+(self.board.size)):
                    if final_list_dia[j]==True:
                        match_dia_black_backward+=1
            elif final_list_dia[i]==False:
                if match_dia_black_backward>=5:
                        #self.respond('black wins')
                    dia_b_check=1
                    #print('diaBb')
                    break
                else:
                    match_dia_black_backward=0


        #if match_col_black<5 and match_row_black<5 and match_dia_black_forward<5 and match_dia_black_backward<5:
            #self.respond('unknown')
        if dia_b_check==1 or dia_f_check==1 or row_check==1 or col_check==1:
            wincheck=1
            self.gameOver=True
            self.win_color=1
            return



        ###########################CHECK WHITE###################################
        first_stone_point=0

        for i in color_list:
            if i == 2:
                color_check=i
                break
            first_stone_point+=1
        #print(first_stone_point)
        
        final_list = self.board.connected_component(first_stone_point)
        #print(final_list)

        #check row 5
        row_check=0
        match_row_white=0
        for i in final_list:
            if i == True:
                match_row_white+=1
            elif i == False:
                if match_row_white>=5:
                    row_check=1
                    #print('row')
                    break
                else:
                    match_row_white=0


        match_col_white=0
        col_check=0
        for i in range(len(final_list)):
            if final_list[i]==True and col_check != 1:
                checkpoint=i
                for j in range(checkpoint,len(final_list),+(self.board.size+1)):
                    if final_list[j]==True:
                        match_col_white+=1

            elif final_list[i] == False:
                if match_col_white >= 5:
                    col_check=1
                    #print('col')
                    break
                else:
                    match_col_white=0
            #else:
                #break


        final_list_dia=self.board.connected_component_dia(first_stone_point)


        dia_f_check=0
        match_dia_white_forward=0
        for i in range(len(final_list_dia)):
            if final_list_dia[i]==True and dia_f_check!=1:
                checkpoint=i
                for j in range(checkpoint,len(final_list_dia),+(self.board.size+2)):
                    if final_list_dia[j] == True:
                        match_dia_white_forward+=1
            elif final_list_dia[i]==False:
                if match_dia_white_forward>=5:
                    dia_f_check=1
                    #print('diaF')
                    break
                else:
                    match_dia_white_forward=0


        dia_b_check=0
        match_dia_white_backward=0
        for i in range(len(final_list_dia)):
            if final_list_dia[i]==True and dia_b_check!=1:
                checkpoint=i
                for j in range(checkpoint,len(final_list),+(self.board.size)):
                    if final_list_dia[j]==True:
                        match_dia_white_backward+=1
            elif final_list_dia[i]==False:
                if match_dia_white_backward>=5:
                    dia_b_check=1
                    #print('diaB')
                    break
                else:
                    match_dia_white_backward=0

        if dia_b_check==1 or dia_f_check==1 or row_check==1 or col_check==1:
            wincheck=1
            self.gameOver=True
            self.win_color=2
            return

        check_empty=self.board.get_empty_points()

        if len(check_empty)==0:
            self.win_color=3
            self.gameOver=True


def point_to_coord(point, boardsize):
    """
    Transform point given as board array index 
    to (row, col) coordinate representation.
    Special case: PASS is not transformed
    """
    if point == PASS:
        return PASS
    else:
        NS = boardsize + 1
        return divmod(point, NS)


def format_point(move):
    """
    Return move coordinates as a string such as 'A1', or 'PASS'.
    """
    assert MAXSIZE <= 25
    column_letters = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
    if move == PASS:
        return "PASS"
    row, col = move
    if not 0 <= row < MAXSIZE or not 0 <= col < MAXSIZE:
        raise ValueError
    return column_letters[col - 1] + str(row)


def move_to_coord(point_str, board_size):
    """
    Convert a string point_str representing a point, as specified by GTP,
    to a pair of coordinates (row, col) in range 1 .. board_size.
    Raises ValueError if point_str is invalid
    """
    if not 2 <= board_size <= MAXSIZE:
        raise ValueError("board_size out of range")
    s = point_str.lower()
    if s == "pass":
        return PASS
    try:
        col_c = s[0]
        if (not "a" <= col_c <= "z") or col_c == "i":
            raise ValueError
        col = ord(col_c) - ord("a")
        if col_c < "i":
            col += 1
        row = int(s[1:])
        if row < 1:
            raise ValueError
    except (IndexError, ValueError):
        raise ValueError("invalid point: '{}'".format(s))
    if not (col <= board_size and row <= board_size):
        raise ValueError("point off board: '{}'".format(s))
    return row, col


def color_to_int(c):
    """convert character to the appropriate integer code"""
    color_to_int = {"b": BLACK, "w": WHITE, "e": EMPTY, "BORDER": BORDER}
    return color_to_int[c]
