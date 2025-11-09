# src/ui/screens/play_display.py
import os
import pygame
import random
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
FLASH_COLOR = (255, 235, 59)

FLASH_PERIOD = 0.5
HEADER_H = 44
EVENT_H = 0.20
TITLE_Y = 4
ROW_minH = 20
ROW_maxH = 26
TEAM_ROWS = 15
PAD = 16
GAP = 10

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
        self.font = pygame.font.SysFont("Arial", 16)
        self.font_hdr = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_title = pygame.font.SysFont("Arial", 26, bold=True)
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

        # music flag
        self._playing_music = False

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

    def _music_start(self):
        random_number = random.randint(1, 8)
        print(f"now playing: {random_number}.mp3")
        song_path = os.path.expanduser(f"assets/music/{random_number}.mp3")
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        # pygame.mixer.music.set_volume(0.5) # Uncomment + Adjust if too loud
    
    def _music_stop(self):
        pygame.mixer.music.stop()

    def update(self, dt: float):
        # nothing to do if countdown isn't active
        if not self._countdown_running or self._countdown_finished:
            return

        # compute elapsed seconds
        now = time.monotonic()
        elapsed = now - self._countdown_start if self._countdown_start is not None else 0.

        # Start at 17
        if (elapsed // 1) == 13 and not self._playing_music:
            print("Starting background music...")
            self._playing_music = True
            self._music_start()

        # if not self._playing_music:
        #     self._music_stop()

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
        Restarts the pre-game countdown and resets music flag every time the screen is entered.
        """
        self._countdown_running = True
        self._countdown_start = time.monotonic()
        self._countdown_finished = False
        self._sent_start_code = False
        self._sent_end_code = False
        self._playing_music = False

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
                    print("Stopping background music...")
                    self._music_stop()
                    manager.switch_to("player_entry")
                return

    def draw(self, surface: pygame.Surface):
        #self._ensure_layout(surface)
        surface.fill(BG)

        # --- compute layout up front so team panels don't overlap the event box ---
        full_w, full_h = surface.get_size()
        event_h = max(72, int(full_h * EVENT_H))
        event_rect = pygame.Rect(PAD, full_h - PAD - event_h, full_w - PAD*2, event_h)

        total_w = full_w - (PAD * 2) - GAP
        panel_w = total_w // 2
        panel_h = full_h - (PAD * 3) - event_h   # <-- reserve vertical space for event panel
        self.left_rect  = pygame.Rect(PAD, PAD, panel_w, panel_h)
        self.right_rect = pygame.Rect(PAD + panel_w + GAP, PAD, panel_w, panel_h)

        # Build live lists from state.players (expected: dict pid -> {codename, team, equip, hardware_id?})
        players_dict = getattr(self.state, "players", {}) or {}
        red, green = [], []
        red_total, green_total = 0, 0

        for pid, pdata in players_dict.items():
            team = _norm_team(_get(pdata, "team"))

            try:
                score_value = int(_get(pdata, "score") or 0)
            except ValueError:
                score_value = 0

            row = {
                "codename": _get(pdata, "codename"),
                "equip_id": _get(pdata, "equip"),
                #"score": _get(pdata, "score") or "0", # score is going to default to 0 for now
                "score": str(score_value),
                "has_base": (pdata.get("has_base") if isinstance(pdata, dict) else getattr(pdata, "has_base", False)) or False,
            }

            if team == "Red":
                red.append(row)
                red_total += score_value
            elif team == "Green":
                green.append(row)
                green_total += score_value

        #sort players from high to low within each team
        red.sort(key=lambda r: int(r["score"]), reverse=True)
        green.sort(key=lambda r: int(r["score"]), reverse=True)

        #score flashing
        flash_red = red_total > green_total
        flash_green = green_total > red_total

        # draw both panels (left then right)
        self._draw_panel(surface, self.left_rect, "Red", red, TEAM_CAP, RED_ACCENT, team_score = red_total, flash = flash_red)
        self._draw_panel(surface, self.right_rect, "Green", green, TEAM_CAP, GREEN_ACCENT, team_score=green_total, flash=flash_green)

        # draw a simple "Current Game Action" area across the bottom quarter
        #full_w, full_h = surface.get_size()
        #event_h = max(80, full_h // 4) # bottom quarter, min 80px
        #event_rect = pygame.Rect(PAD, full_h - PAD - event_h, full_w - PAD*2, event_h)

        line_h = 22
        max_lines = (event_rect.height - (PAD * 2) - 8)
        events = list(getattr(self.state, "event_log", []))[-max_lines:]
        start_y = event_rect.bottom - PAD - (len(events) * line_h)
        x = event_rect.x + PAD
        y = max(event_rect.y + PAD + 28, start_y)

        for e in events:
            txt = e["text"] if isinstance(e, dict) else str(e)
            txt = self._ellipsize(txt, event_rect.width - PAD * 2, self.font)
            surface.blit(self.font.render(txt, True, TEXT), (x, y))
            y += line_h

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

    def _draw_panel(self, surface, rect, team_name, rows, cap, accent, *, team_score = 0, flash=False):
        # Panel background
        pygame.draw.rect(surface, PANEL, rect, border_radius=12)

        # Title with count
        title = f"{team_name}  ({len(rows)}/{cap})"
        title_surf = self.font_title.render(title, True, accent)
        title_pos = (rect.x + PAD, rect.y + PAD)
        surface.blit(title_surf, title_pos)

        #Score text
        score_text = f"Score: {team_score}"
        blink_on = flash and (int(time.monotonic() / FLASH_PERIOD) % 2 == 0)
        score_color = FLASH_COLOR if blink_on else TEXT
        score_surf = self.font_title.render(score_text, True, score_color)
        surface.blit(score_surf, (title_pos[0] + title_surf.get_width() + 14, title_pos[1]))

        # Layout metrics
        header_y = title_pos[1] + title_surf.get_height() + TITLE_Y
        avail_w = rect.width - (PAD * 2)

        # --- variable-width columns with 3-space gaps ---
        col_boxes_rel, gap_px = self._measure_columns(rows, avail_w)
        # Convert relative boxes (starting from 0) to absolute positions within the panel
        col_boxes_abs = [(rect.x + PAD + x_rel, w) for (x_rel, w) in col_boxes_rel]

        # Column headers (centered)
        for (label, (x_start, w)) in zip(COLUMNS, col_boxes_abs):
            self._blit_centered(surface, self.font_hdr, label, x_start, w, header_y, self.font_hdr.get_height())

        #autosize rows
        rows_target = max(TEAM_ROWS, len(rows))
        top_hearders = header_y + self.font_hdr.get_height() + GAP
        height_avail = (rect.bottom - PAD) - top_hearders
        row_h = int(max(ROW_minH, min(ROW_maxH, height_avail/rows_target)))

        # Lazy load and scale the base icon
        if self._base_icon is None:
            try:
                raw = pygame.image.load("assets/baseicon.jpg").convert_alpha()
                # scale so height fits inside row
                icon_h = max(16, row_h - 8)
                scale = icon_h / raw.get_height()
                icon_w = max(16, int(raw.get_width() * scale))
                self._base_icon = pygame.transform.smoothscale(raw, (icon_w, icon_h))
            except Exception:
                self._base_icon = None

        # Rows (centered within each variable-width column)
        row_y = top_hearders
        #for r in rows:
         #   cells = [r["has_base"], r["codename"], r["equip_id"], r["score"]]
          #  for(x_start, w), cell in zip(col_boxes_abs, cells):
           #     self._blit_centered(surface, self.font, cell, x_start, w, row_y, row_h)
            #row_y += row_h
            #if row_y > rect.bottom - PAD:
             #   break


        for r in rows:
            # Draw base icon (first column) if player has it
            base_idx = 0
            if r.get("has_base") and self._base_icon is not None:
                x_start, w = col_boxes_abs[base_idx]
                ix = x_start + (w - self._base_icon.get_width()) // 2
                iy = row_y + (row_h - self._base_icon.get_height()) // 2
                surface.blit(self._base_icon, (ix, iy))
                    
            cells = [r["codename"], r["equip_id"], r["score"]]
            for (x_start, w), cell in zip(col_boxes_abs[1:], cells):
                self._blit_centered(surface, self.font, cell, x_start, w, row_y, row_h)
            row_y += row_h
            if row_y > rect.bottom - PAD:
                break
