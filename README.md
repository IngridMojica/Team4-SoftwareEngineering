# UI & Widgets – Player Entry Screen (feature/ui-entry-widgets)

This branch implements the **UI components** for the Player Entry screen.

## Files Created
- `src/ui/widgets/widgets_core.py` → Base widgets (`Label`, `Button`)
- `src/ui/widgets/inputs.py` → Input widgets (`TextInput`, `TeamSelector`)
- `src/ui/screens/player_entry.py` → Main Player Entry screen logic
- `src/config.py` → Added initial config constants (`TEAM_CAP = 15`, window size, default ports)

## Features Implemented
- **Player Entry Form**
  - Player ID (numeric only)
  - Codename (text input)
  - Equipment ID (numeric only)
  - Team selector (Red / Green, highlights selected team)
- **Add Player Button**
  - Validates inputs
  - Enforces team capacity (`TEAM_CAP = 15`)
  - Adds player to in-memory state
  - Stubbed DB/UDP integration (works even if DB/UDP not ready)
- **Keyboard Shortcuts**
  - `TAB`: cycle between fields
  - `F12`: clear form
  - `F5`: trigger start callback
- **Team Counts**
  - Updates live in the chart
  - Shows “team is full” message when reaching the cap

## Notes for Integration
- `config.py` is **shared**; other teammates should add DB/UDP constants here if needed.
- DB and UDP functions are **stubbed by default** if the real modules aren’t available.
- My part is focused only on **UI & widgets**. Database, networking, and graphs are handled by other teammates.
