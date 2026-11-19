# Cue sheet for EP8 "SINAEPT — avaliar ou transformar?" — exec'd by build.py (helpers live there).
# Cast: grey pawns = people / institutions, gold pawn = the student, robot = technology / AI, docs = norms and reports.
# Anchors: S("phrase") = start of a phrase that occurs exactly once in the source words, E("phrase") = its end.

SRC_NOTE = "Fonte: Portaria Inep nº 545, de 15/10/2026 · Diário Oficial da União de 16/10/2026, Seção 1 (Extra C), p. 7"
SRC_DIM = "Fonte: Portaria Inep nº 545/2026, art. 7º (as cinco dimensões avaliativas do Sinaept)"
SRC_DADOS = "Fonte: Portaria Inep nº 545/2026, art. 18, § 2º"

_NW = [_norm(w["text"]) for w in ALLW]


def P(phrase):
    toks = [_norm(x) for x in phrase.split()]
    toks = [x for x in toks if x]
    hits = [i for i in range(len(_NW) - len(toks) + 1) if _NW[i:i + len(toks)] == toks]
    if len(hits) != 1:
        raise ValueError(f"phrase '{phrase}' found {len(hits)} times: {hits}")
    return hits[0], hits[0] + len(toks) - 1


def S(phrase, dt=0.0):
    return T(P(phrase)[0], dt)


def E(phrase, dt=0.0):
    return TE(P(phrase)[1], dt)


def Pl(txt, t, p, **kw):
    p = list(p)
    if kw.get("r") and p[1] < 0.5:
        p[1] = 0.5
    return it("plate", txt=txt, t=t, p=p, **kw)


def Sym(txt, t, p, size=0.7, **kw):
    return it("plate", txt=txt, t=t, p=list(p), w=size, h=size, bg="gold", fs=0.8, quiet=True, **kw)


def stack(rows, y0=4.3, dy=0.78, x=0.0, z=0.6, w=3.9, h=0.56, bg="white", fs=0.6, out=None, badge=None, bx=2.15):
    """rows = [(txt, t)] or [(txt, t, bg)] -> plates stacked top to bottom (side panel list)"""
    its = []
    for k, r in enumerate(rows):
        txt, t = r[0], r[1]
        b = r[2] if len(r) > 2 else bg
        kw = dict(w=w, h=h, bg=b, fs=fs)
        if out is not None:
            kw["out"] = out
        its.append(Pl(txt, t, [x, y0 - k * dy, z], **kw))
        if badge:
            bk = dict(rad=0.24, kind=badge, p=[x + bx, y0 - k * dy, z + 0.25], t=t + 0.18, quiet=True)
            if out is not None:
                bk["out"] = out
            its.append(it("badge", **bk))
    return its


def row(n, y=0, z=2.0, x0=-5.4, dx=1.2, t=0.0, mat=None, s=0.36):
    return [it("pawn", p=[x0 + k * dx, y, z], s=s, mat=(mat(k) if callable(mat) else (mat or "grey")), t=t + 0.04 * k, quiet=True) for k in range(n)]


# =================================================================== HOOK (his own opening question, before the vinheta)
# "De que adianta avaliar milhares de cursos técnicos e produzir milhões de informações,"
full("q0", 0.0, E("produzir milhões de informações", 0.25), [
    *[it("doc", txt="", head="#0457E7", w=0.9, h=1.2, p=[-6.0 + k * 1.5, 0.9, -0.8 + (k % 2) * 0.5], t=0.02 + k * 0.05, r=[0, 0.2, 0.02], quiet=True) for k in range(9)],
    Pl("DE QUE ADIANTA", 0.0, [0, 6.3, 0], w=5.2, h=0.9, bg="plate", fs=0.7),
    Pl("AVALIAR MILHARES DE CURSOS", S("avaliar milhares"), [0, 5.0, 0.4], w=9.0, h=1.0, bg="white", fs=0.68),
    Pl("PRODUZIR MILHÕES DE INFORMAÇÕES", S("produzir milhões de informações"), [0, 3.6, 0.8], w=10.2, h=1.0, bg="white", fs=0.66),
], cam=(0.8, 3.8, 18.6), look=(0, 3.1, 0), moves=[[0, 7.0, (0, 3.6, 16.8), (0, 3.1, 0), "sine.out"]])
sfx(0.0, "slam", -10, 0, "hook impact frame 0")

chip("c1", S("se ao final", -0.05), E("realmente aprendem", 0.3), [("SE O ESTUDANTE", S("se ao final")), (f'NÃO {G("APRENDE MAIS")}?', S("realmente aprendem"))])
emph(S("se ao final", -0.05), E("realmente aprendem", 0.3), 1.18)

# "Avaliar a educação profissional é uma coisa. Usar a avaliação para transformá-la é outra, muito diferente."
side("q1", S("Avaliar a educação profissional é uma", -0.2), E("outra muito diferente", 0.35), [
    it("doc", txt="RELATÓRIO", head="#0457E7", w=1.7, h=2.1, p=[-1.2, 2.2, -0.2], t=S("Avaliar a educação profissional é uma", 0.15), r=[0, 0.25, 0.03], float=0.05),
    Pl("AVALIAR", S("Avaliar a educação profissional é uma", 0.1), [-1.1, 4.5, 0.2], w=2.3, h=0.62, bg="plate"),
    Pl("É UMA COISA", S("é uma coisa"), [-1.1, 3.8, 0.3], w=2.3, h=0.5, bg="white", fs=0.5),
    it("pawn", p=[1.3, 0, 0.6], s=0.5, mat="gold", t=S("Usar a avaliação para transformá", 0.05)),
    Pl("TRANSFORMAR", S("Usar a avaliação para transformá", 0.1), [1.2, 4.5, 0.4], w=2.5, h=0.62, bg="gold", fs=0.56),
    Pl("É OUTRA", S("outra muito diferente"), [1.2, 3.8, 0.5], w=2.5, h=0.5, bg="white", fs=0.5),
], cam=(0.2, 3.3, 13.2), look=(0, 2.5, 0))
chip("c2", S("sobre essa diferença", -0.1), TE(73, 0.3), [("É SOBRE ESSA", S("sobre essa diferença")), (G("DIFERENÇA"), S("sobre essa diferença", 0.5))], side_="left")

# =================================================================== BODY
# "Em 15 de outubro de 2026, o Inep editou a Portaria 545, publicada no Diário Oficial da União no dia seguinte. Ela disciplina o Sistema Nacional de Avaliação..."
full("portaria", S("Em 15 de outubro", -0.1), TE(124, 0.6), [
    it("calendar", txt="15 OUT 2026", p=[-5.6, 3.6, 0], s=1.0, t=S("Em 15 de outubro", 0.2)),
    Pl("INEP", S("O Inep editou"), [-1.9, 5.9, 0], w=2.6, h=1.0, bg="plate", fs=0.72),
    it("doc", txt="PORTARIA", head="#C9A45A", w=2.9, h=3.5, p=[0.2, 2.6, 0.4], t=S("editou a portaria"), r=[0, 0.18, 0.03], float=0.05),
    Pl("Nº 545", S("545 publicada"), [1.9, 5.9, 0.2], w=3.2, h=1.0, bg="gold", fs=0.74),
    Pl("DIÁRIO OFICIAL · 16/10/2026", S("Diário Oficial da União"), [5.6, 4.4, 0.6], w=5.4, h=0.8, bg="white", fs=0.56),
    Pl("AVALIAÇÃO DA EDUCAÇÃO PROFISSIONAL E TECNOLÓGICA", S("disciplina o Sistema", 0.3), [1.6, 0.4, 2.2], w=10.6, h=0.8, bg="white", fs=0.54, r=[-0.3, 0, 0]),
    Pl("SINAEPT", T(124, -0.05), [5.6, 3.0, 0.9], w=4.4, h=1.2, bg="gold", fs=0.76),
], cam=(0.6, 3.6, 18.2), look=(0.6, 3.0, 0))

chip("c3", S("É um movimento importante", -0.1), E("É um movimento importante", 0.3), [("UM MOVIMENTO", S("É um movimento importante")), (G("IMPORTANTE"), S("movimento importante", 0.25))])

