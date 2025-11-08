# packet_handler.py
def _find_pid_by_equip(state, equip_id):
    """Return player PID for given equipment id, or None."""
    for pid, pdata in (state.players or {}).items():
        try:
            if int(pdata.get("equip")) == int(equip_id):
                return pid
        except Exception:
            pass
    return None

def handle_packet(msg: str, state, udp_send=None):
    """
    Minimal packet handler for incoming UDP messages.
    msg: string like "12:34" or "123"
    udp_send(equip_id) is optional callback to send numeric replies (function(equip_id:int))
    """
    if not msg:
        return

    msg = msg.strip()
    # handle attacker:target style
    if ":" in msg:
        parts = msg.split(":")
        if len(parts) != 2:
            return
        a_str, b_str = parts[0].strip(), parts[1].strip()
        # base scoring codes
        if b_str in ("43", "53"):
            try:
                attacker_equip = int(a_str)
            except ValueError:
                return
            pid = _find_pid_by_equip(state, attacker_equip)
            if pid is None:
                return
            # determine which base was hit
            code = int(b_str)
            # 53 -> red base scored => green attacker gets credit
            if code == 53:
                if state.players[pid].get("team", "").lower().startswith("g"):
                    state.players[pid]["score"] = int(state.players[pid].get("score", 0)) + 100
                    state.players[pid]["has_base"] = True
            # 43 -> green base scored => red attacker gets credit
            elif code == 43:
                if state.players[pid].get("team", "").lower().startswith("r"):
                    state.players[pid]["score"] = int(state.players[pid].get("score", 0)) + 100
                    state.players[pid]["has_base"] = True
            # reply with attacker equip id if udp_send provided
            if udp_send:
                try:
                    udp_send(attacker_equip)
                except Exception:
                    pass
            return

        # normal tag a:b
        try:
            attacker_equip = int(a_str)
            hit_equip = int(b_str)
        except ValueError:
            return

        attacker_pid = _find_pid_by_equip(state, attacker_equip)
        hit_pid = _find_pid_by_equip(state, hit_equip)

        if attacker_pid and hit_pid:
            att_team = (state.players[attacker_pid].get("team") or "").lower()
            hit_team = (state.players[hit_pid].get("team") or "").lower()
            # opposing teams => attacker gains +10
            if (att_team and hit_team) and (att_team != hit_team):
                state.players[attacker_pid]["score"] = int(state.players[attacker_pid].get("score", 0)) + 10
                # reply with hit equipment id
                if udp_send:
                    try:
                        udp_send(hit_equip)
                    except Exception:
                        pass
            else:
                # friendly fire: both lose 10, send two transmissions:
                state.players[attacker_pid]["score"] = int(state.players[attacker_pid].get("score", 0)) - 10
                state.players[hit_pid]["score"] = int(state.players[hit_pid].get("score", 0)) - 10
                if udp_send:
                    try:
                        udp_send(hit_equip) # equipment id of player who got hit
                        udp_send(attacker_equip) # equipment id of attacker
                    except Exception:
                        pass
        return

    # single integer packet (someone reported they were hit)
    try:
        val = int(msg)
    except ValueError:
        return
    # when data is received, software broadcasts equipment id of the hit player
    if udp_send:
        try:
            udp_send(val)
        except Exception:
            pass