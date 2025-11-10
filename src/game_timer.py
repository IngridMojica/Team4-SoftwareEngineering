# src/game_timer.py
from enum import Enum
import time

class GameState(Enum):
    LOBBY = "LOBBY"
    COUNTDOWN = "COUNTDOWN"
    PLAYING = "PLAYING"
    ENDED = "ENDED"

class GameTimer:
    def __init__(self, start_countdown=30, play_seconds=6*60):
        self.state = GameState.LOBBY
        self.start_countdown_total = int(start_countdown)
        self.play_total = int(play_seconds)
        self._t0 = None  # when current phase started

    # ---- phase control ----
    def start_countdown(self):
        self.state = GameState.COUNTDOWN
        self._t0 = time.monotonic()

    def start_gameplay(self):
        self.state = GameState.PLAYING
        self._t0 = time.monotonic()

    def end_game(self):
        self.state = GameState.ENDED
        self._t0 = None

    # ---- timing helpers ----
    def _elapsed(self) -> int:
        return int(time.monotonic() - self._t0) if self._t0 is not None else 0

    def remaining_seconds(self) -> int:
        if self.state == GameState.COUNTDOWN:
            return max(0, self.start_countdown_total - self._elapsed())
        if self.state == GameState.PLAYING:
            return max(0, self.play_total - self._elapsed())
        return 0

    def tick(self):
        """Call this once per frame / loop to advance state."""
        if self.state == GameState.COUNTDOWN and self.remaining_seconds() == 0:
            self.start_gameplay()
        elif self.state == GameState.PLAYING and self.remaining_seconds() == 0:
            self.end_game()

    # ---- label for UI ----
    def label(self) -> str:
        if self.state == GameState.COUNTDOWN:
            return f"Game starts in: {self.remaining_seconds():02d}s"
        if self.state == GameState.PLAYING:
            s = self.remaining_seconds()
            return f"Time: {s//60}:{s%60:02d}"
        if self.state == GameState.ENDED:
            return "Game Over"
        return "Waiting…"