# Alimentação embarcada

A unidade vestível utiliza duas células Li‑ion 18650 em série (2S), associadas a um BMS 2S e a um conversor DC–DC MP1584EN.

```text
18650 + 18650 em série
        |
       BMS 2S
        |
     MP1584EN
        |
 barramento regulado
        |
 ESP32 + estágio do motor + LED
```

## Procedimento recomendado
1. Monte primeiro o conjunto de baterias e BMS sem conectar o ESP32.
2. Conecte o MP1584EN.
3. Meça a saída do conversor.
4. Ajuste o trimpot até aproximadamente 3,3 V.
5. Desligue a alimentação.
6. Só então conecte o circuito embarcado.
7. Ligue novamente e confira a tensão sob operação.

No protótipo validado, foram observados aproximadamente **3,26 a 3,29 V** no barramento do ESP32 com Wi‑Fi ativo.

## Segurança
- Não carregue células de lítio sem circuito e carregador apropriados.
- Evite curto-circuito e inversão de polaridade.
- Não utilize células danificadas ou deformadas.
- O BMS não substitui os cuidados de montagem e inspeção.
