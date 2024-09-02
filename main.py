import pygame
import math
import opponentController


DEBUG = False
DIFFICULTY = 10

BOARD_SIZE = 650
SELECTOR_LENGTH = 315
FPS = 60
WINDOW = pygame.display.set_mode((BOARD_SIZE,BOARD_SIZE))
PIECE_SIZE = BOARD_SIZE/8
PIECE_OFFSET = BOARD_SIZE/8.75912409
CORNER = (BOARD_SIZE/25, BOARD_SIZE/28) # X = 0 and Y = 1
CIRCLE_SIZE = PIECE_SIZE/2.15

CHESS_BOARD = pygame.transform.scale(pygame.image.load("Assets/board.jpg"), (BOARD_SIZE, BOARD_SIZE))

pygame.display.set_caption("Chess")

# indexes of pieces: pawn=0,bishop=1,horse=2,rook=3,queen=4,king=5; white has a prefix of 0, black 1
# is_ai 0 is white
# indexes for locations: [colorPrefix][pieceTypeIndex][individualPieceIndex]
pieces = [[]]
PROMOTION_SELECTOR = pygame.transform.scale(pygame.image.load("Assets/selector.jpg"), (SELECTOR_LENGTH, SELECTOR_LENGTH/3.9195))

board = [[(-1) for x in range(8)]for y in range(8)] # board indexes [y-vertical on screen][x] = (is_ai, piece_type, piece_index)
chessAI = opponentController.ChessAI(DIFFICULTY)

# Controlled cells are in the form as follows: -1 if not controlled; 
#                                               1 if controlled actively (a piece)
#                                               2 if controlled passively (a pawns diagonal)
#                                               3 if not controlled but can be moved in to (in front of a pawn)
white_controlled = [[-1 for x in range(8)]for y in range(8)]
black_controlled = [[-1 for x in range(8)]for y in range(8)]
ai_first = False # This determines wheter ai will play as white - changed on start by the player

def movePiece(button: list, mouseClick: bool, keys_pressed, player_possible_moves: list):
    if keys_pressed[pygame.K_ESCAPE]:
        return Falsed
    else:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        poss_moves = AllMoves(button, False,board)
        for y in range(8):
            for x in range(8):
                x_in = False
                y_in = False
                if mouse_x < ( (CORNER[0]+PIECE_OFFSET*x) + PIECE_SIZE) and mouse_x > (CORNER[0]+PIECE_OFFSET*x):
                    x_in = True
                if mouse_y < ( (CORNER[1]+PIECE_OFFSET*y) + PIECE_SIZE) and mouse_y > (CORNER[1]+PIECE_OFFSET*y):
                    y_in = True

                if (((x_in and y_in) and mouseClick) and ((y, x) in poss_moves)) and ( ((button[1], button[2]),(y, x)) in [((i[0][1],i[0][2]),i[1]) for i in player_possible_moves] ):   
                    is_ai = button[0][0]
                    board[button[1]][button[2]] = -1
                    board[y][x] = button[0]

                    # If its a promoting pawn dont end players move
                    if button[0][1] == 0 and (is_ai == 0 and y == 0):
                        return "pause"
                    
                    # If move is castling move rook too
                    if button[0][1] == 5 and y == 7 and button[1] == 7 and button[2] == 4:
                        if x == 6:
                            board[7][7] = -1
                            board[7][5] = (is_ai, 3, 1)
                        elif x == 2:
                            board[7][0] = -1
                            board[7][3] = (is_ai, 3, 0)

                    
                    return True
        return False


def PickPromotion():
    x,y = (BOARD_SIZE/2-SELECTOR_LENGTH/2, BOARD_SIZE/2-SELECTOR_LENGTH/3.9195/2)

    distance = SELECTOR_LENGTH/4
    mouse_x, mouse_y = pygame.mouse.get_pos()

    for i in range(4):
        x_i = x+i*distance
        if mouse_x < (x_i+distance) and mouse_x > x_i and mouse_y < (y+SELECTOR_LENGTH/3.9195/2) and mouse_y > y:
            for j in range(9):
                if board[0][j] != -1 and board[0][j][1] == 0: 
                    board[0][j] = (0,i+1,2)
                    return False
    return True


