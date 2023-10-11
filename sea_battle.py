import random
import time

class BoardException(Exception):
    pass

class BoardWrongShipException(BoardException):
    pass

class BoardOutException(BoardException):
    def __str__(self) -> str:
        return 'Координаты выстрела за пределами доски!'
    
class BoardUseException(BoardException):
    def __str__(self) -> str:
        return 'Вы уже стреляли в эту клетку.'
    
class Dot:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def __eq__(self, other: object) -> bool:
        return self.x == other.x and self.y == other.y

    def __str__(self) -> str:
        return f'Dot({self.x}, {self.y})'
    
class Ship:
    def __init__(self, bow: Dot, length: int, vertical: bool) -> None:
        self.bow = bow
        self.length = length
        self.lives = length
        self.vertical = vertical

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            start_x = self.bow.x
            start_y = self.bow.y
            if self.vertical:
                start_y += i
            else:
                start_x += i
            ship_dots.append(Dot(start_x, start_y))
        return ship_dots

    def is_hit(self, dot):
        return dot in self.dots
    

class Board:
    def __init__(self, size, hid=False) -> None:
        self.size = size
        self.hid = hid
        self.field = [['O'] * size for _ in range(size)]
        self.busy = []
        self.ships = []
        self.last_hit = []
        self.count_destroy_ships = 0

    def __str__(self) -> str:
        result = '  | ' + ' | '.join(map(str, range(1, self.size + 1))) + ' |'
        for i, row in enumerate(self.field):
            result += f'\n{i+1} | ' + ' | '.join(row) + ' |'
        if self.hid:
            result = result.replace('■', 'O')
        return result
    
    def out(self, d: Dot):
        return not (0 <= d.x < self.size and 0 <= d.y < self.size)
    
    def contour(self, ship, visible=False):
        around = [(i, j) for i in range(-1, 2) for j in range(-1, 2)]
        for dot in ship.dots:
            for dx, dy in around:
                curr_dot = Dot(dot.x + dx, dot.y + dy)
                if not self.out(curr_dot) and curr_dot not in self.busy:
                    if visible:
                        self.field[curr_dot.x][curr_dot.y] = '.'
                    self.busy.append(curr_dot)
                
    def add_ship(self, ship):
        for d in ship.dots:
            if d in self.busy or self.out(d):
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = '■'
            self.busy.append(d)
        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if d in self.busy:
            raise BoardUseException()
        if self.out(d):
            raise BoardOutException()
        
        self.busy.append(d)
        for ship in self.ships:
            if ship.is_hit(d):
                self.field[d.x][d.y] = 'X'
                print('Попадение!')
                ship.lives -= 1
                if ship.lives == 0:
                    self.count_destroy_ships += 1
                    self.contour(ship, visible=True)
                    print('Корабль уничтожен!')
                    self.last_hit = []
                    return False
                else:
                    print('Корабль ранен!')
                    self.last_hit.append(d)
                    return True
        self.field[d.x][d.y] = '.'
        print('Мимо')
        return False
    
    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count_destroy_ships == len(self.ships)
    
class Player:
    def __init__(self, board, enemy) -> None:
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()
    
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                time.sleep(2)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        last = self.enemy.last_hit
        while True:
            if last:
                if len(last) == 1:
                    near = ((0, 1), (0, -1), (1, 0), (-1, 0))
                else:
                    if last[0].x == last[-1].x:
                        near = ((0, 1), (0, -1))
                    else:
                        near = ((1, 0), (-1, 0))
                dx, dy = random.choice(near)
                d = random.choice((Dot(last[-1].x + dx, last[-1].y + dy), Dot(last[0].x + dx, last[0].y + dy)))
            else:
                d = Dot(random.randint(0, 5), random.randint(0, 5))
            if d not in self.enemy.busy and not self.enemy.out(d):
                break
        time.sleep(0.1 * random.randint(15, 50))
        print(f'Ход компьютера: {d.x + 1} {d.y + 1}')
        return d
    
class User(Player):
    def ask(self):
        while True:
            coords = input('Введите координаты выстрела:\t').split()
            if len(coords) != 2:
                print('Введите 2 координаты!')
                continue
            x, y = coords
            if not all((x.isdigit(), y.isdigit())):
                print('Координаты должны быть числами')
                continue
            return Dot(int(x) - 1, int(y) - 1)
        
class Game:
    def __init__(self, size = 6) -> None:
        self.lens = (3, 2, 2, 1, 1, 1, 1)
        self.size = size
        ai_board = self.random_board()
        user_board = self.random_board()
        ai_board.hid = True

        self.ai = AI(ai_board, user_board)
        self.pl = User(user_board, ai_board)

    def try_gen_board(self):
        attempts = 0
        board = Board(size=self.size)
        for i in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(random.randint(0, self.size), random.randint(0, self.size)), i, bool(random.randint(0, 1)))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board
    
    def random_board(self):
        board = None
        while board is None:
            board = self.try_gen_board()
        return board
    
    @staticmethod
    def greet():
        print('-' * 20)
        print('  Приветствуем вас в игре морской бой    ')
        print('-' * 20)
        print(' Формат ввода(для справки): x y ')
        print(' x - номер строки  ')
        print(' y - номер столбца ')
        print('-' * 20)

    def print_boards(self):
        print('-' * self.size * 10)
        print('Ваша доска:'.ljust((self.size + 1) * 4 - 1) + ' ' * self.size + 'Доска AI:')
        for s1, s2 in zip(self.pl.board.__str__().split('\n'), self.ai.board.__str__().split('\n')):
            print(s1 + ' ' * self.size + s2)

    def loop(self):
        step = 0
        while True:
            self.print_boards()
            if step % 2 == 0:
                print('Ваш ход!')
                repeat = self.pl.move()
            else:
                print('Ходит AI')
                repeat = self.ai.move()
            if repeat:
                step -= 1

            if self.ai.board.defeat():
                self.print_boards()
                print('Вы выйграли!')
                break
            if self.pl.board.defeat():
                self.print_boards()
                print('AI выйграл!')
                break
            step += 1

    def start(self):
        self.greet()
        self.loop()


game = Game()
game.start()