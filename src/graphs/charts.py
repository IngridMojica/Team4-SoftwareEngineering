import pygame as pg

def draw_bar_chart(surf, rect, data: dict, title="Chart"):

    pg.draw.rect(surf, (40, 40, 50), rect, border_radius=8)

    font = pg.font.Font(None, 20)
    title_surf = font.render(title, True, (230, 230, 235))

    surf.blit(title_surf, (rect.x + (rect.width - title_surf.get_width()) // 2, rect.y + 6))

    if not data:
        return
    
    total = max(data.values()) or 1
    bar_w = rect.width - 20
    bar_h = 22
    y = rect.y + 30

    for team, count in data.items():
        w = int((count/total) * bar_w)

        color = (200,60,60) if team=="Red" else (60,180,90)

        pg.draw.rect(surf, color, (rect.x+10, y, w, bar_h), border_radius=6)

        label = font.render(f"{team}: {count}", True, (240,240,250))

        surf.blit(
            label,
            (rect.x+15, y+5)
        )

        y += bar_h + 10

def draw_team_table(surf, rect, players: dict, title="Teams", headers=("RED TEAM", "GREEN TEAM")):
    
    # Panel
    pg.draw.rect(surf, (40, 40, 50), rect, border_radius=12)

    # Title
    font_title = pg.font.Font(None, 26)
    title_surf = font_title.render(title, True, (230, 230, 235))
    surf.blit(
        title_surf,
        (rect.x + (rect.width - title_surf.get_width()) // 2, rect.y + 8)
    )

    # Gather names by team 
    red   = [p.get("codename") or f"PID {pid}" for pid, p in players.items() if p.get("team") == "Red"]
    green = [p.get("codename") or f"PID {pid}" for pid, p in players.items() if p.get("team") == "Green"]

    # Table
    top_after_title = rect.y + 8 + title_surf.get_height() + 8
    table_rect = pg.Rect(rect.x + 10, top_after_title, rect.width - 20, rect.height - (top_after_title - rect.y) - 10)

    # Header row
    header_h  = 30
    font_head = pg.font.Font(None, 22)
    head_bg   = pg.Rect(table_rect.x, table_rect.y, table_rect.width, header_h)
    pg.draw.rect(surf, (55, 55, 70), head_bg, border_radius=6)

    col_w = table_rect.width // 2
    surf.blit(font_head.render(headers[0], True, (235, 205, 205)), (table_rect.x + 8, table_rect.y + 6))
    surf.blit(font_head.render(headers[1], True, (205, 235, 205)), (table_rect.x + col_w + 8, table_rect.y + 6))

    # Column separator + outer border
    pg.draw.line(surf, (80, 80, 95), (table_rect.x + col_w, table_rect.y), (table_rect.x + col_w, table_rect.bottom), 1)
    pg.draw.rect(surf, (80, 80, 95), table_rect, width=1, border_radius=6)

    # Dynamically size rows so up to 15 fit
    rows  = 15
    available_h  = table_rect.height - header_h - 2
    row_h        = max(18, available_h // rows)
    font_cell_sz = 22 if row_h >= 20 else 20
    font_cell    = pg.font.Font(None, font_cell_sz)

    y            = table_rect.y + header_h + 1
    max_rows     = max(len(red), len(green))
    visible_rows = min(rows, available_h // row_h)


    for i in range(min(max_rows, visible_rows)):
        row_y = y + i * row_h

        if i % 2 == 0:
            pg.draw.rect(surf, (47, 47, 60), (table_rect.x, row_y, table_rect.width, row_h))

        # column - RED
        if i < len(red):
            left_text = f"{i + 1}. {red[i]}"
            surf.blit(
                font_cell.render(left_text, True, (245, 245, 245)),
                (table_rect.x + 8, row_y + 4)
            )

        # column - GREEN
        if i < len(green):
            right_text = f"{i + 1}. {green[i]}"
            surf.blit(
                font_cell.render(right_text, True, (245, 245, 245)), 
                (table_rect.x + col_w + 8, row_y + 4)
            )
