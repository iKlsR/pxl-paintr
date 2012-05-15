import pygame, sys
import os
from optparse import OptionParser
from time import time

parser = OptionParser(
    usage = "usage: %prog [options] file"
)

(options, args) = parser.parse_args()

if len(args) != 1:
    print 'did you read the readme? add the filename..'
    sys.exit(1)

filename = args[0]
filename_exten = filename
filename_unsaved = filename + '*'
filename_final = filename_unsaved

def parse_size():
    width, height = options.size.split('x')
    return int(width), int(height)

black = 0x00, 0x00, 0x00
white = 0xFF, 0xFF, 0xFF
background_color = 0x12, 0x0E, 0x1C
grey = 0x39, 0x39, 0x39
grey_a = (0x00, 0x00, 0x00, 0x00)
grid_color = 0x41, 0x41, 0x41

scale = 8       #pixel size on scaled canvas
brush_size = 8  #can be synonymous with pixel size if grid is on !!NOT UTILIZED AS YET

canvas_w = 64
canvas_h = 64

canvas = pygame.Surface((canvas_w, canvas_h), pygame.SRCALPHA)
mini_view = pygame.Surface((256, 256), pygame.SRCALPHA)
#canvas.set_at((0, 0), white)
#canvas.set_at((canvas_w - 1, canvas_h - 1), black)        #useful for seeing the width and height

pygame.font.init()
font = pygame.font.Font(None, 16)

palette = {
    '0': (0x00, 0x00, 0x00, 0xff),
    '1': (0xff, 0x00, 0x00, 0xff),
    '2': (0xff, 0xff, 0x00, 0xff),
    '3': (0x00, 0xff, 0x00, 0xff),
    '4': (0x00, 0xff, 0xff, 0xff),
    '5': (0x00, 0x00, 0xff, 0xff),
    '6': (0xff, 0x00, 0xff, 0xff),
    '7': (0xff, 0xff, 0xff, 0xff),
    '8': (0xff, 0x80, 0x00, 0xff),
    '9': (0x80, 0x80, 0x80, 0xff),
}

color = palette['1'] #0x00, 0x00, 0x00, 0xff
(grid_stat, selected_col, mini_prev) = ('on', color, 'off')


def from_hsla(h,s,l,a):
    color = pygame.Color(0)
    color.hsla = h,s,l,a
    return color

def to_hsla(r,g,b,a=255):
    return pygame.Color(r,g,b,a).hsla

def draw_marker(surface, (x,y)):
    pygame.draw.rect(surface, (255,255,255,255), (x-3,y-3,7,7), 1)
    pygame.draw.rect(surface, (0,0,0,255), (x-2,y-2,5,5), 1)

import math
def create_color_circle(sel_hue, sel_sat, sel_light, sel_alpha):
    box = pygame.Surface((200, 200), pygame.SRCALPHA)
    pixels = pygame.PixelArray(box)
    radius_min2 = 73*73
    radius_max2 = 90*90
    for x in range(200):
        for y in range(200):
            dx = (x - 100)
            dy = (y - 100)
            if 50 <= x < 150 and 50 <= y < 150:
                sat = (x-50)/99.0 * 100.0
                light = (y-50)/99.0 * 100.0
                pixels[x,y] = from_hsla(sel_hue, sat, light, 100.0)
            elif 194 <= y < 197 and 50 <= x < 150:
                pixels[x,y] = from_hsla(sel_hue, sel_sat, sel_light, (x-50)/199.0*100.0)
            elif radius_min2 < (dx*dx + dy*dy) < radius_max2:
                hue = math.degrees(math.atan2(dy, dx)) + 180
                pixels[x,y] = from_hsla(hue, 100, 50, 100.0)
    pygame.draw.rect(box, (64,64,64,255), (49, 193, 102, 5), 1)
    pygame.draw.rect(box, (64,64,64,255), (49, 49, 102, 102), 1)
    a = math.radians(sel_hue)
    draw_marker(box, (100 - math.cos(a) * 81,100 - math.sin(a) * 81)) # circle slider
    draw_marker(box, (50 + sel_sat*0.99,50 + sel_light*0.99)) # box slider
    draw_marker(box, (50 + sel_alpha*0.99,195)) # alpha slider
    return box

class ColorControl(object):
    def __init__(self, pos, hsla):
        self.pos = pos
        self.hsla = hsla
        self.box = create_color_circle(*hsla)
        self.dirty = False

    def frame(self, screen):
        if self.dirty:
            self.box = create_color_circle(*self.hsla)
            self.dirty = False
        screen.blit(self.box, self.pos)

    def inside(self, (x, y)):
        dx = x - self.pos[0]
        dy = y - self.pos[1]
        return 0 <= dx < 200 and 0 <= dy < 200

    def inside_aslider(self, (dx, dy)):
        return 194 <= dy and 50 <= dx < 150

    def inside_tslider(self, (dx, dy)):
        return 50 <= dy < 150 and 50 <= dx < 150

    def mousedown(self, (x, y)):
        dx = x - self.pos[0]
        dy = y - self.pos[1]
        hue,sat,light,alpha = self.hsla
        if self.inside_aslider((dx, dy)):
            alpha = (dx - 50) / 99.0 * 100.0
        elif self.inside_tslider((dx, dy)):
            sat = (dx-50)/99.0 * 100.0
            light = (dy-50)/99.0 * 100.0
        elif dy < 193:
            hue = math.degrees(math.atan2(dy-100, dx-100)) + 180
        self.dirty = True
        self.hsla = hue,sat,light,alpha

