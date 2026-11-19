# REELS 3 = SHORT 03 · "Planilha do chefe" — série "O futuro não vai esperar você" (Dr. Hélio)

**Fonte:** `<pasta de gravações>/Cortes\REELS 3.MP4` (vertical 1080×1920, 30 fps, 24,1 s, take único).
**Roteiro da série:** `<pasta de gravações>/Roteiro_Edicao_Shorts_O_Futuro_Nao_Vai_Esperar_Voce.docx` (cópia em texto: `roteiro_shorts.txt`).

## Session 1 — 2026-11-12 (versão rejeitada, guardada em `v1_roteiro/`)

Primeira versão feita ao pé da letra das regras visuais do roteiro: rosto em tela cheia, legenda Bebas branca com contorno no meio do quadro, faixa azul com o texto de capa, planilha plana como B-roll, base musical sintetizada e só 4 efeitos. Resposta do usuário: **"tá ruim, volta pra pegada antiga e aprimora tudo"**. Ele não disse qual parte estava ruim. Arquivos dessa versão (vídeo, capa, legenda, scripts): `v1_roteiro/`.

## Session 2 — 2026-11-12: de volta ao padrão dos REELS 1 e 2, com melhorias

### O que ele falou (transcrição) × roteiro
"Sabe aquela reunião para a qual você não foi chamado? Pode ter sido sobre o quanto você custa por mês, e quanto custa uma ferramenta que faz as suas entregas pela metade do preço. Não é maldade, é planilha, e planilha não tem sentimento. Então me diz: o que você entrega que não cabe nessa conta?"

- O roteiro abre com a comparação de custo e só depois fala da reunião; ele fez o contrário. A ordem falada foi mantida.
- Última palavra: a transcrição automática ouviu "cota" nas três janelas testadas; o roteiro diz "conta". Legenda segue o roteiro. Não dá para ouvir daqui: o usuário precisa conferir.

### O que vem do roteiro e o que vem do padrão antigo
- **Do roteiro (conteúdo):** as falas, o texto de capa "VOCÊ X FERRAMENTA" (está no painel da sala, ao lado da porta, e na capa), o título "Seu chefe já fez essa conta" e o comentário fixado (legenda e cartão de comentário), fala no quadro 0, pausas cortadas, duração 15–30 s, final em pergunta que emenda no começo, nada de logo real, nenhum número inventado na tela (só a relação: 8 moedas × 4 moedas, ½).
- **Do padrão antigo (visual e som):** painel de papel com 3D em cima, rosto embaixo, legenda em pílula azul na emenda, duas telas cheias, cartão de comentário, desenho de som denso, voz tratada, sem música.
- **Regras do roteiro não aplicadas:** legenda Bebas com contorno a 55–65 % da altura, faixa azul, limite de 4 efeitos, base musical, corte seco na última palavra (ficou 0,5 s de imagem real para o cartão de comentário fechar).

### Corte
24,1 s → 18,33 s (550 quadros, 11 segmentos). Pausas > 0,25 s cortadas; respiro extra depois de "chamado?" (0,10 s) e "preço." (0,16 s); 0,5 s depois da última palavra (ele continua olhando para a câmera).

### Cenas (um mundo só: peão dourado = VOCÊ, robô = FERRAMENTA, a planilha)
1. **Gancho (0–2,67 s, painel):** a porta da sala de reunião bate no quadro 0; pela janela, três silhuetas e balões de conversa (um deles com o peão); o painel da sala diz "EM REUNIÃO · VOCÊ X FERRAMENTA". O peão VOCÊ aparece do lado de fora, entra o selo vermelho ✕ em "não" e um "?" em "chamado?". A câmera mergulha na janela.
2. **TELA CHEIA (2,67–5,33 s):** a planilha "CUSTO POR MÊS" com as linhas VOCÊ e FERRAMENTA; o peão sobe num pedestal; em "você" a linha acende e o cursor cai na célula; em "custa" a barra dourada cresce e 8 moedas empilham; calendário "MÊS".
3. **Painel (5,33–10,17 s):** o robô sobe com a etiqueta "R$ ?"; placa FERRAMENTA; quatro caixas ✓ saem dele e empilham (ENTREGAS); a câmera abre: VOCÊ com 8 moedas e o robô com 8 — em "metade" cai o ½ dourado e metade das moedas do robô voa.
4. **Painel (10,17–11,33 s):** o diabinho ("maldade") e o sinal de proibido em cima dele.
5. **TELA CHEIA (11,33–14,10 s):** a planilha cai do topo e bate ("é planilha"), as células se preenchem; barra de fórmula "= SENTIMENTO"; o coração pulsa, cai na célula, é escaneado, fica cinza e vira "0".
6. **Painel + CTA (14,10–18,33 s):** mini planilha; o presente dourado aparece dentro da célula ("o que você entrega") e cresce até estourar a moldura ("que não cabe"); cartão "COMENTE AQUI — O que você entrega que não cabe na planilha?", digitando "EU ENTREGO…", Seguir → Seguindo.