# "O Brasil precisa avaliar a qualidade da educação profissional que oferece, conhecer suas instituições, acompanhar seus estudantes e entender como a formação se relaciona com o mundo do trabalho"
side("why", S("O Brasil precisa avaliar", -0.2), E("se relaciona com o mundo do trabalho", 0.35), [
    Pl("O BRASIL PRECISA", S("O Brasil precisa avaliar", 0.15), [0, 5.0, 0.2], w=3.4, h=0.58, bg="plate"),
    *stack([("AVALIAR A QUALIDADE", S("avaliar a qualidade"), "gold"), ("CONHECER AS INSTITUIÇÕES", S("conhecer suas instituições")),
            ("ACOMPANHAR OS ESTUDANTES", S("acompanhar seus estudantes")), ("LIGAR FORMAÇÃO E TRABALHO", S("a formação se relaciona"))],
           y0=4.1, dy=0.8, w=4.2, h=0.54, fs=0.52, badge="ok", bx=2.3),
], cam=(0, 3.0, 13.0), look=(0, 2.7, 0))

chip("c4", S("Mas faço uma ressalva", -0.1), E("Mas faço uma ressalva", 0.3), [("MAS FAÇO", S("Mas faço uma ressalva")), (f'UMA {G("RESSALVA")}', S("uma ressalva"))])

# "O maior desafio não é criar mais um sistema de avaliação. É impedir que ele reproduza as limitações que já conhecemos."
side("desafio", S("O maior desafio", -0.2), E("limitações que já conhecemos", 0.35), [
    Pl("O MAIOR DESAFIO", S("O maior desafio", 0.12), [0, 5.0, 0.2], w=3.4, h=0.6, bg="plate"),
    it("doc", txt="SISTEMA", head="#9A9BA5", w=1.6, h=2.0, p=[-1.3, 2.3, 0], t=S("criar mais um sistema"), r=[0, 0.25, 0.03]),
    Pl("NÃO É CRIAR MAIS UM", S("não é criar mais"), [0, 4.2, 0.4], w=4.0, h=0.56, bg="red", fs=0.54),
    it("badge", rad=0.4, kind="x", p=[-0.3, 3.2, 0.8], t=S("criar mais um sistema", 0.3), quiet=True),
    Pl("É NÃO REPETIR", S("É impedir que ele"), [0.9, 2.2, 1.0], w=3.2, h=0.6, bg="gold", fs=0.56),
    Pl("AS LIMITAÇÕES DE SEMPRE", S("as limitações que já"), [0, 0.35, 2.3], w=4.3, h=0.54, bg="white", fs=0.52, r=[-0.4, 0, 0]),
], cam=(0, 3.1, 13.0), look=(0, 2.5, 0))

chip("c5", S("E quais são elas", -0.1), E("Quais são essas limitações", 0.3), [("QUAIS SÃO", S("E quais são elas")), (f'ESSAS {G("LIMITAÇÕES")}?', S("Quais são essas limitações"))])

# "Ao longo de décadas construímos uma cultura preocupada em demonstrar que a escola funciona. Quantos alunos se matricularam? Quantos concluíram? Quantos laboratórios... Quantos professores..."
QN = [("MATRÍCULAS", S("Quantos alunos se matricularam")), ("CONCLUINTES", S("Quantos concluíram")), ("LABORATÓRIOS", S("Quantos laboratórios")),
      ("PROFESSORES", S("Quantos professores foram"))]
side("indic", S("Ao longo de décadas", -0.2), E("professores foram contratados", 0.35), [
    Pl("DÉCADAS PROVANDO QUE", S("Ao longo de décadas", 0.12), [0, 5.2, 0.2], w=4.0, h=0.54, bg="plate", fs=0.52),
    Pl("A ESCOLA FUNCIONA", S("que a escola funciona"), [0, 4.5, 0.3], w=4.0, h=0.6, bg="gold", fs=0.56),
    *sum([[it("bar", w=0.62, h=2.4, d=0.6, mat="blue", p=[-1.65 + k * 1.1, 0, 0.2], t=t, quiet=True, grow=[[t, 0.5, 0.45 + 0.16 * k]]),
           Pl(txt, t + 0.05, [0, 3.55 - k * 0.0, 0.6], w=3.2, h=0.52, bg="white", fs=0.52, out=(QN[k + 1][1] - 0.05 if k < 3 else None))]
          for k, (txt, t) in enumerate(QN)], []),
], cam=(0, 3.1, 13.0), look=(0, 2.4, 0))

chip("c6", S("São perguntas importantes", -0.1), E("comprova que o estudante aprendeu", 0.35), [("PERGUNTAS IMPORTANTES,", S("São perguntas importantes")),
                                                                                                ("MAS NENHUMA COMPROVA", S("mas nenhuma delas")),
                                                                                                (f'QUE O ALUNO {G("APRENDEU")}', S("comprova que o estudante"))])

# "Uma instituição pode ter um belo prédio, laboratórios modernos, um projeto pedagógico bem escrito e altos índices de aprovação."
side("predio", S("Uma instituição pode ter", -0.2), E("altos índices de aprovação", 0.35), [
    it("box", w=2.6, h=2.0, d=1.6, mat="blue", own=True, p=[0, 1.0, -0.6], t=S("Uma instituição pode ter", 0.15)),
    it("box", w=1.0, h=2.9, d=1.2, mat="blue", own=True, p=[-1.9, 1.45, -0.9], t=S("um belo prédio"), quiet=True),
    *stack([("BELO PRÉDIO", S("um belo prédio")), ("LABORATÓRIOS MODERNOS", S("laboratórios modernos")),
            ("PROJETO BEM ESCRITO", S("um projeto pedagógico")), ("ALTA APROVAÇÃO", S("altos índices"))],
           y0=5.2, dy=0.66, w=4.0, h=0.5, fs=0.52, badge="ok", bx=2.2),
], cam=(0, 3.4, 13.2), look=(0, 2.7, 0))

chip("c7", S("resta a pergunta principal", -0.2), E("para o qual foi formado", 0.35), [("A PERGUNTA PRINCIPAL:", S("resta a pergunta principal")),
                                                                                       ("O ESTUDANTE SAIU", S("O estudante saiu dali")),
                                                                                       (f'SABENDO {G("FAZER")}?', S("sabendo fazer"))])
emph(S("O estudante saiu dali", -0.1), E("para o qual foi formado", 0.3), 1.2)

# "Estamos formando pessoas para a saúde, a indústria, a tecnologia, o comércio, o agronegócio e os serviços. Competências que envolvem segurança, responsabilidade e decisões que afetam a vida de outras pessoas"
AREAS = [("SAÚDE", S("para a saúde")), ("INDÚSTRIA", S("a indústria a tecnologia")), ("TECNOLOGIA", S("a tecnologia o comércio")),
         ("COMÉRCIO", S("o comércio o agronegócio")), ("AGRONEGÓCIO", S("o agronegócio e os")), ("SERVIÇOS", S("e os serviços"))]
