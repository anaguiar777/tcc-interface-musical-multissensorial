# Dados experimentais

Este diretório reúne os valores consolidados apresentados no TCC.

## Ensaio de queda controlada

Arquivo: `ensaio_queda_resumo.csv`

- corpo: 39 g;
- alturas: 0,5; 1; 2; 3; 4; 5 cm;
- 10 quedas independentes por altura;
- pad 4 / nota MIDI 71;
- primeiro impacto válido por repetição;
- janela de 0,60 s para classificar repiques;
- mapeamento experimental: velocity 1–127 → PWM 80–255.

Correlação altura × velocity:
- Spearman: ρ = 0,944;
- Pearson: r = 0,818.

## Ensaio acústico

Arquivo: `ensaio_acustico_resumo.csv`

- PWM: 80, 115, 150, 185, 220, 255;
- 3 repetições;
- 8 s ligado;
- 2 s desligado;
- gravação com microfone condensador em WAV.

Correlação PWM × frequência acústica:
- Spearman: ρ = 0,988;
- Pearson: r = 0,984.

A frequência acústica é uma medida indireta do comportamento do motor. Não representa medição direta de aceleração ou amplitude mecânica da vibração.
