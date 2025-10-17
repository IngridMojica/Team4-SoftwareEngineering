import pygame as pg
from ui.screens.player_entry import PlayerEntry

class DummyState:
    def __init__(self):
        self.team_counts = {"Red": 0, "Green": 0}
        self.players = {}
        self.addr = "127.0.0.1"  # host/ip string

def main():
    pg.init()
    screen = pg.display.set_mode((800, 500))
    clock = pg.time.Clock()
    state = DummyState()
    entry_screen = PlayerEntry(state, on_start=lambda: print("Starting game..."))
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                running = False
            entry_screen.handle_event(ev)
        entry_screen.update(dt)
        entry_screen.draw(screen)
        pg.display.flip()
    pg.quit()

if __name__ == "__main__":
    main()