def hoverOnButton(temp_board: list):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    for y_index in range(8):
        for x_index in range(8):
            if temp_board[y_index][x_index] != -1:
                x_in = False
                y_in = False
                x = CORNER[0] + PIECE_OFFSET*x_index
                y = CORNER[1] + PIECE_OFFSET*y_index
                if mouse_x < ( x + PIECE_SIZE) and mouse_x > x:
                    x_in = True
                if mouse_y < (y + PIECE_SIZE) and mouse_y > y:
                    y_in = True
                if ( (x_in and y_in) and temp_board[y_index][x_index][0] == 0):
                    return (temp_board[y_index][x_index],y_index,x_index)
    return -1


def drawWindow(circle_loc_index, temp_board: list):
    WINDOW.blit(CHESS_BOARD, (0,0))
    surface = pygame.Surface((BOARD_SIZE, BOARD_SIZE), pygame.SRCALPHA)

    if circle_loc_index != -1:
         y,x = int(CORNER[1]+circle_loc_index[1]*PIECE_OFFSET), int(CORNER[0]+circle_loc_index[2]*PIECE_OFFSET)
         pygame.draw.circle(surface, (0,0,0,50), (x + PIECE_SIZE/2, y + PIECE_SIZE/2+(BOARD_SIZE/260) ), CIRCLE_SIZE)
    
    for y in range(8):
        for x in range(8):
            if temp_board[y][x] != -1:
                is_ai = temp_board[y][x][0]
                pieceType = temp_board[y][x][1]
                if y == 0 and is_ai==0 and pieceType==0:
                    WINDOW.blit(PROMOTION_SELECTOR, (BOARD_SIZE/2-SELECTOR_LENGTH/2, BOARD_SIZE/2-SELECTOR_LENGTH/3.9195/2))
                else:
                    color = int(ai_first != is_ai)
                    WINDOW.blit(pieces[color][pieceType], (CORNER[0] + x*PIECE_OFFSET, CORNER[1]+ y*PIECE_OFFSET))
            if white_controlled[y][x] != -1 and DEBUG:
                colors = (255,0,0,50), (0,255,0,50), (0,0,255,50)
                is_ai = colors[white_controlled[y][x]-1]
                pygame.draw.rect(surface, is_ai, pygame.Rect(CORNER[0] + x*PIECE_OFFSET, CORNER[1]+ y*PIECE_OFFSET, PIECE_SIZE,PIECE_SIZE))
    WINDOW.blit(surface, (0,0))    
    pygame.display.update()


def main():
    global ai_first
    player_color = (input("White or Black? (w/b): ")).lower()
    if player_color == "b":
        ai_first = True

    for color in range(2):
        pieces.append([])
        for i in range(6):
            pieces[color].append(pygame.transform.scale(pygame.image.load(f"Assets/{color}{i}.png"), (PIECE_SIZE, PIECE_SIZE)))
    
    StartingBoard()

    clock = pygame.time.Clock()
    run = True

    choosing = False
    mouseClick = False
    selectedButton = -1
    playerTurn = not ai_first
    pause = False
    circle_loc_index = -1

    player_possible_moves = PossibleMoves(0, board)

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONUP:
                mouseClick = True
            else: mouseClick = False
        keys_pressed = pygame.key.get_pressed()
        drawWindow(circle_loc_index, board)

        if not pause:
            if playerTurn:
                activeButton = hoverOnButton(board)
                if activeButton != -1 and activeButton != selectedButton and mouseClick:
                    choosing = True
                    mouseClick = False
                    selectedButton = tuple(activeButton)
                    circle_loc_index = tuple(selectedButton)
                if choosing:
                    tmp = movePiece(selectedButton, mouseClick, keys_pressed, player_possible_moves)
                    if tmp == "pause":
                        pause = True
                        choosing = False
                    elif tmp:
                        playerTurn = False
                        choosing = False
            else:
                all_black_possibleMoves = PossibleMoves(1, board)
                if all_black_possibleMoves ==[]:
                    #Stalemate
                    run=False
                    GameOver("None", True)
                elif all_black_possibleMoves==-1:
                    run = False
                    GameOver("Player")
                else: move = chessAI.turn(board, not ai_first)
                
                #Checking whether black took its own piece...
                try:
                    if board[move[0][1]][move[0][2]][0]==board[move[1][0]][move[1][1]][0]:
                        raise RuntimeError("Black took its own piece")
                except: pass

                board[move[0][1]][move[0][2]] = -1
                board[move[1][0]][move[1][1]] = move[0][0]

                #Prepare for whites turn
                player_possible_moves = PossibleMoves(0, board)
                if player_possible_moves ==[]:
                    #Stalemate
                    run = False
                    GameOver("None", True)
                elif player_possible_moves==-1:
                    run = False
                    GameOver("AI")

                playerTurn = True
            
        if pause and mouseClick:
            pause = PickPromotion()

