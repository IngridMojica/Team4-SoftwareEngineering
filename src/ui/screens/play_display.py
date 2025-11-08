# src/ui/screens/play_display.py
import pygame
import time
from udp_broadcast import send_special_code

# Try to read TEAM_CAP from your project config; fall back to 6 if not present.
try:
    from src.config import TEAM_CAP  # if your team defined it here
except Exception:
    TEAM_CAP = 6

# Colors & layout
BG = (18, 18, 22)
PANEL = (28, 28, 36)
TEXT = (235, 235, 245)
MUTED = (170, 170, 180)
RED_ACCENT = (220, 70, 70)
GREEN_ACCENT = (70, 200, 120)

HEADER_H = 44
ROW_H = 28
PAD = 16
GAP = 24

# Column labels (variable-width columns; 3-space gaps)
COLUMNS = ["Base", "Codename", "Equip ID", "Score"]


def _norm_team(t: str) -> str:
    t = (t or "").strip().lower()
    if t.startswith("r"):
        return "Red"
    if t.startswith("g"):
        return "Green"
    return "Unassigned"


def _get(d, key, default=""):
    """Works with dict-like or object players; returns str."""
    try:
        v = d.get(key, default)
    except AttributeError:
        v = getattr(d, key, default)
    return "" if v is None else str(v)


