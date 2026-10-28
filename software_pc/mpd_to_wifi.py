import csv
import socket
import time
from datetime import datetime

import mido

# ============================================================
# CONFIGURACAO
# ============================================================

ESP32_IP = "172.20.10.2"  # ajuste conforme a rede
UDP_PORT = 4210

INPUT_NAME = "MPD218 0"

MAX_OBSERVED_VELOCITY = 30
MIN_PWM = 80
MAX_PWM = 255
DEBOUNCE_S = 0.08

PAD_MAP = {
    68: 1, 69: 2, 70: 3, 71: 4,
    72: 5, 73: 6, 74: 7, 75: 8,
    60: 9, 61: 10, 62: 11, 63: 12,
    64: 13, 65: 14, 66: 15, 67: 16,
}

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
destino = (ESP32_IP, UDP_PORT)


def velocity_para_pwm(velocity: int) -> int:
    if velocity <= 0:
        return 0

    pwm = round((velocity / MAX_OBSERVED_VELOCITY) * MAX_PWM)
    return max(MIN_PWM, min(MAX_PWM, pwm))


def enviar(msg: str) -> None:
    sock.sendto(msg.encode("utf-8"), destino)


def encontrar_porta() -> str:
    nomes = mido.get_input_names()

    if INPUT_NAME in nomes:
        return INPUT_NAME

    candidatos = [n for n in nomes if "MPD218" in n.upper()]

    if not candidatos:
        raise RuntimeError(
            "MPD218 nao encontrado. Portas disponiveis: "
            + ", ".join(nomes)
        )

    return candidatos[0]


def main() -> None:
    porta = encontrar_porta()
    print(f"Entrada MIDI: {porta}")
    print(f"ESP32: {ESP32_IP}:{UDP_PORT}")

    ultimo_evento = 0.0

    with open("dados_pwm.csv", "a", newline="", encoding="utf-8") as arq:
        writer = csv.writer(arq)

        if arq.tell() == 0:
            writer.writerow([
                "timestamp",
                "pad",
                "nota_midi",
                "velocity",
                "pwm",
            ])

        with mido.open_input(porta) as entrada:
            try:
                for msg in entrada:
                    if msg.type == "note_on" and msg.velocity > 0:
                        agora = time.monotonic()

                        if agora - ultimo_evento < DEBOUNCE_S:
                            continue

                        ultimo_evento = agora

                        velocity = int(msg.velocity)
                        pwm = velocity_para_pwm(velocity)
                        pad = PAD_MAP.get(msg.note, "?")

                        enviar(f"ON,{pwm}")

                        writer.writerow([
                            datetime.now().isoformat(timespec="milliseconds"),
                            pad,
                            msg.note,
                            velocity,
                            pwm,
                        ])
                        arq.flush()

                        print(
                            f"Pad {pad} | nota={msg.note} | "
                            f"velocity={velocity} | PWM={pwm}"
                        )

                    elif (
                        msg.type == "note_off"
                        or (msg.type == "note_on" and msg.velocity == 0)
                    ):
                        enviar("OFF")

            except KeyboardInterrupt:
                pass

            finally:
                enviar("OFF")
                sock.close()


if __name__ == "__main__":
    main()
