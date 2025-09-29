# Files in this branch (udp)

    udp_broadcast.py: send_equipment_id, send_hit, send_special_code
    udp_receiver.py: Receiver class, start_receiver() / stop(), get_message_nowait()

# Ports & addresses (defaults)

    Send (outgoing → traffic generator / game): 127.0.0.1:7500
    Receive (incoming events): bind 0.0.0.0:7501

# Message formats

    Incoming (from devices / trafficgenerator): "attacker:hit" (e.g. 12:34) or sometimes single integer.
    Outgoing (reply): single integer string — equipment id of player who got hit (e.g. "34").
    Special codes: 202 = start, 221 = game end (send 221 three times).

# Run a quick test

    Start receiver (terminal A):
        python udp_receiver.py

    Run broadcast (terminal B) - this will send a sequence of packets:
        python udp_broadcast.py