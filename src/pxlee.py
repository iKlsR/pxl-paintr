import pygame, sys
import os
from optparse import OptionParser
from time import time

from pygame import gfxdraw

import ui

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

palette_key = '1'
color = palette['1'] #0x00, 0x00, 0x00, 0xff
(grid_stat, selected_col, mini_prev) = ('on', color, 'off')

controls = [
    ui.HueSlider(ui.Rect(600,  200, 200, 200), ui.to_hsla(*color)), #(255, 1.0, 0.5, 1.0)),
    ui.ToneSlider(ui.Rect(650, 250, 100, 100), ui.to_hsla(*color)), #(255, 1.0, 0.5, 1.0)),
    ui.AlphaSlider(ui.Rect(600, 415, 200, 11), ui.to_hsla(*color)), #(255, 1.0, 0.5, 1.0)),
]

def color_change(hsla, feedback=True):
    global color
    for control in controls:
        control.hsla = hsla
        if not isinstance(control, ui.HueSlider):
            control.cache = None
    color = ui.from_hsla(*hsla)
    if feedback:
        palette[palette_key] = color

for control in controls:
    control.trigger = color_change



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
            if palette_key == key:
                x,y,w,h = area
                x,y = x+w/2, y+h/2
                screen.fill((0,0,0), (x-2,y-2,4,4))
        
        if grid_stat == 'on':
            grid(screen, ((canvasW * scale), (canvasY * scale)))

        for control in controls:
            control.animation_frame(screen)

def shortcut(_unicode):
    global grid_color, color, grid_stat, selected_col, mini_prev, filename_final, palette_key

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
        palette_key = _unicode
        print palette[_unicode]
        hsla = ui.to_hsla(*palette[_unicode])
        print hsla
        color_change(hsla, feedback=False)
        selected_col = color

mousemode = None

def dispatch(event):
    global mousemode
    if event.type == pygame.MOUSEBUTTONDOWN:
        match = None
        for control in controls:
            if control.area.hit(event.pos):
                match = control
        if match is not None:
            mousemode = match.mousedown(event.pos)
            return True
    if event.type == pygame.QUIT:
        sys.exit()
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        sys.exit()
    elif event.type == pygame.KEYDOWN:
        shortcut(event.unicode)
    elif event.type == pygame.MOUSEMOTION and mousemode is not None:
        mousemode.mousedrag(event.pos)
    elif event.type == pygame.MOUSEBUTTONUP:
        mousemode = None
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

pygame.mouse.set_visible(False)

while 1:
    pygame.display.set_caption('pxl paintr - %s | grid: %s | color: %s | preview: %s' % \
                              (os.getcwd() + '\\' + filename_final, grid_stat, selected_col, mini_prev))
    for event in pygame.event.get():
        dispatch(event)
    
    animation_frame(screen)
	
    #temporary.. project really needs to be cleaned up.. you hear that.. Cheery :) 
    mousexx, mouseyy = pygame.mouse.get_pos()

    screen.fill((0xFF,0xFF,0xFF), (mousexx, mouseyy-2, 1, 5))
    screen.fill((0xFF,0xFF,0xFF), (mousexx-2, mouseyy, 5, 1))
#    pygame.gfxdraw.box(screen, (mousexx, mouseyy, 5, 5), (0xFF, 0xFF, 0xFF, 200))
	
    pygame.display.flip()
    
pygame.quit()   #ide friendly
