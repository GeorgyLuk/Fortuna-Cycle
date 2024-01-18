import os
import sys
import math
import random

import pygame

pygame.init()
size = width, height = 1920, 1080
screen = pygame.display.set_mode(size)
fps = 120


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["Fortuna Cycle", "",
                  "Управление",
                  "Передвигайтесь на W, A, S, D",
                  "Стреляйте на ЛКМ",
                  "Выход - Esc",
                  "Нажмите любую кнопку, чтобы начать"]

    fon = load_image('start_bg.jpeg')
    screen.blit(fon, (0, 0))
    font = pygame.font.SysFont('Arial', 36)
    text_coord = 100
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 1000
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(fps)


def game_over(time):
    end_text = ["Игра окончена", "",
                f"Набранные очки:{scorelbl.score}",
                f"Секунд прожито: {time}",
                "Нажмите Esc"]

    fon = pygame.Surface((500, 600))
    fon.fill((10, 10, 10))
    screen.blit(fon, (1000, 200))
    font = pygame.font.SysFont('Arial', 36)
    text_coord = 250
    for line in end_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 1010
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                # Используем только Esc, чтобы предотвратить случайное нажатие
                if event.key == pygame.K_ESCAPE:
                    return  # завершаем сессию
        pygame.display.flip()
        clock.tick(fps)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существуетw
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Cursor(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        # определим его вид
        self.image = load_image('cursor.png')
        # размеры
        self.rect = self.image.get_rect()
        self.rect.x = 5
        self.rect.y = 20

    def follow(self, eve):
        self.rect.x, self.rect.y = eve.pos


class Character(pygame.sprite.Sprite):
    # отвечает за персонажа под управлением игрока
    def __init__(self, *group):
        super().__init__(*group)
        # вид
        self.image = load_image('cycle_character.png')
        # размеры
        self.rect = self.image.get_rect()
        self.rect.x = 900
        self.rect.y = 0
        # характеристики
        self.vx = self.vy = 5
        self.vd = 4
        self.hp = 100
        self.invinsible = False
        self.reloaded = True

    def move(self, vx, vy):
        self.rect = self.rect.move(vx, vy)

    def update(self):
        hits = pygame.sprite.spritecollide(self, enemies, False)
        if hits and not self.invinsible:
            self.hp = self.hp - len(hits) * 20
            # после получения удара получает период неуязвимости и запускает таймер события, снимающего неуязвимость
            self.invinsible = True
            pygame.time.set_timer(RECOVER_AFTER_HIT, 500, True)

        if self.hp <= 0:
            self.kill()
            global running
            running = False

    def shoot(self, target):
        dx = target[0] - self.rect.x
        dy = target[1] - self.rect.y
        if dx == 0 and dy == 0:
            return
        else:
            if self.reloaded:
                hypot = math.hypot(dx, dy)
                cos = dx / hypot
                sin = dy / hypot
                Bullet(self.rect.x + 10, self.rect.y + 20, cos, sin, all_sprites, bullets)
                self.reloaded = False
                pygame.time.set_timer(RELOAD, 200, True)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, cos, sin, *group):
        super().__init__(*group)
        # вид
        image = load_image('bullet.png')
        angle_r = math.atan2(sin, cos)
        angle = math.degrees(angle_r)
        self.image = pygame.transform.rotate(image, -angle)
        # размеры
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.ms = 20  # Скорость движения в пикселях за кадр в любом направлении
        self.vx = self.ms * cos
        self.vy = self.ms * sin

    def update(self):
        self.rect = self.rect.move(self.vx, self.vy)


