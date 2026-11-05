"""Genera el index.html de HyperFrames a partir del plan de escenas.

Lienzo 1080×1920. Zona segura de anuncios en Reels: x 65–1015, y 269–1248.
Gráficos en y 280–690, persona en panel abierto (×0,9) en y 700–1866.
"""
import html

PANEL_TOP, PANEL_MARGEN, PANEL_ESCALA = 700, 54, 0.9
CAP_Y = 1120

ICONOS = {
    "documento": '<rect x="26" y="14" width="68" height="92" rx="8" fill="none" stroke="#fff" stroke-width="5"/><path d="M40 40H80M40 58H80M40 76H66" stroke="#fff" stroke-width="5" stroke-linecap="round"/>',
    "camara": '<rect x="14" y="34" width="66" height="56" rx="10" fill="none" stroke="#fff" stroke-width="5"/><path d="M84 54 L108 40 V84 L84 70Z" fill="#fff"/>',
    "diana": '<circle cx="60" cy="60" r="44" fill="none" stroke="#fff" stroke-width="5"/><circle cx="60" cy="60" r="24" fill="none" stroke="#fff" stroke-width="5"/><circle cx="60" cy="60" r="8" fill="var(--acento)"/>',
    "chat": '<path d="M16 24H104V84H52L28 104V84H16Z" fill="none" stroke="#fff" stroke-width="5" stroke-linejoin="round"/>',
    "grafico": '<path d="M18 104H106" stroke="#fff" stroke-width="5" stroke-linecap="round"/><rect x="26" y="66" width="18" height="30" fill="#fff"/><rect x="54" y="44" width="18" height="52" fill="#fff"/><rect x="82" y="18" width="18" height="78" fill="var(--acento)"/>',
    "persona": '<circle cx="60" cy="40" r="24" fill="#fff"/><path d="M16 108C16 70 104 70 104 108Z" fill="#fff"/>',
    "check": '<circle cx="60" cy="60" r="44" fill="none" stroke="#fff" stroke-width="5"/><path d="M38 62L54 78L84 44" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>',
}
ONDA = "M60 330 C130 330 150 90 230 90 S330 400 400 380 S500 40 590 70 S690 410 770 400 S850 240 900 280 S980 470 1020 470"
E = 'ease:"power3.out"'


def esc(t):
    return html.escape(str(t))


def _titulo(pid, esc_d, js):
    a, b = esc_d.get("linea1", ""), esc_d.get("linea2", "")
    ta, tb = esc_d["_t1"], esc_d["_t2"]
    wa = "".join(f'<span class="tw">{esc(x)}</span> ' for x in a.split())
    wb = "".join(f'<span class="tw">{esc(x)}</span> ' for x in b.split())
    h = f'<div class="title"><div class="t1" id="{pid}a">{wa}</div>'
    if wa:
        js.append(f'tl.from("#{pid}a .tw",{{opacity:0,y:10,filter:"blur(10px)",duration:.3,stagger:.05,{E}}},{ta:.3f});')
    if wb:
        fs = 84 if len(b) <= 26 else max(54, int(84 * 26 / len(b)))
        h += f'<div class="t2" id="{pid}b" style="font-size:{fs}px">{wb}<i class="ul" id="{pid}u"></i></div>'
        js.append(f'tl.from("#{pid}b .tw",{{opacity:0,y:12,filter:"blur(12px)",duration:.34,stagger:.07,{E}}},{tb:.3f});')
        js.append(f'tl.from("#{pid}u",{{scaleX:0,duration:.45,ease:"power2.inOut"}},{tb + .22:.3f});')
    return h + "</div>"


def _chip(cid, texto, top, t, js, extra=""):
    js.append(f'tl.from("#{cid}",{{opacity:0,y:14,duration:.28,{E}}},{t:.3f});')
    return f'<div class="chip" id="{cid}" style="{extra or "left:0;right:0;margin:auto;width:max-content"};top:{top}px">{esc(texto)}</div>'