colorctl = ColorControl((894-200, 0), to_hsla(*white))

def plot((x, y)):
    x = int(x / scale)
    y = int(y / scale)
    if 0 <= x < canvas_w and 0 <= y < canvas_h:
        canvas.set_at((x, y), color)
        
def del_plot((x, y)):
    x = int(x / scale)
    y = int(y / scale)
    if 0 <= x < canvas_w and 0 <= y < canvas_h:
        canvas.set_at((x, y), (0, 0, 0, 0))

def grid(surf, (x, y)):
    for loc in range(-1, x, scale):
        thickness = 1
        surf.fill(grid_color, (loc, 0, thickness, y))
    for loc in range(-1, y, scale):
        thickness = 1
        surf.fill(grid_color, (0, loc, x, thickness))

def animation_frame(screen):
        screen.fill(background_color)
        (w, y) = screen.get_size()
        canvasW, canvasY = canvas.get_size()
        global mini_prev, mini_view
        
        #draws before the canvas so the lines aren't etched into the graphics
        if grid_stat == 'off':
            grid(screen, ((canvasW * scale), (canvasY * scale)))
        
        view = pygame.transform.scale(canvas, (canvas_w * scale, canvas_h * scale))
        mini_view = pygame.transform.scale(canvas, (canvas_w * 4, canvas_h * 4))
        screen.blit(view, (0, 0))
        
        if mini_prev == 'off':
            #do nothing
            mini_prev = 'off'
        else:
            mini_prev = 'on'
            screen.blit(mini_view, (w - (canvas_w * 4), 0))
                
        screen.fill(black, (0, y - 28, w, 28))
        for index, key in enumerate('1234567890'):
            keycolor = palette[key]
            area = (index * 45 + 2, screen.get_height() - 28, 40, 36)
            screen.fill(keycolor, area)
            complement = 255 - keycolor[0], 255 - keycolor[1], 255 - keycolor[2], 0xFF
            screen.blit(font.render(key, True, complement), area)
        
        if grid_stat == 'on':
            grid(screen, ((canvasW * scale), (canvasY * scale)))

        colorctl.frame(screen)

def shortcut(_unicode):
    global grid_color, color, grid_stat, selected_col, mini_prev, filename_final

    if _unicode == 'h':
        if grid_stat == 'off':
            grid_stat = 'on'
            grid_color = grey
        else:
            grid_stat = 'off'
            grid_color = background_color
            
    elif _unicode == 'p':
        if mini_prev == 'off':
            mini_prev = 'on'
        else:
            mini_prev = 'off'  
    elif _unicode == 'f':
        canvas.fill((0, 0, 0, 0), (0, 0, (canvas_w * scale), (canvas_h * scale)))    
    elif _unicode == 's':
        global mini_view
        pygame.image.save(mini_view, filename_exten + '.png')
        filename_final = filename_exten + '.png'
    elif _unicode in palette:
        color = palette[_unicode]
        selected_col = color

def dispatch(event):
    if event.type == pygame.QUIT:
        sys.exit()
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        sys.exit()
    elif event.type == pygame.KEYDOWN:
        shortcut(event.unicode)
    elif event.type == pygame.MOUSEBUTTONDOWN and colorctl.inside(event.pos):
        colorctl.mousedown(event.pos)
    elif event.type == pygame.MOUSEMOTION and colorctl.inside(event.pos) and (1 in event.buttons):
        colorctl.mousedown(event.pos)
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        plot(event.pos)
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
        del_plot(event.pos)
    elif event.type == pygame.MOUSEMOTION and event.buttons == (1, 0, 0):   #( | )
        plot(event.pos)
    elif event.type == pygame.MOUSEMOTION and event.buttons == (0, 0, 1):   #( | )
        del_plot(event.pos)
  
os.environ['SDL_VIDEO_CENTERED'] = '1'      
pygame.display.init()
screen = pygame.display.set_mode((894, 600))

while 1:
    pygame.display.set_caption('pxl paintr - %s | grid: %s | color: %s | preview: %s' % \
                              (os.getcwd() + '\\' + filename_final, grid_stat, selected_col, mini_prev))
    for event in pygame.event.get():
        dispatch(event)
    animation_frame(screen)
    pygame.display.flip()
    
pygame.quit()   #ide friendly
