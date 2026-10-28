import socket

HOST = "localhost"
PORT = 9100

text = "PEDIDO LOCAL #123\nMargarita x1\nCoca-Cola x1"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(text.encode())
    
print("Ticket enviado")