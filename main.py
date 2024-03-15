from pygame import *
from random import randint
import json


#фоновая музыка
mixer.init()
mixer.music.load('pap_rouch.ogg')
mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')
fire_sound.set_volume(0.1)
shot = mixer.Sound('fire_shot.ogg')
shot.set_volume(0.1)
#шрифты и надписи
font.init()
font1 = font.SysFont(None, 80)
win = font1.render('YOU WIN!', True, (255, 255, 255))
lose = font1.render('YOU LOSE!', True, (180, 0, 0))
font2 = font.SysFont(None, 36)
#нам нужны такие картинки:
img_back = "galaxy.jpg" #фон игры
img_hero = "rocket.png" #герой
img_bullet = "bullet.png" #пуля
img_enemy = "ufo.png" #враг

health = 9
score = 0 #сбито кораблей
lost = 0 #пропущено кораблей
max_lost = 3 #проиграли, если пропустили столько


#класс-родитель для других спрайтов
class GameSprite(sprite.Sprite):
 #конструктор класса
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        #вызываем конструктор класса (Sprite):
        sprite.Sprite.__init__(self)

        #каждый спрайт должен хранить свойство image - изображение
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed

        #каждый спрайт должен хранить свойство rect - прямоугольник, в который он вписан
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

 #метод, отрисовывающий героя на окне
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

#класс главного игрока
class Rocket(GameSprite):
   #метод для управления спрайтом стрелками клавиатуры
    def update(self):
        keys = key.get_pressed()
        if keys[K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_d] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
 #метод "выстрел" (используем место игрока, чтобы создать там пулю)
    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)

#класс спрайта-врага  
class Enemy(GameSprite):
   #движение врага
    def update(self):
        self.rect.y += self.speed
        global lost
       #исчезает, если дойдет до края экрана
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost = lost + 1
#класс спрайта-пули  
class Bullet(GameSprite):
   #движение врага
    def update(self):
        self.rect.y += self.speed
       #исчезает, если дойдет до края экрана
        if self.rect.y < 0:
            self.kill()

#создаем окошко
win_width = 700
win_height = 500
display.set_caption("Shooter")
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load(img_back), (win_width, win_height))


#создаем спрайты
ship = Rocket(img_hero, 250, win_height - 100, 80, 100, 20)

monsters = sprite.Group()
for i in range(1, 6):
    monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(4, 5))
    monsters.add(monster)

bullets = sprite.Group()

#переменная "игра закончилась": как только там True, в основном цикле перестают работать спрайты
finish = False
#основной цикл игры:
try:
    with open('high_score.json', 'r') as file:
        high_score = json.load(file)
except FileNotFoundError:
    high_score = 0

run = True #флаг сбрасывается кнопкой закрытия окна
while run:
    #событие нажатия на кнопку Закрыть
    for e in event.get():
        if e.type == QUIT:
            run = False
        #событие нажатия на пробел - спрайт стреляет
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                fire_sound.play()
                ship.fire()
        if e.type == MOUSEBUTTONDOWN:
                # Если было сделано нажатие мыши
                # Сбросим все переменные и перезапустим игру
                finish = False
                health = 9
                score = 0
                lost = 0
                ship.rect.x = 250
                ship.rect.y = win_height - 100
                monsters.empty()
                bullets.empty()

                # Создаем новых врагов
                for i in range(1, 6):
                    monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(4, 5))
                    monsters.add(monster)

    if not finish:
        #обновляем фон
        window.blit(background,(0,0))

        #производим движения спрайтов   
        ship.update()
        monsters.update()
        bullets.update()

        #условия поражения

        #условия победы
        if sprite.groupcollide(monsters, bullets, True, True):
            shot.play()
            score += 1
            speed = score
            if score >= 50:
                speed = 50
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50,  randint(int(4 + (speed*0.1)), int(5 + (speed*0.1))))
            monsters.add(monster)
        if len(monsters) < 5:  # Если врагов меньше 5, добавить нового
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(int(4 + (speed*0.1)), int(5 + (speed*0.1))))
            monsters.add(monster)
        if score > high_score:
            high_score = score
        with open('high_score.json', 'w') as file:
            json.dump(high_score, file)

        window.blit(font2.render("Рекорд: " + str(high_score), 1, (255, 255, 255)), (10, 80))

        health_text = font2.render("Здоровье: " + str(health), 1, (255, 255, 255))
        window.blit(health_text, (550, 20))
        if health == 0:
            finish == False
            run == False
        #пишем текст на экране
        text = font2.render("Счет: " + str(score), 1, (255, 255, 255))
        window.blit(text, (10, 20))

        text_lose = font2.render("Пропущено: " + str(lost), 1, (255, 255, 255))
        window.blit(text_lose, (10, 50))

        
        if sprite.spritecollide(ship, monsters, False):
            sprite.spritecollide(ship, monsters, True)
            health -= 3
            
        #обновляем их в новом местоположении при каждой итерации цикла
        ship.reset()
        monsters.draw(window)
        bullets.draw(window)

        display.update()
    #цикл срабатывает каждую 0.05 секунд
    time.delay(50)
    