import pygame, math

class Rect(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def __iter__(self):
        return iter((self.x, self.y, self.width, self.height))

    def hit(self, (x,y)):
        x -= self.x
        y -= self.y
        return 0 <= x < self.width and 0 <= y < self.height

    @property
    def center(self):
        return self.x + self.width*0.5, self.y + self.height*0.5

    def pad(self, count):
        return Rect(self.x - count, self.y - count, self.width + count*2, self.height + count*2)

class AlphaSlider(object):
    cache = None
    trigger = None
    def __init__(self, area, hsla):
        self.area = area
        self.hsla = hsla

    def animation_frame(self, screen):
        if self.cache is None:
            self.cache = pygame.Surface((self.area.width, self.area.height), pygame.SRCALPHA)
            data = pygame.PixelArray(self.cache)
            hue, sat, light, _ = self.hsla
            for i in range(self.area.width):
                alpha = i / float(self.area.width-1)
                data[i,:] = from_hsla(hue, sat, light, alpha*100)
            del data
        hue, sat, light, alpha = self.hsla
        screen.blit(self.cache, tuple(self.area))
        pygame.draw.rect(screen, (64,64,64,255), tuple(self.area.pad(1)), 1)
        render_marker(screen, (self.area.x + (self.area.width-1) * alpha, self.area.y + 0.5 * self.area.height))

    def set_value(self, (x, y)):
        hue, sat, light, _ = self.hsla
        alpha = float(x - self.area.x) / self.area.width
        alpha = min(1.0, max(0.0, alpha))
        self.hsla = hue, sat, light, alpha*100
        if self.trigger:
            self.trigger(self.hsla)

    def mousedown(self, position):
        self.set_value(position)
        return self

    def mousedrag(self, position):
        self.set_value(position)

class ToneSlider(object):
    cache = None
    trigger = None
    def __init__(self, area, hsla):
        self.area = area
        self.hsla = hsla

    def animation_frame(self, screen):
        if self.cache is None:
            self.cache = pygame.Surface((self.area.width, self.area.height), pygame.SRCALPHA)
            data = pygame.PixelArray(self.cache)
            hue, _, _, alpha = self.hsla
            for i in range(self.area.width):
                sat = i / float(self.area.width-1)
                for j in range(self.area.height):
                    light = j / float(self.area.height-1)
                    data[i,j] = from_hsla(hue, sat*100, light*100, alpha)
            del data
        hue, sat, light, alpha = self.hsla
        screen.blit(self.cache, tuple(self.area))
        pygame.draw.rect(screen, (64,64,64,255), tuple(self.area.pad(1)), 1)
        render_marker(screen, (self.area.x + (self.area.width-1) * sat, self.area.y + (self.area.height-1) * light))

    def set_value(self, (x, y)):
        hue, _, __, alpha = self.hsla
        sat = float(x - self.area.x) / self.area.width
        sat = min(1.0, max(0.0, sat))
        light = float(y - self.area.y) / self.area.height
        light = min(1.0, max(0.0, light))
        self.hsla = hue, sat*100, light*100, alpha
        if self.trigger:
            self.trigger(self.hsla)

    def mousedown(self, position):
        self.set_value(position)
        return self

    def mousedrag(self, position):
        self.set_value(position)

class HueSlider(object):
    cache = None
    trigger = None
    def __init__(self, area, hsla):
        self.area = area
        self.hsla = hsla

    def animation_frame(self, screen):
        cx, cy = self.area.width*0.5, self.area.height*0.5
        r2 = min(cx,cy)**2
        if self.cache is None:
            self.cache = pygame.Surface((self.area.width, self.area.height), pygame.SRCALPHA)
            data = pygame.PixelArray(self.cache)
            for i in range(self.area.width):
                dx = i - cx
                dx2 = dx**2
                for j in range(self.area.height):
                    dy = j - cy
                    dy2 = dy**2
                    if r2*0.8 <= dx2+dy2 < r2:
                        hue = math.degrees(math.atan2(dy, dx)) + 180
                        data[i,j] = from_hsla(hue, 100, 50, 100.0)
            del data
        hue, sat, light, alpha = self.hsla
        angle = math.radians(hue)
        screen.blit(self.cache, tuple(self.area))
        r = math.sqrt(r2*0.9)
        render_marker(screen, (self.area.x + cx - math.cos(angle) * r, self.area.y + cy - math.sin(angle) * r))

    def set_value(self, (x, y)):
        (cx,cy) = self.area.center
        dx = x - cx
        dy = y - cy
        _, sat, light, alpha = self.hsla
        hue = math.degrees(math.atan2(dy, dx)) + 180
        self.hsla = hue, sat, light, alpha
        if self.trigger:
            self.trigger(self.hsla)

    def mousedown(self, position):
        self.set_value(position)
        return self

    def mousedrag(self, position):
        self.set_value(position)

# some things to wonder about...
#class shared_property(object):
#    def __init__(self, value):
#        self.value = value
#
#class eventrouter(object):
#    def __init__(self):
#        self.routes = {}
#    
#    def register(self, name, fn):
#        self.routes[name] = fn
#
#    def __call__(self, name, *a, **kw):
#        return self.routes[name](*a, **kw)

def render_marker(surface, (x,y)):
    pygame.draw.rect(surface, (255,255,255,255), (x-3,y-3,7,7), 1)
    pygame.draw.rect(surface, (0,0,0,255), (x-2,y-2,5,5), 1)

def from_hsla(h,s,l,a):
    color = pygame.Color(0)
    color.hsla = h,s,l,a
    return color

def to_hsla(r,g,b,a=255):
    return pygame.Color(r,g,b,a).hsla

