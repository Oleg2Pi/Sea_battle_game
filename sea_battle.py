class Board:
    board = [['O' for _ in range(6)] for _ in range(6)]

    def create_board(self):
        for i in range(6):
            self.board[i].append('|')
        for i in range(6):
            self.board[i].insert(0, str(i+1))
        self.board.insert(0, [' '])
        for i in range(6):
            self.board[0].append('|')
            self.board[0].append(i+1)
        self.board[0].append('|')
        return self.board
    
    @property
    def print_board(self):
        for i in self.board:
            print(*i)
    

class Ship:
    pass

class Player:
    pass

class Person(Player):
    pass

class AI(Player):
    pass

def print_boards(board_player, board_ai):
    list_names = ['Player\'s board: ', 'AI\'s board: ']
    list_boards = [board_player, board_ai]
    for name in list_names:
        print(name, end=' '* 16)
    
    

if __name__ == '__main__':
    board_player = Board()
    board_ai = Board()
    # print_boards(board_player, board_ai)
    board_player.print_board