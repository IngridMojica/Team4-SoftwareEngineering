import pygame as pg

def draw_bar_chart(surf, rect, data: dict, title="Chart"):
    """
    Very simple horizontal bar chart for team counts.
    data: {"Red": int, "Green": int}
    """
    pg.draw.rect(surf, (40, 40, 50), rect, border_radius=8)
    font = pg.font.Font(None, 24)
    surf.blit(font.render(title, True, (230, 230, 235)), (rect.x+8, rect.y+6))

    if not data:
        return
    
    total = max(data.values()) or 1
    bar_w = rect.width - 20
    bar_h = 30
    y = rect.y + 40

    for team, count in data.items():
        w = int((count/total) * bar_w)
        color = (200,60,60) if team=="Red" else (60,180,90)
        pg.draw.rect(surf, color, (rect.x+10, y, w, bar_h), border_radius=6)
        label = font.render(f"{team}: {count}", True, (240,240,250))
        surf.blit(label, (rect.x+15, y+5))
        y += bar_h + 10
