# main.py
import sys
import pygame
from src.ui.screens.player_entry import PlayerEntry  # << use real screen

# -----------------------------
# Config
# -----------------------------
WIDTH, HEIGHT = 900, 600
FPS = 60
SPLASH_DURATION_MS = 3000  # 3 seconds
APP_TITLE = "Laser Tag - Sprint 2"
LOGO_PATH = "assets/logo.jpg"  # path to your logo

# -----------------------------
# Shared App State for screens
# -----------------------------
class AppState:
    def __init__(self):
        # team name -> count (used by charts)
        self.team_counts = {"Red": 0, "Green": 0}
        # pid -> {codename, team, equip}
        self.players = {}
        # where UDP should broadcast by default (can be changed later)
        self.addr = "127.0.0.1"

# -----------------------------
# Base Screen Class
# -----------------------------
class BaseScreen:
    def __init__(self, manager):
        self.manager = manager

    def on_enter(self): pass
    def on_exit(self): pass
    def handle_event(self, event): pass
    def update(self, dt): pass
    def draw(self, surface): surface.fill((20, 20, 25))

# -----------------------------
# Splash Screen
# -----------------------------
class SplashScreen(BaseScreen):
    def on_enter(self):
        self.start_time = pygame.time.get_ticks()
        self.logo = pygame.image.load(LOGO_PATH).convert_alpha()
        self.logo = pygame.transform.smoothscale(self.logo, (400, 300))

    def update(self, dt):
        elapsed = pygame.time.get_ticks() - self.start_time
        if elapsed >= SPLASH_DURATION_MS:
            self.manager.switch_to("player_entry")

    def handle_event(self, event):
        # allow any key or click to skip splash
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self.manager.switch_to("player_entry")

    def draw(self, surface):
        surface.fill((10, 12, 20))
        surface.blit(self.logo, self.logo.get_rect(center=(WIDTH//2, HEIGHT//2)))

# -----------------------------
# Player Entry Screen (REAL UI)
# -----------------------------
class PlayerEntryScreen(BaseScreen):
    def __init__(self, manager, state: AppState):
        super().__init__(manager)
        # create the actual PlayerEntry view and tell it how to start the game
        self.view = PlayerEntry(
            state=state,
            on_start=lambda: self.manager.switch_to("play")
        )

    # delegate lifecycle + io to the real view so all buttons/inputs work
    def on_enter(self): 
        if hasattr(self.view, "on_enter"): 
            self.view.on_enter()

    def on_exit(self): 
        if hasattr(self.view, "on_exit"): 
            self.view.on_exit()

    def handle_event(self, event):
        self.view.handle_event(event)

    def update(self, dt):
        self.view.update(dt)

    def draw(self, surface):
        self.view.draw(surface)

# -----------------------------
# Play Screen (stub)
# -----------------------------
class PlayScreen(BaseScreen):
    def on_enter(self):
        self.font = pygame.font.SysFont("consolas", 28)

    def draw(self, surface):
        surface.fill((12, 16, 18))
        text = self.font.render("Play Screen - game goes here", True, (220, 235, 220))
        surface.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2)))

# -----------------------------
# Screen Manager
# -----------------------------
class ScreenManager:
    def __init__(self):
        self.registry = {}
        self.active = None

    def register(self, name, screen):
        self.registry[name] = screen

    def switch_to(self, name):
        if self.active:
            self.active.on_exit()
        self.active = self.registry[name]
        self.active.on_enter()

# -----------------------------
# App / Main loop
# -----------------------------
class App:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption(APP_TITLE)

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        # shared state for DB/UDP/UI
        self.state = AppState()

        self.manager = ScreenManager()
        self.manager.register("splash", SplashScreen(self.manager))
        self.manager.register("player_entry", PlayerEntryScreen(self.manager, self.state))
        self.manager.register("play", PlayScreen(self.manager))
        self.manager.switch_to("splash")

        self.running = True

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                else:
                    if self.manager.active:
                        self.manager.active.handle_event(event)

            if self.manager.active:
                self.manager.active.update(dt)
                self.manager.active.draw(self.screen)

            pygame.display.flip()

        pygame.quit()
        sys.exit()

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    App().run()