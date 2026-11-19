# EP8 "SINAEPT" — cut plan (source word indices of transcripts/EP8.json)
HOOK = [(25, 73)]            # "De que adianta avaliar milhares de cursos técnicos... É sobre essa diferença que vamos conversar" then the vinheta
DROP = [
    (19, 24, "'Hoje quero começar com uma pergunta' (the question already opened the video)"),
    (74, 79, "'E vamos conversar muito neste episódio'"),
    (101, 107, "garbled 'ela já estava para todos entenderem que'"),
    (120, 122, "'e foi criado' (the Sinaept was instituted earlier; the ordinance implements it)"),
    (164, 165, "'Vamos lá?'"),
    (573, 576, "'E vamos em frente.'"),
    (1346, 1353, "slip 'Mas basta descobrir onde a educação profissional falha' (he corrects it right after)"),
    (1695, 1699, "'Esse papo melhora ou não?'"),
    (1716, 1749, "rambling share request"),
    (1760, 1761, "'e fui'"),
]
HOLD = {48: 0.25, 73: 0.3, 18: 0.15, 163: 0.2, 234: 0.2, 331: 0.3, 489: 0.3, 655: 0.3, 802: 0.3, 936: 0.3, 1099: 0.3, 1216: 0.25, 1285: 0.25,
        1369: 0.3, 1489: 0.25, 1660: 0.3, 1715: 0.3, 1759: 0.4}
