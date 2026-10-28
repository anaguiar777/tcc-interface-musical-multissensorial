import socket
import time

import mido

ESP32_IP = "172.20.10.2"  # ajuste conforme a rede
UDP_PORT = 4210

MIN_PWM = 80
MAX_PWM = 255
DEBOUNCE_S = 0.08

PAD_MAP = {
    68: 1, 69: 2, 70: 3, 71: 4,
    72: 5, 73: 6, 74: 7, 75: 8,
    60: 9, 61: 10, 62: 11, 63: 12,
    64: 13, 65: 14, 66: 15, 67: 16,
}


def velocity_para_pwm(velocity: int) -> int:
    if velocity <= 0:
        return 0

    pwm = MIN_PWM + (
        (velocity - 1)
        * (MAX_PWM - MIN_PWM)
        / 126
    )

    return max(MIN_PWM, min(MAX_PWM, round(pwm)))


def escolher_porta() -> str:
    portas = mido.get_input_names()
    candidatos = [p for p in portas if "MPD218" in p.upper()]

    if not candidatos:
        raise RuntimeError(
            "MPD218 nao encontrado. Portas: " + ", ".join(portas)
        )

    for i, porta in enumerate(candidatos):
        print(f"[{i}] {porta}")

    escolha = int(input("Escolha a entrada: "))
    return candidatos[escolha]


def main() -> None:
    porta = escolher_porta()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    destino = (ESP32_IP, UDP_PORT)

    ultimo_evento = 0.0

    with mido.open_input(porta) as entrada:
        try:
            for msg in entrada:
                if msg.type == "note_on" and msg.velocity > 0:
                    agora = time.monotonic()

                    if agora - ultimo_evento < DEBOUNCE_S:
                        continue

                    ultimo_evento = agora

                    pwm = velocity_para_pwm(msg.velocity)
                    pad = PAD_MAP.get(msg.note, "?")

                    sock.sendto(
                        f"ON,{pwm}".encode("utf-8"),
                        destino,
                    )

                    print(
                        f"Pad {pad} | velocity={msg.velocity} | PWM={pwm}"
                    )

                elif (
                    msg.type == "note_off"
                    or (msg.type == "note_on" and msg.velocity == 0)
                ):
                    sock.sendto(b"OFF", destino)

        except KeyboardInterrupt:
            pass

        finally:
            sock.sendto(b"OFF", destino)
            sock.close()


if __name__ == "__main__":
    main()
