# SWARM 2.0
print('Importing Dependencies')
import sys
import pygame
import os
from pygame.locals import *
import math
from random import *
import pkgutil
import time
from importlib.resources import files

print('Setting Constants')
# Constants
screenSize = screenWidth, screenHeight = 640, 480

black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
aqua = (0, 255, 255)
teal = (0, 128, 128)
screen = None
hiveList = None
flowerList = None

print('Creating Classes')
ROOT_PATH = files("images")

class Hive:
    def __init__(self):
        self.x = math.trunc(screenWidth / 2)
        self.y = math.trunc(screenHeight / 2)
        self.foodStore = 20
        self.beeList = []
        img_path = os.path.join(ROOT_PATH, 'hive.png')
        self.image = pygame.transform.scale2x(pygame.image.load(img_path).convert_alpha())
        self.imagerect = self.image.get_rect()
        self.imagerect.centerx, self.imagerect.centery = self.x, self.y

    def update(self):
        screen.blit(self.image, self.imagerect)
        for kBee in self.beeList:
            kBee.update()

    def makeBee(self):
        self.beeList.append(Bee(self))


class Flower:
    def __init__(self):
        self.x = randint(20, screenWidth - 20)
        self.y = randint(20, screenHeight - 20)
        self.foodStore = 10
        self.colorcycle = self.foodStore * 10
        self.colorCounter = 0
        self.color = red
        img_path = os.path.join(ROOT_PATH, 'flower.png')
        self.image = pygame.image.load(img_path).convert_alpha()
        self.imagerect = self.image.get_rect()
        self.imagerect.centerx, self.imagerect.centery = self.x, self.y

        # Flower Scent Box
        self.senseBox = pygame.Rect((self.x - 1), (self.y - 1), 3, 3)
        self.senseBox.inflate_ip(15, 15)

    def update(self):
        # self.setColor()
        # pygame.draw.circle(screen,self.color,(self.x,self.y),5,4)
        # pygame.draw.rect(screen,self.color,self.senseBox,1)
        screen.blit(self.image, self.imagerect)

    def setColor(self):
        if self.colorCounter > self.foodStore * 10:
            self.color = white
        else:
            self.color = red

        if self.colorCounter == self.colorcycle:
            self.colorCounter = 0
        else:
            self.colorCounter += 1


class Scent:
    def __init__(self, x, y, strength, decay):
        self.x = x
        self.y = y
        self.strength = strength
        self.decay = decay
        self.tUpdate = time.time()
        self.vx = 0
        self.vy = 0

    def decay(self):
        timeElapsed = time.time() - self.tUpdate
        self.strength = (self.strength) * (.5) ^ (timeElapsed / self.decay)

    def move(self):
        timeElapsed = time.time() - self.tUpdate
        self.x = self.x + self.vx * timeElapsed
        self.y = self.y + self.vy * timeElapsed

    def update(self):
        self.decay()
        # self.move()


