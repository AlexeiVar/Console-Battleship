# Импортирую randint из random, чтобы дальше делать случайные точки
# Так же импортирую choice чтобы можно было выбрать направление корабля случайно
from random import randint, choice


# Начало создания ошибок, можно некоторые было бы сделать как одни, но как по мне так более точно
class ShotOutBoardException(Exception):
    def __str__(self):
        return 'Выстрел вне поля'


class ShipOutBoardException(Exception):
    def __str__(self):
        return 'Корабль вне поля'


class ShipPlacementException(Exception):
    def __str__(self):
        return 'Корабль стоит слишком близко к другому кораблю'


class ShotSameSpaceException(Exception):
    def __str__(self):
        return 'Выстрел в эту точку уже был сделан'


# Конец создания ошибок


# Класс точки, нужен в основном для сравнения двух точек между друг другом
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Это только для отладки
    def __str__(self):
        return f"X={self.x}, Y={self.y}"

    # Позволит сравнивать две точки
    def __eq__(self, other):
        if (self.x == other.x) and (self.y == other.y):
            return True
        else:
            return False


# Класс корабля, создается в основном по алгоритму, сам бы возможно сделал немного иначе
class Ship:
    def __init__(self, lenght, bow_pos_x, bow_pos_y, facing):
        self.lenght = lenght
        self.bow_pos = Dot(bow_pos_y, bow_pos_x)
        self.facing = facing  # может быть horizontal(пойдет направо) и vertical (пойдет вниз)
        self.lives = lenght

    # Метод возвращает все свои точки в виде списка
    @property
    def dots(self):
        all_dots = [self.bow_pos]
        if self.lenght > 1:
            if self.facing == "horizontal":
                for i in range(self.lenght - 1):
                    all_dots.append(Dot(self.bow_pos.x + i + 1, self.bow_pos.y))
                return all_dots
            else:
                for i in range(self.lenght - 1):
                    all_dots.append(Dot(self.bow_pos.x, self.bow_pos.y + i + 1))
                return all_dots
        else:
            return all_dots


# Доска собственно для обоих игроков, сделано опять-таки по алгоритму, сделал бы скорее всего так же и сам
class Board:
    def __init__(self, hidden):
        self.hidden = hidden
        self.live_ships = 0
        self.ship_list = []
        self.board = [
            ["О", "О", "О", "О", "О", "О"],
            ["О", "О", "О", "О", "О", "О"],
            ["О", "О", "О", "О", "О", "О"],
            ["О", "О", "О", "О", "О", "О"],
            ["О", "О", "О", "О", "О", "О"],
            ["О", "О", "О", "О", "О", "О"],
        ]

    # Проверяет находиться ли точка вне поля
    def out(self, dot):
        if (dot.x > 5) or (dot.y > 5) or (dot.x < 0) or (dot.y < 0):
            return True
        else:
            return False

    # Обводит корабль (позволяет посмотреть все его соседние клетки)
    def contour(self, ship):
        neighbors = []
        ship_dots = ship.dots
        for space in ship_dots:
            # Поскольку все соседи просто отличаются x или/и y на -1 или 1,
            # при помощи двойного цикла можно найти их всех
            for x in range(-1, 2):
                for y in range(-1, 2):
                    # Понятно что если у точки не изменить координаты то мы получим её же, поэтому пропускаем
                    if x == 0 and y == 0:
                        continue
                    # Уже есть метод для проверки находится ли точка на доске мы можем ей воспользоваться
                    if self.out(Dot(space.x - x, space.y - y)):
                        continue
                    # Точка не соседняя если это сам корабль
                    if Dot(space.x - x, space.y - y) in ship_dots:
                        continue
                    # Поскольку нам не доступен .set, просто проведем проверку, что этой точки еще нет в списке
                    if Dot(space.x - x, space.y - y) not in neighbors:
                        neighbors.append(Dot(space.x - x, space.y - y))
        return neighbors

    # Метод ставит корабли на доску
    def add_ship(self, ship):
        # Убедимся что мы не пытаемся поставить корабль на корабль, нужно это сделать только раз так как проверка на
        # соседство предотвратит любые другие случаи пересекания
        if self.board[ship.bow_pos.x][ship.bow_pos.y] == "■":
            raise ShipPlacementException
        # Получим все клетки корабля
        occupied = ship.dots
        # Перед тем как что-то делать с кораблем, проверим поместиться ли он на доску
        for space in occupied:
            if self.out(space):
                raise ShipOutBoardException
            # Проверим чтобы не было рядом кораблей
            for existing in self.ship_list:
                if space in self.contour(existing):
                    raise ShipPlacementException
        # Технически в связи с условиями задания не обязательно вручную повышать количество живых кораблей
        # Но это позволит увеличить стартовое количество кораблей при необходимости
        self.live_ships += 1
        self.ship_list.append(ship)
        for space in occupied:
            self.board[space.x][space.y] = "■"

    # Выводит доску
    def show(self):
        i = 1
        # Сначала делаем строку, где будет номер колоны, вставляем сразу же с отделителем и всеми пробелами
        print("  | 1 | 2 | 3 | 4 | 5 | 6 |")
        if self.hidden:
            # Создаю пустой список, он будет использоваться для вывода скрытой доски
            concealed = []
            # Поскольку у нас список в списке (двумерный массив), нужно все это делать через цикл, чтобы "разобрать" его
            for row in self.board:
                concealed.append(list(map(lambda x: x.replace('■', 'О'), row)))
            # Ну и сам вывод прост, логика для обоих одинакова, выводим i, чтобы пометить номер строки,
            # один элемент списка и добавляем отделитель, пробелы python поставит сам
            for row in concealed:
                print(i, "|", row[0], "|", row[1], "|", row[2], "|", row[3], "|", row[4], "|", row[5], "|")
                i += 1
        else:
            for row in self.board:
                print(i, "|", row[0], "|", row[1], "|", row[2], "|", row[3], "|", row[4], "|", row[5], "|")
                i += 1

    # Делает выстрел по доске
    def shoot(self, dot):
        if self.out(dot):  # Скорее всего эти два нада перенести будет ниже
            raise ShotOutBoardException
        if self.board[dot.x][dot.y] == "X":
            raise ShotSameSpaceException
        # Проверка есть ли там корабль, позволит реализовать второй ход если есть попадание и уничтожение кораблей
        if self.board[dot.x][dot.y] == "■":
            ship_hit = True
            # Проверяю какой именно корабль был подбит
            for ship in self.ship_list:
                if dot in ship.dots:
                    # Снижаю его жизни на 1
                    ship.lives -= 1
                # И если корабль уничтожен то удаляю его, понижаю количество живых кораблей на доске и сообщаю об этом игроку
                if ship.lives == 0:
                    self.ship_list.remove(ship)
                    self.live_ships -= 1
                    print("Корабль уничтожен!")
        else:
            ship_hit = False
        # Ну и в конце помечаю что по клетке постреляли
        self.board[dot.x][dot.y] = "X"
        return ship_hit


