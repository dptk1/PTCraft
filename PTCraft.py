import os
import pygame
import random

# инициализация pygame
pygame.init()
pygame.display.set_caption('PTCraft')

pygame.mixer.music.load('data/music.mp3')
pygame.mixer.music.play()

# создание экрана
size = width, height = 1080, 720
screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()


# загрузка изображения
def load_image(name):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    image.set_colorkey((0, 0, 0))
    image = image.convert_alpha()
    return image


# класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.x = x
        self.y = y

        self.v = -1

        self.r_of_break = 240

        self.image_right = load_image("steve1.png")
        self.image_left = pygame.transform.flip(self.image_right, 1, 0)

        self.image = self.image_right
        self.rect = self.image_right.get_rect()

        self.rect = self.rect.move(self.x, self.y)

    def update_image(self, args):
        if args == 1:
            self.image = self.image_right
        else:
            self.image = self.image_left


# класс мира
class World:
    def __init__(self, width, height, start_dirt_h, max_dirt_h, min_dirt_h):
        self.blocks = pygame.sprite.Group()
        self.air = pygame.sprite.Group()

        self.width = width
        self.height = height

        self.world_center = width // 2

        self.h = start_dirt_h
        self.max_dirt_h = max_dirt_h
        self.min_dirt_h = min_dirt_h

    def generate(self):  # генерация мира
        for i in range(self.width):
            self.update_h()
            dirt_level = random.randint(2, 3)
            for j in range(self.height):

                if i == 0 or j == 0 or j + 1 == self.height or i + 1 == self.width:
                    self.blocks.add(Border(i * 60 - self.world_center * 60, (self.height - j - 1) * 60))

                elif self.h > self.height - j - 1:
                    self.air.add(Air(i * 60 - self.world_center * 60, (self.height - j - 1) * 60))

                elif self.h == self.height - j - 1:
                    self.blocks.add(Grass(i * 60 - self.world_center * 60, (self.height - j - 1) * 60))

                elif self.h + dirt_level > self.height - j - 1:
                    self.blocks.add(Dirt(i * 60 - self.world_center * 60, (self.height - j - 1) * 60))

                else:
                    self.blocks.add(Stone(i * 60 - self.world_center * 60, (self.height - j - 1) * 60))

    def update_h(self):  # обновление высоты земли
        if self.h == self.max_dirt_h:
            delta_h = random.randint(-1, 0)
        elif self.h == self.min_dirt_h:
            delta_h = random.randint(0, 1)
        else:
            delta_h = random.randint(-1, 1)

        self.h += delta_h


# класс блоков
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.breakable = True

        self.x = x
        self.y = y

    def can_be_reached_by_player(self, player_x, player_y):
        pass

    def update(self, arg):
        self.rect = self.rect.move(-arg[0], -arg[1])


# класс блока земли
class Grass(Block):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.image = load_image("grass.png")

        self.rect = self.image.get_rect()

        self.rect = self.rect.move(self.x, self.y)


# класс блока камня
class Stone(Block):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.image = load_image("stone.png")

        self.rect = self.image.get_rect()

        self.rect = self.rect.move(self.x, self.y)


# класс блока грязи
class Dirt(Block):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.image = load_image("dirt.png")

        self.rect = self.image.get_rect()

        self.rect = self.rect.move(self.x, self.y)


# класс блока воздуха
class Air(Block):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.image = load_image("air.png")

        self.rect = self.image.get_rect()

        self.rect = self.rect.move(self.x, self.y)


# класс блока больера
class Border(Block):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.image = load_image("border.png")

        self.breakable = False

        self.rect = self.image.get_rect()

        self.rect = self.rect.move(self.x, self.y)


# создание мира
world = World(40, 40, 20, 30, 10)
world.generate()

# словарь блоков которые можно поставить
blocks_d = {0: Grass, 1: Dirt, 2: Stone}

# выбранный игроком блок
selected_block = Grass

# генерация мира и создание групп спрайтов
blocks = world.blocks
air = world.air

blocks_bar = pygame.sprite.Group()
blocks_bar.add(Grass(5, 180))
blocks_bar.add(Dirt(5, 245))
blocks_bar.add(Stone(5, 310))

stroke = 1

# создание персонажа
player = Player(540, 360)
blocks.update((0, 200))
air.update((0, 200))

