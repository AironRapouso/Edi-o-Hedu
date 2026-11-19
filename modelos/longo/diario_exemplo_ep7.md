# EP7 — "A educação profissional do futuro" (YouTube 16:9 + 3 shorts + Spotify)

## Session 1 — 2026-11-17/18
**Fonte:** Drive (link do vídeo bruto) → `../raw/source.mp4` (1920×1080, 29.97 fps, 22:58). Sem roteiro no Drive (o "Episódio 6 Educação Técnica" é de outro vídeo): edição estruturada a partir da fala.
**Tema:** novas DCN da EPT (Parecer CNE/CP nº 21/2026). Gravado antes da homologação (MEC 10/11/2026 → Resolução CNE/CP nº 2/2026): nota de atualização na cena "parecer" e na descrição. "75 artigos" não confirmado.
**Corte (`cut.py` + `plan.py`):** 22:58 → 19:04. HOOK = palavras 5–72 (até "Vamos pensar nisso?"), vinheta, corpo, tela final. Removidos: pré-rolo, "Se não vejamos", "Isso é um aberrácio", "trabalhador que recebeu a sua profissão e está mudando", "ou seu comentário", "Fui.". Quadro: crop 1600×900 (x122,y30) ampliado para 1080p; FACE (960,449).
**Lição:** o primeiro HOOK (5–75) levou "Olá, meus amigos" para antes da vinheta; só apareceu na transcrição do Spotify. Conferir sempre a última palavra do gancho.
**Cenas (`hf/cues.py`):** 37 cenas 3D + 19 chips; âncoras A()/Z() por prefixo de palavra (K com janela −8: cuidado com palavras curtas "E", "A", "O"). Render 136 min (`render_long.sh`, cache <pasta de cache>). Áudio `audio/sound.py` → `../EP7_final.mp4` (−14 LUFS, −1.3 dBTP).
**Shorts (`vert/`):** 3 cortes no look dos Reels com gancho de título de 1,7 s cobrindo o painel (novo `vhook`): c1 chamamento (49–69 + 2147–2185), c2 IA (1129–1183), c3 10 mil (1277–1328) → `../shorts/`. Capas em `../shorts/capas` (takes 1003.80, 995.00, 1099.83 s).
**Thumbnail:** `../thumbnail/thumb.html` (take 1003.80 s, mãos abertas) → `../EP7_thumbnail.jpg`.
**Spotify:** `SPOTIFY/EP_EDU7` (fonte = audio_raw.wav do corte), nº 31 → `../spotify/`. `SPOTIFY/EP_EDUP` é uma tentativa descartada (pode apagar).
**Drive:** Podcast N.O.E › PRONTOS PARA POSTAR › A EDUCAÇÃO PROFISSIONAL DO FUTURO , subpastas 1/2/3. Conector limita upload a 10 MB: vídeos e MP3 ficam para o usuário arrastar.

## Session 2 — 2026-11-18 (user: long video must NOT be in the Reels look)
User approved shorts/capas/thumbnail/Spotify, rejected the long video ("idêntico ao Reels"). Rebuilt in the earlier long-video standard:
`hfl/` = EP_AULA_INVERTIDA build.py + `ep7_cues.py` (pills, pair, chain, qstack, checks, optstack, stack2, beats, 2 side data panels, 7 intertitles, seal, lower thirds, end screen) + 15 fresh Pexels clips (`broll/`, graded by the loop in session log; list in ../../broll_usados.txt).
cut.py now takes `INTER = {word: "In"}` in plan.py (2.2 s intertitle gaps) → 19:20. Voice = v1 treated stem remapped segment by segment to the new timeline (`audio/voice_long.wav`), SFX = the template's discreet wav set, loudnorm → `../EP7_final.mp4` (−14.0 LUFS, offset 0 ms). v1 kept as `../EP7_final_v1_estilo_reels.mp4`; its cut in `v1_reels/` (the shorts were built from it and are unchanged).
Render 115 min (`render_long2.sh`, cache <pasta de cache>).
