import socket
import time

ESP32_IP = "172.20.10.2"  # troque pelo IP atual
UDP_PORT = 4210

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
destino = (ESP32_IP, UDP_PORT)

try:
    print("PWM 255 por 5 segundos...")
    sock.sendto(b"ON,255", destino)
    time.sleep(5)

finally:
    sock.sendto(b"OFF", destino)
    sock.close()

print("Teste finalizado.")
