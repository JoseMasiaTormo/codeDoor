import json
import time
from pathlib import Path

CODES_FILE = Path("codes.json")

def load_codes():
    if CODES_FILE.exists():
        return json.loads(CODES_FILE.read_text())
    return []

def main():
    print("==== PANEL DE ACCESO AL BAÑO ====")
    while True:
        code = input("\nIntroduce código (o 'salir'): ").strip()
        if code.lower() == "salir":
            break
        
        codes = load_codes()
        now = time.time()
        find = any(
            c["code"] == code and c["expire"] > now
            for c in codes
        )
        
        if find:
            print(">>> ACCESO CONCEDIDO.")
        else:
            print(">>> CÓDIGO INCORRECTO.")

if __name__ == "__main__":
    main()