class Bee:
    def __init__(self, hive):

        # Home
        self.hive = hive

        # Starting Position
        self.x = float(randint(-30, 30) + hive.x)
        self.y = float(randint(-30, 30) + hive.y)
        img_path = os.path.join(ROOT_PATH, 'bee.png')
        self.image = pygame.image.load(img_path).convert_alpha()
        self.imagerect = self.image.get_rect()
        self.imagerect.centerx, self.imagerect.centery = self.x, self.y
        self.direction = 1

        # Speed info
        self.speedx = 0
        self.speedy = 0
        self.speedTargetMag = 1

        # Time of creation
        self.tUpdate = time.time()
        self.tTarget = time.time()

        # Box for testing collisions
        self.senseThresh = 15
        self.senseBox = pygame.Rect((self.x - .5 * self.senseThresh), (self.y - .5 * self.senseThresh),
                                    2 * self.senseThresh, 2 * self.senseThresh)

        self.tThresh = 2
        self.wanderTThresh = 30
        self.cargo = 0
        self.color = green
        self.target = []
        self.discovery = []

        self.map = beeMap(hive)

        self.update()

    def update(self):

        buddyBee = self.sense(self.hive.beeList, 1)

        if buddyBee != [] and self.map.places['flower'] != [] and self.map.places['flower'].foodStore != 1:
            for bee in buddyBee:
                if bee.map.places['flower'] == []:
                    print("HEY FRIEND!")
                    bee.map.addFlower(self.map.places['flower'])
                    bee.target = self.map.places['flower']

        if self.target == []:
            self.target = self.sense(flowerList)

            if self.target == []:
                self.wander()
            else:

                self.move()
                self.map.addFlower(self.target)

        elif isinstance(self.target, Hive):
            if (abs(self.x - self.target.x) < self.senseThresh) and (abs(self.y - self.target.y) < self.senseThresh):
                self.dropOff()
            else:
                self.move()

        elif isinstance(self.target, Flower):
            if (abs(self.x - self.target.x) < 1) and (abs(self.y - self.target.y) < 1):
                self.map.addFlower(self.target)
                self.harvest()
            else:
                self.move()
        else:
            self.move()

        if self.speedx < 0 and self.direction == 1:
            self.image = pygame.transform.flip(self.image, True, False)
            self.direction = -1

        if self.speedx > 0 and self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)
            self.direction = 1

        self.imagerect.centerx, self.imagerect.centery = self.x, self.y
        screen.blit(self.image, self.imagerect)
        # pygame.draw.circle(screen,self.color,(math.trunc(self.x),math.trunc(self.y)),3,1)
        # pygame.draw.rect(screen,self.color,self.senseBox,1)

    def wander(self):
        if (globalTime - self.tTarget) > self.wanderTThresh:
            self.target = self.hive
            return

        if (globalTime - self.tUpdate) > self.tThresh:
            self.speedx = gauss(0, .3)
            self.speedy = gauss(0, .3)
            self.tThresh = randint(1, 5)
            self.tUpdate = time.time()

        if (self.x + self.speedx) >= screenWidth:
            self.speedx = -self.speedx
        elif (self.x + self.speedx) <= 0:
            self.speedx = -self.speedx

        if (self.y + self.speedy) >= screenHeight:
            self.speedy = -self.speedy
        elif (self.y + self.speedy) <= 0:
            self.speedy = -self.speedy

        self.x += self.speedx
        self.y += self.speedy

        # Update sense box
        self.senseBox.centerx = self.x
        self.senseBox.centery = self.y

    def move(self):
        if self.target == []:
            self.wander()
            return

        distx = self.target.x - self.x
        disty = self.target.y - self.y
        dist = math.hypot(distx, disty)
        vectx = distx / dist
        vecty = disty / dist

        self.speedx = self.speedTargetMag * vectx
        self.speedy = self.speedTargetMag * vecty

        self.x += self.speedTargetMag * vectx
        self.y += self.speedTargetMag * vecty

        # Update sense box
        self.senseBox.centerx = self.x
        self.senseBox.centery = self.y

        self.tTarget = time.time()

    def sense(self, targetList, returnAll=0):

        itemsSensed = []
        sensed = self.senseBox.collidelistall([x.senseBox for x in targetList])
        if returnAll == 0 and sensed != []:
            itemsSensed = targetList[sensed[0]]
        else:
            itemsSensed = [targetList[x] for x in sensed]

        return itemsSensed

    def harvest(self):

        if flowerList.count(self.target) == 0:
            self.target = []
            self.wander()

        else:
            img_path = os.path.join(ROOT_PATH, 'beewFood.png')
            self.image = pygame.image.load(img_path).convert_alpha()
            self.imagerect = self.image.get_rect()
            self.imagerect.centerx, self.imagerect.centery = self.x, self.y
            if self.direction == -1:
                self.image = pygame.transform.flip(self.image, True, False)

            self.target.foodStore -= 1
            self.cargo += 1
            self.color = aqua

            if self.target.foodStore == 0:
                flowerList.remove(self.target)

            self.target = self.hive

    def dropOff(self):
        if self.cargo == 0:
            self.target = []
            self.wander()
            return
        img_path = os.path.join(ROOT_PATH, 'bee.png')
        self.image = pygame.image.load(img_path).convert_alpha()
        self.imagerect = self.image.get_rect()
        self.imagerect.centerx, self.imagerect.centery = self.x, self.y
        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)

        self.hive.foodStore += self.cargo
        self.cargo = 0
        self.color = green

        if self.map.places['flower'] != []:
            self.target = self.map.places['flower']
        else:
            self.target = []
            self.wander()

        # print ("Hive food Store: " + str(self.hive.foodStore))


class beeMap:

    def __init__(self, hive):
        self.places = {'hivePosition': [hive.x, hive.y]}
        self.places['flower'] = []

    def addFlower(self, flower):
        self.places['flower'] = flower


# print 'Initiating Classes'


# Initialize Everything
def main():
    global screen, hiveList, flowerList, globalTime
    pygame.init()
    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption('BEEZ!')
    img_path = os.path.join(ROOT_PATH, 'field.png')
    background = pygame.image.load(img_path).convert_alpha()

    hiveList = []
    numHives = 1
    for kHive in range(numHives):
        hiveList.append(Hive())

    flowerList = []
    numFlowers = 20
    for kFlower in range(numFlowers):
        flowerList.append(Flower())

    beeLimit = 2

    # Main Game Loop
    while True:

        # Set FPS
        pygame.time.delay(20)

        # Clear screen
        # screen.fill(aqua)
        screen.blit(background, (0, 0))

        # GlobalTime
        globalTime = time.time()

        if len(flowerList) < 10:
            for x in range(11):
                flowerList.append(Flower())

        # Draw Shit
        for kHive in hiveList:
            kHive.update()

        for kFlower in flowerList:
            kFlower.update()

        if len(hiveList[0].beeList) < beeLimit:
            hiveList[0].makeBee()

        # Event Handling
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:

                if event.key == K_b:
                    hiveList[0].makeBee()
                if event.key == K_f:
                    flowerList.append(Flower())

                if event.key == K_ESCAPE:
                    pygame.event.post(pygame.event.Event(QUIT))

            if event.type == MOUSEBUTTONUP:
                if event.button == 3:
                    mousex, mousey = event.pos
                    for dbee in hiveList[0].beeList:
                        deadBee = dbee.senseBox.collidepoint(mousex, mousey)
                        print('deadBee')
                        if deadBee:
                            hiveList[0].beeList.remove(dbee)

        pygame.display.update()

    # Need this  to exit smoothly
    pygame.quit()


if __name__ == '__main__':
    main()