def GameOver(winner: str, stalemate=False):
    drawWindow(-1, board)
    
    run = True
    pygame.font.init()
    my_font = pygame.font.Font(None, 100)
    if not stalemate:
        text = my_font.render(f"{winner} won", True, (0,0,0))
    else: text = my_font.render(f"Its a stalemate", True, (0,0,0))
    text_rect = text.get_rect(center=(BOARD_SIZE/2, BOARD_SIZE/2))
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
    
        WINDOW.blit(text, text_rect)    
        pygame.display.update()


def PossibleMoves(is_ai: bool, temp_board: list, kingPos=-1):
    """
    Args:
        is_ai (bool): The side of the player who is controlling the board 0 for a human player(down on the board) and 1 for the AI (up on the board).
        temp_board (list): A 2D list representing the current state of the chess board.
        kingPos (tuple, optional): The position of the king on the board. Defaults to -1 and finds it on its own (time consuming).

    Returns:
        list: A list of possible moves for the chosen side taking into account the king and the rules of chess. 
        If there are no possible moves, it returns either -1 (indicating mate for the chosen side) or an empty list indicating a stalemate.
    """
    whiteMoves = ControlledCells(0, temp_board)
    blackMoves = ControlledCells(1, temp_board)
    if kingPos==-1:
        for y in range(8):
            try:
                index = temp_board[y].index((is_ai, 5, 0))
                kingPos = (y, index)
            except ValueError: pass
        if not InBounds(kingPos[0], kingPos[1]) or kingPos==-1:
            raise RuntimeError("King not found")

    if is_ai: 
        opponent_controlled = white_controlled
        own_controlled = black_controlled
        own_moves = blackMoves
    else: 
        opponent_controlled = black_controlled
        own_controlled = white_controlled
        own_moves = whiteMoves

    king_moves = AllMoves((temp_board[kingPos[0]][kingPos[1]], kingPos[0], kingPos[1]), False, temp_board)
    if opponent_controlled[kingPos[0]][kingPos[1]] == 1:
        #In check
        possibleMoves = []
        king_zero_moves = king_moves.__len__() == 0
        for move in king_moves:
            possibleMoves.append( ( (temp_board[kingPos[0]][kingPos[1]], kingPos[0], kingPos[1]), move))

        rook_check, bishop_check, knight_check, pawn_check = False, False, False, False

        # Bishop check
        for i in sum(BishopMoves(kingPos[0], kingPos[1], False, temp_board),[]):
            y = i[0]
            x = i[1]
            if (temp_board[y][x] != -1 and temp_board[y][x][0] == abs(is_ai-1)) and (temp_board[y][x][1] == 1 or temp_board[y][x][1] == 4):
                bishop_check = True
                if own_controlled[y][x] in (1,2):
                    possibleMoves.append((y,x))
                    bishop_check = False 
                for y_i in range(y+int(math.copysign(1, kingPos[0]-y)), kingPos[0], int(math.copysign(1, kingPos[0]-y)) ):
                    x_i = x+abs(y-y_i)*int(math.copysign(1, kingPos[1]-x))
                    if own_controlled[y_i][x_i] in (1,3):
                        bishop_check = False
                        possibleMoves.append((y_i,x_i))

        # Rook check
        for i in sum(RookMoves(kingPos[0], kingPos[1], False, temp_board), []):
            y = i[0]
            x = i[1]
            if (temp_board[y][x] != -1 and temp_board[y][x][0] == (abs(is_ai-1))) and (temp_board[y][x][1] == 3 or temp_board[y][x][1] == 4):
                rook_check = True
                if own_controlled[y][x] in (1,2):
                    possibleMoves.append((y,x))
                    rook_check = False 
                if x - kingPos[1] == 0:
                    for y_i in range(y, kingPos[0], int(math.copysign(1, kingPos[0]-y))):
                        if own_controlled[y_i][x] in (1,3):
                            possibleMoves.append((y_i,x))
                            rook_check = False
                for x_i in range(x, kingPos[1], int(math.copysign(1, kingPos[1]-x))):
                    if own_controlled[y][x_i] in (1,3):
                        possibleMoves.append((y,x_i))
                        rook_check = False
        # Knight check
        horseyPositions = []
        for i in (-2,-1, 1,2):
            y = kingPos[0]
            x = kingPos[1]
            horseyPositions.extend([(y+i, int(x + abs(2/i))), (y+i, int(x - abs(2/i)))])
        for pos in horseyPositions:
            if InBounds(pos[0], pos[1]) and (temp_board[pos[0]][pos[1]] != -1) and (temp_board[pos[0]][pos[1]][0] == abs(is_ai-1) and temp_board[pos[0]][pos[1]][1] == 2):
                if own_controlled[pos[0]][pos[1]] in (-1, 3):
                    knight_check = True
                else: possibleMoves.append(pos)
        #Pawn check
        pawnY = int(kingPos[0]-1+2*is_ai)
        try: 
            possiblePawns = list( (temp_board[pawnY][kingPos[1]+1], temp_board[pawnY][kingPos[1]-1]) )
            for i in range(len(possiblePawns)):
                possiblePawn = list(possiblePawns[i])
                possiblePawn.pop(2)
                if possiblePawn == [abs(is_ai-1), 0]:
                    if own_controlled[pawnY][int(kingPos[1]-(i*2-1))] in (-1, 3):                    
                        pawn_check=True
                    else: possibleMoves.append((pawnY, int(kingPos[1]-(i*2-1))))
                    
        except: pass
        if king_zero_moves and (bishop_check or rook_check or knight_check or pawn_check): 
            #Mate
            return(-1)
        else:
            returnMoves = []
            for move in possibleMoves:
                try: list(move[0])
                except:
                    for move2 in own_moves:
                        if move2[1] == move: returnMoves.append(move2+(temp_board[move2[1][0]][move2[1][1]],))

                else: returnMoves.append(move+(temp_board[move[1][0]][move[1][1]],))
            if returnMoves.__len__()<possibleMoves.__len__():
                print(f"own: {own_moves}")
                print(f"possible: {possibleMoves}")
                print(f"return: {returnMoves}")
            return returnMoves
    
    for move in king_moves:
        own_moves.append( ( (temp_board[kingPos[0]][kingPos[1]], kingPos[0], kingPos[1]), move, temp_board[move[0]][move[1]]))
    return own_moves


