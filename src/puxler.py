#!/usr/bin/env python

'''beautiful pygame boilerplate'''
'''http://iiklsr.wordpress.com/py/boilerplate'''

import pygame
import sys,os

color = {
    'white': (0xFF, 0xFF, 0xFF, 0xFF),
    'black': (0x00, 0x00, 0x00, 0xFF),
    'red':   (0xFF, 0x00, 0x00, 0xFF),
    'green': (0x00, 0xFF, 0x00, 0xFF),
    'blue':  (0x00, 0x00, 0xFF, 0xFF),
    'orange':(0xFF, 0xFF, 0x00, 0xFF),
    'yellow':(0x00, 0xFF, 0xFF, 0xFF),
    'purple':(0xFF, 0x00, 0xFF, 0xFF),
}

class __skeleton(object):
    def __init__(self, (width, height), handle = None , title = 'untitled'):
        self.width = width
        self.height = height
        self.title = title
        self.handle = handle

        pygame.display.init()
        if self.handle == 1: os.environ['SDL_VIDEO_CENTERED'] = '1'

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)

        self.img = pygame.image.load('../img/rain.png').convert()
        self.imgx, self.imgy = 256, 258
        self.selected_color = (0xFF, 0xFF, 0xFF)
        
    def unicode_(self, key):
        if key == 'q':
            sys.exit()

    def updt(self):
        pass
    
    def msg(self):
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            self.unicode_(event.unicode)
            if event.key == pygame.K_ESCAPE:
                sys.exit()
        elif event.type == pygame.MOUSEMOTION and event.buttons == (1, 0, 0):
            pos = pygame.mouse.get_pos()
            if pos[0] < self.imgx and pos[1] < self.imgy:
                self.selected_color = self.screen.get_at(pos)
                selected_col = self.selected_color
                        
    def crt(self):
        self.screen.fill(self.selected_color)
        self.screen.blit(self.img, (0, 0))
        self.updt()

if __name__ == '__main__':
    instance = __skeleton((256, 258 * 2), 1, 'puxler')
        
    while 1:
        for event in pygame.event.get():
            instance.msg()
        instance.crt()
        pygame.display.flip()
