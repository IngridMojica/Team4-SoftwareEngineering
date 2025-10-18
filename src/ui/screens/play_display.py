# src/ui/screens/play_display.py
import pygame

# Try to read TEAM_CAP from your project config; fall back to 6 if not present.
try:
    from src.ui.config import TEAM_CAP  # if your team defined it here
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
COLUMNS = ["ID", "Codename", "Equip ID", "Hardware ID"]


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
        pass

    def draw(self, surface: pygame.Surface):
        self._ensure_layout(surface)
        surface.fill(BG)

        # Build live lists from state.players (expected: dict pid -> {codename, team, equip, hardware_id?})
        players_dict = getattr(self.state, "players", {}) or {}
        red, green = [], []
        for pid, pdata in players_dict.items():
            team = _norm_team(_get(pdata, "team"))
            row = {
                "id": pid,
                "codename": _get(pdata, "codename"),
                "equip_id": _get(pdata, "equip"),
                "hardware_id": _get(pdata, "hardware_id"),
            }
            if team == "Red":
                red.append(row)
            elif team == "Green":
                green.append(row)

        self._draw_panel(surface, self.left_rect, "Red", red, TEAM_CAP, RED_ACCENT)
        self._draw_panel(surface, self.right_rect, "Green", green, TEAM_CAP, GREEN_ACCENT)

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
            cells = [r["id"], r["codename"], r["equip_id"], r["hardware_id"]]
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

        # Rows (centered within each variable-width column)
        row_y = header_y + HEADER_H
        for r in rows:
            cells = [r["id"], r["codename"], r["equip_id"], r["hardware_id"]]
            for (x_start, w), cell in zip(col_boxes_abs, cells):
                self._blit_centered(surface, self.font, cell, x_start, w, row_y, ROW_H)
            row_y += ROW_H
            if row_y > rect.bottom - PAD:
                break

        # Footer hint
        hint = "F5 to open Play • Esc to exit"
        surface.blit(self.font.render(hint, True, MUTED), (rect.x + PAD, rect.bottom - PAD - 18))