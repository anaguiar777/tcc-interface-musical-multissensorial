import csv
import socket
import time
from datetime import datetime
from pathlib import Path

PWM_TESTE = [80, 115, 150, 185, 220, 255]
REPETICOES = 3

TEMPO_LIGADO_S = 8.0
TEMPO_DESLIGADO_S = 2.0
CONTAGEM_INICIAL_S = 5


def enviar(sock, destino, mensagem):
    sock.sendto(mensagem.encode("utf-8"), destino)


def main():
    ip = input("IP do ESP32: ").strip()
    porta = int(input("Porta UDP [4210]: ") or "4210")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    destino = (ip, porta)

    pasta = Path(
        "ensaio_audio_pwm_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    pasta.mkdir(exist_ok=True)

    cronograma = pasta / "cronograma_pwm.csv"

    print("\nInicie a gravacao WAV.")
    print("Mantenha microfone, ganho e distancia fixos.")
    input("Pressione ENTER quando a gravacao estiver rodando...")

    for s in range(CONTAGEM_INICIAL_S, 0, -1):
        print(s)
        time.sleep(1)

    t0 = time.monotonic()

    with open(cronograma, "w", newline="", encoding="utf-8") as arq:
        writer = csv.writer(arq)
        writer.writerow([
            "repeticao",
            "pwm",
            "inicio_motor_s",
            "fim_motor_s",
            "inicio_silencio_s",
            "fim_silencio_s",
        ])

        try:
            for repeticao in range(1, REPETICOES + 1):
                for pwm in PWM_TESTE:
                    inicio = time.monotonic() - t0

                    enviar(sock, destino, f"ON,{pwm}")
                    print(
                        f"Rep {repeticao} | PWM {pwm} | ON "
                        f"({inicio:.3f} s)"
                    )

                    time.sleep(TEMPO_LIGADO_S)

                    fim = time.monotonic() - t0
                    enviar(sock, destino, "OFF")

                    inicio_silencio = fim
                    time.sleep(TEMPO_DESLIGADO_S)
                    fim_silencio = time.monotonic() - t0

                    writer.writerow([
                        repeticao,
                        pwm,
                        f"{inicio:.3f}",
                        f"{fim:.3f}",
                        f"{inicio_silencio:.3f}",
                        f"{fim_silencio:.3f}",
                    ])
                    arq.flush()

        finally:
            enviar(sock, destino, "OFF")
            sock.close()

    print("\nPare a gravacao.")
    print("Cronograma:", cronograma.resolve())


if __name__ == "__main__":
    main()
