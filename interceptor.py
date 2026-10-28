import socket
import re
import json
import random
import time
from pathlib import Path

CODES_FILE = Path("codes.json")
EXPIRY_MINUTES = 120

PATTERN =  re.compile(r"\bLOCAL\b", re.IGNORECASE)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 9100))
server.listen(5)
print("Escuchando en el puerto 9100...")

def load_codes():
    if CODES_FILE.exists():
        return json.loads(CODES_FILE.read_text())
    return []

def save_codes(codes):
    CODES_FILE.write_text(json.dumps(codes, indent=2))
    
def gen_code():
    codes = load_codes()
    new = {
        "code": f"{random.randint(0, 999999):06d}",
        "expire": time.time() + EXPIRY_MINUTES * 60,
    }
    codes.append(new)
    save_codes(codes)
    print(f"Código generado: {new['code']}") 
    
    return new

while True:
    conn, addr = server.accept()
    data = conn.recv(4096).decode(errors="ignore")
    print(f"Ticket recibido:\n{data}")
    if PATTERN.search(data):
        new = gen_code()
        respuesta = f"OK|{new['code']}|{new['expire']}"
    else:
        respuesta = "IGNORADO"
        print("No es un pedido local, ignoramos.")
    conn.sendall(respuesta.encode())
    conn.close()