# создание спрайта игрока
player_sprite = pygame.sprite.Group()
player_sprite.add(player)

# переменная отвечающая за игровой цикл
running = True

# переменные отвечающие за движение персонажа
right = False
left = False
can_jump = False

# переменные для выполнения прыжка
jump_range = 20

# игровой цикл
while running:
    # обработка эвентов
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # реакция на нажатие клавиш
        print(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            # обработка ломания блока
            for block in blocks:
                if event.pos[0] - 60 < block.rect.x < event.pos[0] and \
                        event.pos[1] - 60 < block.rect.y < event.pos[1]:
                    if block.breakable:
                        if ((block.rect.x - 540) ** 2 + (block.rect.y - 360) ** 2) ** 0.5 <= player.r_of_break:
                            air.add(Air(block.rect.x, block.rect.y))
                            block.kill()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            for block_of_air in air:
                if event.pos[0] - 60 < block_of_air.rect.x < event.pos[0] and \
                        event.pos[1] - 60 < block_of_air.rect.y < event.pos[1]:
                        if ((block_of_air.rect.x - 540) ** 2 + (block_of_air.rect.y - 360) ** 2) ** 0.5 <= player.r_of_break:
                            blocks.add(selected_block(block_of_air.rect.x, block_of_air.rect.y))
                            block_of_air.kill()

        # обработка выбора блока
        if event.type == pygame.KEYDOWN and event.key == 49:
            selected_block = blocks_d[0]
            stroke = 1

        if event.type == pygame.KEYDOWN and event.key == 50:
            selected_block = blocks_d[1]
            stroke = 2

        if event.type == pygame.KEYDOWN and event.key == 51:
            selected_block = blocks_d[2]
            stroke = 3

        # обработка нажатия стрелки навлево
        if event.type == pygame.KEYDOWN and event.key == 275 and not left:
            player.update_image(1)
            right = True

        if event.type == pygame.KEYUP and event.key == 275:
            right = False

        # обработка нажатия стрелки направо
        if event.type == pygame.KEYDOWN and event.key == 276 and not right:
            player.update_image(0)
            left = True

        if event.type == pygame.KEYUP and event.key == 276:
            left = False

        # обработка нажатия стрелки наверх
        if event.type == pygame.KEYDOWN and event.key == 32 and \
                (pygame.sprite.spritecollideany(player, blocks) or can_jump) and jump_range <= 0:
            can_jump = False
            jump_range = 20
            player.v = 20

    # физика игрока
    if not pygame.sprite.spritecollideany(player, blocks):
        player.v -= 1
        blocks.update((0, -player.v))
        air.update((0, -player.v))
        if pygame.sprite.spritecollideany(player, blocks):
            if player.v < 0:
                can_jump = True
            blocks.update((0, player.v))
            air.update((0, player.v))
            player.v = 0

    # движение вправо
    if right:
        blocks.update((3, 0))
        air.update((3, 0))
        if pygame.sprite.spritecollideany(player, blocks):
            blocks.update((-3, 0))
            air.update((-3, 0))

    # движение влево
    if left:
        blocks.update((-3, 0))
        air.update((-3, 0))
        if pygame.sprite.spritecollideany(player, blocks):
            blocks.update((3, 0))
            air.update((3, 0))

    # сокращение задержки прыжка
    jump_range -= 1

    # прорисовка блоков и игрока
    blocks.draw(screen)
    air.draw(screen)
    blocks_bar.draw(screen)
    player_sprite.draw(screen)

    pygame.draw.rect(screen, (0, 0, 0), (5, 180, 60, 60), 3)
    pygame.draw.rect(screen, (0, 0, 0), (5, 245, 60, 60), 3)
    pygame.draw.rect(screen, (0, 0, 0), (5, 310, 60, 60), 3)
    if stroke == 1:
        pygame.draw.rect(screen, (255, 255, 255), (5, 180, 60, 60), 3)
    if stroke == 2:
        pygame.draw.rect(screen, (255, 255, 255), (5, 245, 60, 60), 3)
    if stroke == 3:
        pygame.draw.rect(screen, (255, 255, 255), (5, 310, 60, 60), 3)

    pygame.display.flip()

    # задержка в 17 мс
    clock.tick(60)

    # заполнение экрана синим цветом
    screen.fill((0, 0, 255))
