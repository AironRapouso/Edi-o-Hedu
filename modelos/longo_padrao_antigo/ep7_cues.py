# Cue sheet for EP7 "A educação profissional do futuro" in the LONG-VIDEO STANDARD (EP_AULA_INVERTIDA / EP_ESCOLA):
# full-frame talking head, vinheta, intertitles, lower thirds, side stacks, bottom pills/chains, one data panel, fresh B-roll,
# discreet SFX. (User, 2026-11-18: long videos keep this standard; the Reels look is only for the shorts.)

UPDATE_NOTE = ("Atualização: parecer homologado pelo MEC em 10/11/2026; deu origem à Resolução CNE/CP nº 2, de 11/11/2026 · "
               "Fonte: gov.br/mec/cne")


def KC(prefix, after):
    """first source word from after-8 on that starts with prefix AND is in the cut"""
    i = max(0, after - 8)
    while True:
        i = K(prefix, i)
        if _out(SRCW[i]["start"]) is not None or _out(SRCW[i]["start"] + 0.06) is not None:
            return i
        i += 1


def A(prefix, after, dt=0.0):
    return T(KC(prefix, after), dt)


def Z(prefix, after, dt=0.0):
    return TE(KC(prefix, after), dt)


def cam_shift(s, e, x=-420):
    tw("#cam", "{x:0}", f"{{x:{x}}}", s, 0.7, "power3.inOut")
    tw("#cam", f"{{x:{x}}}", "{x:0}", e - 0.4, 0.6, "power3.inOut")


def panel(cid, s, e):
    cam_shift(s - 0.05, e + 0.1)
    clip(cid, s, e, f'<div class="in"><div id="{cid}-p" class="panel"><div class="grid"></div></div></div>', track=3)
    life(cid, s, e, 0.01, 0.01)
    tw(f"#{cid}-p", "{x:840}", "{x:0}", s - 0.05, 0.7, "power3.inOut")
    tw(f"#{cid}-p", "{x:0}", "{x:840}", e - 0.45, 0.6, "power3.inOut")
    NEUTRAL.append((s, e))


_qstack, _checks, _optstack = qstack, checks, optstack


def qstack(cid, s, e, *a, **k):
    NEUTRAL.append((s, e))          # side stacks: camera at 1.0 so the text never touches his head
    _qstack(cid, s, e, *a, **k)


def checks(cid, s, e, *a, **k):
    NEUTRAL.append((s, e))
    _checks(cid, s, e, *a, **k)


def optstack(cid, s, e, *a, **k):
    NEUTRAL.append((s, e))
    _optstack(cid, s, e, *a, **k)


# ================================================================ ABERTURA (cold open)
broll("soldador", T(5, -0.1), Z("renda", 30, 0.3), 1.0)
pills("ab1", T(5, -0.1), Z("renda", 30, 0.3), ["FORMAR MAIS PROFISSIONAIS", "AMPLIAR OPORTUNIDADES", "PRIMEIRO EMPREGO"],
      [A("formar", 5), A("ampliar", 10), A("primeiro", 17)])
pair("ab2", A("O", 49, -0.1), Z("profissional", 66, 0.4), "MAIS ESCOLAS TÉCNICAS?", "REPENSAR A ORGANIZAÇÃO?", A("mais", 52), A("repensar", 60))
beats("ab3", A("Vamos", 70, -0.1), Z("nisso", 71, 0.5), ["VAMOS PENSAR NISSO?"], [A("Vamos", 70)], size=150)

vs, ve = gap("VINHETA")
els.append(f'<video id="vin" class="clip vinv" src="assets/vinheta.mp4" playsinline data-has-audio="true" '
           f'data-start="{qd(vs)}" data-duration="{qd(ve - vs)}" data-track-index="4" data-volume="1.25"></video>')
lower_third("lt1", T(92, -0.1), T(92, 5.2), "Professor · Educador · Especialista em Educação")
seal_s = gap("I1")[1] + 0.3
clip("seal", seal_s, gap("TELA_FINAL")[0] - 0.4, '<div class="in"><div class="seal">EDUCAÇÃO PROFISSIONAL <b>·</b> NOVAS DIRETRIZES</div></div>', track=2, style="z-index:30")
tw("#seal > .in", "{opacity:0,x:30}", "{opacity:.6,x:0}", seal_s, 0.6)