class Creature(pygame.sprite.Sprite):
    def __init__(self, x, y, *group):
        super().__init__(*group)
        # вид
        self.image = load_image('strider_front.png')
        # размеры
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.ms = 4
        self.vx = self.vy = 0
        self.hp = 50

    def update(self):
        dx = character.rect.x - self.rect.x
        dy = character.rect.y - self.rect.y
        if dx == 0 and dy == 0:
            self.vx = self.vy = 0
        else:
            hypot = math.hypot(dx, dy)
            cos = dx / hypot
            sin = dy / hypot
            self.vx = self.ms * cos
            self.vy = self.ms * sin
            angle = math.degrees(math.atan2(sin, cos))
            if -45 < angle < 45:
                self.image = load_image('strider_right.png')
            elif 45 < angle < 135 or -135 < angle < -45:
                self.image = load_image('strider_front.png')
            else:
                self.image = load_image('strider_left.png')

        self.move(self.vx, self.vy)

        shots = pygame.sprite.spritecollide(self, bullets, True)
        if shots:
            self.hp = self.hp - len(shots) * 20
        if self.hp <= 0:
            scorelbl.score += 10
            self.kill()

    def move(self, vx, vy):
        self.rect = self.rect.move(vx, vy)


class Item(pygame.sprite.Sprite):
    # отвечает за подбираемые предметы
    def __init__(self, x, y, *group):
        super().__init__(*group)
        # вид
        self.image = load_image('Strider_Head.png')
        # размеры
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Healthbar(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        # вид
        self.width, self.height = 500, 30
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((50, 50, 50))
        pygame.draw.rect(self.image, pygame.Color(90, 249, 208), (0, 0, self.width, self.height))
        pygame.draw.rect(self.image, pygame.Color('white'), (0, 0, self.width, self.height), 1)
        # размеры
        self.rect = self.image.get_rect()
        self.rect.x = 710
        self.rect.y = 1050

    def update(self):
        redline = character.hp * 5
        self.image.fill((50, 50, 50))
        pygame.draw.rect(self.image, pygame.Color(90, 249, 208), (0, 0, redline, self.height))
        pygame.draw.rect(self.image, pygame.Color('white'), (0, 0, self.width, self.height), 1)


class Scorelabel(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        # вид
        self.width, self.height = 100, 50
        self.font = pygame.font.SysFont('arial', 36)
        self.score = 0
        self.image = self.font.render(str(self.score), 1, pygame.Color('black'))

        # размеры
        self.rect = self.image.get_rect()
        self.rect.x = 1820
        self.rect.y = 0

    def update(self):
        self.image = self.font.render(str(self.score), 1, pygame.Color('black'))


if __name__ == '__main__':
    pygame.display.set_caption('Fortuna Cycle')

    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    RECOVER_AFTER_HIT = pygame.USEREVENT + 1
    RELOAD = pygame.USEREVENT + 2
    STRIDER_SPAWN = pygame.USEREVENT + 3
    start_screen()
    start_clock = pygame.time.Clock()
    pygame.time.set_timer(STRIDER_SPAWN, 5000)

    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    character = Character(all_sprites)
    healthbar = Healthbar(all_sprites)
    scorelbl = Scorelabel(all_sprites)
    Creature(1500, 900, all_sprites, enemies)
    cursor = Cursor(all_sprites)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                character.shoot(event.pos)
            if event.type == pygame.MOUSEMOTION:
                cursor.follow(event)
            if event.type == RECOVER_AFTER_HIT:
                character.invinsible = False
            if event.type == RELOAD:
                character.reloaded = True
            if event.type == STRIDER_SPAWN:
                amount = pygame.time.get_ticks()//10010 + 1
                for _ in range(amount):
                    Creature(random.randint(10, 1800), 1000, all_sprites, enemies)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            if keys[pygame.K_w]:
                character.move(-character.vd, -character.vd)
            elif keys[pygame.K_s]:
                character.move(-character.vd, character.vd)
            else:
                character.move(-character.vx, 0)
        elif keys[pygame.K_d]:
            if keys[pygame.K_w]:
                character.move(character.vd, -character.vd)
            elif keys[pygame.K_s]:
                character.move(character.vd, character.vd)
            else:
                character.move(character.vx, 0)
        elif keys[pygame.K_w]:
            character.move(0, -character.vy)
        elif keys[pygame.K_s]:
            character.move(0, character.vy)
        all_sprites.update()

        # отрисовка
        screen.fill(pygame.Color('#f4ca16'))
        all_sprites.draw(screen)
        if pygame.mouse.get_focused():
            pygame.mouse.set_visible(False)
        else:
            pygame.mouse.set_visible(True)

        # завершение
        pygame.display.flip()
        clock.tick(fps)
    game_over(start_clock.tick() // 1000)
    pygame.quit()
