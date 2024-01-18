import os
import sys
import math
import random

import pygame

pygame.init()
size = width, height = 1920, 1080
screen = pygame.display.set_mode(size)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует
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
        self.rect.x = 0
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
            # после получения удара получает период неуязвимости
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
    fps = 120
    clock = pygame.time.Clock()
    RECOVER_AFTER_HIT = pygame.USEREVENT + 1
    RELOAD = pygame.USEREVENT + 2
    STRIDER_SPAWN = pygame.USEREVENT + 3
    pygame.time.set_timer(STRIDER_SPAWN, 5000)

    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    cursor = Cursor(all_sprites)
    character = Character(all_sprites)
    healthbar = Healthbar(all_sprites)
    scorelbl = Scorelabel(all_sprites)
    Creature(1500, 900, all_sprites, enemies)

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
    pygame.quit()
