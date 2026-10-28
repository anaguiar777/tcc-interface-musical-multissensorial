# Reprodução do protótipo — Interface Musical Multissensorial com MPD218 e ESP32

Este diretório reúne a documentação necessária para reproduzir o protótipo desenvolvido no PFC2 **“Desenvolvimento e Validação de uma Interface Musical Digital Multissensorial para Acessibilidade Musical”**.

## 1. Objetivo do sistema

O protótipo recebe eventos MIDI produzidos pelo controlador Akai MPD218 e utiliza informações como o instante de acionamento e a \`velocity\` para gerar feedback vibrotátil e visual.

O objetivo **não é reproduzir fisicamente o som do MIDI** por vibração ou luz. A proposta é fornecer representações sensoriais alternativas de aspectos da interação musical, como:

- ocorrência dos eventos;
- intensidade relativa do acionamento;
- pulsação e organização temporal;
- padrões rítmicos.

## 2. Arquitetura

\`\`\`text
Akai MPD218
     |
     | USB / MIDI
     v
Computador + Python
     |
     | UDP / Wi-Fi
     v
ESP32
     |
     +---- GPIO 18 / PWM ---- MOSFET ---- Vibracall 1027
     |
     +---- GPIO 21 / PWM ---- resistor --- LED de alto brilho
\`\`\`

Durante a operação normal, a unidade embarcada utiliza alimentação própria. O MPD218 permanece conectado por USB ao computador.

## 3. Componentes principais

### Controle e comunicação

- 1 × Akai MPD218;
- 1 × ESP32;
- computador com Python;
- rede Wi-Fi local ou hotspot.

### Canal vibrotátil

- 1 × motor Vibracall 1027;
- 1 × MOSFET IRLZ44N;
- 1 × resistor de 220 Ω em série com o gate;
- 1 × resistor de 47 kΩ entre gate e GND;
- 1 × diodo Schottky 1N5819 em paralelo com o motor.

### Canal visual

- 1 × LED de alto brilho;
- 1 × resistor de 220 Ω.

### Alimentação embarcada

- 2 × células Li-ion 18650 de 3,7 V em configuração 2S;
- 1 × BMS 2S;
- 1 × conversor DC–DC MP1584EN;
- fiação e conectores adequados.

A saída do conversor deve ser ajustada e verificada com multímetro antes da conexão ao circuito embarcado. No protótipo, o barramento de alimentação do ESP32 foi mantido próximo de 3,3 V.

## 4. Ligações do canal vibrotátil

A topologia utilizada é do tipo \`low-side\`:

1. GPIO 18 do ESP32 → resistor de 220 Ω → gate do IRLZ44N;
2. resistor de 47 kΩ entre gate e GND;
3. source do MOSFET → GND;
4. drain do MOSFET → terminal negativo do motor;
5. terminal positivo do motor → barramento de alimentação;
6. diodo 1N5819 em paralelo com o motor:
   - cátodo no positivo do motor;
   - ânodo no lado conectado ao drain;
7. todos os módulos compartilham a mesma referência de GND.

O GPIO fornece apenas o sinal de controle. A corrente do motor é proveniente do barramento de alimentação.

## 5. Ligação do canal visual

1. GPIO 21 do ESP32;
2. resistor de 220 Ω;
3. LED de alto brilho;
4. GND.

O firmware aplica ao LED o mesmo valor PWM utilizado como referência para o canal vibrotátil.

## 6. Comunicação UDP

A implementação validada utiliza:

- porta UDP: **4210**;
- comando de acionamento: \`ON,pwm\`;
- comando de desligamento: \`OFF\`.

Exemplo:

\`\`\`text
ON,180
OFF
\`\`\`

O endereço IP do ESP32 depende da rede utilizada e deve ser atualizado no programa executado no computador.

## 7. MIDI

O software no computador utiliza Python com as bibliotecas \`mido\` e \`python-rtmidi\`.

Mapeamento de notas utilizado no MPD218:

| Pad | Nota MIDI |
|---:|---:|
| 1 | 68 |
| 2 | 69 |
| 3 | 70 |
| 4 | 71 |
| 5 | 72 |
| 6 | 73 |
| 7 | 74 |
| 8 | 75 |
| 9 | 60 |
| 10 | 61 |
| 11 | 62 |
| 12 | 63 |
| 13 | 64 |
| 14 | 65 |
| 15 | 66 |
| 16 | 67 |

## 8. Mapeamento de velocity para PWM

Durante o desenvolvimento foi utilizada inicialmente uma referência superior de \`velocity = 30\`, com PWM mínimo de 80 e saturação em 255.

Os ensaios posteriores mostraram que esse limite produz saturação precoce para impactos mais intensos. Para a caracterização experimental foi utilizado um mapeamento que distribui toda a faixa MIDI válida entre PWM 80 e 255:

\`\`\`text
velocity = 1   -> PWM = 80
velocity = 127 -> PWM = 255
\`\`\`

A documentação do repositório público deve preservar as duas estratégias, identificando a primeira como configuração original do protótipo e a segunda como refinamento experimental obtido durante a validação.

## 9. Caixa impressa em 3D

O circuito foi acondicionado em uma caixa modelada em duas peças:

- \`caixa_corpo.stl\`;
- \`caixa_tampa.stl\`.

O desenvolvimento da geometria contou com apoio do ambiente Cursor durante a elaboração e os ajustes do modelo digital. Os arquivos STL permitem reproduzir o invólucro utilizado no protótipo.

As fotografias da montagem final serão adicionadas à documentação posteriormente.

## 10. Estrutura proposta para o repositório público

\`\`\`text
.
├── README.md
├── firmware_esp32/
│   ├── platformio.ini
│   └── src/
│       └── main.cpp
├── software_pc/
│   ├── mpd_visual.py
│   └── testes/
│       ├── teste_queda_controlada.py
│       └── teste_audio_pwm.py
├── hardware/
│   ├── esquema_conexoes.md
│   └── 3d/
│       ├── caixa_corpo.stl
│       └── caixa_tampa.stl
├── dados_experimentais/
└── docs/
    └── fotos/
\`\`\`

## 11. Sequência recomendada de reprodução

1. montar o estágio MOSFET sem o motor e verificar o sinal de controle;
2. conectar o motor e testar comandos UDP fixos;
3. testar o LED separadamente;
4. verificar a tensão do sistema de alimentação antes de conectar o ESP32;
5. conectar ESP32 à rede Wi-Fi;
6. confirmar o IP atribuído;
7. executar o software Python e selecionar a entrada MIDI do MPD218;
8. testar \`ON,255\` e \`OFF\`;
9. confirmar o funcionamento do motor e do LED;
10. somente depois integrar o conjunto à caixa e à estrutura vestível.

## 12. Ensaios utilizados no TCC

A documentação também inclui os procedimentos utilizados para:

- teste de estabilidade UDP;
- ensaio com corpo de 39 g e alturas controladas;
- filtragem de repiques;
- caracterização \`velocity → PWM\`;
- caracterização acústica \`PWM → frequência dominante\`.

Esses ensaios têm finalidade técnica. Eles não substituem estudos perceptivos com usuários nem medição mecânica da vibração por acelerômetro.

## 13. Licença e reutilização

Antes da publicação definitiva, deve ser escolhida uma licença para o código e para os arquivos de hardware/3D. O repositório deve informar claramente as condições de reutilização, modificação e redistribuição.