for lab in INTERTITLES:
    intertitle(lab)

# ================================================================ antes da PARTE 1 · por que interessa
chain("b0a", A("E", 122, -0.1), Z("tecnológica", 133, 0.4), ["DIRETRIZES CURRICULARES NACIONAIS", "EDUCAÇÃO PROFISSIONAL E TECNOLÓGICA"],
      [A("diretrizes", 126), A("educação", 130)], label="O TEMA DE HOJE", size=40)
WHO_SW = A("interessa", 164, -0.1)
qstack("b0b", A("esse", 149, -0.1), WHO_SW, ["PROFESSORES", "ESPECIALISTAS", "DOUTORES E GESTORES", "ACADEMIA"],
       [A("professores", 154), A("especialistas", 157), A("doutores", 159), A("academia", 162)], side="right", title="NÃO INTERESSA SÓ A")
broll("oficina", WHO_SW, Z("profissional", 190, 0.3), 1.0)
optstack("b0c", WHO_SW, Z("profissional", 190, 0.3), ["FAMÍLIAS", "ESTUDANTES", "TRABALHADORES", "EMPRESÁRIOS", "MILHÕES DE BRASILEIROS"],
         [A("famílias", 168), A("estudantes", 170), A("trabalhadores", 173), A("empresários", 177), A("milhões", 180)], side="left", title="INTERESSA A")
pills("b0d", A("estamos", 202, -0.1), Z("futuro", 212, 0.5), ["EMPREGO", "RENDA", "PRODUTIVIDADE", "FUTURO"],
      [A("emprego", 206), A("renda", 208), A("produtividade", 210), A("futuro", 212)])

# ================================================================ PARTE 1 · AS NOVAS DIRETRIZES
ds, de = A("Em", 223, -0.2), Z("75", 261, 1.0)
panel("par", ds, de)
clip("parc", ds, de, '<div class="in"><div class="pc"><div class="kicker" style="position:static;margin-bottom:30px">CONSELHO NACIONAL DE EDUCAÇÃO</div>'
     '<div id="par-0" class="bebas" style="font-size:92px;line-height:.95">PARECER CNE/CP</div>'
     '<div id="par-1" class="bebas gold" style="font-size:170px;line-height:.9">Nº 21/2026</div>'
     '<div id="par-2" class="fact" style="margin-top:26px">aprovado em <b>outubro de 2026</b></div>'
     '<div id="par-3" class="fact" style="margin-top:14px;font-size:36px">novas <b class="gold">Diretrizes Curriculares Nacionais</b><br>da Educação Profissional e Tecnológica</div>'
     f'<div class="src">{UPDATE_NOTE}</div></div></div>', track=4)
life("parc", ds, de, 0.3, 0.25)
appear("#par-0", A("Conselho", 227), 0.35)
appear("#par-2", A("Conselho", 227, 0.3), 0.35)
appear("#par-3", A("diretrizes", 237), 0.4)
tw("#par-1", "{opacity:0,scale:1.2}", "{opacity:1,scale:1}", A("21", 249), 0.4, "expo.out")
sfx("pop", A("Conselho", 227), 0.3)
sfx("pop", A("21", 249), 0.35)
T2 = A("educação", 288, -0.1)
qstack("p1a", A("trata", 263, -0.1), T2, ["INTELIGÊNCIA ARTIFICIAL", "FORMAÇÃO AO LONGO DA VIDA", "CERTIFICAÇÕES INTERMEDIÁRIAS", "RECONHECER COMPETÊNCIAS"],
       [A("inteligência", 271), A("formação", 274), A("certificações", 283), A("reconhecimento", 285)], side="right", title="O QUE O TEXTO TRAZ")
qstack("p1b", T2, Z("trabalho", 311, 0.4), ["EAD E ENSINO HÍBRIDO", "ESTÁGIO", "FORMAÇÃO DE PROFESSORES", "ESCOLA + TRABALHO"],
       [A("educação", 288), A("estágio", 297), A("formação", 298), A("integração", 302)], side="left", title="E TAMBÉM")
stack2("p1c", A("Mas", 336, -0.1), Z("regulamentação", 350, 0.5), ["ESTAMOS MUDANDO A EDUCAÇÃO", f'OU SÓ A {G("REGULAMENTAÇÃO")}?'],
       [A("Estamos", 342), A("ou", 346)], size=104)
