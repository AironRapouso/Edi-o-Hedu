# Cue sheet for EP7 "A educação profissional do futuro" — exec'd by build.py (helpers live there).
# Cast: grey pawns = people / institutions, gold pawn = the student (o estudante no centro), robot = technology / AI.
# Anchors use A()/Z(): first word starting with a prefix after a source index (robust to small index slips).

UPDATE_NOTE = ("Atualização: o Parecer CNE/CP nº 21/2026 foi homologado pelo MEC em 10/11/2026 e deu origem à "
               "Resolução CNE/CP nº 2, de 11/11/2026 · Fonte: gov.br/mec/cne")


def A(prefix, after, dt=0.0):
    return T(K(prefix, max(0, after - 8)), dt)


def Z(prefix, after, dt=0.0):
    return TE(K(prefix, max(0, after - 8)), dt)


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


# =================================================================== HOOK (his own opening, before the vinheta)
# "O Brasil precisa formar mais profissionais, ampliar oportunidades, preparar seus jovens para o primeiro emprego..."
full("q0", 0.0, Z("renda", 30, 0.3), [
    *[it("pawn", p=[-6.4 + k * 1.6, 0, -0.6 + (k % 2) * 0.5], s=0.55, mat=("gold" if k == 4 else "grey"), t=0.02 + k * 0.05, quiet=True) for k in range(9)],
    Pl("O BRASIL PRECISA", 0.0, [0, 6.3, 0], w=5.2, h=0.9, bg="plate", fs=0.7),
    Pl("FORMAR MAIS PROFISSIONAIS", A("formar", 5), [0, 5.0, 0.4], w=8.6, h=1.0, bg="gold", fs=0.7),
    Pl("AMPLIAR OPORTUNIDADES", A("ampliar", 10), [-3.3, 3.6, 0.8], w=5.6, h=0.8, bg="white", fs=0.64),
    Pl("PRIMEIRO EMPREGO", A("primeiro", 17), [3.3, 3.6, 0.8], w=5.0, h=0.8, bg="white", fs=0.64),
    Pl("NOVOS CAMINHOS", A("novos", 20), [0, 2.5, 1.2], w=5.0, h=0.8, bg="white", fs=0.64),
], cam=(0.8, 3.8, 18.6), look=(0, 3.1, 0), moves=[[0, 8.0, (0, 3.6, 16.8), (0, 3.1, 0), "sine.out"]])
sfx(0.0, "slam", -10, 0, "hook impact frame 0")

chip("c1", A("Mas", 36, -0.1), Z("pergunta", 44, 0.3), [("COMEÇO COM", A("começar", 38)), (f'UMA {G("PERGUNTA")}', A("pergunta", 44))])