def _onda(s, pid, js):
    h = _titulo(pid, s, js)
    chips = s.get("chips", [])[:2]
    lados = ["left:110px", "right:110px"]
    for i, c in enumerate(chips):
        h += _chip(f"{pid}c{i}", c["texto"], 428, c["_t"], js, lados[i])
    h += (f'<svg class="abs" style="left:65px;top:495px" width="950" height="190" viewBox="0 0 1080 500" preserveAspectRatio="none">'
          f'<line x1="60" y1="480" x2="1020" y2="480" class="axis" vector-effect="non-scaling-stroke"/>'
          f'<path id="{pid}p" d="{ONDA}" pathLength="1" fill="none" stroke="var(--acento)" stroke-width="7" stroke-linecap="round" '
          f'vector-effect="non-scaling-stroke" stroke-dasharray="1" stroke-dashoffset="1"/></svg>'
          f'<div id="{pid}d" class="abs" style="left:950px;top:662px;width:24px;height:24px;border-radius:50%;background:var(--acento)"></div>')
    t0, t1 = s["_trazo"]
    js.append(f'gsap.set("#{pid}p",{{opacity:0}});tl.set("#{pid}p",{{opacity:1}},{t0:.3f});'
              f'tl.to("#{pid}p",{{strokeDashoffset:0,duration:{t1 - t0:.3f},ease:"none"}},{t0:.3f});'
              f'tl.from("#{pid}d",{{opacity:0,scale:0,duration:.2,{E}}},{t1 - .05:.3f});')
    return h


def _barras(s, pid, js):
    h = _titulo(pid, s, js)
    barras = s.get("barras", [])[:3]
    alto = 72 if len(barras) <= 2 else 54
    paso = 106 if len(barras) <= 2 else 72
    for i, b in enumerate(barras):
        top = 468 + i * paso
        ancho = max(50, int(770 * max(0.02, min(1.0, float(b.get("valor", 1))))))
        color = "var(--acento)" if b.get("acento") else "#fff"
        h += (f'<div class="lab" id="{pid}l{i}" style="left:65px;width:150px;top:{top + alto // 2 - 20}px">{esc(b["etiqueta"])}</div>'
              f'<div class="bar" id="{pid}b{i}" style="left:225px;top:{top}px;width:{ancho}px;height:{alto}px;background:{color}"></div>')
        js.append(f'tl.from("#{pid}l{i}",{{opacity:0,duration:.2}},{b["_t"] - .05:.3f});'
                  f'tl.from("#{pid}b{i}",{{scaleX:0,transformOrigin:"left center",duration:.5,{E}}},{b["_t"]:.3f});')
    return h


def _secuencia(s, pid, js):
    h = _titulo(pid, s, js)
    items = [str(x) for x in s.get("items", [])][:7]
    n = len(items)
    tam = 96
    sep = 120 if n >= 6 else 150
    x0 = (1080 - ((n - 1) * sep + tam)) // 2
    js.append(f'tl.from("#{pid} .day",{{opacity:0,duration:.25}},{s["_t0"] + .25:.3f});')
    for i, it in enumerate(items):
        h += f'<div class="day" id="{pid}i{i}" style="left:{x0 + i * sep}px"><span>{esc(it)}</span></div>'
        js.append(f'tl.to("#{pid}i{i}",{{backgroundColor:"{s["_acento"]}",borderColor:"{s["_acento"]}",duration:.1}},{s["_ti"] + i * 0.1:.3f});')
    np = int(s.get("personas", 0) or 0)
    for c in range(min(np, 8)):
        x = (1080 - (min(np, 8) * 108 - 20)) // 2 + c * 108
        h += (f'<svg class="abs" id="{pid}p{c}" style="left:{x}px;top:572px" width="88" height="96" viewBox="0 0 110 120">'
              f'<circle cx="55" cy="36" r="26" fill="#A1A1AA"/><path d="M10 116 C10 80 100 80 100 116Z" fill="#A1A1AA"/></svg>')
        js.append(f'tl.from("#{pid}p{c}",{{opacity:0,y:14,duration:.2,{E}}},{s["_tp"] + c * 0.08:.3f});')
    return h