S1, S2 = A("Pode", 368, -0.05), A("Pode", 380, -0.05)
broll("salavazia", A("uma", 354, -0.1), S1, 1.0)
checks("p1d", A("uma", 354, -0.1), Z("exige", 396, 0.4), [("USA IA", True, A("usar", 357)), ("ENSINA DO MESMO JEITO", False, A("mesmo", 364)),
       ("EQUIPAMENTO EXCELENTE", True, A("equipamentos", 370)), ("RESULTADO FRACO", False, A("fracos", 377)),
       ("MILHARES DE VAGAS", True, A("milhares", 382)), ("POUCOS COM COMPETÊNCIA", False, A("poucos", 387))], side="left", title="UMA ESCOLA PODE")
pair("p1e", A("modernizar", 400, -0.1), Z("suficiente", 408, 0.5), "MODERNIZAR A NORMA", "NÃO É SUFICIENTE", A("modernizar", 400), A("mas", 406), mid="MAS")
checks("p1f", A("Não", 423, -0.1), Z("regulamentação", 466, 0.3), [("FUNDAMENTOS JURÍDICOS", True, A("fundamentos", 432)), ("EFEITOS PEDAGÓGICOS", True, A("consequências", 436)),
       ("FORMAÇÃO DOCENTE", True, A("formação", 443)), ("EAD E CERTIFICAÇÃO", True, A("regras", 447)), ("IMPACTOS ECONÔMICOS", True, A("impactos", 463))],
       side="right", title="O QUE A EQUIPE ESTUDOU")
optstack("p1g", A("Desse", 468, -0.1), Z("Educação", 514, 0.4), ["NOTA TÉCNICA", "ENSAIO CRÍTICO", "MEMORIAL TÉCNICO", "PROPOSTAS DE AJUSTE", "ESTUDO DE IMPACTO", "DOSSIÊ AO CNE E AO MEC"],
         [A("nota", 471), A("ensaio", 475), A("memorial", 478), A("propostas", 482), A("estudo", 491), A("dossiê", 500)], side="left", title="O QUE PRODUZIMOS", size=48)
stack2("p1h", A("Nosso", 521, -0.1), Z("técnica", 546, 0.4), ["NÃO É DESMERECER O TRABALHO", f'É {G("CONTRIBUIR")} COM O DEBATE'],
       [A("não", 523), A("oferecer", 539)], size=96)
beats("p1i", A("não", 554, -0.1), Z("profundas", 572, 0.4), ["NÃO SÓ NO PAPEL.", "NA REALIDADE."], [A("não", 554), A("realidade", 561)], size=150)

# ================================================================ PARTE 2 · UM PAÍS, MUITAS REALIDADES
M2 = A("O", 604, -0.1)
checks("p2a", A("primeiro", 586, -0.1), M2, [("ESCOLAS ESTRUTURADAS", True, A("escolas", 590)), ("LABORATÓRIOS", True, A("laboratórios", 592)),
       ("PROFESSORES ESPECIALISTAS", True, A("professores", 593)), ("EMPRESAS PARA A PRÁTICA", True, A("empresas", 596))], side="right", title="MUNICÍPIO GRANDE")
broll("cidadepequena", M2, A("Mas", 628, -0.1), 1.0)
qstack("p2b", M2, Z("menor", 664, 0.5), ["PEQUENO E DISTANTE", "JOVENS QUEREM ESTUDAR", "TRABALHADORES TAMBÉM", "EMPRESAS PRECISAM", "MENOS OPORTUNIDADES?"],
       [A("pequeno", 608), A("jovens", 631), A("trabalhadores", 636), A("empresas", 644), A("menos", 658)], side="left", title="MUNICÍPIO PEQUENO")
broll("onlineaula", A("existem", 678, -0.1), Z("professor", 711, 0.3), 0.5)
qstack("p2c", A("existem", 678, -0.1), Z("professor", 711, 0.3), ["SIMULADORES", "AMBIENTES VIRTUAIS", "LABORATÓRIOS REMOTOS", "AULAS AO VIVO", "APOIO AO PROFESSOR"],
       [A("simuladores", 695), A("ambientes", 696), A("laboratórios", 698), A("aulas", 700), A("recursos", 706)], side="right", title="A TECNOLOGIA LEVA LONGE")
