# Lote "todos os vídeos do canal → Spotify" — estado em 11/11/2026 22:40

Pedido do usuário (11/11): fazer o episódio de Spotify de TODOS os vídeos longos do canal (sem shorts) e deixar
tudo pronto para postar, em par com o YouTube. Trabalhar sem perguntar. Voz: Francisca (edge-tts). Não refazer
os 5 antigos.

## Canal (29 vídeos longos, ordem de publicação = número do arquivo)
01 T6e8 · 02 QBkm · 03 xcRV · 04 CeMc · 05 qvtu  → JÁ PRONTOS (pipeline antigo; export.py já sabe os nomes)
06 7A15 IA em nível humano · 07 YzJY #5 parte 1 · 08 RT68 #5 parte 2 · 09 5Wdr A culpa é do professor
10 oOSz #6 · 11 vTg8 diploma prova competência · 12 H5eW #7 Universidade Lego · 13 mKK- Reflexão PISA 2025
14 -YRr #8 tempo integral · 15 ZaBM alunos já usam IA · 16 lu0Y #9 escola privada · 17 1kBi #10 quem responde
18 SynE formação continuada · 19 y_xL IDEB melhorou · 20 wOZz Professor + IA #EP2 · 21 7t5Z média da escola
22 HkvY #EP3 um ano a mais · 23 IxT7 Papo Reto #1 · 24 hQXE Papo Reto #2 · 25 jSMC Papo Reto #3
26 2NU7 pensar ou concordar · 27 UHAv o aluno está aprendendo · 28 ZqDu Papo Reto #4
29 GnN-re_oCXw "O medo de errar…" Papo Reto — ESTREIA 12/11 no YouTube: baixar e fazer depois.
Pastas: SPOTIFY/EP_<4 primeiras letras do id>. Títulos/datas em EP_*/src/info.txt; descrição do YouTube em src/desc_youtube.txt.

## Estado (atualizado 17/11/2026)
- 30 episódios prontos em SPOTIFY/PRONTOS_PARA_POSTAR e TODOS publicados no Spotify for Creators (01-05 pelo usuário,
  06-30 por mim). Último: 30 A4j9mL0w4OE "Qual profissão vai acabar primeiro?" (YouTube 16/11/2026).
- Rotina quando o usuário pedir "vê os novos": listar o canal (/videos, sem shorts), comparar com as pastas EP_*,
  baixar, prep, plan (numerar 31, 32, ...), build, verify, export, publicar (método na memória spotify-podcast-standard).
- Título no Spotify: solto, sem número nem rótulo (regex em publicar: tira "Episódio N —", "#N —", "Papo Reto (#N) —",
  "Reflexão —", "Especial —", "#EPn").
- Cuidados aprendidos: (1) fim de span por ⟨t⟩ pode cortar a última palavra curta — conferir no verify_edges; se cortar,
  usar trecho inteiro (índice) ou [t0, t1, "raw"]; (2) o corte por fim~ negativo pode cair antes de uma palavra baixa
  (H5eW "dois"); (3) vídeos com retake repetido: vTg8 (533-564 s) e H5eW (trechos 193-212).

## Como fazer cada episódio (pipeline em SPOTIFY/_pipeline, rodar de dentro dessa pasta)
1. `python -X utf8 prep.py ../EP_xxxx` → edit/transcript.txt. Ler. Notação:
   `#i [mm:ss|s]` trecho de fala i · `‖i` pausa curta · `⟨t⟩` início da palavra seguinte (ponto de corte)
   `⟨fim~a | b⟩` buraco sem fala entre a e b (se a linha não mostra "(Ns)" de pausa, ali tem som: cortar)
   `⟪som …⟫` som colado no começo/fim do trecho · `(SOM, pulado)` o mix já pula · `⟦texto⟧` fala que o whisper pulou (é fala, manter).
2. Escrever edit/plan.json (modelo: EP_vTg8/edit/plan.json): name "NN_slug", title, youtube_id, summary, refs (opcional),
   blocks {cold, b1..bn} com title (+ "say" quando o título tem sigla/número ruim para a voz) e spans,
   narration {intro, recap, outro}. A fala "Bloco N. título" é automática; o último bloco vira "Encerramento".
   Span [a, b]: inteiro = índice de trecho; decimal = ⟨t⟩ (início da palavra seguinte ao corte);
   decimal NEGATIVO em b = fim~ da última palavra; [t0, t1, "raw"] = exato. `python w.py ../EP t0 t1` mostra palavras com tempo.
3. `python -X utf8 build.py ../EP_xxxx` (narração + mix + master + descrição com capítulos) — 1,5 a 7 min.
4. `python -X utf8 verify_narr.py ../EP_xxxx` e `python -X utf8 verify_edges.py ../EP_xxxx`.

## Regras de edição (padrão aprovado)
- cold open = gancho inicial do vídeo (antes da vinheta do YouTube); cortar a vinheta/música do vídeo.
- Cortar: "se inscreva", "joinha", "comenta aí", "link na descrição", "fui!", retakes repetidos (ex.: vTg8 533–564 s).
- Manter "manda para…/compartilhe" quando funciona em áudio. Não cortar conteúdo do apresentador.
- Narração sem siglas: escrever "inteligência artificial", números por extenso, sem travessão.
- Episódio longo: 6 a 12 blocos. recap = 3 ideias. outro = "Siga o podcast…".
- Dados citados: checar quando soar estranho e avisar o usuário; não mexer na fala.
