from random import randint
class FieldException(Exception):
    pass

class FieldOutException(FieldException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class FieldUsedException(FieldException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class FieldWrongShipException(FieldException):
    pass

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, g, v):
        self.bow = bow
        self.g = g
        self.v = v
        self.lives = g

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.g):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.v == 0:
                cur_x += i

            elif self.v == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots

class Field:
    def __init__(self, hid = False, size = 6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.board = [ ["."]*size for _ in range(size) ]

        self.busy = []
        self.ships = []

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.board):
            res += f"\n{i+1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", ".")
        return res

    def out(self, d):
        return not((0<= d.x < self.size) and (0<= d.y < self.size))

    def contour(self, ship, verb = False):
        near = [
            (-1, -1), (-1, 0) , (-1, 1),
            (0, -1), (0, 0) , (0 , 1),
            (1, -1), (1, 0) , (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.board[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise FieldWrongShipException()
        for d in ship.dots:
            self.board[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise FieldOutException()

        if d in self.busy:
            raise FieldUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.board[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb = True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.board[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []

class Player:
    def __init__(self, field, enemy):
        self.field = field
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except FieldException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0,5), randint(0, 5))
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d

class User(Player):
    def ask(self):
        while True:
            cords = (input("Ваш ход: ").split())

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not(x.isdigit()) or not(y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x-1, y-1)


class Game:
    def try_field(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        field = Field(size = self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0,1))
                try:
                    field.add_ship(ship)
                    break
                except FieldWrongShipException:
                    pass
        field.begin()
        return field

    def random_field(self):
        field = None
        while field is None:
            field = self.try_field()
        return field

    def __init__(self, size = 6):
        self.size = size
        pl = self.random_field()
        co = self.random_field()
        co.hid = False

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def greet(self):
        print("  Вас приветсвует  ")
        print("  игра Морской бой ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-"*20)
            print("Доска пользователя:")
            print(self.us.field)
            print("-"*20)
            print("Доска компьютера:")
            print(self.ai.field)
            print("-"*20)
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.field.count == 7:
                print("-"*20)
                print("Пользователь выиграл!")
                break

            if self.us.field.count == 7:
                print("-"*20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()