broll("enfermagem", A("Há", 723, -0.1), Z("trabalho", 749, 0.3), 2.0)
checks("p2d", A("Mas", 713, -0.1), Z("trabalho", 749, 0.3), [("TUDO VIRTUAL", False, A("tudo", 718)), ("PRÁTICA PRESENCIAL", True, A("prática", 727)),
       ("LABORATÓRIO", True, A("procedimentos", 730)), ("SUPERVISÃO DIRETA", True, A("supervisão", 742)), ("AMBIENTE REAL", True, A("vivência", 745))], side="left")
pair("p2e", A("Então", 751, -0.1), Z("relevante", 777, 0.4), "PRESENCIAL", "DIGITAL", A("presencial", 758), A("digital", 761), mid="+", label="CADA UM NO LUGAR CERTO")
qstack("p2f", A("Um", 779, -0.1), Z("exclusiva", 829, 0.4), ["PROIBIR POLOS COMPARTILHADOS", "FISCALIZAÇÃO", "IDENTIDADE INSTITUCIONAL", "QUALIDADE", "TUDO PRECISA SER EXCLUSIVO?"],
       [A("proibir", 790), A("fiscalização", 810), A("identidade", 811), A("qualidade", 814), A("Toda", 824)], side="right", title="A PROPOSTA")
chain("p2g", A("Dois", 830, -0.1), A("Porque", 866, -0.15), ["DOIS PROJETOS AUTORIZADOS", "ESPAÇO FÍSICO COMUM", "RESPONSABILIDADES SEPARADAS"],
      [A("projetos", 831), A("espaços", 846), A("responsabilidades", 852)], label="E SE FOSSE ASSIM?", size=36)
broll("lab", A("Porque", 866, -0.1), Z("oportunidades", 888, 0.3), 2.0)
pills("p2h", A("Porque", 866, -0.1), Z("oportunidades", 888, 0.3), ["LABORATÓRIOS", "SALAS", "EQUIPAMENTOS", "CUSTA MUITO CARO"],
      [A("laboratórios", 870), A("salas", 871), A("equipamentos", 872), A("custa", 875)])
checks("p2i", A("compartilhar", 891, -0.1), Z("sustentabilidade", 927, 0.4), [("COMPARTILHAR CREDENCIAMENTO", False, A("credenciamento", 897)),
       ("TRANSFERIR RESPONSABILIDADE", False, A("transferir", 901)), ("DISPENSAR SEGURANÇA", False, A("dispensar", 907)),
       ("COOPERAR COM CRITÉRIO", True, A("cooperação", 918))], side="left", title="COMPARTILHAR ESPAÇO NÃO É")
stack2("p2j", A("Fazer", 937, -0.1), A("Significa", 946, -0.15), ["FAZER MAIS COM MENOS", G("NÃO É ENSINAR MENOS")], [A("Fazer", 937), A("não", 941)], size=120)
pills("p2k", A("Significa", 946, -0.1), Z("acontece", 960, 0.4), ["USAR MELHOR OS RECURSOS", "EVITAR DESPERDÍCIOS", "INVESTIR NA APRENDIZAGEM"],
      [A("usar", 947), A("evitar", 953), A("investir", 956)], size=36)

# ================================================================ PARTE 3 · O QUE O TRABALHADOR JÁ SABE
broll("torno", A("Imagine", 970, -0.1), A("Faz", 1001, -0.1), 3.0)
qstack("p3a", A("Imagine", 970, -0.1), A("Faz", 1001, -0.1), ["15 ANOS DE TRABALHO", "CONHECE OS EQUIPAMENTOS", "DOMINA OS PROCEDIMENTOS", "RESOLVE PROBLEMAS", "QUER VOLTAR A ESTUDAR"],
       [A("15", 975), A("conhece", 982), A("domina", 985), A("resolve", 988), A("decide", 997)], side="right", title="UM TRABALHADOR")
