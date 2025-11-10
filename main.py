# main.py
import sys
import pygame
from collections import deque
import time

# === UI Screens ===
from src.ui.screens.player_entry import PlayerEntry  # real entry screen
from src.ui.screens.play_display import PlayDisplay  # real play screen

# === Networking / Packets ===
from udp_receiver import start_receiver
from udp_broadcast import send_equipment_id, send_special_code
from packet_handler import handle_packet

# === Timer (Sprint 4) ===
from src.game_timer import GameTimer, GameState

# -----------------------------
# Config
# -----------------------------
WIDTH, HEIGHT = 900, 600
FPS = 60
SPLASH_DURATION_MS = 3000  # 3 seconds
APP_TITLE = "Laser Tag - Sprint 4"
LOGO_PATH = "assets/logo.jpg"  # path to your logo

# -----------------------------
# Shared App State for screens
# -----------------------------
class AppState:
    def __init__(self):
        # team name -> count (used by charts)
        self.team_counts = {"Red": 0, "Green": 0}
        # pid -> {codename, team, equip, score, has_base}
        self.players = {}
        # rolling play-by-play log
        self.event_log = deque(maxlen=200)
        # where UDP should broadcast by default (can be changed later)
        self.addr = "127.0.0.1"

        # --- Sprint 4 Timers (attached to shared state) ---
        # 30s pre-game countdown → 6 min gameplay timer
        self.timer = GameTimer(start_countdown=30, play_seconds=6*60)

    def name_(self, pid):
        player = self.players.get(pid, {})
        return player.get("codename") or str(pid)

    # play-by-play helpers
    def log_tag(self, shooter_pid, target_pid, friendly=False):
        sname = self.name_(shooter_pid)
        tname = self.name_(target_pid)
        if friendly:
            text = f"Friendly fire: {sname} tagged teammate {tname} (−10 each)"
        else:
            text = f"{sname} tagged {tname} (+10 {sname})"
        self.event_log.append({"ts": time.time(), "text": text})

    def log_base(self, shooter_pid, base_color):
        sname = self.name_(shooter_pid)
        text = f"{sname} scored the {base_color} base! (+100)"
        self.event_log.append({"ts": time.time(), "text": text})


# -----------------------------
# Base Screen Class
# -----------------------------
class BaseScreen:
    def __init__(self, manager):
        self.manager = manager

    def on_enter(self): 
        pass

    def on_exit(self): 
        pass

    def handle_event(self, event): 
        pass

    def update(self, dt): 
        pass

    def draw(self, surface): 
        surface.fill((20, 20, 25))


# -----------------------------
# Splash Screen
# -----------------------------
class SplashScreen(BaseScreen):
    def on_enter(self):
        self.start_time = pygame.time.get_ticks()
        try:
            self.logo = pygame.image.load(LOGO_PATH).convert_alpha()
            self.logo = pygame.transform.smoothscale(self.logo, (400, 300))
        except Exception:
            # fallback if logo not found
            self.logo = pygame.Surface((400, 300), pygame.SRCALPHA)
            self.logo.fill((30, 30, 40))

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
        surface.blit(self.logo, self.logo.get_rect(center=(WIDTH // 2, HEIGHT // 2)))


# -----------------------------
# Player Entry Screen (REAL UI)
# -----------------------------
class PlayerEntryScreen(BaseScreen):
    def __init__(self, manager, state: AppState):
        super().__init__(manager)
        self.state = state
        # create the actual PlayerEntry view and tell it how to start the game
        self.view = PlayerEntry(
            state=state,
            on_start=lambda: self.manager.switch_to("play")
        )

    # delegate lifecycle + io to the real view so all buttons/inputs work
    def on_enter(self):
        # reset any end-of-game one-shot flags when coming back to lobby
        app = getattr(self.manager, "_app", None)
        if app:
            app._end_broadcasted = False
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
# Play Display Screen (uses your real PlayDisplay view)
# -----------------------------
class PlayDisplayScreen(BaseScreen):
    def __init__(self, manager, state: AppState):
        super().__init__(manager)
        self.state = state
        self.view = PlayDisplay(state)

    def on_enter(self):
        # restart the 30s pre-game countdown each time the play screen opens
        if self.state.timer.state != GameState.COUNTDOWN:
            self.state.timer.start_countdown()
        if hasattr(self.view, "enter"):
            self.view.enter()

    def handle_event(self, event):
        # forward events to the PlayDisplay view; pass manager so the view can switch screens if needed
        if hasattr(self.view, "handle_event"):
            self.view.handle_event(event, manager=self.manager)

    def update(self, dt):
        # advance timer each frame (handles transition COUNTDOWN -> PLAYING -> ENDED)
        self.state.timer.tick()
        self.view.update(dt)

    def draw(self, surface):
        self.view.draw(surface)


# -----------------------------
# Screen Manager
# -----------------------------
class ScreenManager:
    def __init__(self):
        self.registry = {}
        self.active = None
        self._app = None  # back reference to App for small resets

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

        # shared state for DB/UDP/UI (includes Sprint 4 timer)
        self.state = AppState()

        # start UDP receiver
        self.receiver = start_receiver(bind_addr="0.0.0.0", port=7501)

        # screens
        self.manager = ScreenManager()
        self.manager._app = self  # allow small resets from screens
        self.manager.register("splash", SplashScreen(self.manager))
        self.manager.register("player_entry", PlayerEntryScreen(self.manager, self.state))
        self.manager.register("play", PlayDisplayScreen(self.manager, self.state))
        self.manager.switch_to("splash")

        self.running = True

        # one-shot end-code guard
        self._end_broadcasted = False

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            # --- events ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                else:
                    if self.manager.active:
                        self.manager.active.handle_event(event)

            # --- network poll (non-blocking) ---
            if hasattr(self, "receiver"):
                if self.state.timer.state != GameState.ENDED:
                    # process at most one packet per frame while active
                    msg = self.receiver.get_message_nowait()
                    if msg:
                        text, addr = msg

                        # mini wrapper so UI can reply with equipment id to sender
                        def _udp_send(equip_id: int):
                            try:
                                send_equipment_id(int(equip_id), addr=self.state.addr, port=7500)
                            except Exception:
                                pass

                        handle_packet(text, self.state, udp_send=_udp_send)
                else:
                    # drain any leftovers quickly to keep UI stable, but do not update state
                    while self.receiver.get_message_nowait():
                        pass

            # --- update & draw current screen ---
            # capture state before update to detect transitions
            prev_state = self.state.timer.state

            if self.manager.active:
                self.manager.active.update(dt)
                self.manager.active.draw(self.screen)

            # detect transition to ENDED and broadcast end code 221 exactly once
            if prev_state != self.state.timer.state and self.state.timer.state == GameState.ENDED:
                # stop background music if play screen provided a helper
                try:
                    if getattr(self.manager.active, "view", None) and hasattr(self.manager.active.view, "_music_stop"):
                        self.manager.active.view._music_stop()
                except Exception:
                    pass
                # tell traffic generator to stop
                if not self._end_broadcasted:
                    try:
                        send_special_code(221, repeat=3, addr=self.state.addr, port=7500)
                    except Exception:
                        print("Failed to send end code 221")
                    self._end_broadcasted = True

            pygame.display.flip()

        # clean shutdown
        if hasattr(self, "receiver"):
            try:
                self.receiver.stop()
            except Exception:
                pass

        pygame.quit()
        sys.exit()


# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    App().run()