full("areas", S("Estamos formando pessoas", -0.1), E("a vida de outras pessoas", 0.5), [
    Pl("FORMAMOS PESSOAS PARA", S("Estamos formando pessoas", 0.1), [0, 6.3, 0], w=7.4, h=0.95, bg="plate", fs=0.66),
    *[Pl(txt, t, [-4.3 + (k % 3) * 4.3, 4.9 - (k // 3) * 1.15, 0.4], w=3.9, h=0.85, bg="white", fs=0.6) for k, (txt, t) in enumerate(AREAS)],
    *row(10, t=S("para a saúde"), mat=lambda k: "gold" if k % 3 == 1 else "grey"),
    Pl("SEGURANÇA · RESPONSABILIDADE", S("envolvem segurança"), [0, 2.5, 1.0], w=9.0, h=0.85, bg="plate", fs=0.6),
    Pl("DECISÕES QUE AFETAM VIDAS", S("decisões que afetam"), [0, 1.4, 1.5], w=9.0, h=0.95, bg="gold", fs=0.66),
], cam=(0, 3.8, 18.8), look=(0, 3.2, 0))

# "Por isso, não podemos confundir a entrega de um diploma com a demonstração de uma competência."
side("diploma", S("não podemos confundir a entrega", -0.6), E("demonstração de uma competência", 0.4), [
    Pl("NÃO CONFUNDIR", S("não podemos confundir a entrega", 0.12), [0, 5.1, 0.2], w=3.2, h=0.58, bg="red"),
    it("doc", txt="DIPLOMA", head="#C9A45A", w=1.6, h=2.0, p=[-1.35, 2.6, 0], t=S("entrega de um diploma"), r=[0, 0.28, 0.03], float=0.05),
    Sym("≠", S("com a demonstração"), [0.0, 2.7, 0.8], size=0.6),
    it("pawn", p=[1.35, 1.5, 0.3], s=0.5, mat="gold", t=S("com a demonstração", 0.15)),
    Pl("COMPETÊNCIA", S("de uma competência"), [1.3, 3.9, 0.5], w=2.4, h=0.56, bg="gold", fs=0.52),
    Pl("DIPLOMA", S("entrega de um diploma", 0.1), [-1.35, 3.9, 0.5], w=2.0, h=0.56, bg="white", fs=0.54),
], cam=(0, 3.2, 13.0), look=(0, 2.7, 0))

chip("c8", S("O que a portaria do INEP", -0.1), E("o mérito da portaria", 0.3), [("O QUE A PORTARIA", S("O que a portaria do INEP")), (f'{G("PROPÕE")}?', S("INEP propõe")),
                                                                              ("TEM UM MÉRITO", S("reconhecer o mérito"))])

# "O Sinaept se organiza em cinco dimensões: condições de oferta e formação; fluxo e rendimento; desempenho dos estudantes, inclusive habilidades práticas; oferta x mundo do trabalho; egressos"
side("dim", S("SINAEPT se organiza", -0.25), E("as trajetórias dos egressos", 0.4), [
    it("numeral", txt="5", size=0.9, p=[-1.75, 4.75, 0.0], t=S("em cinco dimensões"), r=[0, 0.25, 0], spin=0.12, louder=2),
    Pl("DIMENSÕES DO SINAEPT", S("SINAEPT se organiza", 0.1), [0.55, 5.0, 0.2], w=3.3, h=0.56, bg="plate", fs=0.5),
    *sum([[it("numeral", txt=str(k + 1), size=0.42, p=[-2.15, 3.72 - k * 0.74, 0.5], t=t, r=[0, 0.25, 0], quiet=True),
           Pl(txt, t + 0.05, [0.3, 3.95 - k * 0.74, 0.6], w=3.9, h=0.52, bg=("gold" if k == 2 else "white"), fs=0.46)]
          for k, (txt, t) in enumerate([("CONDIÇÕES DE OFERTA E FORMAÇÃO", S("Primeira as condições")), ("FLUXO E RENDIMENTO", S("Segunda o fluxo")),
                                        ("DESEMPENHO + HABILIDADES PRÁTICAS", S("Terceira o desempenho")), ("OFERTA × MUNDO DO TRABALHO", S("Quarta a relação")),
                                        ("TRAJETÓRIA DOS EGRESSOS", S("E quinta"))])], []),
], cam=(0, 2.7, 13.0), look=(0, 2.6, 0))

chip("c9", S("o INEP não olha apenas", -0.1), E("Isso é positivo", 0.35), [("NÃO SÓ INFRAESTRUTURA", S("não olha apenas")), ("DESEMPENHO E RESULTADOS", S("Olha também para o desempenho")),
                                                                         (G("ISSO É POSITIVO"), S("Isso é positivo"))])

# "Mas uma boa norma não garante, por si só, uma boa avaliação. O verdadeiro teste estará nos instrumentos, nas metodologias e nos ciclos avaliativos."
side("norma", S("Mas uma boa norma", -0.2), E("nos ciclos avaliativos", 0.35), [
    it("doc", txt="NORMA", head="#0457E7", w=1.5, h=1.9, p=[-1.5, 4.2, -0.4], t=S("Mas uma boa norma", 0.15), r=[0, 0.3, 0.04], float=0.04),
    Pl("BOA NORMA", S("uma boa norma não", 0.05), [0.8, 4.75, 0.2], w=2.8, h=0.54, bg="plate", fs=0.54),
    Pl("≠ BOA AVALIAÇÃO", S("só uma boa avaliação"), [0.8, 4.05, 0.3], w=2.8, h=0.54, bg="red", fs=0.5),
    Pl("O VERDADEIRO TESTE", S("O verdadeiro teste"), [0, 3.05, 0.5], w=3.8, h=0.52, bg="gold", fs=0.52),
    *stack([("INSTRUMENTOS", S("nos instrumentos")), ("METODOLOGIAS", S("nas metodologias")), ("CICLOS AVALIATIVOS", S("nos ciclos avaliativos"))],
           y0=2.3, dy=0.66, w=3.8, h=0.5, fs=0.52),
], cam=(0, 2.8, 13.0), look=(0, 2.5, 0))

# "Como avaliar habilidades práticas? Como comparar cursos de realidades diferentes? Como reconhecer metodologias inovadoras? Como evitar que repitam informações? Como transformar resultados em melhoria?"
HOWS = [("AVALIAR HABILIDADES PRÁTICAS", S("Como avaliar habilidades")), ("COMPARAR REALIDADES DIFERENTES", S("Como comparar cursos")),
        ("RECONHECER O QUE É INOVADOR", S("como reconhecer metodologias")), ("NÃO PEDIR O MESMO DADO DE NOVO", S("como evitar que as"))]
full("como", S("Como avaliar habilidades", -0.1), E("em melhoria de aprendizagem", 0.5), [
    it("text", txt="?", size=1.5, mat="gold", p=[-5.4, 5.0, 0.2], t=S("Como avaliar habilidades", 0.2), spin=0.3),
    Pl("COMO...", S("Como avaliar habilidades", 0.1), [0, 6.3, 0], w=4.0, h=0.95, bg="plate", fs=0.7),
    *[Pl(txt, t, [-3.2 + (k % 2) * 6.4, 4.9 - (k // 2) * 1.15, 0.5], w=6.0, h=0.85, bg="white", fs=0.5) for k, (txt, t) in enumerate(HOWS)],
    Pl("TRANSFORMAR RESULTADO EM APRENDIZAGEM", S("como transformar os resultados"), [0, 2.3, 1.2], w=11.0, h=1.05, bg="gold", fs=0.62),
    *row(10, t=S("como transformar os resultados", 0.1), mat="gold"),
], cam=(0, 3.8, 18.8), look=(0, 3.2, 0))

chip("c10", S("Produzir diagnóstico", -0.1), E("em soluções", 0.35), [("DIAGNÓSTICO É FÁCIL.", S("Produzir diagnóstico")), ("DIFÍCIL É A", S("Difícil é")), (G("SOLUÇÃO"), S("em soluções"))])
emph(S("Difícil é", -0.1), E("em soluções", 0.3), 1.18)

chip("c11", S("A educação profissional precisa demonstrar", -0.1), E("precisa demonstrar competências", 0.35),
     [("A EDUCAÇÃO PROFISSIONAL", S("A educação profissional precisa demonstrar")), ("PRECISA DEMONSTRAR", S("precisa demonstrar competências")),
      (G("COMPETÊNCIAS"), S("demonstrar competências", 0.3))], side_="left")

# "Um estudante conclui o curso técnico de enfermagem, cumpriu a carga horária, foi aprovado e recebeu o diploma. Como saber se desenvolveu as habilidades...? Apenas com perguntas teóricas? Evidentemente, não."
ENF = S("Como saber se ele", -0.05)
side("enf", S("Um estudante conclui", -0.2), E("Evidentemente não", 0.35), [
    it("pawn", p=[-1.6, 0, 0.6], s=0.5, mat="gold", t=S("Um estudante conclui", 0.15)),
    Pl("TÉCNICO EM ENFERMAGEM", S("curso técnico de enfermagem"), [0, 5.2, 0.2], w=4.1, h=0.58, bg="plate", fs=0.52),
    *stack([("CARGA HORÁRIA", S("cumpriu a carga")), ("APROVADO", S("foi aprovado")), ("DIPLOMA", S("recebeu o diploma"))],
           y0=4.3, dy=0.7, x=0.5, w=3.0, h=0.52, fs=0.54, badge="ok", bx=1.7, out=ENF),
    Pl("DESENVOLVEU AS HABILIDADES?", ENF + 0.1, [0.2, 4.3, 0.5], w=4.2, h=0.56, bg="gold", fs=0.48),
    Pl("SÓ PROVA TEÓRICA?", S("Apenas com perguntas"), [0.4, 3.3, 0.7], w=3.4, h=0.56, bg="white", fs=0.52),
    it("badge", rad=0.42, kind="x", p=[2.0, 3.7, 1.0], t=S("Evidentemente não")),
], cam=(0, 3.1, 13.0), look=(0, 2.7, 0))

chip("c12", S("Precisamos de avaliações práticas", -0.1), E("sempre que pertinentes", 0.3), [("AVALIAÇÃO PRÁTICA", S("Precisamos de avaliações práticas")),
                                                                                           (f'E SITUAÇÕES {G("SIMULADAS")}', S("situações simuladas"))])

# "Um técnico em eletrotécnica: basta perguntar os princípios de um circuito? Ou avaliar se interpreta um problema e aplica os procedimentos de segurança?  Um estudante de
#  desenvolvimento de sistemas conhece conceitos de programação. Mas consegue analisar um problema, desenvolver uma solução e identificar falhas?"
PR = S("Um estudante de desenvolvimento", -0.05)
side("prat", S("Um técnico em eletrotécnica", -0.2), E("identificar falhas", 0.35), [
    Pl("ELETROTÉCNICA", S("Um técnico em eletrotécnica", 0.12), [0, 5.2, 0.2], w=3.4, h=0.58, bg="plate", out=PR),
    it("box", w=1.3, h=1.0, d=0.9, mat="blue", own=True, p=[-1.5, 0.5, 0.5], t=S("princípios de um circuito"), out=PR),
    Pl("SÓ A TEORIA DO CIRCUITO?", S("basta perguntar"), [0, 4.3, 0.4], w=4.2, h=0.54, bg="grey", fs=0.5, out=PR),
    Pl("INTERPRETA O PROBLEMA", S("interpreta um problema"), [0.3, 3.4, 0.6], w=3.8, h=0.54, bg="white", fs=0.5, out=PR),
    Pl("APLICA A SEGURANÇA", S("aplica os procedimentos"), [0.3, 2.6, 0.8], w=3.8, h=0.54, bg="gold", fs=0.52, out=PR),
    Pl("DESENVOLVIMENTO DE SISTEMAS", PR + 0.12, [0, 5.2, 0.2], w=4.3, h=0.58, bg="plate", fs=0.48),
    it("robot", p=[-1.6, 0, 0.8], s=0.48, t=PR + 0.2, r=[0, 0.5, 0], eyesOn=S("conceitos de programação")),
    Pl("CONHECE OS CONCEITOS", S("conhece conceitos"), [0.3, 4.3, 0.4], w=3.8, h=0.52, bg="grey", fs=0.5),
    *stack([("ANALISA O PROBLEMA", S("analisar um problema")), ("DESENVOLVE A SOLUÇÃO", S("desenvolver uma solução")), ("IDENTIFICA FALHAS", S("identificar falhas"), "gold")],
           y0=3.5, dy=0.7, x=0.5, w=3.4, h=0.52, fs=0.5),
], cam=(0, 3.1, 13.0), look=(0, 2.7, 0))

chip("c13", S("Não estou defendendo", -0.1), E("precisa de instrumentos próprios", 0.35), [("NÃO É TUDO IGUAL.", S("Não estou defendendo")), ("CADA FORMAÇÃO,", S("Cada formação precisa")),
                                                                                         (f'SEU {G("INSTRUMENTO")}', S("instrumentos próprios"))])

side("rigor", S("Isso exige rigor", -0.2), E("na construção das avaliações", 0.35), [
    Pl("ISSO EXIGE", S("Isso exige rigor", 0.12), [0, 4.9, 0.2], w=2.8, h=0.58, bg="plate"),
    *stack([("RIGOR CIENTÍFICO", S("rigor científico")), ("CRITÉRIOS CLAROS", S("critérios claros")), ("PROFESSORES E ESPECIALISTAS", S("professores e especialistas"), "gold")],
           y0=3.95, dy=0.82, w=4.2, h=0.56, fs=0.52, badge="ok", bx=2.3),
    *[it("pawn", p=[-1.2 + k * 1.2, 0, 1.6], s=0.34, mat=("gold" if k == 1 else "grey"), t=S("professores e especialistas", 0.05 * k), quiet=True) for k in range(3)],
], cam=(0, 3.0, 13.0), look=(0, 2.6, 0))

chip("c14", S("saber repetir uma informação", -0.1), E("valor à formação profissional", 0.35), [("REPETIR", S("saber repetir uma informação")), ("NÃO É APLICAR", S("não é saber aplicá")),
                                                                                              (f'{G("APLICAR")} É O VALOR', S("capacidade de aplicar"))])

# "Estamos construindo um sistema nacional de avaliação em plena era da inteligência artificial. Vamos avaliar a educação do futuro só com os instrumentos do passado? Eu espero que não."
full("ia", S("Estamos construindo um sistema", -0.1), E("Eu espero que não", 0.5), [
    it("robot", p=[-5.0, 0, 0.6], s=0.9, t=S("Estamos construindo um sistema", 0.2), r=[0, 0.5, 0], eyesOn=S("inteligência artificial")),
    Pl("UM SISTEMA NACIONAL DE AVALIAÇÃO", S("um sistema nacional de avaliação em"), [1.4, 6.2, 0], w=9.6, h=0.95, bg="plate", fs=0.58),
    Pl("NA ERA DA INTELIGÊNCIA ARTIFICIAL", S("em plena era"), [1.4, 4.9, 0.4], w=9.6, h=0.95, bg="blue", fs=0.58),
    Pl("EDUCAÇÃO DO FUTURO", S("a educação do futuro"), [-0.9, 3.4, 0.8], w=5.4, h=0.9, bg="gold", fs=0.62),
    Pl("INSTRUMENTOS DO PASSADO?", S("instrumentos do passado"), [4.3, 2.2, 1.1], w=6.4, h=0.9, bg="red", fs=0.6),
    it("clock", p=[5.6, 0.6, 1.4], s=0.5, t=S("instrumentos do passado", 0.15), fill=[[S("instrumentos do passado", 0.15), 1.6, 0.9]], color=0xe5484d),
], cam=(0.6, 3.7, 18.6), look=(0.6, 3.1, 0))

side("digital", S("hoje é possível usar", -0.2), E("úteis a professores e estudantes", 0.35), [
    Pl("HOJE É POSSÍVEL", S("hoje é possível usar", 0.12), [0, 5.25, 0.2], w=3.4, h=0.58, bg="plate"),
    *stack([("AVALIAÇÕES DIGITAIS", S("avaliações digitais")), ("ESTUDOS DE CASO", S("estudos de caso")), ("SIMULAÇÕES", S("e simulações")),
            ("EVOLUÇÃO DAS COMPETÊNCIAS", S("acompanhar a evolução")), ("DEVOLUTIVAS ÚTEIS", S("oferecer devolutivas"), "gold")],
           y0=4.4, dy=0.72, w=4.2, h=0.52, fs=0.5),
], cam=(0, 2.9, 13.0), look=(0, 2.6, 0))

chip("c15", S("Mas atenção", -0.1), E("resolveu nada disso", 0.3), [("ATENÇÃO:", S("Mas atenção")), ("TECNOLOGIA NÃO É", S("tecnologia não significa")),
                                                         (f'{G("QUALIDADE")} AUTOMÁTICA', S("automaticamente qualidade"))])

# "Uma prova ruim continua ruim, mesmo aplicada num computador muito moderno. ... está na qualidade do que conseguimos avaliar."
side("prova", S("Uma prova ruim", -0.2), E("do que conseguimos avaliar", 0.35), [
    it("doc", txt="PROVA", head="#E5484D", w=1.4, h=1.7, p=[-1.4, 1.5, 0], t=S("Uma prova ruim", 0.15), r=[0, 0.25, 0.03], float=0.05),
    Pl("PROVA RUIM", S("Uma prova ruim", 0.1), [0, 5.0, 0.2], w=3.0, h=0.6, bg="red"),
    it("box", w=1.6, h=1.1, d=0.2, mat="blue", own=True, p=[1.3, 1.6, 0.3], t=S("num computador")),
    Pl("NO COMPUTADOR MODERNO", S("num computador"), [0.3, 4.1, 0.4], w=4.0, h=0.54, bg="white", fs=0.5),
    Pl("CONTINUA RUIM", S("continua ruim", 0.1), [0.3, 3.3, 0.6], w=3.2, h=0.54, bg="red", fs=0.52),
    Pl("VALE O QUE SE CONSEGUE AVALIAR", S("está na qualidade"), [0, 0.35, 2.3], w=4.4, h=0.54, bg="gold", fs=0.46, r=[-0.4, 0, 0]),
], cam=(0, 3.1, 13.0), look=(0, 2.5, 0))

chip("c16", S("Também não proponho", -0.1), E("vivência concreta", 0.35), [("A PRÁTICA NÃO SAI:", S("Também não proponho")), ("LABORATÓRIO, EQUIPAMENTO,", S("exigem laboratório")),
                                                                         (f'SUPERVISÃO E {G("VIVÊNCIA")}', S("supervisão e vivência"))])

side("combinar", S("O que defendo é combinar", -0.2), E("automatizar a burocracia", 0.35), [
    Pl("COMBINAR", S("O que defendo é combinar", 0.15), [0, 5.1, 0.2], w=2.8, h=0.6, bg="gold"),
    Pl("MÉTODOS TRADICIONAIS", S("metodologias tradicionais"), [-0.1, 4.2, 0.4], w=3.9, h=0.54, bg="plate", fs=0.5),
    Sym("+", S("e novas tecnologias", -0.05), [0, 3.5, 0.7], size=0.42),
    Pl("NOVAS TECNOLOGIAS", S("e novas tecnologias"), [0.1, 2.8, 0.6], w=3.9, h=0.54, bg="blue", fs=0.52),
    it("robot", p=[-1.7, 0, 1.2], s=0.42, t=S("Usar a inteligência disponível"), r=[0, 0.5, 0], eyesOn=S("melhorar a avaliação e")),
    Pl("PARA MELHORAR A AVALIAÇÃO", S("melhorar a avaliação e"), [0.5, 1.75, 1.2], w=3.9, h=0.52, bg="gold", fs=0.46),
    Pl("NÃO SÓ A BUROCRACIA", S("não apenas para automatizar"), [0.7, 0.9, 1.3], w=3.4, h=0.52, bg="red", fs=0.5),
], cam=(0, 3.0, 13.0), look=(0, 2.5, 0))

chip("c17", S("O Brasil não é um único", -0.1), E("único território educacional", 0.35), [("O BRASIL NÃO É", S("O Brasil não é um único")), ("UM ÚNICO", S("um único território")),
                                                                                        (G("TERRITÓRIO"), S("território educacional"))], side_="left")

# "O Brasil é um país continental... Uma região agroindustrial precisa de formações diferentes das de um polo tecnológico. Um município turístico... outro que expande seus serviços de saúde."
REG = [("AGROINDÚSTRIA", S("Uma região agroindustrial")), ("POLO TECNOLÓGICO", S("um polo tecnológico")), ("TURISMO", S("Um município turístico")),
       ("SERVIÇOS DE SAÚDE", S("expande seus serviços"))]
full("brasil", S("O Brasil é um país continental", -0.1), E("seus serviços de saúde", 0.5), [
    Pl("UM PAÍS CONTINENTAL", S("um país continental"), [0, 6.3, 0], w=7.0, h=0.95, bg="plate", fs=0.66),
    Pl("ECONOMIAS DIFERENTES · REALIDADES DESIGUAIS", S("Com economias regionais"), [0, 5.1, 0.3], w=11.4, h=0.8, bg="white", fs=0.5),
    *sum([[Pl(txt, t, [-4.8 + k * 3.2, 3.6, 0.8], w=3.0, h=0.8, bg=("gold" if k % 2 == 0 else "blue"), fs=0.44),
           it("pawn", p=[-4.8 + k * 3.2, 0, 1.6], s=0.5, mat=("gold" if k % 2 == 0 else "grey"), t=t + 0.1, quiet=True)] for k, (txt, t) in enumerate(REG)], []),
    Pl("FORMAÇÕES DIFERENTES", S("precisa de formações diferentes"), [0, 2.3, 1.3], w=7.0, h=0.85, bg="plate", fs=0.6),
], cam=(0, 3.8, 18.8), look=(0, 3.2, 0))

side("territorio", S("acerta ao incluir", -0.9), E("a esses arranjos locais", 0.35), [
    Pl("EM CADA TERRITÓRIO", S("acerta ao incluir", 0.1), [0, 5.2, 0.2], w=3.8, h=0.58, bg="gold", fs=0.54),
    Pl("NÃO SÓ NA INTENÇÃO", S("não pode ficar só"), [0, 4.45, 0.3], w=3.8, h=0.5, bg="red", fs=0.5, out=S("Precisamos de instrumentos que", -0.05)),
    *stack([("ONDE ESTÃO AS OPORTUNIDADES", S("onde estão as oportunidades")), ("SETORES EM TRANSFORMAÇÃO", S("quais setores estão")),
            ("ONDE FALTAM PROFISSIONAIS", S("onde faltam profissionais")), ("COMO A ESCOLA RESPONDE", S("como as instituições podem"), "gold")],
           y0=3.6, dy=0.74, w=4.3, h=0.52, fs=0.46),
], cam=(0, 2.9, 13.0), look=(0, 2.5, 0))

chip("c18", S("Uma avaliação nacional precisa", -0.1), E("contexto de cada instituição", 0.3), [("COMPARAR, SIM.", S("Uma avaliação nacional precisa")),
                                                                                               (f'IGNORAR O {G("CONTEXTO")}, NÃO', S("não pode ignorar o contexto"))])
chip("c18b", S("O Brasil precisa de uma educação profissional nacional", -0.1), E("territorial em suas respostas", 0.35),
     [("NACIONAL NA QUALIDADE", S("O Brasil precisa de uma educação profissional nacional")), (f'{G("TERRITORIAL")} NAS RESPOSTAS', S("territorial em suas respostas"))], side_="left")

# "Agora, um tema que costuma ficar em segundo plano: o custo. Quanto custará implementar esse sistema? Avaliar cada estudante, acompanhar egressos, produzir relatórios."
side("custo", S("Agora um tema", -0.2), E("Essas perguntas precisam ser feitas", 0.35), [
    it("coins", p=[-1.5, 0.2, 0.8], s=0.8, t=S("Agora um tema", 0.15)),
    Pl("O CUSTO", S("O custo da formação"), [0, 5.1, 0.2], w=2.8, h=0.62, bg="gold"),
    Pl("QUANTO CUSTARÁ?", S("Quanto custará"), [0.2, 4.3, 0.4], w=3.6, h=0.56, bg="plate", fs=0.54),
    *stack([("AVALIAR CADA ESTUDANTE", S("Avaliar cada estudante")), ("ACOMPANHAR EGRESSOS", S("acompanhar egressos")), ("PRODUZIR RELATÓRIOS", S("produzir relatórios"))],
           y0=3.4, dy=0.7, x=0.5, w=3.5, h=0.52, fs=0.48),
], cam=(0, 3.0, 13.0), look=(0, 2.5, 0))

chip("c19", S("Uma avaliação cara", -0.1), E("todo o território nacional", 0.35), [("CARA E COMPLEXA DEMAIS", S("Uma avaliação cara")),
                                                                                  ('<span class="r">NÃO CHEGA AO PAÍS TODO</span>', S("pode não alcançar"))])

# "A portaria prioriza o aproveitamento de informações já existentes, evitando coletas redundantes... Isso é muito positivo, mas precisa virar prática. Por que informar os mesmos dados a vários sistemas?"
DD = S("Porque uma instituição deve", -0.05)
side("dados", S("A portaria prioriza", -0.2), E("Para que isso", 0.35), [
    it("doc", txt="PORTARIA", head="#C9A45A", w=1.5, h=1.9, p=[-1.5, 4.2, -0.4], t=S("A portaria prioriza", 0.15), r=[0, 0.3, 0.04], float=0.04),
    Pl("USAR DADOS QUE JÁ EXISTEM", S("o aproveitamento de"), [0.7, 4.7, 0.2], w=3.3, h=0.54, bg="gold", fs=0.4),
    Pl("SEM COLETA REDUNDANTE", S("evitando coletas"), [0.7, 4.0, 0.3], w=3.3, h=0.54, bg="white", fs=0.44),
    Pl("PRECISA VIRAR PRÁTICA", S("mas precisa virar"), [0, 3.0, 0.6], w=4.0, h=0.56, bg="plate", fs=0.52, out=DD),
    *[it("doc", txt="", head="#9A9BA5", w=0.9, h=1.1, p=[-1.3 + k * 1.3, 1.6, 0.8], t=DD + 0.1 + 0.12 * k, r=[0, 0.2, 0.02], quiet=k > 0) for k in range(3)],
    Pl("OS MESMOS DADOS, VÁRIOS SISTEMAS?", S("os mesmos dados"), [0, 3.0, 0.9], w=4.4, h=0.56, bg="red", fs=0.42),
], cam=(0, 3.0, 13.0), look=(0, 2.7, 0))

chip("c20", S("Por que tomar o tempo", -0.1), E("que não melhoram o ensino", 0.35), [("POR QUE TOMAR O TEMPO", S("Por que tomar o tempo")), ("DO PROFESSOR E DO GESTOR", S("de professores e gestores com")),
                                                                                   ('<span class="r">COM O QUE NÃO MELHORA O ENSINO?</span>', S("que não melhoram"))])

# "Eu sempre defendo: fazer mais com menos desperdício. Nunca fazer menos pela aprendizagem. Eficiência não é precarização. É investir em instrumentos confiáveis, integrar dados com segurança e liberar professores..."
full("efic", S("fazer mais com menos", -0.2), E("o que importa formar estudantes", 0.5), [
    Pl("FAZER MAIS COM MENOS DESPERDÍCIO", S("fazer mais com menos"), [0, 6.2, 0], w=10.6, h=1.0, bg="gold", fs=0.62),
    Pl("NUNCA MENOS PELA APRENDIZAGEM", S("Nunca fazer menos"), [0, 4.95, 0.3], w=10.0, h=0.9, bg="plate", fs=0.6),
    Pl("EFICIÊNCIA ≠ PRECARIZAÇÃO", S("Eficiência não é"), [0, 3.8, 0.6], w=8.0, h=0.85, bg="red", fs=0.6, out=S("É investir em", -0.05)),
    *[Pl(txt, t, [-4.1 + k * 4.1, 3.7, 0.8], w=3.8, h=0.9, bg="white", fs=0.44) for k, (txt, t) in
      enumerate([("INSTRUMENTOS CONFIÁVEIS", S("É investir em", 0.1)), ("DADOS INTEGRADOS", S("integrar dados")), ("PROFESSOR LIVRE PARA ENSINAR", S("liberar professores"))])],
    *row(10, t=S("formar estudantes"), mat="gold"),
    Pl("O QUE IMPORTA: FORMAR ESTUDANTES", S("para o que importa"), [0, 2.2, 1.3], w=10.0, h=0.95, bg="gold", fs=0.6),
], cam=(0, 3.8, 18.8), look=(0, 3.2, 0))

chip("c21", S("E precisamos avaliar a própria", -0.1), E("oferece a sociedade", 0.35), [("AVALIAR A AVALIAÇÃO:", S("avaliar a própria avaliação")), ("QUANTO CUSTA?", S("Quanto custa")),
                                                                                      ("QUE DECISÃO MELHORA?", S("Que decisões ajudam")), (f'QUE {G("BENEFÍCIO")} TRAZ?', S("Que benefícios"))])

# "Outra dimensão na portaria é o acompanhamento dos egressos. Eles continuaram estudando? Trabalham na área em que se formaram?"
side("egressos", S("acompanhamento dos egressos", -0.3), E("em que se formaram", 0.35), [
    *[it("pawn", p=[-1.8 + k * 0.9, 0, 1.0 + (k % 2) * 0.4], s=0.36, mat=("gold" if k == 2 else "grey"), t=S("acompanhamento dos egressos", 0.05 * k), quiet=k > 0) for k in range(5)],
    Pl("OS EGRESSOS", S("acompanhamento dos egressos"), [0, 5.0, 0.2], w=3.2, h=0.6, bg="plate"),
    Pl("CONTINUARAM ESTUDANDO?", S("Eles continuaram estudando"), [0, 4.1, 0.4], w=4.1, h=0.56, bg="white", fs=0.5),
    Pl("TRABALHAM NA ÁREA?", S("trabalham na área"), [0, 3.3, 0.6], w=4.1, h=0.56, bg="white", fs=0.52),
], cam=(0, 3.0, 13.0), look=(0, 2.4, 0))

chip("c22", S("São informações valiosas", -0.1), E("com qualidade educacional", 0.35), [("DADO VALIOSO, MAS", S("São informações valiosas")), ("EMPREGABILIDADE", S("confundir empregabilidade")),
                                                                                      (f'NÃO É {G("QUALIDADE")}', S("com qualidade educacional"))])

# "Imagine dois estudantes. Um conclui um excelente curso técnico em uma região estagnada. O outro se forma em um polo industrial em expansão. Se o segundo consegue emprego rápido... a segunda escola é melhor? Claro que não."
side("dois", S("Imagine dois estudantes", -0.2), E("Claro que não", 0.4), [
    it("text", txt="2", size=1.2, mat="gold", p=[0, 4.6, -0.2], t=S("Imagine dois estudantes", 0.15), spin=0.3, out=S("Um conclui um excelente", -0.05)),
    it("pawn", p=[-1.3, 0, 0.8], s=0.5, mat="gold", t=S("Um conclui um excelente")),
    Pl("CURSO EXCELENTE", S("excelente curso técnico"), [-1.2, 4.6, 0.3], w=2.3, h=0.52, bg="gold", fs=0.42),
    Pl("REGIÃO ESTAGNADA", S("região economicamente"), [-1.2, 3.9, 0.4], w=2.3, h=0.52, bg="grey", fs=0.42),
    it("pawn", p=[1.3, 0, 0.8], s=0.5, mat="grey", t=S("O outro se forma")),
    Pl("POLO EM EXPANSÃO", S("polo industrial"), [1.25, 4.6, 0.3], w=2.3, h=0.52, bg="blue", fs=0.42),
    Pl("EMPREGO RÁPIDO", S("consegue um emprego"), [1.25, 3.9, 0.4], w=2.3, h=0.52, bg="white", fs=0.44),
    Pl("A SEGUNDA ESCOLA É MELHOR?", S("a segunda escola"), [0, 2.9, 1.0], w=4.3, h=0.56, bg="plate", fs=0.46),
    it("badge", rad=0.45, kind="x", p=[0, 2.0, 1.4], t=S("Claro que não")),
], cam=(0, 3.1, 13.0), look=(0, 2.6, 0))

chip("c23", S("Há fatores econômicos", -0.1), E("territoriais envolvidos", 0.3), [("HÁ FATORES", S("Há fatores econômicos")), ("ECONÔMICOS, SOCIAIS", S("fatores econômicos", 0.3)),
                                                                                (f'E {G("TERRITORIAIS")}', S("territoriais envolvidos"))])

side("penal", S("Se a avaliação ignorar", -0.2), E("sobre realidades complexas", 0.35), [
    Pl("SE IGNORAR O CONTEXTO", S("Se a avaliação ignorar", 0.12), [0, 5.0, 0.2], w=4.1, h=0.56, bg="plate", fs=0.5),
    it("box", w=1.6, h=1.5, d=1.2, mat="blue", own=True, p=[-1.2, 0.75, 0.2], t=S("penalizar boas instituições")),
    Pl("PUNE BOAS ESCOLAS", S("penalizar boas instituições"), [0.2, 4.1, 0.4], w=3.8, h=0.56, bg="red", fs=0.52),
    Pl("POR PROBLEMAS FORA DO ALCANCE", S("por problemas que"), [0.2, 3.3, 0.6], w=4.2, h=0.52, bg="white", fs=0.42),
    Pl("SEM CONCLUSÃO SIMPLISTA", S("não produz conclusões"), [0, 0.35, 2.4], w=4.2, h=0.54, bg="gold", fs=0.48, r=[-0.4, 0, 0]),
], cam=(0, 3.0, 13.0), look=(0, 2.5, 0))

chip("c24", S("E o que fazer com o resultado", -0.1), E("mais importante deste episódio", 0.35), [("E DEPOIS DO", S("E o que fazer com o resultado")), (f'{G("RESULTADO")}?', S("resultado da avaliação")),
                                                                                               ("A PERGUNTA MAIS IMPORTANTE", S("Chegamos à pergunta"))])
emph(S("Chegamos à pergunta", -0.1), E("mais importante deste episódio", 0.3), 1.18)

# "Depois que os indicadores forem calculados e os relatórios publicados, o que vai acontecer? A escola vai receber orientações úteis? O professor...? Os gestores...? O estudante...?"
WHO4 = [("ESCOLA: ORIENTAÇÃO ÚTIL?", S("A escola vai receber")), ("PROFESSOR: ONDE ESTÁ A DIFICULDADE?", S("O professor vai entender")),
        ("GESTOR: O QUE PRIORIZAR?", S("Os gestores vão saber")), ("ESTUDANTE: SUPERA AS LACUNAS?", S("O estudante vai conseguir"))]
full("depois", S("Depois que os indicadores", -0.1), E("superar suas lacunas", 0.5), [
    *[it("doc", txt="", head="#0457E7", w=0.9, h=1.2, p=[-6.3 + k * 0.62, 0.9, -0.8], t=S("os relatórios publicados", 0.04 * k), r=[0, 0.2, 0.02], quiet=k > 0) for k in range(4)],
    Pl("INDICADORES CALCULADOS · RELATÓRIOS PUBLICADOS", S("Depois que os indicadores", 0.1), [0, 6.3, 0], w=11.6, h=0.85, bg="plate", fs=0.5),
    Pl("E AGORA?", S("o que vai acontecer"), [0, 5.2, 0.3], w=3.6, h=0.9, bg="gold", fs=0.7),
    *sum([[Pl(txt, t, [-3.2 + (k % 2) * 6.4, 3.9 - (k // 2) * 1.15, 0.6], w=6.1, h=0.85, bg=("gold" if k == 3 else "white"), fs=0.42),
           it("pawn", p=[-3.0 + k * 2.0, 0, 2.2], s=0.42, mat=("gold" if k == 3 else "grey"), t=t + 0.1, quiet=True)] for k, (txt, t) in enumerate(WHO4)], []),
], cam=(0, 3.8, 18.8), look=(0, 3.2, 0))

chip("c25", S("Se nada disso acontecer", -0.1), E("não transforma a educação", 0.35), [("SENÃO, É SÓ MAIS UMA", S("Se nada disso acontecer")),
                                                                                   ('<span class="r">MÁQUINA DE INFORMAÇÃO</span>', S("máquina de produzir")),
                                                                                   (f'E ISSO NÃO {G("TRANSFORMA")}', S("por si só não transforma"))])

# "A transformação acontece quando a avaliação muda as decisões pedagógicas, institucionais e públicas. Por isso defendo o Sinaept orientado à melhoria contínua: que identifique o problema..."
side("melhoria", S("A transformação acontece quando", -0.2), E("instituições públicas e privadas", 0.35), [
    Pl("A AVALIAÇÃO MUDA DECISÕES", S("A transformação acontece quando", 0.12), [0, 5.3, 0.2], w=3.8, h=0.56, bg="plate", fs=0.54),
    Pl("MELHORIA CONTÍNUA", S("melhoria contínua"), [0, 4.6, 0.3], w=3.8, h=0.58, bg="gold", fs=0.54),
    *stack([("IDENTIFICA O PROBLEMA", S("identifica o problema")), ("ENTENDE AS CAUSAS", S("entender suas causas")), ("RESPEITA OS SISTEMAS DE ENSINO", S("respeite os sistemas")),
            ("RECONHECE A INOVAÇÃO", S("reconheça a inovação")), ("ESTIMULA A QUALIDADE", S("estimule a qualidade"))],
           y0=3.75, dy=0.68, x=-0.2, w=4.0, h=0.5, fs=0.44, badge="ok", bx=2.25),
], cam=(0, 2.8, 13.0), look=(0, 2.6, 0))

chip("c26", S("Não basta somente saber", -0.1), TE(1369, 0.35), [("NÃO BASTA SABER", S("Não basta somente saber")), ("ONDE FALHA.", S("onde ela falha")),
                                                               (f'É PRECISO {G("AJUDAR A MELHORAR")}', S("Precisamos é"))])

# "O Brasil tem uma longa trajetória de planos, indicadores e avaliações. ... não adianta aperfeiçoar a forma de medir sem aperfeiçoar as condições que produzem a aprendizagem.
#  Podemos ter painéis sofisticados e gráficos modernos, mas nenhum gráfico substitui o que acontece entre professor, estudante e conhecimento."
H2 = S("Podemos ter painéis", -0.05)
side("historia", S("O Brasil tem uma longa", -0.2), E("o estudante e o conhecimento", 0.4), [
    Pl("UMA LONGA TRAJETÓRIA DE", S("O Brasil tem uma longa", 0.12), [0, 5.25, 0.2], w=4.2, h=0.54, bg="plate", fs=0.5, out=H2),
    *stack([("PLANOS", S("de planos indicadores")), ("INDICADORES", S("indicadores e avaliações educacionais")), ("AVALIAÇÕES", S("avaliações educacionais Muitos"))],
           y0=4.5, dy=0.66, w=3.2, h=0.5, bg="grey", fs=0.54, out=H2),
    Pl("A LIÇÃO:", S("há uma lição"), [0, 2.45, 0.6], w=2.4, h=0.52, bg="gold", fs=0.54, out=H2),
    Pl("MEDIR MELHOR NÃO BASTA", S("Não adianta aperfeiçoar"), [0, 1.7, 0.9], w=4.2, h=0.54, bg="red", fs=0.48, out=H2),
    Pl("SEM MELHORAR AS CONDIÇÕES", S("as condições que produzem"), [0, 0.35, 2.4], w=4.3, h=0.52, bg="white", fs=0.46, r=[-0.4, 0, 0], out=H2),
    *[it("bar", w=0.55, h=2.2, d=0.55, mat="blue", p=[-1.8 + k * 0.9, 0, -0.6], t=H2 + 0.1 + 0.06 * k, quiet=k > 0, grow=[[H2 + 0.1 + 0.06 * k, 0.5, 0.4 + 0.14 * k]]) for k in range(5)],
    Pl("PAINÉIS E GRÁFICOS", H2 + 0.15, [0, 5.1, 0.2], w=3.8, h=0.58, bg="plate", fs=0.54),
    Pl("NENHUM GRÁFICO SUBSTITUI", S("nenhum gráfico substitui"), [0, 4.3, 0.4], w=4.2, h=0.54, bg="red", fs=0.46),
    *[it("pawn", p=[-1.2 + k * 1.2, 0, 1.4], s=0.42, mat=("gold" if k == 1 else "grey"), t=S("entre professor", 0.08 * k), quiet=k > 0) for k in range(2)],
    Pl("PROFESSOR · ESTUDANTE · CONHECIMENTO", S("entre professor"), [0, 3.45, 0.6], w=4.4, h=0.56, bg="gold", fs=0.38),
], cam=(0, 3.0, 13.0), look=(0, 2.5, 0))

chip("c27", S("avaliação precisa ser", -0.25), E("em preparação para a avaliação", 0.35), [("A AVALIAÇÃO SERVE", S("avaliação precisa ser")), (f'À {G("EDUCAÇÃO")}.', S("avaliação precisa ser", 0.9)),
                                                                                        ("NÃO O CONTRÁRIO", S("E não transformar a educação"))])

side("objetivo", S("O objetivo de um curso técnico", -0.2), E("terá cumprido o seu papel", 0.35), [
    Pl("O OBJETIVO DO CURSO TÉCNICO", S("O objetivo de um curso técnico", 0.12), [0, 5.2, 0.2], w=4.3, h=0.56, bg="plate", fs=0.46),
    Pl("NÃO É NOTA NO EXAME", S("não é tirar boa nota"), [-0.2, 4.4, 0.4], w=3.8, h=0.54, bg="grey", fs=0.5),
    it("badge", rad=0.3, kind="x", p=[2.0, 4.6, 0.8], t=S("exame nacional")),
    it("pawn", p=[-1.4, 0, 1.0], s=0.55, mat="gold", t=S("É formar profissionais")),
    Pl("PROFISSIONAL COMPETENTE", S("É formar profissionais"), [0.4, 3.4, 0.6], w=3.8, h=0.56, bg="gold", fs=0.48),
    Pl("QUE CONTINUA APRENDENDO", S("capazes de continuar"), [0.4, 2.6, 0.8], w=3.8, h=0.54, bg="white", fs=0.48),
], cam=(0, 3.0, 13.0), look=(0, 2.6, 0))

chip("c28", S("E eu volto à pergunta", -0.1), E("volto à pergunta inicial", 0.3), [("DE VOLTA À", S("E eu volto à pergunta")), (f'PERGUNTA {G("INICIAL")}', S("pergunta inicial"))])

side("passo", S("O Brasil está construindo", -0.2), E("mais importante começa agora", 0.4), [
    it("doc", txt="PORTARIA", head="#C9A45A", w=1.6, h=2.0, p=[-1.4, 2.3, 0], t=S("O Brasil está construindo", 0.15), r=[0, 0.28, 0.03], float=0.05),
    Pl("UM PASSO NECESSÁRIO", S("É um passo necessário"), [0, 5.1, 0.2], w=4.0, h=0.58, bg="green", fs=0.52),
    Pl("Nº 545", S("com a portaria 545"), [1.0, 3.4, 0.6], w=1.8, h=0.52, bg="gold", fs=0.56),
    Pl("A HISTÓRIA NÃO TERMINA AÍ", S("a história não termina"), [0.3, 4.3, 0.4], w=4.0, h=0.54, bg="white", fs=0.46),
    Pl("O MAIS IMPORTANTE COMEÇA AGORA", S("A parte mais importante"), [0, 0.35, 2.4], w=4.4, h=0.54, bg="gold", fs=0.42, r=[-0.4, 0, 0]),
], cam=(0, 3.0, 13.0), look=(0, 2.5, 0))

chip("c29", S("Definir metodologias", -0.1), E("informação em resultados", 0.35), [("METODOLOGIAS", S("Definir metodologias")), ("INSTRUMENTOS", S("desenvolver instrumentos")),
                                                                                ("CICLOS", S("organizar ciclos")), (f'INFORMAÇÃO → {G("RESULTADO")}', S("transformar informação em"))])
emph(S("a aprendizagem precisa estar", -0.1), E("no centro das decisões", 0.3), 1.2)

# "O futuro da educação profissional não será definido pelo número de cursos avaliados, nem pela quantidade de indicadores ou relatórios. Será definido pela capacidade de formar pessoas mais preparadas..."
F1 = S("será definido pela capacidade", -0.05)
full("futuro", S("o futuro da educação profissional não será", -0.1), E("recursos públicos e privados", 0.5), [
    Pl("O FUTURO DA EDUCAÇÃO PROFISSIONAL", S("o futuro da educação profissional não será", 0.1), [0, 6.3, 0], w=10.6, h=1.0, bg="plate", fs=0.6),
    *[Pl(txt, t, [-4.1 + k * 4.1, 4.7, 0.4], w=3.8, h=0.8, bg="grey", fs=0.5, out=F1) for k, (txt, t) in
      enumerate([("CURSOS AVALIADOS", S("número de cursos avaliados")), ("INDICADORES", S("quantidade de indicadores")), ("RELATÓRIOS", S("ou relatórios"))])],
    Pl("NÃO É QUANTIDADE", S("não será definido pelo"), [0, 3.4, 0.8], w=5.8, h=0.8, bg="red", fs=0.6, out=F1),
    *[Pl(txt, t, [-4.1 + k * 4.1, 4.5, 0.5], w=3.8, h=0.95, bg="gold", fs=0.44) for k, (txt, t) in
      enumerate([("PESSOAS MAIS PREPARADAS", S("formar pessoas mais preparadas")), ("MAIS OPORTUNIDADES", S("ampliar oportunidades e")), ("RECURSOS BEM USADOS", S("usar melhor os recursos"))])],
    *row(10, t=S("formar pessoas mais preparadas", 0.1), mat="gold"),
], cam=(0, 3.8, 19.0), look=(0, 3.3, 0))

chip("c30", S("Daqui a dez anos", -0.1), E("mais importante para o Brasil", 0.3), [("DAQUI A", S("Daqui a dez anos")), (f'{G("10 ANOS")}:', S("dez anos")),
                                                                                 ("O QUE VAI IMPORTAR?", S("o que será mais importante"))])

side("dez", S("Demonstrar que avaliamos", -0.2), E("uma formação profissional melhor", 0.4), [
    it("bar", w=0.9, h=3.0, d=0.8, mat="blue", p=[-1.3, 0, 0.2], t=S("Demonstrar que avaliamos", 0.15), quiet=True, grow=[[S("Demonstrar que avaliamos", 0.15), 0.6, 0.8]]),
    Pl("MILHÕES AVALIADOS", S("avaliamos milhões"), [-0.2, 5.0, 0.2], w=3.6, h=0.56, bg="grey", fs=0.52),
    Pl("OU", S("ou demonstrar que"), [0, 4.2, 0.4], w=1.3, h=0.54, bg="plate"),
    *[it("pawn", p=[-0.6 + (k % 3) * 0.95, 0, 0.9 + (k // 3) * 0.8], s=0.34, mat="gold", t=S("milhões de brasileiros", 0.04 * k), quiet=k > 0) for k in range(6)],
    Pl("MILHÕES MAIS BEM FORMADOS", S("milhões de brasileiros"), [0.2, 3.4, 0.6], w=4.2, h=0.58, bg="gold", fs=0.46),
], cam=(0, 3.0, 13.0), look=(0, 2.5, 0))

chip("c31", S("Eu não tenho dúvida", -0.1), E("usar a avaliação para transformar", 0.35), [("AVALIAR, SIM.", S("Precisamos avaliar mas")), ("MAS, SOBRETUDO,", S("mas sobretudo")),
                                                                                         (G("TRANSFORMAR"), S("usar a avaliação para transformar", 0.5))])

# "porque a educação profissional não existe para produzir indicadores, existe para formar pessoas, desenvolver competências e transformar vidas."
full("final", S("porque a educação profissional não existe", -0.1), E("e transformar vidas", 0.6), [
    Pl("A EDUCAÇÃO PROFISSIONAL", S("porque a educação profissional não existe", 0.1), [0, 6.3, 0], w=8.4, h=1.0, bg="plate", fs=0.64),
    Pl("NÃO EXISTE PARA PRODUZIR INDICADORES", S("não existe para produzir"), [0, 5.0, 0.3], w=11.2, h=0.9, bg="red", fs=0.56),
    *[Pl(txt, t, [-4.1 + k * 4.1, 3.6, 0.6], w=3.8, h=1.0, bg="white", fs=0.44) for k, (txt, t) in
      enumerate([("FORMAR PESSOAS", S("existe para formar pessoas")), ("DESENVOLVER COMPETÊNCIAS", S("desenvolver competências e"))])],
    Pl("TRANSFORMAR VIDAS", S("e transformar vidas"), [4.1, 3.6, 0.7], w=3.8, h=1.0, bg="gold", fs=0.5),
    *row(10, t=S("e transformar vidas", 0.1), mat="gold"),
], cam=(0, 3.8, 19.0), look=(0, 3.3, 0))
sfx(S("e transformar vidas"), "chime", -17, 0, "final idea")

# CTA: "responda nos comentários: nossas avaliações estão ajudando a melhorar a aprendizagem ou estamos apenas aprendendo a produzir mais indicadores?"
CTA0, CTA1 = S("e responda nos comentários", -0.2), E("a produzir mais indicadores", 0.4)
side("cta", CTA0, CTA1, [], auto_sfx=False)

chip("c33", S("Essa é uma pergunta que", -0.1), E("que não quer calar", 0.35), [("A PERGUNTA QUE", S("Essa é uma pergunta que")), (f'{G("NÃO QUER CALAR")}', S("não quer calar"))])