beats("p3b", A("Faz", 1001, -0.05), Z("não", 1018, 0.5), ["IGNORAR TUDO ISSO?", "CLARO QUE NÃO."], [A("ignorar", 1003), A("claro", 1016)], size=150)
broll("estudonoite", A("A", 1019, -0.1), Z("trabalho", 1033, 0.3), 1.0)
pills("p3c", A("A", 1019, -0.1), Z("detalhe", 1043, 0.4), ["A LEI JÁ PERMITE", "AVALIAR E APROVEITAR", "O QUE SE APRENDEU NO TRABALHO"],
      [A("permite", 1024), A("avaliar", 1025), A("inclusive", 1031)], size=36)
stack2("p3d", A("Reconhecer", 1067, -0.1), A("O", 1073, -0.15), ["RECONHECER COMPETÊNCIAS", G("NÃO É DISTRIBUIR DIPLOMAS")], [A("Reconhecer", 1067), A("não", 1069)], size=112)
checks("p3e", A("O", 1073, -0.1), Z("respeitadas", 1096, 0.5), [("CONHECIMENTO DEMONSTRADO", True, A("demonstrado", 1077)), ("AVALIAÇÃO SÉRIA", True, A("séria", 1082)),
       ("PROCESSO DOCUMENTADO", True, A("documentado", 1087)), ("EXIGÊNCIAS LEGAIS", True, A("exigências", 1090))], side="right", title="O QUE PRECISA EXISTIR")
pair("p3f", A("O", 1107, -0.1), Z("respeitada", 1127, 0.4), "DIPLOMA", "COMPETÊNCIA REAL", A("diploma", 1108), A("competências", 1111), mid="=")

# ================================================================ PARTE 4 · A IA E O PROFESSOR
IA1 = A("Ela", 1152, -0.1)
broll("robo", A("Existe", 1128, -0.1), IA1, 1.0)
beats("p4a", A("ideia", 1132, -0.1), IA1, ["“A IA RESOLVE SOZINHA.”", "NÃO VAI."], [A("resolver", 1142), A("não", 1150)], size=130)
checks("p4b", IA1, Z("professor", 1181, 0.5), [("OFERECER RECURSOS", True, A("recursos", 1158)), ("PLANEJAR AULAS", True, A("planejamento", 1161)),
       ("IDENTIFICAR DIFICULDADES", True, A("identificar", 1166)), ("NOVAS FORMAS DE APRENDER", True, A("novas", 1170)),
       ("SUBSTITUIR O PROFESSOR", False, A("substitui", 1177))], side="left", title="A IA PODE")
P2 = A("Por", 1214, -0.1)
qstack("p4c", A("O", 1192, -0.1), P2, ["DOMINAR O QUE ENSINA", "CONHECER A PROFISSÃO REAL", "TRANSFORMAR EM APRENDIZAGEM"],
       [A("dominar", 1195), A("conhecer", 1200), A("transformar", 1209)], side="right", title="O PROFESSOR PRECISA")
pair("p4d", P2, Z("juntas", 1229, 0.5), "FORMAÇÃO PEDAGÓGICA", "EXPERIÊNCIA PROFISSIONAL", A("formação", 1216), A("experiência", 1218), mid="+", label="PRECISAM CAMINHAR JUNTAS")
stack2("p4e", A("E", 1252, -0.1), Z("aula", 1272, 0.5), ["FORMAÇÃO CONTINUADA", "NÃO É COLEÇÃO DE CERTIFICADOS", G("É MUDANÇA NA SALA DE AULA")],
       [A("formação", 1254), A("coleção", 1261), A("mudança", 1267)], size=92)

# ================================================================ PARTE 5 · O QUE OS NÚMEROS NÃO MOSTRAM
ts, te = A("Quando", 1276, -0.2), Z("produtividade", 1326, 0.7)
panel("tk", ts, te)
QS = [("quantos <b>concluíram?</b>", A("concluíram", 1296)), ("quantos <b>aprenderam?</b>", A("aprenderam", 1298)), ("quantos <b>mostraram competência?</b>", A("demonstraram", 1300)),
      ("quantos <b>conquistaram oportunidades?</b>", A("conquistaram", 1308)), ("quantos <b>melhoraram de vida?</b>", A("melhoraram", 1313))]