def ControlledCells(is_ai: bool, temp_board: list):
    """
    Updates the list of controlled cells on the chess board based on the current state of the board.

    Args:
        is_ai (bool): The side of the player who is controlling the board 0 for a human player(down on the board) and 1 for the AI (up on the board).
        temp_board (list): A 2D list representing the current state of the chess board.

    Returns:
        list: A list of available moves for the chosen side, including promotions and captures.
    """

    all_controll_moves = []
    availableMoves = []
    controlled = [[-1 for x in range(8)]for y in range(8)]
    for y in range(8):
        for x in range(8):
            current_cell = ((temp_board[y][x]),y,x)
            if current_cell[0] != -1 and current_cell[0][0] == is_ai and current_cell[0][1]!=5:
                temp_availableMoves = AllMoves(current_cell,False, temp_board)
                for i in temp_availableMoves:
                    if InBounds(i[0],i[1]) and (temp_board[i[0]][i[1]] == -1 or temp_board[i[0]][i[1]][0]!=is_ai):
                        availableMoves.append((current_cell, i, temp_board[i[0]][i[1]]))
                if current_cell[0][1]==0: #Change controll value for pawns
                    y_move = int(current_cell[0][0]*2-1)
                    y = current_cell[1]
                    x = current_cell[2]
                    canPromote = ((is_ai == 1 and y == 6) or (is_ai == 0 and y ==1))
                    #Diagonals
                    isActive = (InBounds(y+y_move, x-1) and temp_board[y+y_move][x-1] != -1 and temp_board[y+y_move][x-1][0] != is_ai,
                                InBounds(y+y_move, x+1) and temp_board[y+y_move][x+1] != -1 and temp_board[y+y_move][x+1][0] != is_ai)
                    values = (int(not isActive[0])+1, int(not isActive[1])+1) # Assigns int value to the bool: if controlled(True)->1 else(False)->2
                    all_controll_moves.extend([(y+y_move, x-1, values[0]), (y+y_move, x+1, values[1])])
                    if values[0] == 1 and InBounds(y+y_move, x-1) and temp_board[y+y_move][x-1][0]!=is_ai: 
                        if canPromote: availableMoves.extend(AllPromotions(is_ai, temp_board[int(y+y_move)][x-1], y, x, (y+y_move, x-1)))
                        else: availableMoves.append((current_cell, (y+y_move, x-1), temp_board[int(y+y_move)][x-1]))
                    if values[1] == 1 and InBounds(y+y_move, x+1) and temp_board[y+y_move][x+1][0]!=is_ai:
                        if canPromote: availableMoves.extend(AllPromotions(is_ai, temp_board[int(y+y_move)][x+1], y, x, (y+y_move, x+1)))
                        else: availableMoves.append((current_cell, (y+y_move, x+1), temp_board[int(y+y_move)][x+1]))
                    #Forward
                    firstMove = ((is_ai == 0 and y == 6) or (is_ai == 1 and y ==1))
                    if InBounds(y+y_move, x) and (y+y_move, x) in temp_availableMoves:
                        all_controll_moves.append((y+y_move, x, 3))
                        if temp_board[y+y_move][x] == -1:
                            if canPromote: availableMoves.extend(AllPromotions(is_ai, -1, y, x, (y+y_move, x)))
                            else: availableMoves.append((current_cell, (y+y_move, x), -1))
                    if firstMove and (y+y_move*2, x) in temp_availableMoves: 
                        all_controll_moves.append((int(y+y_move*2), x, 3))
                        if temp_board[int(y+y_move*2)][x] == -1 and temp_board[int(y+y_move)][x] == -1:
                            availableMoves.append((current_cell, (int(y+y_move*2), x), -1))
                else: all_controll_moves.extend(AllMoves(current_cell,True,temp_board))

    for i in all_controll_moves:
        if InBounds(i[0], i[1]):
            if len(i) == 3: value = i[2]
            else: value = 1
            
            if (controlled[ int(i[0]) ][ int(i[1]) ] == 2 and value == 3) or (controlled[ int(i[0]) ][ int(i[1]) ] == 3 and value == 2):
                controlled[ int(i[0]) ][ int(i[1]) ] = 1
            elif value == 1 or (controlled[ int(i[0]) ][ int(i[1]) ] == -1):
                controlled[ int(i[0]) ][ int(i[1]) ] = value

    if is_ai==0: 
        for i in range(8):
            white_controlled[i] = list(controlled[i])
    else: 
        for i in range(8):
            black_controlled[i] = list(controlled[i])

    return availableMoves


