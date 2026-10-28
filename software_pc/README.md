# Software do computador

## Instalação

```bash
python -m pip install -r requirements.txt
```

Conecte o Akai MPD218 por USB e confirme as entradas MIDI:

```bash
python -c "import mido; print(mido.get_input_names())"
```

## Arquivos

- `mpd_to_wifi.py`: implementação do mapeamento original utilizado durante o desenvolvimento do protótipo, com referência superior de velocity 30.
- `mpd_to_wifi_mapeamento_completo.py`: versão refinada utilizada na caracterização experimental, distribuindo velocity 1–127 entre PWM 80–255.
- `teste_motor_udp.py`: teste simples do motor e do LED sem usar o MPD218.
- `testes/teste_queda_controlada.py`: coleta controlada do ensaio com massa conhecida.
- `testes/teste_audio_pwm.py`: sequência automatizada de PWM para gravação acústica.

Antes de executar os programas, ajuste `ESP32_IP` para o IP mostrado pelo monitor serial do ESP32.

## Observação importante

A versão de mapeamento completo foi utilizada para caracterização porque os ensaios mostraram que limitar a referência superior da velocity a 30 provocava saturação precoce. As duas versões estão preservadas para documentar a evolução do projeto.
