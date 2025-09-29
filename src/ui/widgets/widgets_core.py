import pygame as pg

class Label:
    def __init__(self, text, pos, font=None, color=(235,235,240)):
        self.text = text
        self.pos =  pos
        self.font = font or pg.font.Font(None, 28)
        self.color = color

    def draw(self, surf):
        surf.blit(self.font.render(self.text, True, self.color), self.pos)

class Button:
    def __init__(self, rect, text, on_click):
        self.rect = pg.Rect(rect)
        self.text = text
        self.on_click = on_click
        self.font = pg.font.Font(None, 28); self.hover = False

    def handle_event(self, ev):
        if ev.type == pg.MOUSEMOTION:
            self.hover = self.rect.collidepoint(ev.pos)
        elif ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1 and self.rect.collidepoint(ev.pos):
            self.on_click()
            
    def draw(self, surf):
        pg.draw.rect(surf, (70,90,120) if self.hover else (55,70,95), self.rect, border_radius=6)
        txt = self.font.render(self.text, True, (240,240,250))
        surf.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.centery - txt.get_height()//2))