def AllPromotions(is_ai: bool, takenPiece, y: int, x: int, newPos: list):
    availableMoves = []
    possiblePromotions = list((is_ai, i, 2) for i in range(1,5) )
    for newPiece in possiblePromotions:
        temp_button = (newPiece, y, x)
        availableMoves.append((temp_button, newPos, takenPiece))
    return availableMoves


def InBounds(y: int, x: int):
    return ((y>-1 and x>-1) and (y<8 and x<8))


def IsPinned(available_moves: list, y: int, x: int, temp_board: list):
    """
    Checks if a piece is pinned by an opponent's piece.

    Args:
        available_moves (list): A 2D list of possible places the opponents piece could be.
            Contains 4 lists for columns, lines and both diagonal lines respectively.
        y (int): The y-coordinate of the piece to check.
        x (int): The x-coordinate of the piece to check.
        temp_board (list): A temporary representation of the board.

    Returns:
        list: A list of pinned moves if the piece is pinned, -1 otherwise.
    """
    
    piece = temp_board[y][x]
    is_ai = piece[0]
    for i in range(4):
        kingPos = ()
        threats = []
        for j in range(len(available_moves[i])):
            try:
                pos = (available_moves[i][j][0], available_moves[i][j][1])
                if temp_board[pos[0]][pos[1]][0] == is_ai and temp_board[pos[0]][pos[1]][1] == 5:
                    kingPos = pos 
                elif (temp_board[pos[0]][pos[1]][0] != is_ai and temp_board[pos[0]][pos[1]][1] in (1,3,4)):
                    threats.append(((pos), temp_board[pos[0]][pos[1]][1]))

            except TypeError: pass 
        if kingPos != ():
            pinnedMoves = []
            for threat in threats:
                diff_y = (kingPos[0]<y and y<threat[0][0]) or (kingPos[0]>y and y>threat[0][0])
                diff_x = (kingPos[1]<x and x<threat[0][1]) or (kingPos[1]>x and x>threat[0][1])
                if diff_y or diff_x:
                    #Bishop or queen
                    if diff_y and diff_x and threat[1]!=3:
                        for i in range(0,int(kingPos[0]-threat[0][0]), int(math.copysign(1,kingPos[0]-threat[0][0]))):
                            y = threat[0][0]+i
                            x = threat[0][1]+i
                            pinnedMoves.append((y,x))
                    #Rook or queen
                    elif threat[1]!=1 and ((kingPos[0]==y==threat[0][0]) or (kingPos[1]==x==threat[0][1])):
                        for i in range(0,int(kingPos[0]-threat[0][0]), int(math.copysign(1,kingPos[0]-threat[0][0]))):
                            y = threat[0][0]+i
                            x = threat[0][1] 
                            pinnedMoves.append((y,x))
                        for i in range(0,int(kingPos[1]-threat[0][1]), int(math.copysign(1,kingPos[1]-threat[0][1]))):
                            y = threat[0][0]
                            x = threat[0][1]+i
                            pinnedMoves.append((y,x))
                    else: break
                    return pinnedMoves
    return -1


