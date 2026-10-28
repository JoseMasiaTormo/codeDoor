import tkinter as tk
import socket
import json
import random
import time
from pathlib import Path

CODES_FILE = Path("codes.json")
EXPIRY_MINUTES = 120
SEGUNDOS_ABIERTA = 5
cuenta_atras = None

def puerta_cerrada():
    puerta.config(text="PUERTA CERRADA", bg="#c62828")
    
def puerta_introduciendo(evento=None):
    if cuenta_atras is not None:
        return
    if entrada.get():
        puerta.config(text="INTRODUCIENDO CÓDIGO", bg="#f9a825")
    else:
        puerta_cerrada()

def abrir_puerta(segundos=SEGUNDOS_ABIERTA):
    global cuenta_atras
    if segundos > 0:
        puerta.config(text=f"PUERTA ABIERTA ({segundos})", bg="#2e7d32")
        cuenta_atras = ventana.after(1000, abrir_puerta, segundos - 1)
    else:
        cuenta_atras = None
        puerta_cerrada()

def cargar_codigos():
    if CODES_FILE.exists():
        return json.loads(CODES_FILE.read_text())
    return []

def guardar_codigos(codigos):
    CODES_FILE.write_text(json.dumps(codigos, indent=2))

def validar(codigo_input):
    codigos = cargar_codigos()
    ahora = time.time()
    return any(
        c.get("code") == codigo_input and c.get("expire", 0) > ahora
        for c in codigos
    )
    
def escribir_proceso(texto, tipo="info"):
    proceso.config(state="normal")
    proceso.insert("end", texto + "\n", tipo)
    proceso.see("end")
    proceso.config(state="disabled")
    
def limpiar_proceso():
    proceso.config(state="normal")
    proceso.delete("1.0", "end")
    proceso.config(state="disabled")
    
def interpretar(respuesta):
    if respuesta == "IGNORADO":
        return [
            ("2. Buscando la palabra LOCAL...", "info"),
            ("   No es un pedido local", "error"),
            ("   No se genera código", "error")
        ]
    estado, codigo, expira = respuesta.split("|")
    hora = time.strftime("%H:%M", time.localtime(float(expira)))
    return [
        ("2. Buscando la palabra LOCAL...", "info"),
        ("   Pedido local detectado", "ok"),
        (f"3. Código generado: {codigo}", "ok"),
        (f"4. Válido hasta las {hora}", "ok")
    ]

def enviar_ticket():
    contenido = ticket.get("1.0", "end").strip()
    limpiar_proceso()

    if not contenido:
        escribir_proceso("El ticket está vacío", "error")
        return

    boton_enviar.config(state="disabled")
    escribir_proceso("1. Enviando ticket al interceptor...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("localhost", 9100))
            s.sendall(contenido.encode())
            respuesta = s.recv(1024).decode()
    except ConnectionRefusedError:
        escribir_proceso("   Interceptor apagado", "error")
        boton_enviar.config(state="normal")
        return

    pasos = interpretar(respuesta)
    for i, (texto, tipo) in enumerate(pasos):
        ventana.after(700 * (i+1), escribir_proceso, texto, tipo)
    
    ventana.after(700 * (len(pasos) + 1), lambda: boton_enviar.config(state="normal"))

def comprobar(evento=None):
    codigo = entrada.get().strip()
    if not codigo:
        return
    if validar(codigo):
        resultado.config(text="ACCESO CONCEDIDO", fg="green")
        if cuenta_atras is None:
            abrir_puerta()
    else:
        resultado.config(text="CÓDIGO INCORRECTO", fg="red")
        if cuenta_atras is None:
            puerta_cerrada()
    entrada.delete(0, "end")

ventana = tk.Tk()
ventana.title("Control de acceso")
ventana.geometry("1000x1200")

titulo_ticket = tk.Label(ventana, text="Contenido del ticket", font=("Arial", 14))
titulo_ticket.pack(pady=(10, 5))

ticket = tk.Text(ventana, height=5, width=35, font=("Arial", 12))
ticket.pack(pady=5)

boton_enviar = tk.Button(ventana, text="Enviar ticket", command=enviar_ticket)
boton_enviar.pack(pady=5)

proceso = tk.Text(ventana, height=7, width=40, font=("Courier", 11),
                  bg="#1e1e1e", fg="white", state="disabled")
proceso.pack(pady=10)
proceso.tag_config("ok", foreground="#4caf50")
proceso.tag_config("error", foreground="#f44336")
proceso.tag_config("info", foreground="#90caf9")

separador = tk.Frame(ventana, height=2, bg="#cccccc")
separador.pack(fill="x", padx=20, pady=10)

etiqueta = tk.Label(ventana, text="Introduce el código", font=("Arial", 14))
etiqueta.pack(pady=10)

entrada = tk.Entry(ventana, font=("Arial", 14), justify="center")
entrada.pack(pady=5)

entrada.bind("<KeyRelease>", puerta_introduciendo)
entrada.bind("<Return>", comprobar)

boton = tk.Button(ventana, text="Comprobar", command=comprobar)
boton.pack(pady=10)

resultado = tk.Label(ventana, text="", font=("Arial", 14, "bold"))
resultado.pack(pady=10)

puerta = tk.Label(ventana, text="PUERTA CERRADA", font=("Arial", 20, "bold"),
                  bg="#c62828", fg="white", width=22, pady=20)
puerta.pack(pady=15)

nuevo_codigo_label = tk.Label(ventana, text="", font=("Arial", 14, "bold"), fg="blue")
nuevo_codigo_label.pack(pady=10)

ventana.mainloop()