class PlayDisplay:
    """Play screen view: shows Red/Green panels reading live from state.players."""
    def __init__(self, state):
        self.state = state
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 18)
        self.font_hdr = pygame.font.SysFont("Arial", 19, bold=True)
        self.font_title = pygame.font.SysFont("Arial", 22, bold=True)
        self._layout_ready = False
        
        # Countdown
        self._countdown_steps = 30 # countdown from 30 to 1
        self._step_seconds = 1.0  # each number lasts about 1s
        self._go_seconds = 1.0    # show "GO!" for 1s
        self._countdown_total = self._countdown_steps * self._step_seconds + self._go_seconds

        # runtime flags
        self._countdown_running = False
        self._countdown_start = None
        self._countdown_finished = False
        self._sent_start_code = False
        self._sent_end_code = False

        # fonts for overlay
        self._overlay_big_font = None
        self._overlay_small_font = None

        # back button state
        self._back_button_rect = None
        self._back_button_text = "Back to Player Entry"
        self._back_button_font = None

        # base icon
        self._base_icon = None

    # ---------- text helpers for clean alignment ----------
    def _ellipsize(self, text: str, max_w: int, font) -> str:
        """Return text that fits within max_w, using … if needed."""
        text = "" if text is None else str(text)
        if max_w <= 0:
            return ""
        if font.size(text)[0] <= max_w:
            return text
        # If even an ellipsis won't fit, show nothing
        ell = "…"
        if max_w <= font.size(ell)[0]:
            return ""
        ell_w = font.size(ell)[0]
        lo, hi = 0, len(text)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if font.size(text[:mid])[0] + ell_w <= max_w:
                lo = mid
            else:
                hi = mid - 1
        return text[:lo] + ell

    def _blit_centered(self, surface, font, text, box_x, box_w, box_y, box_h):
        safe = self._ellipsize(text, max(0, box_w), font)
        surf = font.render(safe, True, TEXT)
        cx = box_x + box_w / 2
        cy = box_y + box_h / 2
        rect = surf.get_rect(center=(cx, cy))
        surface.blit(surf, rect)

    def _ensure_layout(self, surface: pygame.Surface):
        if self._layout_ready:
            return
        w, h = surface.get_size()
        total_w = w - (PAD * 2) - GAP
        panel_w = total_w // 2
        panel_h = h - (PAD * 2)
        self.left_rect = pygame.Rect(PAD, PAD, panel_w, panel_h)
        self.right_rect = pygame.Rect(PAD + panel_w + GAP, PAD, panel_w, panel_h)
        self._layout_ready = True

    def update(self, dt: float):
        # nothing to do if countdown isn't active
        if not self._countdown_running or self._countdown_finished:
            return

        # compute elapsed seconds
        now = time.monotonic()
        elapsed = now - self._countdown_start if self._countdown_start is not None else 0.0

        # once countdown finishes, mark and send start code
        if elapsed >= self._countdown_total:
            if not self._countdown_finished:
                self._countdown_finished = True
                # broadcast the start code 202
                if not self._sent_start_code:
                    try:
                        send_special_code(202, repeat=1, addr="127.0.0.1", port=7500)
                    except Exception as e:
                        print("Failed to send start code 202")
                    self._sent_start_code = True
            return
        
        # when 6 minute gameplay timer finishes, send end code
        #if gameplay_elapsed >= GAME_DURATION_SECONDS and not self._sent_end_code:
            #self.send_game_end()
    
    def enter(self):
        """
        Restarts the pre-game countdown every time the screen is entered.
        """
        self._countdown_running = True
        self._countdown_start = time.monotonic()
        self._countdown_finished = False
        self._sent_start_code = False
        self._sent_end_code = False

    def send_game_end(self):
        """
        Send game end code 221 three times to configured UDP target.
        """
        if self._sent_end_code:
            return
        addr = getattr(self.state, "addr", "127.0.0.1")
        try:
            send_special_code(221, repeat=3, addr=addr, port=7500)
        except Exception:
            print("Failed to send game end code 221")
        self._sent_end_code = True

    def handle_event(self, event, manager=None):
        """
        Handle input events. 
        If the Back button is clicked switch back to the player entry screen.
        """
        # check left-click in button rect
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self._back_button_rect and self._back_button_rect.collidepoint(pos):
                if manager:
                    manager.switch_to("player_entry")
                return

    def draw(self, surface: pygame.Surface):
        self._ensure_layout(surface)
        surface.fill(BG)

        # Build live lists from state.players (expected: dict pid -> {codename, team, equip, hardware_id?})
        players_dict = getattr(self.state, "players", {}) or {}
        red, green = [], []
        for pid, pdata in players_dict.items():
            team = _norm_team(_get(pdata, "team"))
            row = {
                "codename": _get(pdata, "codename"),
                "equip_id": _get(pdata, "equip"),
                "score": _get(pdata, "score") or "0", # score is going to default to 0 for now
                "has_base": (pdata.get("has_base") if isinstance(pdata, dict) else getattr(pdata, "has_base", False)) or False,
            }
            if team == "Red":
                red.append(row)
            elif team == "Green":
                green.append(row)

        # draw both panels (left then right)
        self._draw_panel(surface, self.left_rect, "Red", red, TEAM_CAP, RED_ACCENT)
        self._draw_panel(surface, self.right_rect, "Green", green, TEAM_CAP, GREEN_ACCENT)

        # draw a simple "Current Game Action" area across the bottom quarter
        full_w, full_h = surface.get_size()
        event_h = max(80, full_h // 4) # bottom quarter, min 80px
        event_rect = pygame.Rect(PAD, full_h - PAD - event_h, full_w - PAD*2, event_h)
        # background + border
        pygame.draw.rect(surface, PANEL, event_rect, border_radius=8)
        pygame.draw.rect(surface, MUTED, event_rect, width=1, border_radius=8)
        # header text
        header_surf = self.font_hdr.render("Current Game Action", True, TEXT)
        surface.blit(header_surf, (event_rect.x + PAD, event_rect.y + PAD))

        # ---------------- Countdown overlay ----------------
        if self._countdown_running and not self._countdown_finished:
            if self._overlay_big_font is None:
                w, h = surface.get_size()
                size = max(48, int(min(w, h) * 0.22))
                self._overlay_big_font = pygame.font.SysFont("Arial", size, bold=True)
            if self._overlay_small_font is None:
                self._overlay_small_font = pygame.font.SysFont("Arial", 20)

            # translucent overlay across full screen
            overlay = pygame.Surface(surface.get_size(), flags=pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 190))
            surface.blit(overlay, (0, 0))

            now = time.monotonic()
            elapsed = now - self._countdown_start if self._countdown_start is not None else 0.0

            # determine which label to show
            if elapsed < self._countdown_steps * self._step_seconds:
                idx = int(elapsed // self._step_seconds)
                label = str(self._countdown_steps - idx)
            elif elapsed < self._countdown_total:
                label = "GO!"
            else:
                label = "" # finished; update() will flip finished flag

            if label:
                big_surf = self._overlay_big_font.render(label, True, TEXT)
                big_rect = big_surf.get_rect(center=(full_w // 2, full_h // 2))
                surface.blit(big_surf, big_rect)
                small = self._overlay_small_font.render("Get ready!", True, MUTED)
                small_rect = small.get_rect(center=(full_w // 2, big_rect.bottom + 28))
                surface.blit(small, small_rect)

        # After countdown finishes, show a subtle "Game started!" status for visual confirmation
        if self._countdown_finished:
            started_surf = self.font.render("Game started!", True, (0,255,255))
            surface.blit(started_surf, (full_w - started_surf.get_width() - 12, 8))
        
        # draw back button to go back to player entry
        btn_w, btn_h = 190, 34
        btn_x, btn_y = full_w - PAD - btn_w, full_h - PAD - btn_h
        self._back_button_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        if self._back_button_font is None:
            self._back_button_font = pygame.font.SysFont("Arial", 18, bold=True)

        pygame.draw.rect(surface, PANEL, self._back_button_rect, border_radius=8)  # button background
        pygame.draw.rect(surface, MUTED, self._back_button_rect, width=1, border_radius=8)  # outline
        label_surf = self._back_button_font.render(self._back_button_text, True, TEXT)
        label_rect = label_surf.get_rect(center=self._back_button_rect.center)
        surface.blit(label_surf, label_rect)

    # ---------------- helpers ----------------

    def _measure_columns(self, rows, avail_w):
        """
        Compute variable-width columns based on pixel widths of headers and cell contents.
        Columns are separated by an exact 3-space gap (in pixels). Everything is centered.
        If total required width exceeds avail_w, columns are scaled proportionally.
        """
        # 3 spaces "gap" measured in pixels (using body font for consistency)
        gap_px = self.font.size("   ")[0]
        n = len(COLUMNS)

        # Measure required width for each column (max of header vs. content)
        col_required = [0] * n
        # Include a small inner breathing room so text doesn't kiss the box edges
        inner_pad_px = self.font.size(" ")[0]  # roughly one space as inner pad

        # Start with header widths
        for i, label in enumerate(COLUMNS):
            col_required[i] = max(col_required[i], self.font_hdr.size(label)[0])

        # Include cell widths
        for r in rows:
            cells = ["", r["codename"], r["equip_id"], r["score"]]
            for i, val in enumerate(cells):
                w = self.font.size("" if val is None else str(val))[0]
                if w > col_required[i]:
                    col_required[i] = w

        # Add inner padding on both sides inside each column box
        col_required = [w + inner_pad_px * 2 for w in col_required]

        total_gaps = gap_px * (n - 1)
        total_required = sum(col_required) + total_gaps

        # If it fits, done. Otherwise scale columns proportionally to fit.
        if total_required > avail_w and sum(col_required) > 0:
            scale = (avail_w - total_gaps) / max(1, sum(col_required))
            # Prevent negative/zero widths
            col_required = [max(10, int(w * scale)) for w in col_required]

        # Compute x positions for each column box
        boxes = []
        x = 0
        for i, w in enumerate(col_required):
            boxes.append((x, w))
            x += w
            if i < n - 1:
                x += gap_px  # 3-space gap

        return boxes, gap_px

    def _draw_panel(self, surface, rect, team_name, rows, cap, accent):
        # Panel background
        pygame.draw.rect(surface, PANEL, rect, border_radius=12)

        # Title with count
        title = f"{team_name}  ({len(rows)}/{cap})"
        surface.blit(self.font_title.render(title, True, accent), (rect.x + PAD, rect.y + PAD))

        # Layout metrics
        header_y = rect.y + PAD + 36
        avail_w = rect.width - (PAD * 2)

        # --- variable-width columns with 3-space gaps ---
        col_boxes_rel, gap_px = self._measure_columns(rows, avail_w)
        # Convert relative boxes (starting from 0) to absolute positions within the panel
        col_boxes_abs = [(rect.x + PAD + x_rel, w) for (x_rel, w) in col_boxes_rel]

        # Column headers (centered)
        for (label, (x_start, w)) in zip(COLUMNS, col_boxes_abs):
            self._blit_centered(surface, self.font_hdr, label, x_start, w, header_y, 20)

        # Lazy load and scale the base icon
        if self._base_icon is None:
            try:
                raw = pygame.image.load("assets/baseicon.jpg").convert_alpha()
                # scale so height fits inside row
                icon_h = max(16, ROW_H - 8)
                scale = icon_h / raw.get_height()
                icon_w = max(16, int(raw.get_width() * scale))
                self._base_icon = pygame.transform.smoothscale(raw, (icon_w, icon_h))
            except Exception:
                self._base_icon = None

        # Rows (centered within each variable-width column)
        row_y = header_y + HEADER_H
        for r in rows:
            # Draw base icon (first column) if player has it
            base_idx = 0
            if r.get("has_base") and self._base_icon is not None:
                x_start, w = col_boxes_abs[base_idx]
                ix = x_start + (w - self._base_icon.get_width()) // 2
                iy = row_y + (ROW_H - self._base_icon.get_height()) // 2
                surface.blit(self._base_icon, (ix, iy))
                    
            cells = [r["codename"], r["equip_id"], r["score"]]
            for (x_start, w), cell in zip(col_boxes_abs[1:], cells):
                self._blit_centered(surface, self.font, cell, x_start, w, row_y, ROW_H)
            row_y += ROW_H
            if row_y > rect.bottom - PAD:
                break