clip("tkc", ts, te, '<div class="in"><div class="pc"><div class="kicker" style="position:static;margin-bottom:26px">UMA INSTITUIÇÃO ANUNCIA</div>'
     '<div id="tk-0" class="bebas gold" style="font-size:190px;line-height:.9"><span id="tk-n">0</span> MIL</div>'
     '<div id="tk-1" class="fact" style="margin-bottom:30px">estudantes matriculados</div>'
     '<div class="facts" style="margin-top:0;align-items:flex-start">'
     + "".join(f'<div id="tk-q{k}" class="fact" style="font-size:36px">{q_}</div>' for k, (q_, _) in enumerate(QS)) + "</div></div></div>", track=4)
life("tkc", ts, te, 0.3, 0.25)
appear("#tk-0", A("10", 1282, -0.1), 0.35)
count("#tk-n", 0, 10, A("10", 1282), 0.7)
appear("#tk-1", A("mil", 1283, 0.2), 0.35)
sfx("pop", A("10", 1282), 0.35)
for k, (_, t) in enumerate(QS):
    appear(f"#tk-q{k}", t, 0.35, 0, 30)
    sfx("tick", t, 0.4)
qstack("p5a", A("Brasil", 1337, -0.1), A("Mas", 1377, -0.1), ["CONDIÇÕES DE OFERTA", "APRENDIZAGEM", "PERMANÊNCIA", "CONCLUSÃO", "EGRESSOS NO TRABALHO"],
       [A("condições", 1355), A("aprendizagem", 1358), A("permanência", 1359), A("conclusão", 1360), A("inserção", 1362)], side="right", title="O SINAEPT AVALIA")
pair("p5b", A("Mas", 1377, -0.05), Z("revelam", 1399, 0.4), "PRODUZIR NÚMEROS", "INTERPRETAR", A("Não", 1389), A("interpretar", 1395), mid="→")
broll("bancada", A("Quanto", 1405, -0.1), A("Não", 1412, 3.2), 0.3)
optstack("p5c", A("Quanto", 1405, -0.1), Z("resultado", 1484, 0.4), ["NÃO É SÓ A MATRÍCULA", "É CONCLUIR E APRENDER", "NÃO O MAIS BARATO", "COM RESPONSABILIDADE", "INVESTIMENTO → RESULTADO"],
         [A("preço", 1417), A("investimento", 1424), A("barato", 1455, -0.6), A("responsabilidade", 1462), A("investimento", 1468)], side="left", title="QUANTO CUSTA FORMAR?", size=50)
checks("p5d", A("Foi", 1485, -0.1), Z("supervisão", 1561, 0.4), [("INFRAESTRUTURA COMPARTILHADA", True, A("uso", 1500)), ("EDUCAÇÃO COM TECNOLOGIA", True, A("precisão", 1509)),
       ("CERTIFICAÇÃO COM CRITÉRIO", True, A("critérios", 1518)), ("REGRAS DE ESTÁGIO", True, A("estágio", 1529)),
       ("AVALIAÇÃO POR RESULTADOS", True, A("avaliação", 1542)), ("DOCÊNCIA E GOVERNANÇA", True, A("formação", 1552))], side="right", title="NOSSAS CONTRIBUIÇÕES")
stack2("p5e", A("Porque", 1614, -0.1), Z("qualidade", 1634, 0.4), ["O DESAFIO NÃO É SÓ ESCREVER", f'É {G("IMPLEMENTAR")} COM QUALIDADE'], [A("desafio", 1617), A("criar", 1626)], size=100)

# ================================================================ PARTE 6 · IMAGINE ALGO DIFERENTE
broll("mecanica", A("Imagine", 1644, -0.1), Z("especializada", 1666, 0.2), 0.3)
pills("p6a", A("Imagine", 1644, -0.1), Z("especializada", 1666, 0.2), ["SOZINHA", "TODOS OS CONTEÚDOS", "TODAS AS TECNOLOGIAS", "TODA A ESTRUTURA"],
      [A("sozinha", 1650), A("conteúdos", 1652), A("tecnologias", 1657), A("estrutura", 1664)], size=36)
broll("obra", A("Imagine", 1667, 0.0), A("Imagine", 1678, 5.0), 0.5)
optstack("p6b", A("Imagine", 1667, 0.0), Z("alcançados", 1736, 0.4), ["INSTITUIÇÕES EM COOPERAÇÃO", "PROFESSOR + TECNOLOGIA", "PERCURSOS PROGRESSIVOS", "SETOR PRODUTIVO PRESENTE", "GESTOR OLHA RESULTADOS"],
         [A("instituições", 1668), A("professores", 1679), A("estudantes", 1692), A("setor", 1708), A("gestores", 1723)], side="left", title="AGORA IMAGINE", size=50)
