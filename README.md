# Team 4 – Laser Tag Game (Sprint 3–4)

This repository contains **Team 4’s Software Engineering Class Project** – a Laser Tag Game simulation that integrates:
- A database-backed Player Entry Screen  
- UDP broadcasting for equipment codes  
- Countdown Timer, Game Timer, and Play Action Display  
- Live “Current Game Action” log  
- Install script and setup documentation for testing on a VM  

---

## Team Members

| Real Name | GitHub Username |
|------------|----------------|
| Ruben Priest | ruben-priest |
| Tyler Bean | FreezyMK1 |
| Timothy Shtunyuk | tshtu21 |
| Diego Peredo | diegop-sys |
| Ingrid Mojica | IngridMojica |

---

## Files & Modules

### Core Application
- `main.py` → Main app loop, screen management, and entry point.  
- `src/ui/screens/player_entry.py` → Player Entry UI (screen logic, DB + UDP integration).  
- `src/ui/screens/play_display.py` → Play Action Display screen (countdown + game timer + event log).  
- `src/graphs/charts.py` → Team bar chart visualization.  
- `src/config.py` → Global constants (`TEAM_CAP`, window size, ports).  
- `src/game_timer.py` → Handles in-game timer and Game Over state logic (Sprint 4).  

### UI Widgets
- `src/ui/widgets/widgets_core.py` → Base widgets (`Label`, `Button`).  
- `src/ui/widgets/inputs.py` → Input widgets (`TextInput`, `TeamSelector`).  

### Networking & Database
- `udp_broadcast.py` → Sends equipment IDs, hits, and special codes over UDP.  
- `udp_receiver.py` → Listens for UDP messages and queues them for processing.  
- `db_players.py` → Handles PostgreSQL player insertion and codename lookup.  
- `udp_files/python_trafficgenerator_v2.py` → Simulates UDP events (e.g., hits and game signals).  

### DevOps & Docs
- `install.sh` → Automated setup script for VMs and local testing.  
- `requirements.txt` → Python dependencies (`pygame`, `psycopg2-binary`).  
- `README.md` → Installation, usage, and submission instructions.  

---

## Features Implemented

### Player Entry Screen
- Player ID (numeric only)  
- Codename (text input)  
- Equipment ID (numeric only)  
- Team selector (Red / Green)  
- Duplicate and capacity checks (using `TEAM_CAP = 15`)  
- Database insert and lookup via `db_players.py`  
- UDP broadcast of equipment ID after adding a player  

### Keyboard Shortcuts
| Key | Action |
|------|--------|
| **TAB** | Cycle between fields (Player ID → Name → Equip) |
| **F12** | Clear form inputs |
| **F5** | Start game / switch to Play Action Display |
| **ESC** | Exit application |

### Play Action Display (Sprint 4 Update)
- Displays team rosters after game start.  
- Countdown before game begins.  
- In-game timer visible throughout the match.  
- Real-time event log shown in “Current Game Action” box (e.g., hits, scoring events).  
- Game Over state stops timer and freezes scores.  
- Live chart of team sizes remains active until end.  

### Database Integration
- PostgreSQL database (`photon`) with `players(id, codename)` table.  
- Insert only if ID does not already exist.  
- Simple testing via `test_db_players.py`.  

### UDP Networking
- **Send:** `127.0.0.1:7500`  
- **Receive:** `0.0.0.0:7501`  
- Message formats:
  - `attacker:hit` (e.g. `12:34`)  
  - Single equipment ID (e.g. `101`)  
  - Special codes: `202` = start game, `221` = end game  

---

## Installation

### Option 1 – Quick VM Setup
```bash
git clone https://github.com/IngridMojica/Team4-SoftwareEngineering.git
cd Team4-SoftwareEngineering
chmod +x install.sh
./install.sh