def AllMoves(selectedButton: list, ignoreKing: bool, temp_board: list):
    """
    This function generates all possible moves for a given chess piece on a temporary board.

    Args:
        selectedButton (list): A list containing the piece type, index, and its current position on the board.
        ignoreKing (bool): A boolean indicating whether to passtrough the king - used when calculating controlled cells.
        temp_board (list): A 2D list representing the current state of the chess board.

    Returns:
        list: A list of tuples containing all possible moves for the given piece.
    """
    is_ai = selectedButton[0][0]
    pieceType = selectedButton[0][1]
    pieceIndex = selectedButton[0][2]
    y = selectedButton[1]
    x = selectedButton[2]
    possibleMoves = []
    available_moves = RookMoves(y,x,ignoreKing,temp_board) + BishopMoves(y,x,ignoreKing,temp_board)

    # Pawn
    if pieceType == 0:
        y_move = (is_ai * 2 - 1)
        firstMove = ((is_ai == 0 and y == 6) or (is_ai == 1 and y == 1))
        # forward
        if InBounds(y+y_move, x) and temp_board[y+y_move][x] == -1:
            possibleMoves.append((y+y_move, x))
        # first move
        if firstMove and InBounds(int(y+y_move*2), x) and temp_board[int(y+y_move*2)][x] == -1 and temp_board[int(y+y_move)][x] == -1:
            possibleMoves.append((int(y+y_move*2), x))
        # diagonals
        if InBounds(y+y_move,x+1) and temp_board[y+y_move][x+1] != -1 and temp_board[y+y_move][x+1][0] == int(not is_ai):
            possibleMoves.append((y+y_move, x+1))
        if InBounds(y+y_move,x-1) and temp_board[y+y_move][x-1] != -1 and temp_board[y+y_move][x-1][0] == int(not is_ai):
            possibleMoves.append((y+y_move, x-1))
    
    #Bishop
    elif pieceType == 1:
        possibleMoves = available_moves[2]+available_moves[3]
    #Horsey
    elif pieceType == 2:
        for i in (-2,-1, 1,2):
            possibleMoves.extend([(y+i, int(x + abs(2/i)) ), (y+i, int(x - abs(2/i)) )])
    #Rook
    elif pieceType == 3:
        possibleMoves = available_moves[0]+available_moves[1]
    #Queen
    elif pieceType == 4:
        possibleMoves = sum(available_moves,[])
    #King
    elif pieceType == 5:
        possibleMoves = KingMoves(y,x,is_ai,temp_board)
        
    #Check for pin
    pinnedMoves = IsPinned(available_moves,y,x, temp_board)
    if pinnedMoves != -1:
        returnMoves = []
        for i in possibleMoves:
            if i in pinnedMoves: returnMoves.append(i)
        return returnMoves

    return possibleMoves


