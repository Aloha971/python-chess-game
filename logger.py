class Logger:

    def __init__(self):
        self.file = open("log.txt", 'w')
    
    def WriteMove(self, old_y, old_x, new_y, new_x, piece_data):
        color = piece_data[0]
        piece_index = piece_data[2]
        
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        pieces = ["B", "N", "R", "Q", "K"]
        piece = ""
        if piece_data[1] != 0: piece = pieces[piece_data[1]-1]
        line = letters[new_x]
        column = 8-new_y

        text = f"c{color}p{piece_data[1]}i{piece_index}:{old_y}{old_x}-{new_y}{new_x}[{piece}{line}{column}]\n"

        self.file.write(text)

    def Close(self, board):
        text = "Final board:\n"
        for line in board:
            text += str(line) + "\n"
        self.file.write(text)
        self.file.close()
    
    def ClearFile(self):
        self.file = open("log.txt", 'w')