import pygame
import sys
import os

# Määrittele värejä
BLUE = (25, 25, 200)
BLACK = (23, 23, 23)
WHITE = (254, 254, 254)

worldx = 1260
worldy = 640
fps = 50
ani = 2
steps = 10

# Alusta pygame
pygame.init()
clock = pygame.time.Clock()
world = pygame.display.set_mode([worldx, worldy])

# Äänentoisto
pygame.mixer.init()
pygame.mixer.music.load("sounds/theme.ogg")
pygame.mixer.music.play(-1)  # Toista musiikkia jatkuvasti
shoot_sound = pygame.mixer.Sound("sounds/shotgun.mp3")
shoot_sound.set_volume(0.3)

# Lataa taustakuva ja skaalaa se
original_backdrop = pygame.image.load("images/stage.jpg")
backdrop = pygame.transform.scale(original_backdrop, (worldx, worldy))
backdropbox = world.get_rect()
backdrop_x = 0


class Player(pygame.sprite.Sprite):
    def __init__(self, imagename, moveslist, jumpkey, shootkey, folder, num_frames):
        pygame.sprite.Sprite.__init__(self)
        self.movex = 0
        self.movey = 0

        self.frame = 0
        self.jump_height = -300  # Hyppykorkeus

        self.num_frames = num_frames
        self.images = [
            pygame.transform.scale(
                pygame.image.load(
                    os.path.join(f"images/{folder}", f"run{i}.png")
                ).convert_alpha(),
                (int(2 * 64), int(2 * 64)),
            )
            for i in range(1, num_frames + 1)
        ]

        self.image = self.images[0]  # Aseta kuva `self.image`-attribuuttiin
        self.rect = self.image.get_rect()  # Aseta `self.rect` hitboxin koon mukaiseksi

        self.hitbox = self.rect.copy()  # Luo pelaajan hitbox
        self.hitbox.width = 50  # Aseta hitboxin leveys
        self.hitbox.height = 100  # Aseta hitboxin korkeus

        self.moveslist = moveslist
        self.jumpkey = jumpkey
        self.shootkey = shootkey
        self.shoot_delay = 1000
        self.last_shot = 0
        self.fall_speed = 5
        self.jump_height = -300
        self.jump_speed = 5
        self.jump_acceleration = 10
        self.bullet_list = pygame.sprite.Group()
        self.on_ground = False
        self.jumping = False
        self.pelaaja2_osumat = 0

    def move_player1(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.jumpkey:
                if self.on_ground or self.jumping:
                    self.jump()
            if event.key == self.shootkey:
                self.shoot()

    def move_player2(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.moveslist[0]:  # Liiku vasemmalle
                self.control(-steps, self.movey)
            elif event.key == self.moveslist[1]:  # Liiku oikealle
                self.control(steps, self.movey)
            if event.key == self.jumpkey and self.on_ground:
                self.jump()
        elif event.type == pygame.KEYUP:
            if event.key == self.moveslist[0] or event.key == self.moveslist[1]:
                self.control(0, self.movey)

    def control(self, x, y):
        self.movex = x
        self.movey = y

    def update(self):
        self.rect.x += self.movex
        self.rect.y += self.movey
        self.movey += self.fall_speed

        if self.rect.y >= worldy - 200:
            self.on_ground = True
            self.rect.y = worldy - 200

        if not self.on_ground and self.movey > 0:
            self.on_ground = True

        self.frame += 1
        if self.frame >= self.num_frames * ani:
            self.frame = 0
        self.image = self.images[self.frame // ani]

        self.bullet_list.update()
        for bullet in self.bullet_list:
            if bullet.rect.left > worldx:
                bullet.kill()

    def jump(self):
        if self.on_ground:
            self.movey = self.jump_height
            self.on_ground = False
            self.jumping = True
        else:
            self.movey += self.jump_acceleration

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.right, self.rect.centery)
            self.bullet_list.add(bullet)
            if shoot_sound:
                shoot_sound.play()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        original_bullet_image = pygame.image.load(
            "images/player1/bullet.png"
        ).convert_alpha()
        self.image = pygame.transform.scale(original_bullet_image, (30, 25))
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.centery = y
        self.speedx = 4  # Luodin nopeus

    def update(self):
        self.rect.x += self.speedx
        if self.rect.left > worldx - 100:
            self.kill()

        # Tarkista osuma x- ja y-akselilla
        hits = pygame.sprite.spritecollide(self, player2_group, False)
        for player in hits:
            if (
                self.rect.right >= player.rect.left
                and self.rect.left <= player.rect.right
                and self.rect.centery >= player.rect.top
                and self.rect.centery <= player.rect.bottom
            ):
                print("Luoti osui pelaajaan 2!")
                self.kill()
                break


player1_moves = [pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_SPACE]
player2_moves = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP]

player1 = Player("Farmer", player1_moves, pygame.K_w, pygame.K_SPACE, "player1", 6)
player2 = Player("AppleThief", player2_moves, pygame.K_UP, pygame.K_RCTRL, "player2", 4)
player2_group = pygame.sprite.Group()
player2_group.add(player2)

player1.rect.x = 100
player1.rect.y = worldy - 200

player2.rect.x = 800
player2.rect.y = worldy - 200

player_list = pygame.sprite.Group()
player_list.add(player1, player2)

main = True
while main:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            main = False

        player1.move_player1(event)
        player2.move_player2(event)

    backdrop_x -= steps
    if backdrop_x < -backdrop.get_width():
        backdrop_x = 0

    for player in player_list:
        if player.rect.top < worldy - 200:
            player.rect.top = worldy - 200

    hits = pygame.sprite.groupcollide(player_list, player2.bullet_list, False, True)
    for player, bullets in hits.items():
        if player != player2:
            print("Pelaaja osui pelaajaan 2")
        else:
            print("Pelaaja 2 on osunut!")
            player2.pelaaja2_osumat += 1
        if player2.pelaaja2_osumat >= 3:
            print(
                f"Pelaaja 2 on saanut {player2.pelaaja2_osumat} osumaa. Peli päättyy."
            )
            print("Paina välilyöntiä (space) aloittaaksesi uudelleen.")
            main = False

    world.blit(backdrop, (backdrop_x, 0))
    world.blit(backdrop, (backdrop_x + backdrop.get_width(), 0))

    player_list.update()
    player1.bullet_list.update()
    player2.bullet_list.update()

    player_list.draw(world)
    player1.bullet_list.draw(world)
    player2.bullet_list.draw(world)

    pygame.display.flip()
    clock.tick(fps)

pygame.mixer.music.stop()

restart = False
while not restart:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            restart = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            restart = True

pygame.quit()
sys.exit()
