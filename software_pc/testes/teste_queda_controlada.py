import csv
import math
import socket
import statistics
import time
from datetime import datetime
from pathlib import Path

import mido

ALTURAS_CM = [0.5, 1, 2, 3, 4, 5]
REPETICOES_POR_ALTURA = 10

PAD_ALVO = 4
NOTA_MIDI_ALVO = 71

MIN_PWM = 80
MAX_PWM = 255

JANELA_REPIQUE_S = 0.60
TEMPO_ESTABILIZACAO_S = 0.20

G = 9.80665


def velocity_para_pwm(velocity):
    if velocity <= 0:
        return 0

    pwm = MIN_PWM + (
        (velocity - 1)
        * (MAX_PWM - MIN_PWM)
        / 126
    )

    return max(MIN_PWM, min(MAX_PWM, round(pwm)))


def escolher_porta_midi():
    portas = mido.get_input_names()

    if not portas:
        raise RuntimeError("Nenhuma entrada MIDI encontrada.")

    for i, porta in enumerate(portas):
        print(f"[{i}] {porta}")

    while True:
        try:
            return portas[int(input("Escolha a entrada MIDI: "))]
        except (ValueError, IndexError):
            print("Opcao invalida.")


def limpar_fila_midi(entrada):
    return sum(1 for _ in entrada.iter_pending())


def ignorar_repiques(entrada):
    inicio = time.monotonic()
    repiques = 0

    while time.monotonic() - inicio < JANELA_REPIQUE_S:
        for msg in entrada.iter_pending():
            if (
                msg.type == "note_on"
                and msg.velocity > 0
                and msg.note == NOTA_MIDI_ALVO
            ):
                repiques += 1

        time.sleep(0.01)

    return repiques


def main():
    porta_midi = escolher_porta_midi()

    massa_g = float(
        input("Massa do corpo em gramas: ").replace(",", ".")
    )
    massa_kg = massa_g / 1000.0

    usar_udp = input(
        "Acionar ESP32 durante o ensaio? [s/N]: "
    ).strip().lower() in ("s", "sim")

    sock = None
    destino = None

    if usar_udp:
        ip = input("IP do ESP32: ").strip()
        porta = int(input("Porta UDP [4210]: ") or "4210")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        destino = (ip, porta)

    pasta = Path(
        "ensaio_queda_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    pasta.mkdir(exist_ok=True)

    bruto = pasta / "dados_quedas.csv"
    resumo = pasta / "resumo_alturas.csv"

    resultados = {h: [] for h in ALTURAS_CM}

    with open(bruto, "w", newline="", encoding="utf-8") as arq:
        campos = [
            "timestamp",
            "altura_cm",
            "repeticao",
            "massa_g",
            "energia_potencial_J",
            "velocidade_teorica_impacto_m_s",
            "pad",
            "nota_midi",
            "velocity",
            "pwm",
            "repiques_ignorados",
        ]

        writer = csv.DictWriter(arq, fieldnames=campos)
        writer.writeheader()

        with mido.open_input(porta_midi) as entrada:
            try:
                for altura in ALTURAS_CM:
                    h_m = altura / 100.0
                    energia = massa_kg * G * h_m
                    v_teorica = math.sqrt(2 * G * h_m)

                    print("\n" + "=" * 60)
                    print(f"ALTURA: {altura} cm")
                    print(f"Energia potencial: {energia:.6f} J")
                    print(f"Velocidade teorica: {v_teorica:.3f} m/s")

                    for repeticao in range(
                        1, REPETICOES_POR_ALTURA + 1
                    ):
                        print(
                            f"\nRepeticao {repeticao}/"
                            f"{REPETICOES_POR_ALTURA}"
                        )

                        input(
                            "Posicione o corpo e pressione ENTER..."
                        )

                        limpar_fila_midi(entrada)
                        time.sleep(TEMPO_ESTABILIZACAO_S)
                        limpar_fila_midi(entrada)

                        print("ARMADO - solte o corpo.")

                        while True:
                            msg = entrada.receive()

                            if (
                                msg.type == "note_on"
                                and msg.velocity > 0
                                and msg.note == NOTA_MIDI_ALVO
                            ):
                                break

                        velocity = int(msg.velocity)
                        pwm = velocity_para_pwm(velocity)

                        if sock:
                            sock.sendto(
                                f"ON,{pwm}".encode("utf-8"),
                                destino,
                            )

                        repiques = ignorar_repiques(entrada)

                        if sock:
                            sock.sendto(b"OFF", destino)

                        linha = {
                            "timestamp": datetime.now().isoformat(
                                timespec="milliseconds"
                            ),
                            "altura_cm": altura,
                            "repeticao": repeticao,
                            "massa_g": massa_g,
                            "energia_potencial_J": f"{energia:.6f}",
                            "velocidade_teorica_impacto_m_s":
                                f"{v_teorica:.4f}",
                            "pad": PAD_ALVO,
                            "nota_midi": NOTA_MIDI_ALVO,
                            "velocity": velocity,
                            "pwm": pwm,
                            "repiques_ignorados": repiques,
                        }

                        writer.writerow(linha)
                        arq.flush()

                        resultados[altura].append(
                            (velocity, pwm, repiques)
                        )

                        print(
                            f"velocity={velocity} | PWM={pwm} | "
                            f"repiques={repiques}"
                        )

            finally:
                if sock:
                    sock.sendto(b"OFF", destino)
                    sock.close()

    with open(resumo, "w", newline="", encoding="utf-8") as arq:
        writer = csv.writer(arq)
        writer.writerow([
            "altura_cm",
            "n",
            "velocity_media",
            "velocity_mediana",
            "velocity_dp",
            "pwm_media",
            "pwm_dp",
            "repiques_ignorados",
            "velocity_127",
        ])

        for altura, dados in resultados.items():
            velocities = [x[0] for x in dados]
            pwms = [x[1] for x in dados]
            repiques = sum(x[2] for x in dados)

            writer.writerow([
                altura,
                len(dados),
                statistics.mean(velocities),
                statistics.median(velocities),
                statistics.stdev(velocities),
                statistics.mean(pwms),
                statistics.stdev(pwms),
                repiques,
                sum(v == 127 for v in velocities),
            ])

    print("\nDados:", bruto.resolve())
    print("Resumo:", resumo.resolve())


if __name__ == "__main__":
    main()
