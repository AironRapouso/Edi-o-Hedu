# Edição HEDU — A Nova Ordem Educacional

Código e modelos usados para editar os vídeos do canal **A Nova Ordem Educacional**: o vídeo longo do YouTube, os shorts e Reels, a thumbnail e as capas, e o episódio em áudio para o Spotify.

O repositório guarda só o que é necessário para editar: scripts, modelos de composição, fontes, a vinheta do canal e a linha de produção do Spotify. Gravações, renders, caches e arquivos de trabalho ficam no computador de edição e estão fora do Git (veja `.gitignore`).

## O que tem aqui

| Pasta | Conteúdo |
| :- | :- |
| `modelos/longo/` | Vídeo longo 16:9 no visual dos Reels (painel de papel com cenas 3D, legenda em pílula palavra por palavra, desenho de som). É o padrão atual. Inclui os 3 shorts tirados do episódio (`vert/`). Modelo: EP7. |
| `modelos/longo/exemplos/` | Plano de corte e cenas do EP8, com âncoras por frase (`S("frase")`, `E("frase")`) em vez de índices de palavra. |
| `modelos/longo_padrao_antigo/` | O padrão anterior do vídeo longo (apresentador em tela cheia, intertítulos, painéis de dados, imagens de apoio). Só se for pedido. |
| `modelos/reels/` | Reels avulsos 9:16: painel 3D em cima, rosto embaixo, rosto estabilizado pela linha dos olhos, voz tratada, capa. Modelo: REELS 3. |
| `modelos/thumbnail/` | Thumbnail azul do vídeo longo, thumbnail da série Papo Reto, a do EP6 (painel de aeroporto) e as capas azuis dos shorts. |
| `spotify/` | Linha de produção do episódio em áudio (`_pipeline/`) e o padrão do podcast (`PADRAO_PODCAST.md`). |
| `assets/` | Fontes (Inter, Bebas Neue, Playfair Display), three.js 0.181, GSAP, a vinheta do canal (`vinheta.mp4`), a bússola da marca e os efeitos sonoros do padrão antigo. |
| `scripts/` | Atalhos para criar um episódio novo, renderizar o longo e criar um Reel. |

Cada modelo traz um diário de exemplo (`diario_exemplo_*.md`) com as decisões e os cuidados de um episódio real.

## Instalação no Linux

Testado como roteiro para Ubuntu/Debian. Em outra distribuição, troque o `apt` pelo gerenciador dela.

