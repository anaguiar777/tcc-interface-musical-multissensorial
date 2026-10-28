# Ligações elétricas

## Canal vibrotátil

Topologia `low-side`:

```text
Barramento +3,3 V
      |
      +------ Motor Vibracall 1027 ------+------ Drain IRLZ44N
      |                                  |
      +-----------|<|--------------------+
                  1N5819
                  catodo no +3,3 V

GPIO18 -- 220 Ω -- Gate IRLZ44N
                    |
                   47 kΩ
                    |
                   GND

Source IRLZ44N -------------------------- GND
```

### Conexões
1. GPIO 18 → resistor 220 Ω → gate do IRLZ44N.
2. Gate → resistor 47 kΩ → GND.
3. Source → GND.
4. Drain → terminal negativo do motor.
5. Terminal positivo do motor → barramento regulado.
6. 1N5819 em paralelo com o motor:
   - cátodo no positivo do motor;
   - ânodo no lado do drain.
7. Todos os GNDs devem ser comuns.

O GPIO controla somente o gate. A corrente do motor não deve ser fornecida diretamente pelo pino do ESP32.

## Canal visual

```text
GPIO21 ---- 220 Ω ---- LED ---- GND
```

O firmware aplica ao LED o mesmo valor PWM recebido para o canal vibrotátil.

## Pinos utilizados
| Função | GPIO |
|---|---:|
| Motor vibrotátil | 18 |
| LED | 21 |

## Comandos UDP
| Comando | Ação |
|---|---|
| `ON,180` | aplica PWM 180 |
| `OFF` | desliga motor e LED |

Porta utilizada: **4210**.