def _pasos(s, pid, js):
    h = _titulo(pid, s, js)
    pasos = s.get("pasos", [])[:4]
    n = max(1, len(pasos))
    hueco = 28
    ancho = (950 - hueco * (n - 1)) // n
    fs = 36 if n <= 3 else 30
    for i, p in enumerate(pasos):
        x = 65 + i * (ancho + hueco)
        ico = ICONOS.get(p.get("icono"), ICONOS["check"])
        h += (f'<div class="card" id="{pid}k{i}" style="left:{x}px;width:{ancho}px"><svg width="76" height="76" viewBox="0 0 120 120">{ico}</svg>'
              f'<div class="cl" style="font-size:{fs}px">{esc(p["texto"])}</div><div class="ok" id="{pid}o{i}">✓</div></div>')
        js.append(f'tl.from("#{pid}k{i}",{{opacity:0,y:22,duration:.32,{E}}},{p["_t"]:.3f});'
                  f'tl.from("#{pid}o{i}",{{opacity:0,scale:.3,duration:.2,{E}}},{p["_t"] + .2:.3f});')
    if s.get("nota"):
        h += _chip(f"{pid}n", s["nota"]["texto"], 626, s["nota"]["_t"], js, "left:0;right:0;margin:auto;width:max-content;padding:8px 24px")
    return h


def _cifra(s, pid, js):
    h = ""
    if s.get("etiqueta"):
        h += _chip(f"{pid}c", s["etiqueta"], 278, s["_t0"] + .03, js, "left:0;right:0;margin:auto;width:max-content;padding:8px 24px")
    if s.get("antes"):
        h += f'<div class="big1" id="{pid}m1" style="top:346px">{esc(s["antes"])}</div>'
        js.append(f'tl.from("#{pid}m1",{{opacity:0,y:12,filter:"blur(8px)",duration:.24,{E}}},{s["_t_antes"]:.3f});')
    cifra = str(s["cifra"])
    fs = 196 if len(cifra) <= 7 else max(110, int(196 * 7 / len(cifra)))
    h += f'<div class="num" id="{pid}num" style="font-size:{fs}px">{esc(cifra)}</div>'
    js.append(f'tl.from("#{pid}num",{{opacity:0,scale:.86,filter:"blur(16px)",duration:.42,{E}}},{s["_t_cifra"]:.3f});')
    if s.get("despues"):
        h += f'<div class="big1" id="{pid}m2" style="top:622px">{esc(s["despues"])}</div>'
        js.append(f'tl.from("#{pid}m2",{{opacity:0,y:12,filter:"blur(8px)",duration:.24,{E}}},{s["_t_despues"]:.3f});')
    return h


def _cta(s, pid, js):
    h = f'<div class="big2" id="{pid}e1" style="top:276px">{esc(s.get("linea1", ""))}</div>'
    js.append(f'tl.from("#{pid}e1",{{opacity:0,y:12,filter:"blur(8px)",duration:.24,{E}}},{s["_t0"] + .06:.3f});')
    et = str(s.get("etiqueta", "")).upper()
    fs = 124 if len(et) <= 8 else max(64, int(124 * 8 / len(et)))
    h += f'<div class="tag" id="{pid}e2" style="font-size:{fs}px">{esc(et)}</div>'
    js.append(f'tl.from("#{pid}e2",{{opacity:0,scale:.82,duration:.3,{E}}},{s["_t_etiqueta"]:.3f});')
    if s.get("linea2"):
        h += f'<div class="big2" id="{pid}e3" style="top:530px">{esc(s["linea2"])}</div>'
        js.append(f'tl.from("#{pid}e3",{{opacity:0,y:12,filter:"blur(8px)",duration:.24,{E}}},{s["_t_linea2"]:.3f});')
    if s.get("nota"):
        h += _chip(f"{pid}n", s["nota"]["texto"], 626, s["nota"]["_t"], js, "left:0;right:0;margin:auto;width:max-content;padding:8px 24px")
    return h


def _solo_titulo(s, pid, js):
    h = _titulo(pid, s, js)
    return h


RENDER = {"onda": _onda, "barras": _barras, "secuencia": _secuencia, "pasos": _pasos,
          "cifra": _cifra, "cta": _cta, "titulo": _solo_titulo}


