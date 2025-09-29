import pygame as pg

class TextInput:
    """Single-line text box; numeric=True restricts to digits."""
    def __init__(self, rect, text="", numeric=False, placeholder=""):
        self.rect = pg.Rect(rect)
        self.text = text
        self.numeric = numeric
        self.placeholder = placeholder
        self.focus = False
        self.font = pg.font.Font(None, 28)

    def handle_event(self, ev):
        if ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
            self.focus = self.rect.collidepoint(ev.pos)
        elif ev.type == pg.KEYDOWN and self.focus:
            if ev.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
            elif ev.key == pg.K_RETURN:
                self.focus = False
            else:
                ch = ev.unicode
                if self.numeric and not ch.isdigit():
                    return
                if ch.isprintable():
                    self.text += ch

    def get_value(self):
        return self.text.strip()

    def set_value(self, s: str):
        self.text = s or ""

    def clear(self):
        self.text = ""

    def draw(self, surf):
        bg = (240, 240, 245)
        border = (50, 140, 255) if self.focus else (90, 110, 140)
        pg.draw.rect(surf, bg, self.rect, border_radius=6)
        pg.draw.rect(surf, border, self.rect, width=2, border_radius=6)
        show = self.text if self.text else self.placeholder
        color = (30, 30, 35) if self.text else (120, 120, 130)
        txt = self.font.render(show, True, color)
        surf.blit(txt, (self.rect.x + 8, self.rect.y + 8))


class TeamSelector:
    """Two buttons (Red/Green). Selected one is bright with thick white outline."""
    def __init__(self, pos, default="Red"):
        self.options = ["Red", "Green"]
        self.idx = self.options.index(default)
        self.font = pg.font.Font(None, 28)
        self.button_rects = [pg.Rect(pos[0] + i * 110, pos[1], 100, 36) for i in range(2)]

    def get_team(self):
        return self.options[self.idx]

    def set_team(self, name):
        if name in self.options:
            self.idx = self.options.index(name)

    def handle_event(self, ev):
        if ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
            for i, r in enumerate(self.button_rects):
                if r.collidepoint(ev.pos):
                    self.idx = i

    def draw(self, surf):
        for i, r in enumerate(self.button_rects):
            active = (i == self.idx)
            color = (200, 60, 60) if i == 0 else (60, 180, 90)
            if not active:
                color = tuple(int(c * 0.6) for c in color)  # dim inactive
            pg.draw.rect(surf, color, r, border_radius=8)
            if active:
                pg.draw.rect(surf, (255, 255, 255), r, width=3, border_radius=8)
            else:
                pg.draw.rect(surf, (30, 30, 35), r, width=2, border_radius=8)
            label = self.font.render(self.options[i], True, (255, 255, 255))
            surf.blit(label, (r.centerx - label.get_width() // 2,
                              r.centery - label.get_height() // 2))