pair("p6c", A("Isso", 1737, -0.1), Z("profissional", 1770, 0.4), "AINDA NÃO É REALIDADE", "É UMA POSSIBILIDADE", A("ainda", 1738), A("possibilidade", 1750), mid="MAS")
chain("p6d", A("Nesse", 1771, -0.1), Z("processo", 1798, 0.5), ["TECNOLOGIA = FERRAMENTA", "COOPERAÇÃO = INSTRUMENTO", "INSTITUIÇÃO RESPONSÁVEL", "ESTUDANTE NO CENTRO"],
      [A("tecnologia", 1774), A("cooperação", 1778), A("instituição", 1782), A("estudante", 1791)], label="NESSE MODELO", size=32)
broll("entrevista", A("Pense", 1838, -0.1), A("Pense", 1853, -0.1), 1.0)
broll("costura", A("Pense", 1853, -0.1), A("Pense", 1876, -0.1), 0.5)
pills("p6e", A("Pense", 1838, -0.1), A("Agora", 1889, -0.1), ["O JOVEM SEM O 1º EMPREGO", "A MÃE QUE PRECISA DE RENDA", "QUEM PAROU DE ESTUDAR"],
      [A("jovem", 1840), A("mãe", 1855), A("pessoa", 1878)], size=34)
beats("p6f", A("Oportunidade", 1904, -0.1), Z("tudo", 1906, 0.5), ["OPORTUNIDADE É TUDO."], [A("Oportunidade", 1904)], size=150)
qstack("p6g", A("Não", 1907, -0.1), Z("recomeço", 1929, 0.5), ["NÃO É SÓ UM CURSO", "FUTURO", "AUTONOMIA", "DIGNIDADE", "RECOMEÇO"],
       [A("curso", 1912, -0.4), A("futuro", 1921), A("autonomia", 1923), A("dignidade", 1925), A("recomeço", 1929)], side="right")
pair("p6h", A("A", 1940, 0.3), Z("geograficamente", 1968, 0.4), "RIGOROSA E CONFIÁVEL", "ACESSÍVEL E INCLUSIVA", A("rigorosa", 1945), A("acessível", 1955), mid="E")

# ================================================================ PARA FECHAR
pair("f1", A("perguntando", 1973, -0.1), Z("profissional", 1990, 0.4), "SÓ MAIS ESCOLAS TÉCNICAS?", "UMA NOVA ORGANIZAÇÃO?", A("apenas", 1978), A("Ou", 1983))
checks("f2", A("Não", 2002, -0.1), Z("trajetórias", 2046, 0.4), [("LEGISLAÇÃO ATUALIZADA", False, A("legislação", 2006)), ("FALAR DE IA", False, A("falar", 2010)),
       ("ANUNCIAR NOVAS VAGAS", False, A("anunciar", 2018)), ("MULTIPLICAR PLATAFORMAS", False, A("multiplicar", 2024)),
       ("MAIS GENTE APRENDENDO", True, A("mais", 2037))], side="left", title="NÃO BASTA")
qstack("f3", A("Precisamos", 2047, -0.1), Z("humana", 2062, 0.5), ["INOVAÇÃO + RESPONSABILIDADE", "QUALIDADE + ACESSO", "EXPANSÃO + SUSTENTABILIDADE", "TECNOLOGIA + VALOR HUMANO"],
       [A("inovação", 2049), A("qualidade", 2052), A("expansão", 2055), A("tecnologia", 2059)], side="right", title="CONCILIAR")
stack2("f4", A("Mas", 2073, -0.1), Z("reais", 2095, 0.4), ["NENHUMA RESOLUÇÃO TRANSFORMA SOZINHA", f'A NORMA PRECISA VIRAR {G("OPORTUNIDADE REAL")}'], [A("nenhuma", 2074), A("normas", 2090)], size=84)
checks("f5", A("Quando", 2096, -0.1), Z("sociedade", 2136, 0.4), [("PROFESSOR ENSINA MELHOR", True, A("professores", 2098)), ("ESTUDANTE APRENDE", True, A("estudantes", 2104)),
       ("FORMAÇÃO LIGADA AO TRABALHO", True, A("formação", 2109)), ("PAÍS MAIS PRODUTIVO", True, A("produtividade", 2119)),
       ("RESULTADO PARA AS PESSOAS", True, A("resultados", 2128))], side="right", title="A TRANSFORMAÇÃO ACONTECE")