def css(est):
    return f"""
:root{{--acento:{est['acento']}}}
@font-face{{font-family:'Inter Tight';font-weight:700;src:url(assets/fonts/inter-tight-latin-700-normal.woff2)}}
@font-face{{font-family:'Inter Tight';font-weight:800;src:url(assets/fonts/inter-tight-latin-800-normal.woff2)}}
@font-face{{font-family:'Instrument Serif';font-style:italic;src:url(assets/fonts/instrument-serif-latin-400-italic.woff2)}}
@font-face{{font-family:'JetBrains Mono';font-weight:500;src:url(assets/fonts/jetbrains-mono-latin-500-normal.woff2)}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:{est['fondo']}}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:{est['fondo']};font-family:'Inter Tight',sans-serif;color:{est['texto']}}}
#bg{{position:absolute;inset:0;background:radial-gradient(circle at 50% 24%,{est['acento']}33,{est['acento']}00 52%),radial-gradient(rgba(255,255,255,.07) 1.5px,transparent 1.6px);background-size:100% 100%,36px 36px}}
#cam{{position:absolute;inset:0;z-index:6;overflow:hidden}}
#camIn{{position:absolute;left:0;top:0;width:1080px;height:1920px}}
#camIn video{{width:1080px;height:1920px;display:block}}
.scene{{position:absolute;inset:0;z-index:4}}
.abs{{position:absolute}}
.axis{{stroke:{est['borde']};stroke-width:3}}
.title{{position:absolute;left:0;right:0;top:280px;text-align:center}}
.t1{{font-size:46px;font-weight:700;letter-spacing:-.02em;line-height:1.1}}
.t2{{position:relative;display:table;margin:2px auto 0;font-family:'Instrument Serif',serif;font-style:italic;font-size:84px;line-height:1.06;letter-spacing:-.01em}}
.tw{{display:inline-block}}
.t2 .tw{{margin-right:.2em}}
.t2 .tw:last-of-type{{margin-right:0}}
.ul{{position:absolute;left:0;right:0;bottom:2px;height:6px;background:var(--acento);border-radius:3px;transform-origin:left center}}
.chip{{position:absolute;padding:14px 28px;border:2px solid {est['borde']};background:{est['superficie']};border-radius:16px;font:500 32px 'JetBrains Mono',monospace;color:{est['texto']};white-space:nowrap}}
.bar{{position:absolute;border-radius:6px 14px 14px 6px}}
.lab{{position:absolute;text-align:center;font:500 30px 'JetBrains Mono',monospace;color:{est['secundario']}}}
.day{{position:absolute;top:446px;width:96px;height:96px;border-radius:50%;border:3px solid {est['borde']};background:{est['superficie']};display:flex;align-items:center;justify-content:center;font:500 34px 'JetBrains Mono',monospace}}
.card{{position:absolute;top:436px;height:182px;background:{est['superficie']};border:2px solid {est['borde']};border-radius:24px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;text-align:center}}
.cl{{font-weight:700;letter-spacing:-.02em}}
.ok{{position:absolute;top:10px;right:10px;width:38px;height:38px;border-radius:50%;background:{est['positivo']};color:#051;display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:800}}
.big1{{position:absolute;left:0;right:0;text-align:center;font-size:50px;font-weight:700;letter-spacing:-.02em}}
.big2{{position:absolute;left:0;right:0;text-align:center;font-size:68px;font-weight:700;letter-spacing:-.02em}}
.num{{position:absolute;left:0;right:0;top:398px;text-align:center;line-height:1.1;font-weight:800;letter-spacing:-.03em;color:{est['brillo']};text-shadow:0 0 56px {est['brillo']}8c}}
.tag{{position:absolute;left:0;right:0;top:362px;margin:auto;width:max-content;padding:6px 48px;background:var(--acento);border-radius:20px;line-height:1.1;font-weight:800;letter-spacing:-.02em}}
.cap{{position:absolute;z-index:10;left:0;right:0;text-align:center;font-size:68px;font-weight:700;letter-spacing:-.02em;line-height:1.12;padding:26px 90px;background:radial-gradient(closest-side,rgba(0,0,0,.62),rgba(0,0,0,0))}}
.cap .w{{display:inline-block}}
.cap .k{{color:{est['acento_texto']}}}
"""


def _subtitulos(grupos, D, cap_full_y, es_persona):
    h, js = [], []
    for i, g in enumerate(grupos):
        s = max(0.0, g[0]["s"] - 0.03)
        sig = grupos[i + 1][0]["s"] - 0.03 if i + 1 < len(grupos) else D
        e = min(sig, max(g[-1]["e"] + 0.25, s + 0.3))
        txt = " ".join(f'<span class="w{" k" if w.get("k") else ""}">{esc(w["t"])}</span>' for w in g)
        y = cap_full_y if es_persona(s + 0.05) else CAP_Y
        h.append(f'<div id="c{i}" class="clip cap" data-start="{s:.3f}" data-duration="{e - s:.3f}" data-track-index="20" style="top:{y}px">{txt}</div>')
        js.append(f'tl.from("#c{i} .w",{{opacity:0,y:12,filter:"blur(8px)",duration:.16,stagger:.02,{E}}},{s:.3f});')
    return h, js