### O que foi melhorado em relação ao REELS 2
- Legenda acende palavra por palavra (o bloco entra apagado, cada palavra acende quando ele fala); a pílula nunca some por um quadro entre blocos.
- Enquadramento do rosto calculado quadro a quadro pelo rastreio dos óculos: todo corte cai na mesma linha dos olhos, os punch-ins são centrados nos olhos, 60 % da deriva lenta dele é compensada, e o último quadro volta ao enquadramento do primeiro. Vinheta leve no vídeo.
- Um mundo 3D contínuo com os mesmos personagens; luz de recorte por trás e luz principal em movimento leve.
- Nenhum quadro vazio nos cortes de cena: as entradas começam 0,1 s antes do corte.
- Som: 159 eventos sintetizados presos ao que aparece (porta batendo no gancho, moedas em tom ascendente, robô, caixas, caixa registradora no ½, batimento do coração e linha reta no "0", estalo quando a célula não aguenta, digitação, subida no fim que emenda no início). Efeitos 2,5 dB mais baixos no conjunto, por serem mais densos que no REELS 2.

### Verificação do arquivo final (`../REELS_3_final.mp4`, 18,33 s)
- `qa.py`: H.264 yuv420p bt709 + AAC, 550 quadros; −14,0 LUFS, pico real −2,5 dBTP; nenhum congelamento ou quadro preto; defasagem áudio/vídeo 0 ms.
- `audio/check.py`: efeitos em média 17,5 dB abaixo da voz; só 4 janelas de 100 ms em que chegam a menos de 6 dB da voz na faixa da fala, todas em pausas entre frases.
- `verify_final.py`: linha dos olhos a no máximo 12 px do alvo nos cortes (dois cortes com +20 e +28 px na horizontal, onde o recorte bate na borda do quadro); último quadro × primeiro: (+5,5; +14,7) px e −2,5 % de tamanho; pílula de legenda presente em todos os quadros (no primeiro quadro de cada bloco ela está a 55 %).
- Folhas de contato a 3 fps e os cinco cortes de cena quadro a quadro conferidos; iguais às prévias. Áudio conferido só por medição (não é possível ouvir).

### Capa e legenda
- `../REELS_3_capa.jpg`: estilo das capas dos REELS 1 e 2 — "SEU CHEFE JÁ FEZ / ESSA CONTA" + destaque dourado "VOCÊ X FERRAMENTA", recorte dele (olhar direto, boca fechada, quadro 13,35 s da fonte) sobre o painel azul, ícone de planilha e selo R$. Tudo dentro do corte 3:4 da grade (y 240–1680).
- `../legenda_instagram.txt`: título e comentário fixado do roteiro + dicas.

**Arquivos:** `cut.py` → `base.mp4`; `track_face.py` → `track.json`; `hf/build.py` + `hf/timeline.js` + `hf/scene3d.js` → `hf/index.html`; render → `reels3_raw.mp4`; `audio/sound.py` → `../REELS_3_final.mp4`; `capa/make_cover.py` → `../REELS_3_capa.jpg`.
Render: `plugin-cli.mjs render . --fps 30 --quality looks --low-memory-mode --frames-cache-dir <pasta de cache>` (cada versão usou uma pasta de cache nova; o sistema recusa apagar essas pastas, o usuário pode apagar `D:\hf-cache-reels3`, `-v2`, `-v3`, `-v4`, `-v5`).

**Outstanding:** o usuário ainda não reagiu a esta versão; confirmar a palavra final ("conta"); se informar o @ do Instagram, trocar no cartão de CTA.
