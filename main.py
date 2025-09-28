import pygame
import sys

# -----------------------------
# Config
# -----------------------------
WIDTH, HEIGHT = 900, 600
FPS = 60
SPLASH_DURATION_MS = 3000  # 3 seconds
APP_TITLE = "Laser Tag - Sprint 2"
LOGO_PATH = "assets/logo.jpg"  # path to your logo

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
        # Load logo when splash starts
        self.logo = pygame.image.load(LOGO_PATH).convert_alpha()
        # Scale to a nice size
        self.logo = pygame.transform.smoothscale(self.logo, (400, 300))

    def update(self, dt):
        elapsed = pygame.time.get_ticks() - self.start_time
        if elapsed >= SPLASH_DURATION_MS:
            self.manager.switch_to("player_entry")

    def draw(self, surface):
        surface.fill((10, 12, 20))
        # Center logo
        surface.blit(self.logo, self.logo.get_rect(center=(WIDTH//2, HEIGHT//2)))

# -----------------------------
# Player Entry Screen (stub)
# -----------------------------
class PlayerEntryScreen(BaseScreen):
    def on_enter(self):
        self.font = pygame.font.SysFont("arial", 28)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.manager.switch_to("play")

    def draw(self, surface):
        surface.fill((18, 22, 28))
        text = self.font.render("Player Entry (press Enter to continue)", True, (230, 230, 240))
        surface.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2)))

# -----------------------------
# Play Screen (stub)
# -----------------------------
class PlayScreen(BaseScreen):
    def on_enter(self):
        self.font = pygame.font.SysFont("consolas", 28)

    def draw(self, surface):
        surface.fill((12, 16, 18))
        text = self.font.render("Play Screen – game goes here", True, (220, 235, 220))
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
        self.manager = ScreenManager()
        self.manager.register("splash", SplashScreen(self.manager))
        self.manager.register("player_entry", PlayerEntryScreen(self.manager))
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