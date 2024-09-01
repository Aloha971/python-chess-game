import main
import csv
    
f_white = open("Assets/openings.txt", mode="w")
f_black = open("Assets/defences.txt", mode="w")
def ResetBoard():
    board = [[(-1) for x in range(8)]for y in range(8)]
    for color in range(2):
        if color==0: y = 6
        else: y = 1

        board[y] = [ (color, 0, i) for i in range(8)]
        board[y-(color-1+color)] = [(color, 3, 0), (color, 2, 0), (color, 1, 0),
                                    (color, 4, 0), (color, 5, 0),
                                    (color, 1, 1), (color, 2, 1), (color, 3, 1)]
    return board

def PrintBoard(board):
    for line in board:
        for piece in line:
            if piece==-1:
                print("|   |", end="")
            else:
                print(f"|{piece[0]}-{piece[1]}|", end="")
        print()


def Main():
    with open("Assets/high_elo_opening.csv", 'r') as csvfile:
        # creating a csv reader object
        csvreader = csv.reader(csvfile)
    
        for current_row_index, row in enumerate(csvreader):
            if current_row_index == 0:
                continue
            board = ResetBoard()
            open_var = False
            all_moves = []
            curr_move_str = []

            for i in row[10]:
                if i == "'":
                    open_var = not open_var
                    if not open_var:
                        all_moves.append("".join(curr_move_str))
                        curr_move_str = []

                elif (open_var):
                    if i == '.':
                        curr_move_str = []
                    else:
                        curr_move_str.append(i)
            if all_moves.__contains__("O-O") or all_moves.__contains__("O-O-O"):
                continue
            
            black = False
            if row[1] == "white": black_side = False
            elif row[1] == "black": black_side = True
            else:
                print(row[1]) 
                raise Exception
            letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
            pieces = ["B", "N", "R", "Q", "K"]
            board_hash = board_hash = HashBoard(board)

            for move in all_moves:
                move = move.replace("+", "")
                column = -1
                row_pos = -1
                if move.__contains__('x'):
                    new_pos = (8-int(move[3]), letters.index(move[2])) #Y, X
                    if move[0].islower(): # Pawn
                        column = letters.index(move[0])
                        piece = 0
                    else:
                        piece = pieces.index(move[0]) + 1

                elif move[0].islower():
                    new_pos = (8-int(move[1]), letters.index(move[0])) #Y, X
                    piece = 0
                else:
                    if move.__len__() == 4:
                        new_pos = (8-int(move[3]), letters.index(move[2]))
                        try:
                            column = letters.index(move[1])
                        except ValueError:
                            row_pos = 8-int(move[1])
                    else:
                        new_pos = (8-int(move[2]), letters.index(move[1]))
                    piece = pieces.index(move[0]) + 1
                
                old_pos = FindPiece(new_pos, black, piece, board, column, row_pos)
                board[new_pos[0]][new_pos[1]] = board[old_pos[0]][old_pos[1]]
                board[old_pos[0]][old_pos[1]] = -1

                if black != black_side:
                    board_hash = HashBoard(board)
                else:
                    if black_side:
                        if move!=all_moves[0]:
                            f_black.write(f"{board_hash} {old_pos[0]}{old_pos[1]}{new_pos[0]}{new_pos[1]}\n")
                    else:
                        f_white.write(f"{board_hash} {7-old_pos[0]}{7-old_pos[1]}{7-new_pos[0]}{7-new_pos[1]}\n") 
                black = not black

def FindPiece(new_pos, color, piece, tmp_board, column, row_pos):
    color = int(color)
    old_pos = -1

    for y, row in enumerate(tmp_board):
        for x, field in enumerate(row):
            if field != -1 and field[0] == color and field[1] == piece and (column == -1 or column==x) and (row_pos == -1 or row_pos==y):
                moves = main.AllMoves((field, y, x), False, tmp_board)
                if moves.__contains__(new_pos):
                    old_pos = (y, x)
    return old_pos

def HashBoard(tmp_board):
    newBoard = []
    for i in tmp_board:
        newBoard.append(tuple(i))
    return str(hash((tuple(newBoard))))


if __name__ == "__main__":
    Main()

f_white.close()
f_black.close()

            
            






