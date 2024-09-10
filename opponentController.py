def ReadFromFiles(file):
    lines = file.readlines()
    storage = {}
    for line in lines:
        board_hash = ""
        i = 0
        while line[i]!=" ":
            board_hash+=line[i]
            i+=1
    
        old_pos = [int(line[i+1]), int(line[i+2])]
        new_pos = [int(line[i+3]), int(line[i+4])]
        storage[int(board_hash)] = (old_pos, new_pos)
    
    return storage


def HashBoard(board, is_maximazing=-1):
    newBoard = []
    for i in board:
        newBoard.append(tuple(i))
    if is_maximazing!=-1:
        return hash((tuple(newBoard), is_maximazing))
    else:
        return hash(tuple(newBoard))


class ChessAI:
    def __init__(self, depth=10):
        self.values = [1,3,3,5,9,100] # Possible values assigned for after capture
        self.board = [[(-1) for x in range(8)]for y in range(8)]
        self.time = __import__('time')
        self.main = __import__('main')
        self.depth = depth
        
        f_white = open("Assets/openings.txt", mode="r")
        f_black = open("Assets/defences.txt", mode="r")

        self.move_storages = (ReadFromFiles(f_white), ReadFromFiles(f_black))

        f_white.close()
        f_black.close()


    def turn(self, temp_board: list, black: bool):
        board_hash = HashBoard(temp_board)
        print(board_hash)
        if board_hash in self.move_storages[black]:
            old_pos = self.move_storages[black][board_hash][0]
            print(f"old:{old_pos}")
            new_pos = self.move_storages[black][board_hash][1]
            print(f"new:{new_pos}")
            piece_data = temp_board[old_pos[0]][old_pos[1]]
            print(f"data{piece_data}")
            target_data = temp_board[new_pos[0]][new_pos[1]]
            print(((piece_data, old_pos[0], old_pos[1]), new_pos, target_data))
            return ((piece_data, old_pos[0], old_pos[1]), new_pos, target_data)

        kingPos = [-1, -1]
        for color in range(2):
            for y in range(8):
                try:
                    index = temp_board[y].index((color, 5, 0))
                    kingPos[color] = (y, index)
                except ValueError: pass

        start_time = self.time.time()
        move = self.minimax(depth=self.depth, board=temp_board, is_maximazing=False, returnMove=True,
                             alpha=-1_000_000, beta=1_000_000, storage={}, moves_counter=1, max_depth=0, kingPos=kingPos)
        print("--- %s seconds ---" % (self.time.time() - start_time))
        print(f"best one {move}")
        
        return move[1]


    def minimax(self, depth, board, is_maximazing, returnMove, alpha, beta, storage, moves_counter, max_depth, kingPos):
        if moves_counter>4_000_000 and max_depth==0: 
            max_depth=depth
            if max_depth%2==1:
                max_depth+=1
            return self.evaluateBoard(board), max_depth
        if depth==max_depth:
            return self.evaluateBoard(board), max_depth
        else:
            if is_maximazing:color=0 
            else: color=1
            possMoves = self.main.PossibleMoves(color, board, kingPos[color])

            evaluations = []
            if possMoves == -1:
                if is_maximazing: return (-1_000_000, max_depth)
                else: return (1_000_000, max_depth)
            if possMoves == []: return (0, max_depth)

            for move in possMoves:
                if move[2] != -1 and move[2][1]==5:
                    if is_maximazing: minimax_value = 1_000_000
                    else: minimax_value = -1_000_000

                else:
                    currPos = (move[0][1], move[0][2])
                    piece = move[0][0]
                    newPos =move[1]
                    temp_board = list(list(i) for i in board)
                    temp_king_pos = [list(kingPos[0]), list(kingPos[1])]
                    if piece[1] == 5:
                        temp_king_pos[piece[0]] = list(newPos)
                        # If move is castling move rook too
                        if currPos == (0, 4):
                            if newPos == (0, 6):
                                board[0][7] = -1
                                board[0][5] = (1, 3, 1)
                            elif newPos == (0, 2):
                                board[0][0] = -1
                                board[0][3] = (1, 3, 0)
                    temp_board[currPos[0]][currPos[1]] = -1
                    temp_board[newPos[0]][newPos[1]] = piece

                    board_hash = HashBoard(temp_board, is_maximazing)
                    if board_hash in storage:
                        minimax_value = int(storage[board_hash][0])

                    else:
                        minimax_value, temp = self.minimax(depth-1, temp_board, not is_maximazing, False, alpha, beta,storage, moves_counter*len(possMoves), max_depth, temp_king_pos)
                        max_depth = temp
                        if max_depth == depth: return self.evaluateBoard(board), max_depth
                        storage[board_hash] = minimax_value, is_maximazing
                
                evaluations.append(minimax_value)
                if is_maximazing:
                    if minimax_value > alpha: alpha=minimax_value
                    if beta<=alpha: 
                        break
                else:
                    if minimax_value < beta: beta=minimax_value
                    if beta<=alpha < alpha: 
                        break
            if returnMove:
                if is_maximazing: 
                    return alpha, possMoves[evaluations.index(alpha)]
                else:
                    return beta, possMoves[evaluations.index(beta)] 

            if is_maximazing:
                return (alpha, max_depth)
            else:
                return (beta, max_depth)


    def evaluateBoard(self, board):
        eval = 0
        for y in board:
            for x in y:
                if x!=-1:
                    if x[0]==0: eval+=self.values[x[1]]
                    else: eval-=self.values[x[1]]
        return eval