```bash
sudo apt update
sudo apt install -y ffmpeg python3 python3-venv python3-pip nodejs npm chromium fonts-dejavu-core git

git clone https://github.com/AironRapouso/Edi-o-Hedu.git
cd Edi-o-Hedu
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- **ffmpeg** precisa estar no PATH. Os scripts chamam `ffmpeg` e `ffprobe` direto.
- **HyperFrames** renderiza as composições HTML em vídeo. Os scripts usam `npx --yes hyperframes@0.8.158` (a versão em que os modelos foram feitos). Para usar outro comando, defina `HF`, por exemplo `export HF="node /caminho/plugin-cli.mjs"`.
- **Chromium/Chrome** é usado pelo HyperFrames e para gerar thumbnails e capas a partir do HTML.
- **faster-whisper** baixa o modelo `large-v3-turbo` na primeira transcrição (cerca de 1,6 GB). Roda na CPU.
- A legenda usa uma fonte monoespaçada em negrito. No Windows era a Consolas, que é da Microsoft e não pode ser distribuída. Os scripts copiam a DejaVu Sans Mono Bold no lugar; para usar outra, defina `MONO_FONT=/caminho/fonte.ttf`.

Os renders gastam muito disco e memória. Aponte o cache para um disco com espaço (`export HF_CACHE=/mnt/dados/hf-cache`) e renderize uma coisa por vez: um vídeo longo de 19 minutos levou cerca de 2h20 num computador de 4 núcleos e 12 GB de RAM.

## Fluxo de um episódio (vídeo longo + 3 shorts + Spotify)

### 1. Criar a pasta do episódio

```bash
bash scripts/novo_episodio.sh EP9 /caminho/da/gravacao.mp4
cd episodios/EP9/edit
```

O script copia o modelo, os recursos e a gravação (`raw/source.mp4`) e troca os nomes de arquivo do modelo (EP7) pelo do episódio.

Antes de editar, confira se a gravação já não foi publicada: transcreva os primeiros minutos e compare com o canal.

### 2. Transcrever

```bash
python3 -X utf8 whisper_transcribe.py ../raw/source.mp4 transcripts/EP9.json
```

Gera a transcrição palavra por palavra, com tempo. O Whisper costuma errar números falados ("vinte e seis" pode virar "1926"): corrija na legenda (`FIX` em `hf/build.py` e em `make_srt.py`).

### 3. Planejar e executar o corte

Edite `plan.py`:

- `HOOK`: o trecho que abre o vídeo antes da vinheta (a pergunta ou a frase mais forte).
- `DROP`: trechos removidos (repetições, deslizes, despedidas repetidas, promessa de próximo vídeo).
- `HOLD`: respiro extra depois de uma palavra.

Os números são índices de palavras da transcrição. Ajuste também o recorte do quadro (`crop=` em `cut.py`) para o enquadramento da gravação.

```bash
python3 -X utf8 cut.py
```

Saídas: `segments.json`, `words_out.json`, `video_only.mp4` e `audio_raw.wav`, já na linha do tempo final (gancho, vinheta de 8 s, corpo, tela final de 20 s).

### 4. Escrever as cenas e montar a composição

Reescreva `hf/cues.py` para a fala do episódio. As funções principais:

- `full(...)`: tela cheia de papel com cena 3D.
- `side(...)`: rosto à esquerda e painel com cena 3D à direita.
- `chip(...)`: palavras grandes ao lado do rosto.
- `emph(...)`: aproximação de câmera em uma frase.
- `it("plate" | "pawn" | "astronaut" | "doc" | "bar" | "badge" | ..., ...)`: objetos da cena.

O exemplo do EP8 (`modelos/longo/exemplos/`) ancora tudo em frases (`S("frase")`), o que evita erro de índice quando o corte muda. Textos fixos (tarja, rodapé de fonte, cartão de comentário, tela final) ficam em `hf/dom_cues.py`.

Dados do episódio que também ficam em `hf/cues.py` (o `build.py` não tem nada fixo de um episódio):

- `LOWER_THIRDS = [(início, fim, "função")]`: as tarjas com o nome; a legenda vai para a direita enquanto uma está na tela.
- `FIXI = {índice_da_palavra: "texto"}`: correção pontual da legenda numa palavra só (`FIX`, no `build.py`, troca a palavra em todas as ocorrências).

#### Personagens (elenco das cenas 3D)

| Personagem | Papel | Chave em `it(...)` |
| :- | :- | :- |
| Peão dourado | o espectador, VOCÊ (o estudante no centro) | `"pawn"` (`mat="gold"`) |
| Peões cinza | pessoas e instituições | `"pawn"` (`mat="grey"`) |
| Astronauta Dr. Hélio (rosto do apresentador, traje #031954, detalhes #010B25 e #F4B04A) | tecnologia / IA, no lugar do antigo robô | `"astronaut"` |

- O astronauta fica em `assets/astronauta.js`, um arquivo só para o vídeo longo, os shorts e os Reels. O `build.py` copia a versão do repositório para `hf/assets/` a cada montagem, e o `build_vert.py` leva a cópia para os shorts.
- Medidas em tamanho 1 (multiplique por `s`): 4,54 de altura, capacete de raio 1,24 com centro em y = 3,3, fones até x = ±1,38, frente do vidro em z = +1,2. O capacete é de vidro: placa que entra nessa esfera aparece por dentro do vidro, então deixe as placas a pelo menos 0,1 dela.
- `eyesOn=t` acende a luz no topo do capacete; `wave=[t, ...]` levanta o braço direito.
- A chave antiga `"robot"` continua valendo e mostra o mesmo astronauta a 0,8 do tamanho (a altura da cabeça do robô), para que as cenas escritas para o robô (EP7, EP8) não encostem nas placas. Em cena nova, use `"astronaut"`.

```bash
cd hf
ffmpeg -y -i ../video_only.mp4 -i ../audio_raw.wav -c:v copy -c:a aac -b:a 192k -shortest assets/base.mp4
python3 -X utf8 build.py
npx --yes hyperframes@0.8.158 snapshot . --at "10,60,120,300"   # prévias e folhas de contato para revisar
```

Todo número na tela leva rodapé com a fonte, conferida antes.

### 5. Renderizar o longo, tratar o áudio e gerar a legenda

```bash
cd ../../../..   # volta para a raiz do repositório
bash scripts/render_longo.sh EP9
```

O script monta a composição, renderiza (`final_raw.mp4`), aplica o tratamento de voz, os efeitos e a vinheta em −14 LUFS (`audio/sound.py` → `episodios/EP9/EP9_final.mp4`), roda a revisão técnica (`qa.py`: congelamentos, quadros em branco, sincronia, volume, folhas de contato) e gera `EP9_legendas.srt`. Se o render cair, rode de novo com `RESUME=1`, desde que a composição não tenha mudado.

Olhe todas as folhas de contato em `edit/verify/qa` antes de entregar.

### 6. Shorts (3 cortes 9:16)

Em `edit/vert/build_vert.py`, edite a tabela `CUTS`: os trechos de cada corte (`rng(palavra_inicial, palavra_final)`) e o título do gancho. O short 1 é o chamamento, publicado junto com o vídeo longo. Cada short abre com a pergunta na fala e na tela.

```bash
cd episodios/EP9/edit/vert
CORTES="c1 chamamento c2 tema2 c3 tema3" bash render_all.sh EP9
```

Saída: `episodios/EP9/shorts/EP9_short1_chamamento_9x16.mp4` e os outros dois, em −14 LUFS.

### 7. Thumbnail e capas

Edite `episodios/EP9/thumbnail/thumb.html` (título de 4 a 6 palavras em pergunta, recorte do apresentador em `host_take.png`) e as capas em `shorts/capas/src/capa_c1.html` a `capa_c3.html` (foto diferente em cada uma). Para recortar o apresentador de um quadro do vídeo:

```bash
ffmpeg -ss 300 -i ../raw/source.mp4 -frames:v 1 quadro.png
rembg i -m u2net_human_seg -a quadro.png host_take.png
```

Para exportar a imagem:

```bash
chromium --headless --disable-gpu --hide-scrollbars --window-size=1280,720 --force-device-scale-factor=1.5 --screenshot=thumb.png thumb.html
ffmpeg -y -i thumb.png -vf scale=1920:1080 -q:v 2 ../EP9_thumbnail.jpg
```

As capas usam `--window-size=1080,1920 --force-device-scale-factor=1`.

### 8. Episódio do Spotify

Rode de dentro de `spotify/_pipeline`. O passo a passo completo, a notação da transcrição e as regras de corte estão em `spotify/_pipeline/PROGRESSO.md` e em `spotify/PADRAO_PODCAST.md`.

```bash
cd spotify/_pipeline
mkdir -p ../EP_SINA/src
ffmpeg -y -i ../../episodios/EP9/edit/audio_raw.wav -ac 1 -ar 48000 ../EP_SINA/src/source.wav
python3 -X utf8 prep.py ../EP_SINA            # transcreve e separa a fala -> EP_SINA/edit/transcript.txt
# escreva EP_SINA/edit/plan.json (blocos, títulos e as três falas da narradora)
python3 -X utf8 build.py ../EP_SINA           # narração (edge-tts), mixagem, master -14 LUFS, descrição com capítulos
python3 -X utf8 verify_narr.py ../EP_SINA
python3 -X utf8 verify_edges.py ../EP_SINA
python3 -X utf8 export.py                     # copia mp3 + texto para spotify/PRONTOS_PARA_POSTAR
```

A narradora é a voz pt-BR Francisca, via `edge-tts`, que precisa de internet. `ffmpeg` vem do PATH (ou da variável `FFMPEG`).

## Reel avulso (série "O futuro não vai esperar você")

```bash
bash scripts/novo_reel.sh REELS_4 /caminho/do/take_vertical.mp4
cd episodios/REELS_4/edit
python3 -X utf8 whisper_transcribe.py raw/source.mp4 transcripts/REELS3.json   # o modelo lê transcripts/REELS3.json
python3 -X utf8 cut.py              # corta as pausas -> base.mp4, words_out.json
python3 -X utf8 track_face.py       # linha dos olhos em cada quadro -> track.json
python3 -X utf8 hf/build.py         # composição: painel 3D, legendas, CTA (reescreva as cenas para o novo texto)
npx --yes hyperframes@0.8.158 render hf --fps 30 --quality looks --low-memory-mode -o reels3_raw.mp4
python3 -X utf8 audio/sound.py      # voz tratada + desenho de som, -14 LUFS -> ../REELS_4_final.mp4
python3 -X utf8 verify_final.py
python3 -X utf8 qa.py ../REELS_4_final.mp4
python3 -X utf8 capa/make_cover.py
```

Os nomes de arquivo internos seguem o REELS 3 (`REELS3.json`, `reels3_raw.mp4`); a pasta do Reel dá o nome do arquivo final. O diário `diario_exemplo_reels3.md` descreve cada etapa.

## Padrão visual em resumo

- Cores: Azul Noturno `#010B25`, Azul Institucional `#031954`, Azul Ordem `#0457E7`, Azul Claro `#5CA2EE`, Branco `#F6F6F8`, Dourado `#F4B04A` (um destaque por peça), papel `#F4F2EC`.
- Fontes: Bebas Neue (títulos e números), Inter (etiquetas, corpo e rodapés), Playfair Display (frases-tese).
- Sem emojis, sem brilho e sem molduras neon. Um rosto expressivo e nítido na thumbnail, com título em pergunta.
- Áudio final em −14 LUFS, sem trilha musical no vídeo.

O padrão completo (regras, decisões da direção e estrutura de entrega) está no documento "PADRÃO DE EDIÇÃO NOE" da Central de Agentes.

## Licenças de terceiros

- Fontes Inter, Bebas Neue e Playfair Display: SIL Open Font License.
- three.js: licença MIT. GSAP: licença padrão da GreenSock.
- A vinheta, a bússola e a identidade visual são do canal A Nova Ordem Educacional.