def KingMoves(y: int, x: int, is_ai: bool, temp_board: list):
    available_moves = []
    if is_ai: controlled = list(white_controlled)
    else: controlled = list(black_controlled)

    # Normal moves
    for y_modifier in range(-1,2,1):
        for x_modifier in range(-1,2,1):
            if InBounds(y+y_modifier, x+x_modifier) and (temp_board[y+y_modifier][x+x_modifier] == -1 or temp_board[y+y_modifier][x+x_modifier][0] != is_ai):
                if controlled[y+y_modifier][x+x_modifier] in (-1,3):
                    # Check if enemy king isnt guarding it
                    safe = True
                    for y_modifier2 in range(-1,2,1):
                        for x_modifier2 in range(-1,2,1):
                            if InBounds(y+y_modifier+y_modifier2, x+x_modifier+x_modifier2) and temp_board[y+y_modifier+y_modifier2][x+x_modifier+x_modifier2] == (abs(is_ai-1), 5, 0):
                                safe=False
                    if safe:
                        available_moves.append((y+y_modifier, x+x_modifier))
    # Castling
    # TODO - check if rook or king has moved
    if is_ai: row = 0
    else: row = 7

    # Check for king
    if temp_board[row][4] != (is_ai, 5, 0):
        return available_moves
    
    # King side
    if temp_board[row][7] != -1 and temp_board[row][7][1] == 3 and temp_board[row][7][0] == is_ai and temp_board[row][7][2] == 1:
        if controlled[row][5] in (-1,3) and controlled[row][6] in (-1,3) and temp_board[row][5] == -1 and temp_board[row][6] == -1:
            available_moves.append((row, 6))
    
    # Queen side
    if temp_board[row][0] != -1 and temp_board[row][0][1] == 3 and temp_board[row][0][0] == is_ai and temp_board[row][0][2] == 0:
        if (controlled[row][3] in (-1,3) and controlled[row][2] in (-1,3)) and (temp_board[row][3] == -1 and temp_board[row][2] == -1 and temp_board[row][1] == -1):
            available_moves.append((row, 2))

    return available_moves


def RookMoves(y_input: int, x_input: int, ignoreKing: bool, temp_board: list):
    possibleMoves=[[],[]] # index 0 = y column index 1 = x row
    is_ai = temp_board[y_input][x_input][0]

    for i in ((-1, 0), (1,0), (0, -1), (0, 1)):
        y = y_input + i[0]
        x = x_input + i[1]
        while(True):
            if not InBounds(y,x): 
                break
            possibleMoves[abs(i[1])].append((y,x))
            if temp_board[y][x] != -1 and not ( (ignoreKing and temp_board[y][x] == (abs(is_ai-1),5,0) ) ):
                break
            
            y += i[0]
            x += i[1]
    return possibleMoves


def BishopMoves(y_input: int, x_input: int, ignoreKing: bool, temp_board: list):
    possibleMoves = [[],[]]
    is_ai = temp_board[y_input][x_input][0]
    x_modifier = 1

    for i in (-1, -1, 1, 1):
        y = y_input + i
        x = x_input + x_modifier
        while(True):
            if not InBounds(y,x): 
                break
            possibleMoves[abs(i)-1].append((y, x))
            if temp_board[y][x] != -1 and not ( (ignoreKing and temp_board[y][x] == (abs(is_ai-1),5,0) ) ):
                break
            
            y += i
            x += x_modifier
        x_modifier=int(x_modifier*-1)
    return possibleMoves


def StartingBoard():
    for color in range(2):
        if color==0: y = 6
        else: y = 1

        board[y] = [ (color, 0, i) for i in range(8)]
        board[y-(color-1+color)] = [(color, 3, 0), (color, 2, 0), (color, 1, 0),
                                    (color, 4, 0), (color, 5, 0),
                                    (color, 1, 1), (color, 2, 1), (color, 3, 1)]


if __name__ == "__main__":
    main()