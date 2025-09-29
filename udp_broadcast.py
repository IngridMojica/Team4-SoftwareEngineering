# udp_broadcast.py
import socket
import time

# Send a single integer representing equipment ID
def send_equipment_id(equip_id: int, addr: str = "127.0.0.1", port: int = 7500):
    _send(str(equip_id), addr, port)

# Send attacker:hit. Optionally send attacker alone if same team
def send_hit(attacker_equip: int, hit_equip: int, same_team: bool = False, addr: str = "127.0.0.1", port: int = 7500):
    _send(f"{attacker_equip}:{hit_equip}", addr, port)
    if same_team:
        time.sleep(0.01)
        _send(str(attacker_equip), addr, port)

# Send a special code multiple times
def send_special_code(code: int, repeat: int = 1, addr: str = "127.0.0.1", port: int = 7500):
    for _ in range(max(1, repeat)):
        _send(str(code), addr, port)
        time.sleep(0.05)

# Low-level UDP send helper
def _send(msg: str, addr: str, port: int):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(msg.encode(), (addr, port))
        print(f"Sent '{msg}' to {addr}:{port}")
    finally:
        s.close()

# Quick test if running this file directly
if __name__ == "__main__":
    send_equipment_id(101, addr="127.0.0.1", port=7501)
    send_hit(12, 34, same_team=True, addr="127.0.0.1", port=7501)
    send_special_code(221, repeat=3, addr="127.0.0.1", port=7501)