# "O Brasil precisa apenas de mais escolas técnicas? Ou precisa, antes de tudo, repensar a maneira como organizar a educação profissional?"
side("q1", A("O", 49, -0.2), Z("profissional", 66, 0.35), [
    *[it("box", w=1.1, h=1.3 + 0.25 * (k % 3), d=1.1, mat="blue", own=True, p=[-1.7 + (k % 3) * 1.7, 0.7, -1.4 + (k // 3) * 1.5], t=A("O", 49, 0.15 + 0.14 * k),
         quiet=k > 2, out=A("Ou", 57, -0.05)) for k in range(6)],
    Pl("MAIS ESCOLAS TÉCNICAS?", A("mais", 52), [0, 4.7, 0.2], w=4.2, h=0.66, bg="plate", out=A("Ou", 57, -0.05)),
    Pl("OU...", A("Ou", 57), [0, 4.9, 0.2], w=1.6, h=0.6, bg="gold"),
    it("text", txt="?", size=1.7, mat="gold", p=[-0.5, 1.6, 0.4], t=A("repensar", 60), spin=0.4, louder=2),
    Pl("REPENSAR A ORGANIZAÇÃO", A("repensar", 60, 0.15), [0, 3.95, 0.4], w=4.3, h=0.62),
    Pl("DA EDUCAÇÃO PROFISSIONAL", A("educação", 66), [0, 0.35, 2.2], w=4.3, h=0.56, bg="white", r=[-0.4, 0, 0]),
], cam=(0.4, 3.6, 13.2), look=(0, 2.3, 0))
emph(A("Vamos", 70, -0.1), Z("nisso", 71, 0.3), 1.2)
chip("c2", A("Vamos", 70, -0.1), Z("nisso", 71, 0.35), [(f'VAMOS {G("PENSAR")} NISSO?', A("Vamos", 70))], side_="left")

# =================================================================== BODY
# "E o tema é as novas Diretrizes Curriculares Nacionais para a educação profissional e tecnológica"
side("tema", A("E", 122, -0.2), Z("tecnológica", 133, 0.35), [
    it("doc", txt="DIRETRIZES", head="#0457E7", w=2.4, h=3.0, p=[0, 2.5, -0.2], t=A("E", 122, 0.15), r=[0, 0.22, 0.03], float=0.05),
    Pl("O TEMA DE HOJE", A("tema", 122), [0, 5.0, 0.2], w=3.0, h=0.6, bg="gold"),
    Pl("CURRICULARES NACIONAIS", A("curriculares", 126), [0, 0.95, 1.6], w=4.2, h=0.56, bg="plate"),
    Pl("EDUCAÇÃO PROFISSIONAL E TECNOLÓGICA", A("educação", 130), [0, 0.3, 2.3], w=4.4, h=0.52, bg="white", fs=0.52, r=[-0.35, 0, 0]),
], cam=(0, 3.0, 13.0), look=(0, 2.4, 0))

# "não interessa apenas a professores, especialistas, doutores e gestores... interessa às famílias, estudantes, trabalhadores, empresários e milhões de brasileiros"
WHO_SW = A("interessa", 164, -0.05)
side("who", A("esse", 149, -0.2), Z("profissional", 190, 0.35), [
    Pl("NÃO É SÓ PARA:", A("esse", 149, 0.15), [0, 4.9, 0.2], w=3.2, h=0.58, bg="plate", out=WHO_SW),
    *stack([("PROFESSORES", A("professores", 154)), ("ESPECIALISTAS", A("especialistas", 157)), ("DOUTORES E GESTORES", A("doutores", 159)),
            ("ACADEMIA", A("academia", 162))], y0=4.0, dy=0.74, w=3.6, bg="grey", out=WHO_SW),
    Pl("INTERESSA A:", WHO_SW + 0.1, [0, 4.9, 0.2], w=3.0, h=0.58, bg="gold"),
    *sum([[it("pawn", p=[-1.9, 3.72 - k * 0.86, 0.5], s=0.2, mat=("gold" if k == 4 else "grey"), t=t, quiet=True),
           Pl(txt, t + 0.05, [0.35, 3.95 - k * 0.86, 0.6], w=3.5, h=0.56, bg=("gold" if k == 4 else "white"), fs=0.58)]
          for k, (txt, t) in enumerate([("FAMÍLIAS", A("famílias", 168)), ("ESTUDANTES", A("estudantes", 170)), ("TRABALHADORES", A("trabalhadores", 173)),
                                        ("EMPRESÁRIOS", A("empresários", 177)), ("MILHÕES DE BRASILEIROS", A("milhões", 180))])], []),
], cam=(0, 3.0, 13.0), look=(0, 2.5, 0))

chip("c3", A("estamos", 202, -0.1), Z("futuro", 212, 0.4), [("EMPREGO", A("emprego", 206)), ("RENDA", A("renda", 208)), ("PRODUTIVIDADE", A("produtividade", 210)),
                                                           (G("FUTURO"), A("futuro", 212))])
emph(A("Primeiro", 214, -0.1), Z("lince", 220, 0.3), 1.18)

# "Em outubro de 2026, o Conselho Nacional de Educação aprovou um novo parecer... É o parecer número 21 de 2026. ...projeto de resolução"
full("parecer", A("Em", 223, -0.1), Z("resolução", 258, 0.6), [
    it("calendar", txt="OUT 2026", p=[-5.6, 3.6, 0], s=1.0, t=A("Em", 223, 0.2)),
    Pl("CONSELHO NACIONAL DE EDUCAÇÃO", A("Conselho", 227), [1.6, 5.9, 0], w=9.4, h=1.0, bg="plate", fs=0.66),
    it("doc", txt="PARECER", head="#C9A45A", w=2.9, h=3.5, p=[0.2, 2.6, 0.4], t=A("parecer", 234), r=[0, 0.18, 0.03], float=0.05),
    Pl("DIRETRIZES DA EDUCAÇÃO PROFISSIONAL", A("diretrizes", 237), [1.6, 0.4, 2.2], w=9.4, h=0.8, bg="white", fs=0.6, r=[-0.3, 0, 0]),
    Pl("Nº 21/2026", A("21", 249), [5.4, 3.9, 0.8], w=3.6, h=1.1, bg="gold", fs=0.74),
    Pl("PROJETO DE RESOLUÇÃO", A("projeto", 256), [5.4, 2.4, 0.8], w=4.6, h=0.8, bg="white", fs=0.62),
], cam=(0.6, 3.6, 18.2), look=(0.6, 3.0, 0))

# "...temas fundamentais: inteligência artificial, formação ao longo da vida, certificações intermediárias, reconhecimento de competências, EAD, estágio, professores, mundo do trabalho"
side("temas", A("trata", 263, -0.2), Z("trabalho", 311, 0.35), [
    Pl("O QUE O TEXTO TRAZ", A("trata", 263, 0.1), [0, 5.25, 0.2], w=3.8, h=0.58, bg="plate"),
    *stack([("INTELIGÊNCIA ARTIFICIAL", A("inteligência", 271), "gold"), ("FORMAÇÃO AO LONGO DA VIDA", A("formação", 274)),
            ("CERTIFICAÇÕES INTERMEDIÁRIAS", A("certificações", 283)), ("RECONHECIMENTO DE COMPETÊNCIAS", A("reconhecimento", 285)),
            ("EAD E ENSINO HÍBRIDO", A("educação", 288)), ("ESTÁGIO", A("estágio", 297)), ("FORMAÇÃO DE PROFESSORES", A("formação", 298)),
            ("ESCOLA + MUNDO DO TRABALHO", A("integração", 302))], y0=4.5, dy=0.62, w=4.3, h=0.5, fs=0.52),
], cam=(0, 2.6, 13.0), look=(0, 2.35, 0))

chip("c4", A("Mas", 336, -0.1), Z("regulamentação", 350, 0.35), [("ALGO ME PREOCUPA:", A("algo", 338)), ("MUDAMOS A EDUCAÇÃO", A("Estamos", 342)),
                                                               (f'OU SÓ A {G("REGULAMENTAÇÃO")}?', A("ou", 346))])

# "uma escola pode usar IA e continuar ensinando do mesmo jeito; ter equipamentos excelentes e resultados fracos; oferecer milhares de vagas e formar poucos"
S1, S2 = A("Pode", 368, -0.05), A("Pode", 380, -0.05)
side("same", A("uma", 354, -0.2), Z("exige", 396, 0.35), [
    it("robot", p=[-1.2, 0, 0.4], s=0.6, t=A("uma", 354, 0.15), r=[0, 0.4, 0], eyesOn=A("inteligência", 358), out=S1),
    Pl("USA IA", A("usar", 357), [-1.2, 3.3, 0.6], w=1.8, h=0.56, bg="blue", out=S1),
    Pl("MESMO JEITO DE SEMPRE", A("mesmo", 364), [0.2, 4.6, 0.2], w=4.0, h=0.6, bg="red", out=S1),
    it("box", w=1.5, h=1.2, d=1.0, mat="blue", own=True, p=[-1.1, 0.6, 0.4], t=S1 + 0.1, out=S2),
    Pl("EQUIPAMENTO EXCELENTE", A("equipamentos", 370), [0, 4.6, 0.2], w=4.0, h=0.6, bg="plate", out=S2),
    it("bar", w=0.9, h=3.0, d=0.8, mat="red", p=[1.3, 0, 0.4], t=A("resultados", 376), quiet=True, grow=[[A("resultados", 376), 0.6, 0.18]], out=S2),
    Pl("RESULTADO FRACO", A("fracos", 377), [0.3, 2.6, 1.4], w=3.2, h=0.56, bg="red", out=S2),
    *[it("pawn", p=[-2.0 + (k % 5) * 1.0, 0, -0.6 + (k // 5) * 1.0], s=0.32, mat="grey", own=True, t=A("milhares", 382, 0.03 * k), quiet=k > 0,
         **({"colors": [[A("poucos", 387), 0xf4b04a]]} if k in (2, 11) else {})) for k in range(15)],
    Pl("MILHARES DE VAGAS", A("milhares", 382), [0, 4.6, 0.2], w=3.6, h=0.6, bg="plate"),
    Pl("POUCOS COM AS COMPETÊNCIAS", A("poucos", 387), [0, 3.8, 0.4], w=4.3, h=0.56, bg="gold", fs=0.54),
], cam=(0, 3.4, 13.0), look=(0, 2.2, 0))

chip("c5", A("modernizar", 400, -0.1), Z("suficiente", 408, 0.4), [("MODERNIZAR A NORMA", A("modernizar", 400)), ("É IMPORTANTE,", A("importante", 404)),
                                                                   ('<span class="r">MAS NÃO É SUFICIENTE</span>', A("mas", 406))])

# "nossa equipe se dedicou a estudar essa proposta: fundamentos jurídicos, consequências pedagógicas, formação docente, EAD/certificação, impactos econômicos"
side("study1", A("Nas", 410, -0.2), Z("regulamentação", 466, 0.3), [
    it("doc", txt="PROPOSTA", head="#0457E7", w=1.5, h=1.9, p=[-1.5, 4.25, -0.4], t=A("Nas", 410, 0.15), r=[0, 0.3, 0.04], float=0.04),
    Pl("ESTUDAMOS A FUNDO", A("estudar", 418), [0.8, 4.4, 0.2], w=2.9, h=0.56, bg="gold", fs=0.56),
    *stack([("FUNDAMENTOS JURÍDICOS", A("fundamentos", 432)), ("CONSEQUÊNCIAS PEDAGÓGICAS", A("consequências", 436)),
            ("FORMAÇÃO DOCENTE", A("formação", 443)), ("EAD, PRESENCIAL E CERTIFICAÇÃO", A("regras", 447)),
            ("IMPACTOS ECONÔMICOS", A("impactos", 463))], y0=3.1, dy=0.66, w=4.3, h=0.52, fs=0.52, badge="ok", bx=2.3),
], cam=(0, 2.8, 13.0), look=(0, 2.4, 0))

# "Desse trabalho nasceu uma nota técnica, um ensaio crítico, um memorial técnico institucional, propostas de aperfeiçoamento, um estudo de impacto e um dossiê"
DOCS = [("NOTA TÉCNICA", A("nota", 471)), ("ENSAIO CRÍTICO", A("ensaio", 475)), ("MEMORIAL TÉCNICO", A("memorial", 478)),
        ("PROPOSTAS DE AJUSTE", A("propostas", 482)), ("ESTUDO DE IMPACTO", A("estudo", 491)), ("DOSSIÊ AO CNE E AO MEC", A("dossiê", 500))]
side("study2", A("Desse", 468, -0.2), Z("Educação", 514, 0.35), [
    Pl("O QUE PRODUZIMOS", A("Desse", 468, 0.1), [0, 5.2, 0.2], w=3.6, h=0.58, bg="plate"),
    *sum([[it("doc", txt="", w=0.62, h=0.8, p=[-1.85, 4.35 - k * 0.74, 0.5], t=t, r=[0, 0.25, 0.03], head=("#C9A45A" if k == 5 else "#0457E7"), quiet=k > 0),
           Pl(txt, t + 0.06, [0.4, 4.35 - k * 0.74, 0.6], w=3.5, h=0.52, bg=("gold" if k == 5 else "white"), fs=0.54)] for k, (txt, t) in enumerate(DOCS)], []),
], cam=(0, 2.8, 13.0), look=(0, 2.5, 0))

chip("c6", A("Quero", 515, -0.1), Z("técnica", 546, 0.35), [("NOSSO PROPÓSITO", A("Nosso", 521)), ('<span class="sk">NÃO É DESMERECER</span>', A("não", 523)),
                                                           (f'É {G("CONTRIBUIR")}', A("oferecer", 539))], strike=(1, A("oferecer", 539, -0.3)))
chip("c7", A("Porque", 548, -0.1), Z("profundas", 572, 0.35), [("UMA NORMA PRECISA FUNCIONAR", A("norma", 550)), ("NÃO SÓ NO PAPEL:", A("não", 554)),
                                                              (f'NA {G("REALIDADE")} DO PAÍS', A("realidade", 561))], side_="left")

# "Imagine dois municípios: o primeiro é grande (escolas, laboratórios, professores, empresas); o segundo é pequeno, longe... mas também tem jovens, trabalhadores, empresas"
M2 = A("O", 604, -0.05)
side("two", A("Imagine", 582, -0.2), Z("menor", 664, 0.4), [
    it("text", txt="2", size=1.6, mat="gold", p=[-0.45, 2.2, 0.2], t=A("Imagine", 582, 0.15), spin=0.3, out=A("primeiro", 586, -0.05)),
    Pl("MUNICÍPIO GRANDE", A("primeiro", 586), [0, 5.2, 0.2], w=3.6, h=0.58, bg="plate", out=M2),
    *[it("box", w=0.8, h=1.0 + 0.5 * (k % 3), d=0.8, mat="blue", own=True, p=[-1.7 + k * 0.86, 0.6 + 0.25 * (k % 3), -0.8], t=A("primeiro", 586, 0.1 + 0.08 * k), quiet=k > 0, out=M2)
      for k in range(5)],
    *stack([("ESCOLAS ESTRUTURADAS", A("escolas", 590)), ("LABORATÓRIOS", A("laboratórios", 592)), ("PROFESSORES ESPECIALIZADOS", A("professores", 593)),
            ("EMPRESAS PARA A PRÁTICA", A("empresas", 596))], y0=4.3, dy=0.62, w=4.2, h=0.5, fs=0.52, out=M2, z=1.4),
    Pl("MUNICÍPIO PEQUENO", A("segundo", 605), [0, 5.2, 0.2], w=3.6, h=0.58, bg="plate"),
    it("box", w=0.9, h=0.9, d=0.9, mat="grey", own=True, p=[0, 0.45, -1.0], t=A("segundo", 605, 0.15)),
    Pl("LONGE DOS GRANDES CENTROS", A("longe", 610), [0, 4.4, 0.4], w=4.2, h=0.5, bg="white", fs=0.52),
    it("pawn", p=[-1.6, 0, 0.9], s=0.42, mat="gold", t=A("jovens", 631)), Pl("JOVENS", A("jovens", 631, 0.05), [-1.6, 0.3, 1.9], w=1.5, h=0.44, r=[-0.4, 0, 0], quiet=True),
    it("pawn", p=[0, 0, 0.9], s=0.42, mat="grey", t=A("trabalhadores", 636)), Pl("TRABALHADORES", A("trabalhadores", 636, 0.05), [0, 0.3, 1.9], w=1.7, h=0.44, r=[-0.4, 0, 0], fs=0.5, quiet=True),
    it("pawn", p=[1.6, 0, 0.9], s=0.42, mat="grey", t=A("empresas", 644)), Pl("EMPRESAS", A("empresas", 644, 0.05), [1.6, 0.3, 1.9], w=1.5, h=0.44, r=[-0.4, 0, 0], quiet=True),
    Pl("MENOS OPORTUNIDADES?", A("menos", 658), [0, 3.4, 1.0], w=4.0, h=0.62, bg="red"),
], cam=(0, 3.4, 13.2), look=(0, 2.3, 0))

chip("c8", A("É", 666, -0.1), Z("profissional", 675, 0.35), [("É AQUI QUE PRECISAMOS", A("aqui", 668)), (f'DISCUTIR A {G("ORGANIZAÇÃO")}', A("discutir", 671))])

# "tecnologias capazes de levar conteúdo de qualidade a regiões isoladas: simuladores, ambientes virtuais, laboratórios remotos, aulas ao vivo, recursos que apoiam o professor"
side("tech", A("existem", 678, -0.2), Z("professor", 711, 0.35), [
    it("robot", p=[-1.6, 0, 1.0], s=0.5, t=A("existem", 678, 0.15), r=[0, 0.5, 0], eyesOn=A("tecnologias", 679)),
    Pl("A TECNOLOGIA CHEGA LONGE", A("tecnologias", 679), [0, 5.2, 0.2], w=4.2, h=0.58, bg="blue", fs=0.56),
    *stack([("SIMULADORES", A("simuladores", 695)), ("AMBIENTES VIRTUAIS", A("ambientes", 696)), ("LABORATÓRIOS REMOTOS", A("laboratórios", 698)),
            ("AULAS AO VIVO", A("aulas", 700)), ("APOIO AO PROFESSOR", A("recursos", 706), "gold")], y0=4.4, dy=0.64, x=0.5, w=3.4, h=0.5, fs=0.54),
], cam=(0, 3.0, 13.0), look=(0, 2.4, 0))

# "Mas isso não significa que tudo possa acontecer virtualmente. Há profissões que exigem prática presencial, laboratório, supervisão direta, ambientes reais"
side("pres", A("Mas", 713, -0.2), Z("trabalho", 749, 0.3), [
    Pl("TUDO VIRTUAL?", A("Mas", 713, 0.15), [-0.3, 5.0, 0.2], w=3.0, h=0.6, bg="plate"),
    it("badge", rad=0.42, kind="x", p=[1.75, 5.0, 0.5], t=A("Não", 722)),
    *stack([("PRÁTICA PRESENCIAL", A("prática", 727)), ("PROCEDIMENTOS DE LABORATÓRIO", A("procedimentos", 730)),
            ("SUPERVISÃO DIRETA", A("supervisão", 742)), ("AMBIENTE REAL DE TRABALHO", A("vivência", 745))], y0=3.9, dy=0.74, w=4.3, h=0.54, fs=0.52),
    it("pawn", p=[0, 0, 1.4], s=0.42, mat="gold", t=A("prática", 727, 0.1)),
], cam=(0, 3.0, 13.0), look=(0, 2.4, 0))

# "a questão não é escolher entre o presencial e o digital. É saber combinar cada um deles no lugar certo."
full("combine", A("Então", 751, -0.1), Z("relevante", 777, 0.4), [
    Pl("PRESENCIAL", A("presencial", 758), [-4.6, 3.6, 0], w=5.0, h=1.3, bg="plate", fs=0.72),
    it("pawn", p=[-4.6, 0, 0.6], s=0.7, mat="grey", t=A("presencial", 758, 0.1), quiet=True),
    Pl("DIGITAL", A("digital", 761), [4.6, 3.6, 0], w=4.2, h=1.3, bg="blue", fs=0.72),
    it("robot", p=[4.6, 0, 0.6], s=0.62, t=A("digital", 761, 0.1), quiet=True, eyesOn=A("digital", 761, 0.3)),
    Pl("ESCOLHER UM?", A("Então", 751, 0.25), [0, 6.2, 0], w=4.4, h=0.8, bg="white", fs=0.64, out=A("combinar", 767, -0.05)),
    Sym("+", A("combinar", 767), [0, 3.6, 0.6], size=1.2),
    Pl("COMBINAR", A("combinar", 767, 0.05), [0, 6.2, 0], w=4.0, h=0.9, bg="gold", fs=0.7),
    Pl("CADA UM NO LUGAR CERTO", A("lugar", 772), [0, 0.5, 2.4], w=8.6, h=0.9, bg="white", fs=0.66, r=[-0.3, 0, 0]),
], cam=(0, 3.6, 18.4), look=(0, 3.0, 0))

# "a proposta de proibir o compartilhamento de polos de EAD entre instituições. Eu compreendo as preocupações com fiscalização, identidade institucional e qualidade"
side("polos", A("Um", 779, -0.2), Z("exclusiva", 829, 0.35), [
    it("box", w=1.9, h=1.5, d=1.3, mat="blue", own=True, p=[0, 0.75, -0.6], t=A("Um", 779, 0.15)),
    Pl("POLO EAD", A("polos", 794), [0, 1.9, 0.2], w=1.9, h=0.5, bg="plate"),
    it("pawn", p=[-1.7, 0, 0.9], s=0.45, mat="gold", t=A("compartilhamento", 792)),
    it("pawn", p=[1.7, 0, 0.9], s=0.45, mat="sky", own=True, t=A("compartilhamento", 792, 0.12), quiet=True),
    it("nosign", rad=0.9, p=[0, 3.5, 0.8], t=A("proibir", 790), s=0.8, colors=[[A("proibir", 790), 0xe5484d]]),
    Pl("PROIBIR O COMPARTILHAMENTO", A("proibir", 790, 0.2), [0, 5.0, 0.2], w=4.4, h=0.56, bg="red", fs=0.52, out=A("Eu", 805, -0.05)),
    Pl("PREOCUPAÇÕES LEGÍTIMAS", A("preocupações", 808), [0, 5.0, 0.2], w=4.2, h=0.56, bg="white", fs=0.54),
    *[Pl(t_, tt, [-1.5 + k * 1.5, 0.3, 2.3], w=1.42, h=0.44, bg="white", fs=0.46, r=[-0.4, 0, 0], quiet=k > 0)
      for k, (t_, tt) in enumerate([("FISCALIZAÇÃO", A("fiscalização", 810)), ("IDENTIDADE", A("identidade", 811)), ("QUALIDADE", A("qualidade", 814))])],
    it("text", txt="?", size=1.3, mat="gold", p=[1.6, 3.0, 1.2], t=A("Toda", 824), spin=0.5, louder=2),
], cam=(0, 3.2, 13.2), look=(0, 2.4, 0))

# "Dois projetos autorizados não poderiam usar espaços físicos comuns, com responsabilidades separadas? ...construir e manter laboratórios custa muito caro"
side("share", A("Dois", 830, -0.2), Z("oportunidades", 888, 0.35), [
    it("box", w=2.4, h=1.5, d=1.4, mat="blue", own=True, p=[0, 0.75, -0.6], t=A("Dois", 830, 0.15)),
    Pl("ESPAÇO COMUM", A("espaços", 846), [0, 1.9, 0.3], w=2.5, h=0.5, bg="plate"),
    it("pawn", p=[-1.6, 0, 1.0], s=0.45, mat="gold", t=A("projetos", 831)), Pl("PROJETO A", A("projetos", 831, 0.05), [-1.6, 0.3, 2.0], w=1.5, h=0.44, r=[-0.4, 0, 0], quiet=True),
    it("pawn", p=[1.6, 0, 1.0], s=0.45, mat="sky", own=True, t=A("projetos", 831, 0.15), quiet=True), Pl("PROJETO B", A("projetos", 831, 0.2), [1.6, 0.3, 2.0], w=1.5, h=0.44, r=[-0.4, 0, 0], quiet=True),
    Pl("AUTORIZADOS E FISCALIZADOS", A("autorizados", 834), [0, 5.1, 0.2], w=4.3, h=0.54, bg="white", fs=0.52),
    Pl("RESPONSABILIDADES SEPARADAS", A("responsabilidades", 852), [0, 4.3, 0.4], w=4.3, h=0.54, bg="green", fs=0.5),
    it("coins", p=[1.7, 2.3, 0.6], s=0.7, t=A("custa", 875)),
    Pl("CUSTA MUITO CARO", A("custa", 875, 0.1), [-0.4, 3.2, 0.8], w=3.2, h=0.58, bg="red"),
], cam=(0, 3.2, 13.2), look=(0, 2.4, 0))
emph(A("Agora", 889, -0.05), Z("atenção", 890, 0.3), 1.2)

# "compartilhar infraestrutura não pode significar compartilhar credenciamento, transferir responsabilidades acadêmicas, dispensar segurança e aprendizagem. Mas ... cooperação"
side("limits", A("compartilhar", 891, -0.2), Z("sustentabilidade", 927, 0.35), [
    Pl("COMPARTILHAR ESPAÇO NÃO É:", A("compartilhar", 891, 0.1), [0, 5.1, 0.2], w=4.4, h=0.56, bg="plate", fs=0.52),
    *stack([("COMPARTILHAR CREDENCIAMENTO", A("credenciamento", 897), "grey"), ("TRANSFERIR RESPONSABILIDADE", A("transferir", 901), "grey"),
            ("DISPENSAR SEGURANÇA", A("dispensar", 907), "grey")], y0=4.2, dy=0.74, x=-0.2, w=3.9, h=0.54, fs=0.5, badge="x", bx=2.2),
    Pl("COOPERAÇÃO", A("cooperação", 918), [0, 1.6, 1.2], w=3.2, h=0.7, bg="green"),
    it("badge", rad=0.4, kind="ok", p=[1.95, 1.6, 1.5], t=A("cooperação", 918, 0.2)),
    Pl("OFERTA COM SUSTENTABILIDADE", A("ampliar", 922), [0, 0.35, 2.3], w=4.3, h=0.52, bg="white", fs=0.5, r=[-0.4, 0, 0]),
], cam=(0, 3.0, 13.0), look=(0, 2.5, 0))

chip("c9", A("E", 929, -0.1), Z("fundamental", 936, 0.3), [("UMA IDEIA", A("ideia", 933)), (G("FUNDAMENTAL"), A("fundamental", 936))])

# "Fazer mais com menos não pode significar ensinar menos. Significa usar melhor os recursos, evitar desperdícios e investir onde a aprendizagem acontece."
full("more", A("Fazer", 937, -0.1), Z("acontece", 960, 0.4), [
    Pl("FAZER MAIS COM MENOS", A("Fazer", 937, 0.1), [0, 5.7, 0], w=9.6, h=1.4, bg="plate", fs=0.74),
    Pl("NÃO É ENSINAR MENOS", A("não", 941), [0, 4.0, 0.4], w=8.6, h=1.1, bg="red", fs=0.7),
    Pl("USAR MELHOR OS RECURSOS", A("usar", 947), [-3.2, 2.2, 0.8], w=5.8, h=0.8, bg="white", fs=0.6),
    Pl("EVITAR DESPERDÍCIOS", A("evitar", 953), [3.2, 2.2, 0.8], w=5.2, h=0.8, bg="white", fs=0.6),
    Pl("INVESTIR ONDE A APRENDIZAGEM ACONTECE", A("investir", 956), [0, 0.7, 1.8], w=10.0, h=0.9, bg="gold", fs=0.56, r=[-0.25, 0, 0]),
], cam=(0, 3.6, 18.4), look=(0, 3.1, 0))

# "Imagine um trabalhador que passou 15 anos exercendo uma atividade... conhece os equipamentos, domina os procedimentos, resolve problemas... decide voltar a estudar"
side("worker", A("Imagine", 970, -0.2), Z("não", 1018, 0.4), [
    it("pawn", p=[-1.5, 0, 0.6], s=0.6, mat="gold", t=A("Imagine", 970, 0.15)),
    it("numeral", txt="15", size=1.15, p=[0.1, 3.55, -0.4], t=A("15", 975), r=[0, 0.25, 0], spin=0.12, louder=2),
    Pl("ANOS DE TRABALHO", A("anos", 976), [0.7, 3.1, 0.9], w=3.2, h=0.54, bg="plate"),
    *stack([("CONHECE OS EQUIPAMENTOS", A("conhece", 982)), ("DOMINA OS PROCEDIMENTOS", A("domina", 985)), ("RESOLVE PROBLEMAS", A("resolve", 988))],
           y0=2.35, dy=0.6, x=0.7, w=3.2, h=0.48, fs=0.48, z=1.2),
    Pl("DECIDE VOLTAR A ESTUDAR", A("decide", 997), [0, 5.2, 0.2], w=4.2, h=0.56, bg="blue", fs=0.54, out=A("Faz", 1001, -0.05)),
    Pl("IGNORAR TUDO O QUE ELE SABE?", A("ignorar", 1003), [0, 5.2, 0.2], w=4.4, h=0.56, bg="red", fs=0.5),
    it("badge", rad=0.45, kind="x", p=[1.9, 4.35, 0.6], t=A("claro", 1016)),
], cam=(0, 3.2, 13.2), look=(0, 2.5, 0))

# "A legislação já permite avaliar e aproveitar conhecimentos adquiridos, inclusive no trabalho... a aprendizagem acontece em diferentes momentos da vida. Mas existe um cuidado"
side("recog", A("A", 1019, -0.2), Z("indispensável", 1066, 0.3), [
    it("doc", txt="LEI", head="#0457E7", w=1.5, h=1.9, p=[-1.5, 3.9, -0.3], t=A("A", 1019, 0.15), r=[0, 0.3, 0.04], float=0.04),
    Pl("JÁ PERMITE", A("permite", 1024), [0.8, 4.5, 0.2], w=2.6, h=0.56, bg="green"),
    Pl("AVALIAR E APROVEITAR", A("avaliar", 1025), [0.8, 3.7, 0.4], w=3.0, h=0.52, bg="white", fs=0.52),
    Pl("O QUE SE APRENDEU NO TRABALHO", A("inclusive", 1031), [0, 2.5, 0.9], w=4.4, h=0.52, bg="white", fs=0.5),
    it("clock", p=[-1.4, 1.1, 1.0], s=0.5, t=A("diferentes", 1058), fill=[[A("diferentes", 1058), 1.6, 0.9]], color=0x0457e7),
    Pl("A VIDA TODA", A("momentos", 1059), [0.7, 1.3, 1.4], w=2.6, h=0.54, bg="gold"),
    Pl("MAS: UM CUIDADO", A("cuidado", 1065), [0, 0.35, 2.4], w=3.6, h=0.56, bg="red", r=[-0.4, 0, 0]),
], cam=(0, 3.0, 13.0), look=(0, 2.5, 0))

# "Reconhecer competências não significa distribuir diplomas. O conhecimento precisa ser demonstrado, a avaliação séria, o processo documentado, as exigências legais respeitadas."
full("notdipl", A("Reconhecer", 1067, -0.1), Z("respeitadas", 1096, 0.45), [
    Pl("RECONHECER COMPETÊNCIAS", A("Reconhecer", 1067, 0.1), [-1.4, 5.9, 0], w=7.6, h=1.1, bg="plate", fs=0.66),
    Pl("NÃO É DISTRIBUIR DIPLOMAS", A("não", 1069), [-1.4, 4.5, 0.4], w=7.6, h=1.0, bg="red", fs=0.64),
    it("doc", txt="DIPLOMA", head="#C9A45A", w=2.6, h=2.0, p=[4.4, 5.1, 0.2], t=A("diplomas", 1072), r=[0, -0.25, 0.04], float=0.05),
    *sum([[Pl(txt, t, [-3.0 + (k % 2) * 6.0, 2.6 - (k // 2) * 1.25, 1.0], w=5.2, h=0.9, bg="white", fs=0.54),
           it("badge", rad=0.36, kind="ok", p=[-3.0 + (k % 2) * 6.0 + 2.6, 2.6 - (k // 2) * 1.25 + 0.3, 1.4], t=t + 0.2, quiet=True)]
          for k, (txt, t) in enumerate([("CONHECIMENTO DEMONSTRADO", A("demonstrado", 1077)), ("AVALIAÇÃO SÉRIA", A("séria", 1082)),
                                        ("PROCESSO DOCUMENTADO", A("documentado", 1087)), ("EXIGÊNCIAS LEGAIS", A("exigências", 1090))])], []),
], cam=(0, 3.6, 18.6), look=(0, 3.1, 0))

chip("c10", A("A", 1098, -0.1), Z("respeitada", 1127, 0.35), [("O DIPLOMA PRECISA", A("diploma", 1108)), ("REPRESENTAR", A("representar", 1110)),
                                                              (G("COMPETÊNCIAS REAIS"), A("competências", 1111))])

# "Existe uma ilusão: a ideia de que a IA vai resolver sozinha os problemas da educação. Não vai. Ela pode ajudar muito... mas não substitui a responsabilidade pedagógica do professor"
IA1 = A("Ela", 1152, -0.05)
side("ia", A("Existe", 1128, -0.2), Z("professor", 1181, 0.4), [
    it("robot", p=[-1.4, 0, 0.6], s=0.62, t=A("Existe", 1128, 0.15), r=[0, 0.45, 0], eyesOn=A("inteligência", 1138)),
    Pl("UMA ILUSÃO", A("ilusão", 1130), [0, 5.2, 0.2], w=2.8, h=0.6, bg="red", out=IA1),
    Pl("“A IA RESOLVE SOZINHA”", A("resolver", 1142), [0.3, 4.3, 0.4], w=4.0, h=0.56, bg="white", fs=0.54, out=IA1),
    it("badge", rad=0.45, kind="x", p=[1.9, 3.5, 0.8], t=A("não", 1150), out=IA1),
    Pl("ELA PODE AJUDAR", IA1 + 0.1, [0, 5.2, 0.2], w=3.4, h=0.6, bg="blue"),
    *stack([("OFERECER RECURSOS", A("recursos", 1158)), ("PLANEJAR AULAS", A("planejamento", 1161)), ("IDENTIFICAR DIFICULDADES", A("identificar", 1166)),
            ("NOVAS FORMAS DE APRENDER", A("novas", 1170))], y0=4.35, dy=0.62, x=0.75, w=3.1, h=0.48, fs=0.46, z=1.0),
    it("pawn", p=[1.5, 0, 1.6], s=0.5, mat="gold", t=A("substitui", 1177)),
    Pl("NÃO SUBSTITUI O PROFESSOR", A("substitui", 1177, 0.1), [0, 0.35, 2.6], w=4.3, h=0.54, bg="gold", fs=0.5, r=[-0.4, 0, 0]),
], cam=(0, 3.2, 13.2), look=(0, 2.5, 0))

# "O professor precisa dominar aquilo que ensina, conhecer o exercício real da profissão e saber transformar esse conhecimento em aprendizagem... caminhar juntas"
P2 = A("Por", 1214, -0.05)
side("prof", A("O", 1192, -0.2), Z("juntas", 1229, 0.4), [
    Pl("O PROFESSOR PRECISA", A("professor", 1193), [0, 5.2, 0.2], w=3.9, h=0.58, bg="plate", out=P2),
    *sum([[it("numeral", txt=str(k + 1), size=0.62, p=[-2.05, 4.0 - k * 1.05, 0.5], t=t, r=[0, 0.25, 0], quiet=True, out=P2),
           Pl(txt, t + 0.06, [0.35, 4.2 - k * 1.05, 0.6], w=3.5, h=0.6, bg="white", fs=0.5, out=P2)]
          for k, (txt, t) in enumerate([("DOMINAR O QUE ENSINA", A("dominar", 1195)), ("CONHECER A PROFISSÃO REAL", A("conhecer", 1200)),
                                        ("TRANSFORMAR EM APRENDIZAGEM", A("transformar", 1209))])], []),
    Pl("FORMAÇÃO PEDAGÓGICA", A("formação", 1216), [0, 4.3, 0.4], w=4.0, h=0.66, bg="blue", fs=0.56),
    Sym("+", A("experiência", 1218, -0.1), [0, 3.3, 0.7], size=0.8),
    Pl("EXPERIÊNCIA PROFISSIONAL", A("experiência", 1218), [0, 2.3, 0.4], w=4.2, h=0.66, bg="plate", fs=0.54),
    Pl("CAMINHAM JUNTAS", A("caminhar", 1228), [0, 0.35, 2.4], w=3.8, h=0.58, bg="gold", r=[-0.4, 0, 0]),
], cam=(0, 3.0, 13.0), look=(0, 2.5, 0))

chip("c11", A("E", 1252, -0.1), Z("aula", 1272, 0.4), [("FORMAÇÃO CONTINUADA", A("formação", 1254)), ('<span class="sk">COLEÇÃO DE CERTIFICADOS</span>', A("coleção", 1261)),
                                                      (f'{G("MUDANÇA")} NA SALA DE AULA', A("mudança", 1267))], strike=(1, A("mudança", 1267, -0.3)))

# "Quando uma instituição anuncia que matriculou 10 mil estudantes, o que nós realmente sabemos? quantas concluíram, aprenderam, demonstraram, conquistaram, melhoraram de vida?"
FUN = [("ENTRARAM", A("entraram", 1293), "ok"), ("CONCLUÍRAM", A("concluíram", 1296), None), ("APRENDERAM", A("aprenderam", 1298), None),
       ("MOSTRARAM COMPETÊNCIA", A("demonstraram", 1300), None), ("NOVAS OPORTUNIDADES", A("conquistaram", 1308), None), ("MELHORARAM DE VIDA", A("melhoraram", 1313), None)]
full("tenk", A("Quando", 1276, -0.1), Z("produtividade", 1326, 0.45), [
    Pl("UMA INSTITUIÇÃO ANUNCIA:", A("Quando", 1276, 0.25), [-3.9, 6.3, 0.4], w=4.6, h=0.7, bg="white", fs=0.5),
    it("numeral", txt="10 MIL", size=1.0, p=[-5.6, 4.6, 0], t=A("10", 1282), r=[0, 0.18, 0], louder=3),
    Pl("MATRICULADOS", A("mil", 1283, 0.1), [-3.9, 3.5, 0.6], w=4.4, h=0.9, bg="plate", fs=0.64),
    Pl("O QUE SABEMOS?", A("sabemos", 1289), [-3.9, 2.2, 0.8], w=4.4, h=0.8, bg="gold", fs=0.6),
    *sum([[Pl(txt, t, [2.6, 6.2 - k * 1.02, 0.4 + k * 0.1], w=5.8 - k * 0.35, h=0.82, bg=("green" if kind else "white"), fs=0.6),
           (it("badge", rad=0.34, kind="ok", p=[2.6 + (5.8 - k * 0.35) / 2 + 0.45, 6.2 - k * 1.02, 0.8], t=t + 0.2, quiet=True) if kind else
            it("text", txt="?", size=0.7, mat="gold", p=[2.6 + (5.8 - k * 0.35) / 2 + 0.2, 5.85 - k * 1.02, 0.8], t=t + 0.15, quiet=True))]
          for k, (txt, t, kind) in enumerate(FUN)], []),
], cam=(0, 3.8, 19.0), look=(0, 3.3, 0))

# "O Brasil instituiu o Sistema Nacional de Avaliação da Educação Profissional e Tecnológica, o Sinaept: condições de oferta, aprendizagem, permanência, conclusão e inserção dos egressos"
side("sinaept", A("Brasil", 1337, -0.2), Z("revelam", 1399, 0.35), [
    Pl("SINAEPT", A("Brasil", 1337, 0.15), [0, 5.2, 0.2], w=3.0, h=0.7, bg="gold"),
    Pl("AVALIAÇÃO DA EDUCAÇÃO PROFISSIONAL", A("Avaliação", 1343), [0, 4.45, 0.3], w=4.4, h=0.46, bg="plate", fs=0.44),
    *sum([[it("bar", w=0.6, h=2.0, d=0.6, mat=("gold" if k == 4 else "blue"), p=[-2.0 + k * 1.0, 0, -0.9], t=t, quiet=True, grow=[[t, 0.5, 0.45 + 0.13 * k]]),
           Pl(txt, t + 0.05, [0, 3.7 - k * 0.0, 0.5], w=3.6, h=0.5, bg="white", fs=0.52, out=(nxt - 0.03 if nxt else None)) if True else None]
          for k, (txt, t, nxt) in enumerate([("CONDIÇÕES DE OFERTA", A("condições", 1355), A("aprendizagem", 1358)), ("APRENDIZAGEM", A("aprendizagem", 1358), A("permanência", 1359)),
                                             ("PERMANÊNCIA", A("permanência", 1359), A("conclusão", 1360)), ("CONCLUSÃO", A("conclusão", 1360), A("inserção", 1362)),
                                             ("EGRESSOS NO TRABALHO", A("inserção", 1362), None)])], []),
    Pl("NÃO BASTA PRODUZIR NÚMEROS", A("Não", 1389), [0, 2.9, 1.0], w=4.3, h=0.52, bg="red", fs=0.5),
    Pl("É PRECISO INTERPRETAR", A("interpretar", 1395), [0, 0.35, 2.4], w=4.0, h=0.56, bg="green", fs=0.54, r=[-0.4, 0, 0]),
], cam=(0, 3.0, 13.0), look=(0, 2.5, 0))

# "Quanto custa, de fato, formar um profissional? Não estou falando apenas do preço de uma matrícula... não para escolher o modelo mais barato... investimento → resultado"
side("cost", A("Quanto", 1405, -0.2), Z("resultado", 1484, 0.35), [
    it("coins", p=[-1.5, 0.2, 0.8], s=0.8, t=A("Quanto", 1405, 0.15)),
    Pl("QUANTO CUSTA FORMAR?", A("custa", 1406), [0, 5.2, 0.2], w=4.2, h=0.6, bg="plate"),
    Pl("PREÇO DA MATRÍCULA", A("preço", 1417), [-0.2, 4.2, 0.4], w=3.6, h=0.54, bg="grey"),
    it("badge", rad=0.3, kind="x", p=[1.95, 4.2, 0.7], t=A("matrícula", 1420), quiet=True),
    Pl("CUSTO ATÉ CONCLUIR E APRENDER", A("investimento", 1424), [0, 3.4, 0.5], w=4.4, h=0.54, bg="gold", fs=0.5),
    Pl("NÃO O MAIS BARATO", A("barato", 1455, -0.6), [0.6, 2.4, 0.9], w=3.3, h=0.52, bg="white", fs=0.52),
    Pl("RESPONSABILIDADE", A("responsabilidade", 1462), [0.6, 1.7, 1.1], w=3.3, h=0.52, bg="white", fs=0.52),
    Pl("INVESTIMENTO → RESULTADO", A("investimento", 1468), [0, 0.35, 2.5], w=4.3, h=0.56, bg="green", fs=0.5, r=[-0.4, 0, 0]),
], cam=(0, 3.0, 13.0), look=(0, 2.5, 0))

# "Foi com essas preocupações que organizamos nossas contribuições técnicas..."
CON = [("INFRAESTRUTURA COMPARTILHADA", A("uso", 1500)), ("EDUCAÇÃO MEDIADA POR TECNOLOGIA", A("precisão", 1509)), ("CERTIFICAÇÃO COM CRITÉRIO", A("critérios", 1518)),
       ("REGRAS DE ESTÁGIO", A("estágio", 1529)), ("AVALIAÇÃO POR RESULTADOS", A("avaliação", 1542)), ("DOCÊNCIA E GOVERNANÇA", A("formação", 1552))]
side("contrib", A("Foi", 1485, -0.2), Z("supervisão", 1561, 0.35), [
    Pl("NOSSAS CONTRIBUIÇÕES", A("contribuições", 1494), [0, 5.25, 0.2], w=4.0, h=0.58, bg="gold"),
    *sum([[it("numeral", txt=str(k + 1), size=0.42, p=[-2.2, 4.3 - k * 0.72, 0.5], t=t, r=[0, 0.25, 0], quiet=True),
           Pl(txt, t + 0.06, [0.3, 4.45 - k * 0.72, 0.6], w=3.9, h=0.5, bg="white", fs=0.46)] for k, (txt, t) in enumerate(CON)], []),
], cam=(0, 2.8, 13.0), look=(0, 2.5, 0))

chip("c12", A("e", 1603, -0.1), Z("decisões", 1613, 0.3), [("A APRENDIZAGEM DO ESTUDANTE", A("aprendizagem", 1607)), (G("NO CENTRO DAS DECISÕES"), A("centro", 1611))])
chip("c13", A("Porque", 1614, -0.1), Z("qualidade", 1634, 0.35), [("O DESAFIO NÃO É SÓ", A("desafio", 1617)), ("ESCREVER DIRETRIZES:", A("escrever", 1621)),
                                                                 (f'É {G("IMPLEMENTAR")} COM QUALIDADE', A("criar", 1626))], side_="left")

# "Agora, eu quero convidar você a imaginar algo diferente."
full("imagine", A("Agora", 1635, -0.1), Z("diferente", 1643, 0.4), [
    Pl("PARTE FINAL", A("Agora", 1635, 0.1), [0, 5.7, 0], w=3.4, h=0.7, bg="gold"),
    Pl("IMAGINE ALGO DIFERENTE", A("imaginar", 1641), [0, 3.9, 0], w=11.0, h=1.6, fs=0.7),
    *[it("pawn", p=[-6.0 + k * 2.0, 0, -0.4], s=0.5, mat=("gold" if k == 3 else "grey"), t=A("Agora", 1635, 0.2 + 0.06 * k), quiet=True) for k in range(7)],
], cam=(0.4, 3.4, 18.4), look=(0.2, 3.0, 0))

# "Imagine uma escola que precise produzir sozinha todos os conteúdos, comprar todas as tecnologias e manter toda a estrutura especializada."
side("alone", A("Imagine", 1644, -0.2), Z("especializada", 1666, 0.3), [
    it("pawn", p=[0, 0, 1.0], s=0.55, mat="grey", t=A("Imagine", 1644, 0.15), shakes=[A("estrutura", 1664, 0.4)]),
    Pl("SOZINHA", A("sozinha", 1650), [0, 0.3, 2.2], w=2.2, h=0.56, bg="red", r=[-0.4, 0, 0]),
    *[it("box", w=2.6 - k * 0.3, h=0.9, d=1.2, mat=m, own=True, p=[0, 2.75 + k * 0.95, 0.2], t=t, drop=2.0) for k, (m, t) in
      enumerate([("blue", A("conteúdos", 1652)), ("sky", A("tecnologias", 1657)), ("gold", A("estrutura", 1664))])],
    *[Pl(txt, t + 0.3, [0, 2.75 + k * 0.95, 0.95], w=2.2 - k * 0.2, h=0.46, bg="white", fs=0.5, quiet=True) for k, (txt, t) in
      enumerate([("CONTEÚDOS", A("conteúdos", 1652)), ("TECNOLOGIAS", A("tecnologias", 1657)), ("ESTRUTURA", A("estrutura", 1664))])],
], cam=(0, 3.2, 13.4), look=(0, 2.6, 0))

# "Imagine instituições trabalhando em cooperação... professores apoiados pela tecnologia... estudantes construindo percursos... setor produtivo... gestores acompanhando resultados"
COOP = [("INSTITUIÇÕES EM COOPERAÇÃO", A("instituições", 1668), "grey"), ("PROFESSOR + TECNOLOGIA", A("professores", 1679), "grey"),
        ("PERCURSOS PROGRESSIVOS", A("estudantes", 1692), "gold"), ("SETOR PRODUTIVO NA FORMAÇÃO", A("setor", 1708), "grey"), ("GESTOR OLHA RESULTADOS", A("gestores", 1723), "grey")]
side("coop", A("Imagine", 1667, -0.15), Z("alcançados", 1736, 0.35), [
    Pl("AGORA IMAGINE:", A("Imagine", 1667, 0.1), [0, 5.25, 0.2], w=3.2, h=0.58, bg="green"),
    *sum([[it("pawn", p=[-2.0, 4.02 - k * 0.86, 0.5], s=0.2, mat=m, t=t, quiet=k > 0),
           Pl(txt, t + 0.05, [0.35, 4.25 - k * 0.86, 0.6], w=3.7, h=0.56, bg=("gold" if m == "gold" else "white"), fs=0.5)] for k, (txt, t, m) in enumerate(COOP)], []),
], cam=(0, 2.9, 13.0), look=(0, 2.6, 0))

chip("c14", A("Isso", 1737, -0.1), Z("profissional", 1770, 0.35), [("AINDA NÃO É REALIDADE", A("ainda", 1738)), (f'É UMA {G("POSSIBILIDADE")}', A("possibilidade", 1750)),
                                                                  ("DENTRO DAS NORMAS", A("respeitar", 1759))])

# "Nesse modelo, a tecnologia é ferramenta, a cooperação é instrumento, a instituição continua responsável e o estudante permanece no centro"
full("model", A("Nesse", 1771, -0.1), Z("processo", 1798, 0.45), [
    it("pawn", p=[0, 0, 0.6], s=0.95, mat="gold", t=A("Nesse", 1771, 0.25), pulses=[A("estudante", 1791)]),
    it("robot", p=[-4.4, 0, -0.4], s=0.6, t=A("tecnologia", 1774), r=[0, 0.5, 0], eyesOn=A("tecnologia", 1774, 0.2)),
    Pl("TECNOLOGIA = FERRAMENTA", A("tecnologia", 1774, 0.1), [-3.4, 4.6, 0], w=5.4, h=0.9, bg="blue", fs=0.5),
    *[it("pawn", p=[3.4 + k * 1.0, 0, -0.6], s=0.5, mat="grey", t=A("cooperação", 1778, 0.06 * k), quiet=k > 0) for k in range(3)],
    Pl("COOPERAÇÃO = INSTRUMENTO", A("cooperação", 1778, 0.1), [3.4, 4.6, 0], w=5.6, h=0.9, bg="plate", fs=0.5),
    Pl("A INSTITUIÇÃO RESPONDE PELA FORMAÇÃO", A("instituição", 1782), [0, 6.1, 0], w=9.6, h=0.9, bg="white", fs=0.56),
    Pl("O ESTUDANTE NO CENTRO", A("estudante", 1791), [0, 0.6, 2.6], w=7.6, h=1.0, bg="gold", fs=0.68, r=[-0.3, 0, 0]),
], cam=(0, 3.8, 18.8), look=(0, 3.1, 0))

chip("c15", A("Mas", 1822, -0.1), Z("lei", 1837, 0.35), [("OLHE ALÉM DO PAPEL,", A("olhar", 1828)), (f'ALÉM DA {G("LETRA DA LEI")}', A("letra", 1834))])

# "Pense naquele jovem que terminou o ensino médio... naquela mãe que precisa aumentar a renda... naquela pessoa que interrompeu os estudos... Oportunidade é tudo."
side("people", A("Pense", 1838, -0.2), Z("tudo", 1906, 0.4), [
    it("pawn", p=[-1.6, 0, 0.6], s=0.5, mat="grey", own=True, t=A("jovem", 1840), colors=[[A("Oportunidade", 1904), 0xf4b04a]]),
    Pl("O JOVEM", A("jovem", 1840, 0.05), [-1.6, 0.3, 1.7], w=1.5, h=0.44, r=[-0.4, 0, 0], quiet=True),
    Pl("SEM O PRIMEIRO EMPREGO", A("primeiro", 1851), [0, 5.2, 0.2], w=4.2, h=0.54, bg="white", fs=0.52, out=A("Pense", 1853, -0.05)),
    it("pawn", p=[0, 0, 0.6], s=0.5, mat="grey", own=True, t=A("mãe", 1855), colors=[[A("Oportunidade", 1904, 0.08), 0xf4b04a]]),
    Pl("A MÃE", A("mãe", 1855, 0.05), [0, 0.3, 1.7], w=1.3, h=0.44, r=[-0.4, 0, 0], quiet=True),
    Pl("PRECISA AUMENTAR A RENDA", A("aumentar", 1858), [0, 5.2, 0.2], w=4.3, h=0.54, bg="white", fs=0.52, out=A("Pense", 1876, -0.05)),
    it("pawn", p=[1.6, 0, 0.6], s=0.5, mat="grey", own=True, t=A("pessoa", 1878), colors=[[A("Oportunidade", 1904, 0.16), 0xf4b04a]]),
    Pl("QUEM PAROU", A("pessoa", 1878, 0.05), [1.6, 0.3, 1.7], w=1.6, h=0.44, r=[-0.4, 0, 0], fs=0.5, quiet=True),
    Pl("QUER RECONSTRUIR A TRAJETÓRIA", A("reconstruir", 1884), [0, 5.2, 0.2], w=4.4, h=0.54, bg="white", fs=0.5, out=A("Oportunidade", 1904, -0.05)),
    Pl("OPORTUNIDADE É TUDO", A("Oportunidade", 1904), [0, 4.4, 0.4], w=4.3, h=0.72, bg="gold"),
], cam=(0, 3.2, 13.0), look=(0, 2.4, 0))

chip("c16", A("Não", 1907, -0.1), Z("recomeço", 1929, 0.4), [("NÃO É SÓ UM CURSO:", A("curso", 1912, -0.4)), ("FUTURO", A("futuro", 1921)), ("AUTONOMIA", A("autonomia", 1923)),
                                                            ("DIGNIDADE", A("dignidade", 1925)), (G("RECOMEÇO"), A("recomeço", 1929))])

# "A educação profissional precisa ser rigorosa, confiável, desenvolver competências, mas também acessível, inclusiva, chegar às pessoas, chegar nas regiões isoladas"
side("balance", A("A", 1940, -0.2), Z("geograficamente", 1968, 0.35), [
    Pl("PRECISA SER", A("A", 1940, 0.15), [0, 5.3, 0.2], w=2.8, h=0.56, bg="white"),
    Pl("RIGOROSA", A("rigorosa", 1945), [-1.15, 4.6, 0.4], w=2.1, h=0.54, bg="plate", fs=0.54),
    Pl("CONFIÁVEL", A("confiável", 1947), [-1.15, 3.85, 0.4], w=2.1, h=0.54, bg="plate", fs=0.54),
    Pl("COMPETÊNCIAS", A("competências", 1950), [-1.15, 3.1, 0.4], w=2.1, h=0.54, bg="plate", fs=0.5),
    Pl("ACESSÍVEL", A("acessível", 1955), [1.15, 4.6, 0.4], w=2.1, h=0.54, bg="gold", fs=0.54),
    Pl("INCLUSIVA", A("inclusiva", 1958), [1.15, 3.85, 0.4], w=2.1, h=0.54, bg="gold", fs=0.54),
    Pl("PERTO DAS PESSOAS", A("chegar", 1960), [1.15, 3.1, 0.4], w=2.1, h=0.54, bg="gold", fs=0.44),
    *[it("pawn", p=[-1.8 + k * 0.9, 0, 1.4 + (k % 2) * 0.4], s=0.34, mat="grey", t=A("chegar", 1964, 0.05 * k), quiet=k > 0) for k in range(5)],
    Pl("ATÉ AS REGIÕES ISOLADAS", A("regiões", 1966), [0, 0.3, 2.6], w=4.2, h=0.52, bg="white", fs=0.52, r=[-0.4, 0, 0]),
], cam=(0, 3.0, 13.0), look=(0, 2.5, 0))

chip("c17", A("Eu", 1969, -0.1), Z("profissional", 1990, 0.35), [("A PERGUNTA DO COMEÇO:", A("perguntando", 1973)), ("SÓ MAIS ESCOLAS TÉCNICAS?", A("apenas", 1978)),
                                                                (f'OU UMA {G("NOVA ORGANIZAÇÃO")}?', A("Ou", 1983))])

# "Não basta ter uma legislação atualizada, falar de IA, anunciar novas vagas, multiplicar instituições e plataformas. Precisamos saber se mais brasileiros aprendem"
NB = [("LEGISLAÇÃO ATUALIZADA", A("legislação", 2006)), ("FALAR DE IA", A("falar", 2010)), ("ANUNCIAR NOVAS VAGAS", A("anunciar", 2018)),
      ("MULTIPLICAR PLATAFORMAS", A("multiplicar", 2024))]
full("nobasta", A("Não", 2002, -0.1), Z("trajetórias", 2046, 0.45), [
    Pl("NÃO BASTA", A("Não", 2002, 0.1), [0, 6.2, 0], w=5.0, h=1.2, bg="red", fs=0.74),
    *sum([[Pl(txt, t, [-3.1 + (k % 2) * 6.2, 4.5 - (k // 2) * 1.2, 0.5], w=5.6, h=0.9, bg="grey", fs=0.54),
           it("badge", rad=0.34, kind="x", p=[-3.1 + (k % 2) * 6.2 + 2.8, 4.85 - (k // 2) * 1.2, 0.9], t=t + 0.2, quiet=True)] for k, (txt, t) in enumerate(NB)], []),
    Pl("MAIS BRASILEIROS APRENDENDO", A("mais", 2037), [0, 1.9, 1.2], w=10.0, h=1.0, bg="green", fs=0.66),
    *[it("pawn", p=[-5.4 + k * 1.2, 0, 2.0], s=0.36, mat=("gold" if k % 3 == 1 else "grey"), t=A("mais", 2037, 0.04 * k), quiet=True) for k in range(10)],
], cam=(0, 3.8, 18.8), look=(0, 3.2, 0))

# "Precisamos conciliar inovação com responsabilidade, qualidade com acesso, expansão com sustentabilidade e tecnologia com valorização humana."
PAIRS = [("INOVAÇÃO", "RESPONSABILIDADE", A("inovação", 2049)), ("QUALIDADE", "ACESSO", A("qualidade", 2052)), ("EXPANSÃO", "SUSTENTABILIDADE", A("expansão", 2055)),
         ("TECNOLOGIA", "VALORIZAÇÃO HUMANA", A("tecnologia", 2059))]
side("pairs", A("Precisamos", 2047, -0.2), Z("humana", 2062, 0.4), [
    Pl("CONCILIAR", A("conciliar", 2048), [0, 5.2, 0.2], w=2.8, h=0.6, bg="gold"),
    *sum([[Pl(a, t, [-1.2, 4.3 - k * 0.86, 0.5], w=2.05, h=0.52, bg="plate", fs=0.48), Sym("+", t + 0.1, [0.0, 4.3 - k * 0.86, 0.75], size=0.36),
           Pl(b, t + 0.25, [1.25, 4.3 - k * 0.86, 0.5], w=2.15, h=0.52, bg="white", fs=0.42, quiet=True)] for k, (a, b, t) in enumerate(PAIRS)], []),
], cam=(0, 3.0, 13.0), look=(0, 2.6, 0))

chip("c18", A("Mas", 2073, -0.1), Z("reais", 2095, 0.35), [("NENHUMA RESOLUÇÃO", A("nenhuma", 2074)), ("TRANSFORMA SOZINHA", A("transformar", 2081)),
                                                          (f'NORMA → {G("OPORTUNIDADE REAL")}', A("normas", 2090))])

# "Quando os professores conseguem ensinar melhor, os estudantes aprender, a formação se conecta ao trabalho, aumenta a produtividade, o investimento gera resultados"
side("when", A("Quando", 2096, -0.2), Z("sociedade", 2136, 0.35), [
    Pl("A TRANSFORMAÇÃO ACONTECE", A("Quando", 2096, 0.1), [0, 5.25, 0.2], w=4.3, h=0.56, bg="plate", fs=0.52),
    *stack([("PROFESSOR ENSINA MELHOR", A("professores", 2098)), ("ESTUDANTE APRENDE", A("estudantes", 2104)), ("FORMAÇÃO LIGADA AO TRABALHO", A("formação", 2109)),
            ("PRODUTIVIDADE DO PAÍS", A("produtividade", 2119)), ("RESULTADO PARA AS PESSOAS", A("resultados", 2128), "gold")], y0=4.4, dy=0.76, x=-0.2, w=3.9, h=0.54, fs=0.48,
           badge="ok", bx=2.2),
], cam=(0, 2.9, 13.0), look=(0, 2.6, 0))

# "A educação profissional do futuro não será medida apenas pelo número de escolas, matrículas ou diplomas. Será medida pela capacidade de transformar
#  conhecimento em competência, competência em oportunidade e oportunidade em desenvolvimento humano."
F1 = A("Ela", 2167, -0.05)
full("final", A("A", 2146, -0.1), Z("humano", 2184, 0.6), [
    Pl("A EDUCAÇÃO PROFISSIONAL DO FUTURO", A("A", 2146, 0.1), [0, 6.3, 0], w=10.0, h=1.0, bg="plate", fs=0.6),
    *[Pl(txt, t, [-4.1 + k * 4.1, 4.6, 0.4], w=3.6, h=0.8, bg="grey", fs=0.56, out=F1) for k, (txt, t) in
      enumerate([("ESCOLAS", A("escolas", 2158)), ("MATRÍCULAS", A("matrículas", 2161)), ("DIPLOMAS", A("diplomas", 2165))])],
    Pl("NÃO SÓ NÚMEROS", A("não", 2151), [0, 3.3, 0.8], w=5.2, h=0.8, bg="red", fs=0.64, out=F1),
    Pl("CONHECIMENTO", A("conhecimento", 2174), [-4.2, 4.4, 0.4], w=3.6, h=0.9, bg="white", fs=0.5),
    Sym("→", A("competência", 2176, -0.1), [-2.1, 4.4, 0.7], size=0.5),
    Pl("COMPETÊNCIA", A("competência", 2176), [0, 4.4, 0.4], w=3.6, h=0.9, bg="white", fs=0.5),
    Sym("→", A("oportunidade", 2179, -0.1), [2.1, 4.4, 0.7], size=0.5),
    Pl("OPORTUNIDADE", A("oportunidade", 2179), [4.2, 4.4, 0.4], w=3.6, h=0.9, bg="white", fs=0.5),
    Pl("DESENVOLVIMENTO HUMANO", A("desenvolvimento", 2183), [0, 2.4, 1.2], w=9.6, h=1.3, bg="gold", fs=0.7),
    *[it("pawn", p=[-5.4 + k * 1.2, 0, 2.2], s=0.36, mat="gold", t=A("desenvolvimento", 2183, 0.1 + 0.04 * k), quiet=True) for k in range(10)],
], cam=(0, 3.8, 19.0), look=(0, 3.3, 0))
sfx(A("desenvolvimento", 2183), "chime", -17, 0, "final idea")

chip("c19", A("E", 2185, -0.1), Z("educacional", 2208, 0.35), [("ESSE É O DESAFIO.", A("desafio", 2189)), ("ESSE É O DEBATE.", A("debate", 2194)),
                                                              (f'A {G("NOVA ORDEM")} EDUCACIONAL', A("nova", 2205))])

# CTA: "participe da conversa deixando um comentário: o que é indispensável para que a educação profissional chegue a mais brasileiros sem perder a qualidade"
CTA0, CTA1 = A("participe", 2248, -0.2), Z("qualidade", 2274, 0.4)
side("cta", CTA0, CTA1, [], auto_sfx=False)
