# Vídeo animado (sem gravação)

Vídeo 9:16 todo em 3D, narrado, feito do roteiro ao arquivo final sem câmera. Modelo: "A bomba já caiu na sua sala" (Método da Aprendizagem Verificável).

| Arquivo | Papel |
| :- | :- |
| `roteiro.json` | Uma fala por cena. É a única entrada de texto. |
| `voz.py` | Gera a narração, acelera, nivela e confere cada fala por transcrição. Escreve `out/narracao.wav` e `out/words.json` (hora de cada palavra). |
| `build.py` | Monta `hf/index.html` com as legendas palavra por palavra. |
| `hf/kit.js` | Comum a todos os vídeos: luz, materiais, astronauta, peões, legendas, relógio. Não muda. |
| `hf/cenas.js` | As cenas deste vídeo. É o arquivo que muda a cada vídeo. |
| `prever.js` | Folha de contato com quadros de cada cena, para revisar antes do render. |
| `render.sh` | Render no HyperFrames e junção do áudio: `out/final.mp4`. |

## Passo a passo

```bash
bash scripts/novo_animado.sh ANIM_2          # copia o modelo para episodios/ANIM_2
cd episodios/ANIM_2                          # edite roteiro.json e hf/cenas.js
python voz.py . --motor clone --ref ../../modelos/animado/voz_ref.wav --temp 1.4 --vel 1.3
python build.py . && node prever.js .        # olhe out/previa/folha.jpg
bash render.sh .
```

O painel de agentes `.claude/workflows/video-animado.js` faz esses passos sozinho (roteiro, checagem, voz, cenas, revisão, render, entrega).

## Voz

- Motor: Chatterbox multilíngue (código aberto, licença MIT, roda na CPU, sem custo). Instalação: `pip install chatterbox-tts faster-whisper soundfile "setuptools<81"` em Python 3.11.
- `--motor clone` copia a voz da amostra `voz_ref.wav`: 30 a 60 s só da voz do Dr. Hélio, sem música nem efeito. A amostra fica fora do Git.
- `--motor provisoria` usa a voz padrão do modelo, para testar o vídeo sem amostra.
- `--vel 1.3` acelera sem mudar o tom. `--temp 1.4` é a temperatura pedida; neste motor ela aumenta a variação e algumas falas saem erradas, por isso cada fala é conferida e refeita (`--tentativas`). Entre 0.8 e 1.0 quase não há refação.
- A nota "confere" de cada fala fica em `out/words.json`. Abaixo de 0,85, ouça antes de publicar.
- Leva cerca de um minuto por fala em 4 núcleos.

## Cenas

- Tudo é função do tempo da timeline: nada de `requestAnimationFrame`, relógio de parede ou acaso.
- Ancore cada momento na cena (`T.c1.t0`) ou na palavra (`quando("c1", "Mas")`), nunca em segundos fixos: trocar a voz não desloca nada.
- Visibilidade com hora marcada: `liga(obj, t)` e `desliga(obj, t)`.
- A legenda ocupa a faixa de 1585 px de altura; não ponha nada por cima.
