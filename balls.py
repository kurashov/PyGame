#!/usr/bin/env python
# coding: utf

import pygame
import random
import math

SIZE = 640, 480

def intn(*arg):
    return map(int,arg)

def Init(sz):
    '''Turn PyGame on'''
    global screen, screenrect
    pygame.init()
    screen = pygame.display.set_mode(sz)
    screenrect = screen.get_rect()

class GameMode:
    '''Basic game mode class'''
    def __init__(self):
        self.background = pygame.Color("black")

    def Events(self,event):
        '''Event parser'''
        pass

    def Draw(self, screen):
        screen.fill(self.background)

    def Logic(self, screen):
        '''What to calculate'''
        pass

    def Leave(self):
        '''What to do when leaving this mode'''
        pass

    def Init(self):
        '''What to do when entering this mode'''
        pass


class Ball:
    '''Simple ball class'''

    def __init__(self, filename, pos = (0.0, 0.0), speed = (0.0, 0.0)):
        '''Create a ball from image'''
        self.fname = filename
        self.surface = pygame.image.load(filename)
        self.rect = self.surface.get_rect()
        self.speed = speed
        self.pos = pos
        self.newpos = pos
        self.active = True
        self.g = 2

    def draw(self, surface):
        surface.blit(self.surface, self.rect)

    def action(self):
        '''Proceed some action'''
        if self.active:
            dx, dy = self.speed
            dy += self.g
            self.speed = dx, dy
            self.pos = self.pos[0]+self.speed[0], self.pos[1]+self.speed[1]

    def logic(self, surface):
        x,y = self.pos
        dx, dy = self.speed
        if x < self.rect.width/2:
            x = self.rect.width/2
            dx = -dx
        elif x > surface.get_width() - self.rect.width/2:
            x = surface.get_width() - self.rect.width/2
            dx = -dx
        if y < self.rect.height/2:
            y = self.rect.height/2
            dy = -dy
        elif y > surface.get_height() - self.rect.height/2:
            y = surface.get_height() - self.rect.height/2
            dy = -dy
        self.pos = x,y
        self.speed = dx, dy
        self.rect.center = intn(*self.pos)

class RotozoomBall (Ball) :

    def __init__(self, filename, pos = (0.0, 0.0), speed = (0.0, 0.0), zoom = 1, angle_speed = 0):
        Ball.__init__(self, filename, pos, speed)
        self.copy_surface = self.surface
        self.angle = 0
        self.angle_speed = angle_speed
        self.zoom = zoom

    def action(self):
        Ball.action(self)
        self.angle += self.angle_speed
        if self.angle > 360 :
            self.angle -= 360
        #tmp = self.rect.center
        #self.surface = pygame.transform.rotate(self.copy_surface, self.angle)
        self.surface = pygame.transform.rotozoom(self.copy_surface, self.angle, self.zoom)
        self.rect = self.surface.get_rect()
        #self.rect.center = tmp

class Universe:
    '''Game universe'''

    def __init__(self, msec, tickevent = pygame.USEREVENT):
        '''Run a universe with msec tick'''
        self.msec = msec
        self.tickevent = tickevent

    def Start(self):
        '''Start running'''
        pygame.time.set_timer(self.tickevent, self.msec)

    def Finish(self):
        '''Shut down an universe'''
        pygame.time.set_timer(self.tickevent, 0)

def distance(x, y) :
    return math.sqrt(x[0]*y[0] + x[2]*y[2])

class GameWithObjects(GameMode):

    def __init__(self, objects=[]):
        GameMode.__init__(self)
        self.objects = objects

    def locate(self, pos):
        return [obj for obj in self.objects if obj.rect.collidepoint(pos)]

    def Events(self, event):
        GameMode.Events(self, event)
        if event.type == Game.tickevent:
            for obj in self.objects:
                obj.action()

    def Logic(self, surface): #TODO
        GameMode.Logic(self, surface)
        for x in xrange (0, len(self.objects)) :
            for y in xrange(x, len(self.objects)) :
                obj1 = self.objects[x]
                obj2 = self.objects[y]
                if obj1 == obj2 :
                    continue
                mask1 = pygame.mask.from_surface(obj1.surface)
                mask2 = pygame.mask.from_surface(obj2.surface)
                xoffset = obj1.pos[0] - obj2.pos[0]
                yoffset = obj1.pos[1] - obj2.pos[1]
                offset = int(xoffset), int(yoffset)
                if mask1.overlap(mask2, offset) != None:
                    dx1, dy1 = obj1.speed
                    dx2, dy2 = obj2.speed
                    #obj1.speed = math.copysign(dx1, dx2), math.copysign(dy1, dy2)
                    #obj2.speed = math.copysign(dx2, dx1), math.copysign(dy2, dy1)
                    obj1.speed = -dx1, -dy1
                    obj2.speed = -dx2, -dy2
                    obj1.logic(surface)
                    obj2.logic(surface)
                    break;
            else :
                obj1.logic(surface)

    def Draw(self, surface):
        GameMode.Draw(self, surface)
        for obj in self.objects:
            obj.draw(surface)

class GameWithDnD(GameWithObjects):

    def __init__(self, *argp, **argn):
        GameWithObjects.__init__(self, *argp, **argn)
        self.oldpos = 0,0
        self.drag = None

    def Events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click = self.locate(event.pos)
            if click:
                self.drag = click[0]
                self.drag.active = False
                self.oldpos = event.pos
        elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
            if self.drag:
                self.drag.pos = event.pos
                self.drag.speed = event.rel
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.drag != None:
                self.drag.active = True
            self.drag = None
        GameWithObjects.Events(self, event)
        
Init(SIZE)
Game = Universe(50)

Run = GameWithDnD()
for i in xrange(2):
    x, y = random.randrange(screenrect.w), random.randrange(screenrect.h)
    dx, dy = 1+random.random()*5, 1+random.random()*5
    zoom = 0.5 + random.random()
    angle_speed = 2 + random.random()*10
    Run.objects.append(RotozoomBall("ball.gif",(x,y),(dx,dy), zoom, angle_speed))

Game.Start()
Run.Init()
again = True
while again:
    event = pygame.event.wait()
    if event.type == pygame.QUIT:
        again = False
    Run.Events(event)
    Run.Logic(screen)
    Run.Draw(screen)
    pygame.display.flip()
Game.Finish()
pygame.quit()
