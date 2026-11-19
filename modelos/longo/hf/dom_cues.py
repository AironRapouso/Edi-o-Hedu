# DOM cues for EP6 — exec'd by build.py after the captions and the camera plan (helpers live there).


def lower_third(cid, s, e, role):
    clip(cid, s, e, f'<div class="in"><div id="{cid}-p" class="lt">{compass(78)}<div><div class="lt-n">HÉLIO LARANJEIRA</div>'
         f'<div class="lt-r">{role}</div><div id="{cid}-u" class="lt-u"></div></div></div></div>', z=10)
    tw(f"#{cid}-p", '{clipPath:"inset(0 100% 0 0)"}', '{clipPath:"inset(0 0% 0 0)"}', s, 0.7, "power3.inOut")
    tw(f"#{cid} .compass", "{rotation:-90}", "{rotation:0}", s, 0.9)
    tw(f"#{cid}-u", "{scaleX:0}", "{scaleX:1}", s + 0.45, 0.5, "power2.inOut")
    js.append(f'tl.to("#{cid}-p",{{opacity:0,duration:.3,ease:"power2.in"}},{q(e - 0.3)});')
    sfx(s, "whoosh_s", -20, -0.6, "lower third")


lower_third("lt1", T(92, -0.1), TE(100, 0.3), "Professor · Educador · Especialista em Educação")
lower_third("lt2", T(2209, -0.1), TE(2219, 0.4), "A Nova Ordem Educacional")

# ---------------------------------------------------------------- vinheta (the channel intro, with its own audio)
vs, ve = gap("VINHETA")
els.append(f'<video id="vin" class="clip vinv" src="assets/vinheta.mp4" playsinline data-has-audio="true" '
           f'data-start="{q(vs)}" data-duration="{q(ve - vs)}" data-track-index="2" data-volume="1.0"></video>')

# ---------------------------------------------------------------- update note (the parecer was homologated after the recording)
ch = next(s for s in SCENES if s["id"] == "parecer")
clip("src1", ch["t0"] + 0.3, ch["t1"], f'<div class="in"><div class="foot" id="srcf">{UPDATE_NOTE}</div></div>', z=6)
tw("#srcf", "{opacity:0}", "{opacity:1}", ch["t0"] + 0.4, 0.4, "power2.out")

# ---------------------------------------------------------------- CTA comment card (in the side panel)
TYPED = "PROFESSOR BEM FORMADO…"
typed_html = "".join(f'<span class="ch" id="ty{k}">{c if c != " " else "&nbsp;"}</span>' for k, c in enumerate(TYPED))
clip("ctac", CTA0, CTA1, f'<div class="in"><div class="card cta" id="cta"><div class="who"><div class="av">{compass(64)}</div>'
     '<div class="nm">A Nova Ordem<br>Educacional</div></div>'
     '<div class="ask mono"><svg width="34" height="34" viewBox="0 0 34 34"><path d="M4 6h26v18H15l-8 7v-7H4Z" fill="#0457E7"/></svg>COMENTE AQUI</div>'
     '<div class="qq play">O que é <b>indispensável</b> para a educação profissional chegar a mais brasileiros <b>sem perder a qualidade?</b></div>'
     f'<div class="field" id="field"><span class="ph" id="ph">Adicione um comentário…</span><span class="tx">{typed_html}<span class="cur" id="cur"></span></span>'
     '<div class="send" id="send"><svg width="36" height="36" viewBox="0 0 34 34"><path d="M17 28V7M7 16 17 6l10 10" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg></div></div>'
     '<div class="likes"><span>Curtir</span><span>Compartilhar</span></div></div></div>', z=6)
tw("#cta", "{opacity:0,x:80,scale:.94}", "{opacity:1,x:0,scale:1}", CTA0 + 0.2, 0.4, "back.out(1.5)")
sfx(CTA0 + 0.2, "pop", -18, 0.5, "comment card")
t0, t1 = A("O", 2257), CTA1 - 0.6
setp("#cur", "{opacity:0}", 0)
setp("#ph", "{opacity:0}", t0)
setp("#cur", "{opacity:1}", t0)
for k in range(len(TYPED)):
    tt = t0 + (t1 - t0) * k / len(TYPED)
    setp(f"#ty{k}", "{display:'inline'}", tt)
    if TYPED[k] != " ":
        sfx(tt, "type", -25, 0.5, "typing")
js.append(f'tl.to("#field",{{borderColor:"#F4B04A",backgroundColor:"#FFF6E3",duration:.2}},{q(t1 + 0.05)});')
tw("#send", "{scale:1}", "{scale:1.25}", t1 + 0.05, 0.12, "power2.out")
sfx(t1 + 0.05, "chime", -20, 0.5, "comment ready")

# ---------------------------------------------------------------- end screen (2 YouTube targets, standard layout)
end_s, end_e = gap("TELA_FINAL")


def logo(scale=1.0):
    s = scale
    return (f'<div class="logo" style="gap:{int(34*s)}px">{compass(int(190*s))}'
            f'<div class="logo-t"><div style="font-size:{int(92*s)}px;line-height:.95">A NOVA</div>'
            f'<div style="font-size:{int(92*s)}px;line-height:.95;color:#5CA2EE">ORDEM</div>'
            f'<div style="font-size:{int(52*s)}px;font-weight:400;letter-spacing:.02em">EDUCACIONAL</div></div></div>')


clip("endsc", end_s, end_e, f'<div class="in"><div class="endbg"><div class="grid"></div>'
     f'<div style="position:absolute;left:1355px;top:150px">{logo(0.36)}</div>'
     '<div class="kicker2" style="position:absolute;left:230px;top:248px">ASSISTA A SEGUIR →</div>'
     '<div class="slot" style="left:230px;top:300px;width:860px;height:484px"></div>'
     '<div class="slot round" style="left:1390px;top:392px;width:300px;height:300px"></div>'
     '<div class="kicker2" style="position:absolute;left:1290px;width:500px;top:722px;text-align:center">INSCREVA-SE NO CANAL</div>'
     '<div class="endq play" style="left:230px;top:806px">Educação é <span class="g">estratégia.</span></div></div></div>', z=30)
tw("#endsc > .in", "{opacity:0}", "{opacity:1}", end_s, 0.5, "power2.out")
tw("#endsc .slot", "{opacity:0,y:30}", "{opacity:1,y:0}", end_s + 0.4, 0.6)
sfx(end_s, "whoosh", -18, 0, "end screen")
