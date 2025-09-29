# udp_receiver.py
import socket
import threading
import queue
from typing import Optional, Tuple

BUFFER_SIZE = 1024

class Receiver:
    def __init__(self, bind_addr: str = "0.0.0.0", port: int = 7501):
        self.bind_addr = bind_addr
        self.port = port
        self._sock = None
        self._queue = queue.Queue()
        self._running = False
    
    # Start the receiver in a background thread
    def start(self):
        if self._running:
            return
        self._running = True
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()
        print(f"Receiver started on {self.bind_addr}:{self.port}")

    # Stop the receiver
    def stop(self):
        self._running = False
        if self._sock:
            self._sock.close()
        print("Receiver stopped")

    def _loop(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((self.bind_addr, self.port))
        self._sock.settimeout(0.5)
        while self._running:
            try:
                data, addr = self._sock.recvfrom(BUFFER_SIZE)
                msg = data.decode().strip()
                if self._validate(msg):
                    self._queue.put((msg, addr))
                    print(f"Received '{msg}' from {addr}")
            except socket.timeout:
                continue
            except OSError:
                break # socket closed

    # Return the next message in the queue if available
    def get_message_nowait(self) -> Optional[Tuple[str, Tuple[str,int]]]:
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    # Check that message is int or int:int
    @staticmethod
    def _validate(msg: str) -> bool:
        parts = msg.split(":")
        if len(parts) == 1:
            return parts[0].isdigit()
        if len(parts) == 2:
            return all(p.isdigit() for p in parts)
        return False

def start_receiver(bind_addr: str = "0.0.0.0", port: int = 7501) -> Receiver:
    r = Receiver(bind_addr, port)
    r.start()
    return r

# Quick test if running this file directly
if __name__ == "__main__":
    receiver = start_receiver()
    try:
        import time
        while True:
            msg = receiver.get_message_nowait()
            time.sleep(0.1)
    except KeyboardInterrupt:
        receiver.stop()