F1 = A("Ela", 2167, -0.1)
pills("f6", A("número", 2156, -0.1), F1, ["ESCOLAS", "MATRÍCULAS", "DIPLOMAS"], [A("escolas", 2158), A("matrículas", 2161), A("diplomas", 2165)], label="NÃO SÓ PELO NÚMERO DE")
chain("f7", F1, Z("humano", 2184, 0.9), ["CONHECIMENTO", "COMPETÊNCIA", "OPORTUNIDADE", "DESENVOLVIMENTO HUMANO"],
      [A("conhecimento", 2174), A("competência", 2176), A("oportunidade", 2179), A("desenvolvimento", 2183)], label="A EDUCAÇÃO PROFISSIONAL DO FUTURO", size=38)
sfx("bell", A("desenvolvimento", 2183), 0.35)
lower_third("lt2", T(2209, -0.1), TE(2219, 0.6), "A Nova Ordem Educacional")
qstack("f8", A("participe", 2248, -0.1), Z("qualidade", 2274, 0.5), ["O QUE É INDISPENSÁVEL", "PARA CHEGAR A MAIS BRASILEIROS", "SEM PERDER A QUALIDADE?"],
       [A("O", 2257), A("chegue", 2266), A("sem", 2271)], side="right", title="COMENTE")

end_s, end_e = gap("TELA_FINAL")
tw("#cam", "{opacity:1}", "{opacity:0}", end_s - 0.9, 0.9, "power2.inOut")
js.append(f'tl.set("#cam",{{opacity:1}},{qd(TOTAL - 0.01)});')
clip("endsc", end_s, end_e, f'<div class="in full endbg"><div class="grid"></div>'
     f'<div class="endlogo" style="left:1355px;top:150px">{logo(0.36)}</div>'
     '<div class="kicker2" style="position:absolute;left:230px;top:248px">ASSISTA A SEGUIR →</div>'
     '<div class="slot" style="left:230px;top:300px;width:860px;height:484px"></div>'
     '<div class="slot round" style="left:1390px;top:392px;width:300px;height:300px"></div>'
     '<div class="kicker2" style="position:absolute;left:1290px;width:500px;top:722px;text-align:center">INSCREVA-SE NO CANAL</div>'
     '<div class="endq play" style="left:230px;bottom:auto;top:806px;font-size:48px">Educação é <em class="gold">estratégia.</em></div></div>', track=6)
life("endsc", end_s, end_e, 0.5, 0.01)
appear("#endsc .slot", end_s + 0.4, 0.6, 30)


def zoom_plan():
    """punch-in zoom per sentence, forced to 1.0 for the whole of every NEUTRAL window (side stacks next to his head)"""
    src = [s for s in SEGS if s["kind"] == "src"]
    words_out = json.load(open(EDIT / "words_out.json", encoding="utf8"))
    last_text = {}
    for w in words_out:
        last_text[w["seg"]] = w["text"]
    base, alt, prev = [], 0, None
    for s in src:
        new_sentence = prev is None or last_text.get(prev["i"], ".")[-1:] in ".?!:" or prev["label"] != s["label"]
        if new_sentence:
            alt ^= 1
        prev = s
        t = s["out"]
        close = next((c for a, b, c in CLOSE if a <= t + 0.05 < b), None)
        base.append((t, (close + (0.06 if alt else 0)) if close else (1.11 if alt else 1.0)))
    neutral = lambda t: any(a - 0.3 <= t < b + 0.4 for a, b in NEUTRAL)
    at = lambda t: next((z for tt, z in reversed(base) if tt <= t + 1e-6), 1.0)
    ev = [(t, 1.0 if neutral(t) else z) for t, z in base]
    for a, b in NEUTRAL:
        ev.append((a - 0.3, 1.0))
        if not neutral(b + 0.4 + 1e-3):
            ev.append((b + 0.4, at(b + 0.4)))
    for t, z in sorted(ev):
        js.append(f'tl.set("#zoom",{{scale:{z}}},{qd(max(t, 0))});')
