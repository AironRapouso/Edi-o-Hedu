# Padrão de edição — A Nova Ordem Educacional no Spotify

Modelo criado a partir do Episódio 1 (O Manifesto). Vale para todos os episódios do YouTube levados para o Spotify.

## Estrutura do episódio (a "trilha")

| # | Peça | O que é |
|---|------|---------|
| 1 | **Vinheta** | Áudio da vinheta oficial do canal (`assets/vinheta.mp4`, 8 s; o áudio já vem extraído em `_pipeline/vinheta.wav`) |
| 2 | **Cold open** | Os primeiros 20–30 s mais fortes da fala do apresentador, sem narração antes |
| 3 | **Apresentação** | Narradora: "Você está ouvindo A Nova Ordem Educacional. Episódio X: [título]. Neste episódio…" |
| 4 | **Blocos** | Para cada tópico: stinger (whoosh + sino) → narradora "Bloco N. [tema]" → fala do apresentador |
| 5 | **Encerramento** | Último bloco, chamado "Encerramento", com a fala de despedida do apresentador |
| 6 | **Para fixar** | Narradora resume as 3 ideias principais do episódio (o momento didático) |
| 7 | **Chamada final** | "Siga o podcast para receber os próximos episódios…" |
| 8 | **Vinheta** | A vinheta oficial fecha o episódio |

Divida em 4 a 6 blocos por episódio. O nome do bloco é a frase-tese do trecho, com 2 a 5 palavras.

## Cortes

- Pausas acima de 0,8 s passam a ter 0,62 s. O ritmo de manifesto fica, os vazios saem.
- Os cortes caem nos silêncios reais do áudio (ou no ponto mais silencioso entre duas palavras), com fades de 12 ms.
- Saem também a vinheta e os efeitos sonoros do vídeo do YouTube, e tomadas repetidas que ficaram no vídeo.
- Sai tudo que só faz sentido no YouTube: "se inscreva", "toque o sininho", "deixe o like", "aqui na tela".
- Saem as muletas ("veja como é importante") e as despedidas repetidas.

## Tratamento de voz

`highpass 75 Hz → redução de ruído leve → −2,5 dB em 280 Hz (embolado) → +2,5 dB em 3,4 kHz (presença/nitidez) → +2 dB acima de 9,5 kHz (brilho) → de-esser → compressor 2,5:1`

## Trilha sonora

- Trilha ambiente sintetizada no próprio script, sem direitos de terceiros: acordes Dm9, B♭maj7, Fmaj7 e C, com reverb.
- O volume é ajustado por região, sem "bombear" nas pausas:
  - baixo sob o apresentador (cerca de 29 dB abaixo da voz)
  - médio sob a narradora
  - mais alto nos stingers
  - some durante a vinheta

## Narradora

- Voz neural "Francisca" (pt-BR, Microsoft) via `edge-tts`, velocidade −8%. É grátis e não tem limite de caracteres.
  - Não use a "Thalita Multilingual": ela pronuncia "Encerramento" com sotaque de inglês.
  - Não use velocidade −4%: o "Bl" de "Bloco" some.
- Os episódios 1 e 2 e a primeira Reflexão usam a voz "Sarah" (ElevenLabs), de antes da troca.
- O volume é igualado ao do apresentador.
- Escreva a narração sem siglas e sem números em algarismos ("inteligência artificial", "dois mil e vinte e cinco").

## Conferência

- `verify_narr.py`: recorta cada fala da narradora do master e confere com o texto (transcrição local, sem cota).
- `verify_edges.py`: transcreve o começo e o fim de cada bloco de fala e mede o volume final. É onde aparece palavra cortada.

## Master

- −14 LUFS integrado, true peak −1,5 dBTP (loudnorm em 2 passadas e limitador).
- Entregas:
  - `.wav` 48 kHz / 24 bits: o melhor para enviar ao Spotify for Creators
  - `.mp3` 320 kbps: backup ou distribuição

## Como fazer o próximo episódio

Os scripts ficam em `SPOTIFY/_pipeline`. Rode tudo de dentro dessa pasta.

1. Crie a pasta `SPOTIFY/EP_xxxx` (as 4 primeiras letras do código do vídeo) e baixe o áudio para `src/source.wav` (mono, 48 kHz) com o `yt_dlp`.
2. `python -X utf8 prep.py ../EP_xxxx` — transcreve no próprio computador e separa a fala pelos silêncios. Leia o `edit/transcript.txt`.
3. Escreva o `edit/plan.json` (use o de qualquer episódio recente como modelo): nome do arquivo, título, resumo, blocos com os trechos e os três textos da narradora (apresentação, "Para fixar" e chamada final). A fala "Bloco N" de cada bloco é gerada sozinha.
4. `python -X utf8 build.py ../EP_xxxx` — gera a narração, mixa, masteriza e escreve a descrição com capítulos em `out/`.
5. `python -X utf8 verify_narr.py ../EP_xxxx` e `python -X utf8 verify_edges.py ../EP_xxxx` para conferir.
6. `python -X utf8 export.py` — copia o `.mp3` e o `.txt` para `SPOTIFY/PRONTOS_PARA_POSTAR` e atualiza o `INDICE.md`.

Para vários de uma vez, `python -X utf8 runner.py` monta e confere sozinho todo episódio que tiver `plan.json` novo (o resultado fica em `queue.log`).

A notação do `transcript.txt` e as regras de corte estão em `_pipeline/PROGRESSO.md`.
