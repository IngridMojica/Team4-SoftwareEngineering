# Team 4 – Laser Tag Game (Sprint 3)

This repository contains **Team 4’s Software Engineering Class Project** – a Laser Tag Game simulation that integrates:
- A database-backed Player Entry Screen  
- UDP broadcasting for equipment codes  
- Countdown Timer and Play Action Display  
- Install Script and setup documentation for testing on a VM  

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
- `src/ui/screens/play_display.py` → Play Action Display screen (countdown + team display).  
- `src/graphs/charts.py` → Team bar chart visualization.  
- `src/config.py` → Global constants (`TEAM_CAP`, window size, ports).  

### UI Widgets
- `src/ui/widgets/widgets_core.py` → Base widgets (`Label`, `Button`).  
- `src/ui/widgets/inputs.py` → Input widgets (`TextInput`, `TeamSelector`).  

### Networking & Database
- `udp_broadcast.py` → Sends equipment IDs, hits, and special codes over UDP.  
- `udp_receiver.py` → Listens for UDP messages and queues them for processing.  
- `db_players.py` → Handles PostgreSQL player insertion and codename lookup.  

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
- Duplicate and capacity checks (uses `TEAM_CAP = 15`)  
- Database insert and lookup via `db_players.py`  
- UDP broadcast of equipment ID after adding a player  

### Keyboard Shortcuts
| Key | Action |
|------|--------|
| **TAB** | Cycle between fields (Player ID → Name → Equip) |
| **F12** | Clear form inputs |
| **F5** | Start game / switch to Play Action Display |
| **ESC** | Exit application |

### Play Action Display
- Displays team rosters after game start.  
- Countdown timer before play begins.  
- Live chart of team sizes.  

### Database Integration
- PostgreSQL database (`photon`) with `players(id, codename)` table.  
- Insert only if ID not already exists.  
- Simple testing via `test_players.py`.  

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