def generar(escenas, grupos, D, est, y0_panel, cap_full_y):
    """escenas: con _t0/_t_fin y tiempos resueltos. y0_panel: fila del video bajo el borde del panel."""
    js, html_esc = [], []
    tramos_persona = [(s["_t0"], s["_t_fin"]) for s in escenas if s["tipo"] == "persona"]
    for i, s in enumerate(escenas):
        if s["tipo"] == "persona":
            continue
        pid = f"s{i}"
        s["_acento"] = est["acento"]
        cuerpo = RENDER[s["tipo"]](s, pid, js)
        html_esc.append(f'<div id="{pid}" class="clip scene" data-start="{s["_t0"]:.3f}" data-duration="{s["_t_fin"] - s["_t0"]:.3f}" data-track-index="5">{cuerpo}</div>')
        if s["_t0"] > 0.01:
            js.append(f'tl.from("#{pid}",{{opacity:0,duration:.14}},{s["_t0"]:.3f});')
        if s["_t_fin"] < D - 0.01:
            js.append(f'tl.to("#{pid}",{{opacity:0,duration:.16,ease:"power2.in"}},{s["_t_fin"] - .18:.3f});')

    panel = f"inset({PANEL_TOP}px {PANEL_MARGEN}px {PANEL_MARGEN}px {PANEL_MARGEN}px round 36px)"
    py = PANEL_TOP - PANEL_ESCALA * y0_panel
    cam = []
    empieza_persona = bool(tramos_persona) and tramos_persona[0][0] < 0.01
    if empieza_persona:
        cam.append('gsap.set("#cam",{clipPath:"inset(0px 0px 0px 0px round 0px)"});gsap.set("#camIn",{scale:1,x:0,y:0,transformOrigin:"0 0"});')
    else:
        cam.append(f'gsap.set("#cam",{{clipPath:"{panel}"}});gsap.set("#camIn",{{scale:{PANEL_ESCALA},x:{PANEL_MARGEN},y:{py},transformOrigin:"0 0"}});')
    for a, b in tramos_persona:
        if a > 0.01:
            cam.append(f'tl.to("#cam",{{clipPath:"inset(0px 0px 0px 0px round 0px)",duration:.34,ease:"power3.inOut"}},{a - .1:.3f});')
            cam.append(f'tl.to("#camIn",{{scale:1,x:0,y:0,duration:.34,ease:"power3.inOut"}},{a - .1:.3f});')
        if b < D - 0.01:
            cam.append(f'tl.to("#cam",{{clipPath:"{panel}",duration:.34,ease:"power3.inOut"}},{b - .12:.3f});')
            cam.append(f'tl.to("#camIn",{{scale:{PANEL_ESCALA},x:{PANEL_MARGEN},y:{py},duration:.34,ease:"power3.inOut"}},{b - .12:.3f});')

    def es_persona(t):
        return any(a <= t < b for a, b in tramos_persona)

    cap_h, cap_js = _subtitulos(grupos, D, cap_full_y, es_persona)
    nl = "\n"
    return f'''<!doctype html>
<html lang="es"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/vendor/gsap.min.js"></script>
<style>{css(est)}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="1080" data-height="1920">
<div id="bg"></div>
{nl.join(html_esc)}
<div id="cam" data-layout-allow-overlap><div id="camIn"><video id="v" class="clip" data-start="0" data-duration="{D}" data-track-index="0" src="assets/video.mp4" muted playsinline></video></div></div>
<div id="caps" data-track-kind="captions">
{nl.join(cap_h)}
</div>
</div>
<script>
window.__timelines=window.__timelines||{{}};
const tl=gsap.timeline({{paused:true}});
{nl.join(cam)}
{nl.join(js)}
{nl.join(cap_js)}
tl.set({{}},{{}},{D});
window.__timelines["main"]=tl;
</script></body></html>
'''