class Player:
    def __init__(self, own_board, enemy_board):
        self.own_board = own_board
        self.enemy_board = enemy_board

    # Оставляем пустым метод для наследства, он будет спрашивать куда выстрелить (делая все проверки) и потом давать
    # точку
    def ask(self):
        pass

    # Делаем сам ход, поскольку в методе выстрела уже есть все нужные проверки мы можем просто использовать их
    # так как если ошибка нам нужно будет просить новый выстрел, просто вызываем метод еще раз
    def move(self):
        try:
            if self.enemy_board.shoot(self.ask()):
                if not self.own_board.hidden:
                    print("Есть попадание!")
                return True
        except (ShotSameSpaceException, ShotOutBoardException):
            # делаем проверку, что стреляет игрок дабы не выводить сообщение для ИИ
            if not self.own_board.hidden:
                print("Выстрел невозможен, выберите другую точку")
            self.move()
        return False


class AI(Player):
    # Все что нужно в этом классе, это генерировать случайный выстрел
    def ask(self):
        return Dot(randint(0, 5), randint(0, 5))


class User(Player):
    def ask(self):
        # спрашиваем координаты, пока не получим их
        while True:
            # Конструкция try except в данном случае поможет нам проверить что введены две цифры
            try:
                target = input("Выберите строку и столб куда стрелять, без пробела:")
                x, y = list(target.strip())
                # Так как игроку показывается что доска имеет значения от 1 до 6, а на самом деле от 0 до 5,
                # снизим значения на 1, это так же гарантирует что это цифры
                x = int(x) - 1
                y = int(y) - 1
                if x<0 or y<0:
                    raise ValueError
            except (ValueError):
                print("Вы неправильно ввели координаты")
            else:
                # Если координаты введены правильно, то отправляем их назад в move
                return Dot(x, y)


class Game:
    def __init__(self):
        self.user_board = self.random_board(False)
        self.ai_board = self.random_board(True)
        self.user = User(self.user_board, self.ai_board)
        self.ai = AI(self.ai_board, self.user_board)

    # Метод создает случайную доску, для игрока (по условию не нужно было давать игроку возможность расставить корабли и
    # так же для ИИ
    def random_board(self, hide):
        board = Board(hide)
        # Для рандомного выбора направления
        direction = ["vertical", "horizontal"]
        # Это длина всех кораблей которые у нас будут в игре
        ship_lenghts = [3, 2, 2, 1, 1, 1, 1]
        # Это нужно для того чтоб не застрять на плохой доске
        i = 0
        for lenght in ship_lenghts:
            # цикл позволит нам пытаться поставить корабль бесконечное число раз
            while True:
                # Если мы вдруг на одну и ту же доску пытаемся 1000 раз поставить корабль, даже если разные,
                # начнем с новой доски
                if i > 999:
                    return self.random_board(hide)
                try:
                    board.add_ship(Ship(lenght, randint(0, 5), randint(0, 5), choice(direction)))
                # У нас уже есть ошибки в самом постановлении кораблей, поэтому используем их
                except (ShipPlacementException, ShipOutBoardException):
                    i += 1
                    continue
                else:
                    # Ну и если ошибки не было то выйдем из цикла while
                    break
        return board

    # Просто метод для вызова текста, делаем его статическим поскольку так правильнее
    @staticmethod
    def greet():
        print("Добро пожаловать в учебный проект 'Морской бой'.")
        print("Цель игры уничтожить корабли противника, пока он не уничтожил ваши.")
        print("Противник будет случайно стрелять по вашей доске, а вам нужно будет вводить координаты формата '16', "
              "обе доски были сгенерированы случайно")
        print("Удачи!")

    def loop(self):
        # Дадим игроку первый выстрел
        while True:
            print("Ваша доска")
            self.user_board.show()
            print("Доска врага")
            self.ai_board.show()
            while self.user.move():
                if self.ai_board.live_ships == 0:
                    break
                pass
            if self.ai_board.live_ships == 0:
                print("Игрок победил!")
                break
            while self.ai.move():
                pass
            if self.user_board.live_ships == 0:
                print("Противник победил!")
                break

    def start(self):
        self.greet()
        self.loop()


game = Game()
game.start()
