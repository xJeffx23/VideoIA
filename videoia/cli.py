#!/usr/bin/env python3
"""VideoIA: del video crudo al anuncio vertical con un solo comando."""
import argparse
import datetime
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import composicion  # noqa: E402

RAIZ = os.environ.get("VIDEOIA_RAIZ") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROYECTO = os.path.abspath(os.environ.get("VIDEOIA_PROYECTO") or RAIZ)
REELS = os.path.join(RAIZ, ".claude/skills/it-reelsmaker/scripts")
HF = ["npx", "--yes", "hyperframes@0.9.14"]
PY = sys.executable
ENV = dict(os.environ, HYPERFRAMES_NO_TELEMETRY="1", DO_NOT_TRACK="1")
EXT = (".mov", ".mp4", ".m4v", ".mkv", ".webm")
FUNC = {"o", "y", "de", "no", "un", "una", "lo", "los", "la", "el", "a", "al", "en", "su", "sus", "se", "le", "que", "si", "e", "u", "del", "con", "por", "para", "mi", "tu"}


class Error(Exception):
    pass


def ruta(*p):
    return os.path.join(PROYECTO, *p)


def paso(txt):
    print(f"\n▸ {txt}", flush=True)


def correr(cmd, cwd=None, salida=False):
    r = subprocess.run(cmd, cwd=cwd, env=ENV, capture_output=True, text=True)
    if r.returncode != 0:
        err = "\n".join(l for l in (r.stderr + r.stdout).splitlines() if "objc[" not in l)
        raise Error(f"Falló: {os.path.basename(cmd[0])} {' '.join(cmd[1:3])}\n{err[-1800:]}")
    return r.stdout if salida else None


def reels(script, *args, cwd):
    return correr([PY, os.path.join(REELS, script), *map(str, args)], cwd=cwd, salida=True)


def ffprobe_json(f):
    return json.loads(correr(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                              "stream=width,height:stream_side_data=rotation:format=duration", "-of", "json", f], salida=True))


def slug(nombre):
    s = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower() or "video"


def buscar_crudo(elegido):
    if elegido:
        if not os.path.isfile(elegido):
            elegido = ruta("Material-Crudo", elegido)
        if not os.path.isfile(elegido):
            raise Error(f"No encuentro el video: {elegido}")
        return os.path.abspath(elegido)
    videos = [f for f in glob.glob(ruta("Material-Crudo", "*")) if f.lower().endswith(EXT)]
    if not videos:
        raise Error("No hay videos en Material-Crudo/. Pon ahí tu video crudo y vuelve a ejecutar videoia.")
    videos.sort(key=os.path.getmtime, reverse=True)
    if len(videos) > 1:
        print(f"Hay {len(videos)} videos; uso el más reciente: {os.path.basename(videos[0])}")
        print("Para elegir otro: videoia --video <archivo>")
    return videos[0]


def normalizar(crudo, trabajo):
    """Deja una copia 1080×1920. Si el formato ya es correcto, usa el original."""
    info = ffprobe_json(crudo)
    st = info["streams"][0]
    w, h = st["width"], st["height"]
    rot = 0
    for sd in st.get("side_data_list", []) or []:
        rot = abs(int(sd.get("rotation", 0)))
    if rot in (90, 270):
        w, h = h, w
    if (w, h) == (1080, 1920):
        return crudo
    salida = os.path.join(trabajo, "fuente.mp4")
    if not os.path.exists(salida) or os.path.getmtime(salida) < os.path.getmtime(crudo):
        if abs(w / h - 9 / 16) > 0.01:
            print(f"Aviso: el video es {w}×{h}; lo recorto al centro para llegar a 9:16 y puede perder parte del encuadre.")
        vf = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920"
        correr(["ffmpeg", "-v", "error", "-y", "-i", crudo, "-vf", vf, "-c:v", "libx264", "-crf", "16", "-preset", "medium",
                "-c:a", "aac", "-b:a", "256k", salida])
    return salida


# ---------- plan ----------

def palabras_fuente(trabajo, stem):
    d = json.load(open(os.path.join(trabajo, "edit/video/transcripts", stem + ".json")))
    return [w for w in d["words"] if w.get("type", "word") == "word"]


def plan_con_ia(palabras, guia, modelo):
    plantilla = open(os.path.join(RAIZ, "videoia/prompt_plan.md"), encoding="utf-8").read()
    tabla = "\n".join(f'{i}\t{w["start"]:.2f}\t{w["text"].strip()}' for i, w in enumerate(palabras))
    prompt = plantilla.replace("{{GUIA}}", guia).replace("{{PALABRAS}}", tabla)
    ultimo = ""
    for intento in range(2):
        texto = prompt if not ultimo else prompt + f"\n\nTu respuesta anterior tenía este problema: {ultimo}\nCorrígelo y responde solo con el JSON."
        cmd = ["claude", "-p", "--output-format", "text", "--tools", "", "--no-session-persistence"]
        if modelo:
            cmd += ["--model", modelo]
        r = subprocess.run(cmd, input=texto, capture_output=True, text=True, cwd=os.path.dirname(RAIZ))
        if r.returncode != 0:
            raise Error("Claude no respondió: " + (r.stderr or r.stdout)[-500:])
        m = re.search(r"\{.*\}", r.stdout, re.S)
        try:
            plan = json.loads(m.group(0) if m else r.stdout)
            validar_plan(plan, palabras)
            return plan
        except (ValueError, KeyError, TypeError, Error) as e:
            ultimo = str(e)
    raise Error(f"El plan de Claude no fue válido: {ultimo}")


def plan_basico(palabras):
    """Sin Claude: títulos con las propias frases, cifras detectadas y cierre con la última frase."""
    frases, ini = [], 0
    for i, w in enumerate(palabras):
        if w["text"].strip()[-1:] in ".?!" or i == len(palabras) - 1:
            frases.append((ini, i))
            ini = i + 1
    escenas = []
    for n, (a, b) in enumerate(frases):
        txt = [palabras[k]["text"].strip().rstrip(",.?!") for k in range(a, b + 1)]
        cifras = [k for k in range(a, b + 1) if re.fullmatch(r"[$€]?\d[\d.,]*", palabras[k]["text"].strip())]
        if n % 3 == 1 and n < len(frases) - 1:
            escenas.append({"tipo": "persona", "desde": a, "hasta": b})
        elif cifras and n > 0:
            k = cifras[0]
            cifra = palabras[k]["text"].strip().rstrip(",.?!")
            if k + 1 <= b and palabras[k + 1]["text"].strip().startswith(","):
                cifra += palabras[k + 1]["text"].strip().rstrip(".?!")
            escenas.append({"tipo": "cifra", "desde": a, "hasta": b, "cifra": cifra, "palabra": k})
        else:
            escenas.append({"tipo": "titulo", "desde": a, "hasta": b, "linea1": " ".join(txt[:4]), "linea2": " ".join(txt[4:8])})
    return {"correcciones": [], "eliminar": [], "acentos": [], "dudas": ["Plan básico sin Claude: revisa los títulos."], "escenas": escenas}


def validar_plan(plan, palabras):
    n = len(palabras)
    esc = plan.get("escenas")
    if not esc:
        raise Error("el plan no tiene escenas")
    tipos = set(composicion.RENDER) | {"persona"}
    previo = -1
    for s in esc:
        if s.get("tipo") not in tipos:
            raise Error(f"tipo de escena desconocido: {s.get('tipo')}")
        if not (0 <= int(s["desde"]) <= int(s["hasta"]) < n):
            raise Error(f"rango de palabras no válido en la escena {s}")
        if int(s["desde"]) <= previo:
            raise Error(f"escenas desordenadas o superpuestas en la palabra {s['desde']}")
        previo = int(s["hasta"])
    texto = re.sub(r"\D", "", "".join(w["text"] for w in palabras))
    for s in esc:
        if s["tipo"] == "cifra":
            dig = re.sub(r"\D", "", str(s.get("cifra", "")))
            if not dig or dig not in texto:
                raise Error(f"la cifra {s.get('cifra')} no aparece en la transcripción")
    for a, b in plan.get("eliminar", []):
        if not (0 <= int(a) <= int(b) < n):
            raise Error("rango de eliminar no válido")
    if len(plan.get("eliminar", [])) and sum(int(b) - int(a) + 1 for a, b in plan["eliminar"]) > n * 0.4:
        raise Error("eliminar quita demasiado del mensaje")


# ---------- corte ----------

def calcular_rangos(wav, trabajo, palabras, eliminar, duracion):
    salida = reels("speech_mask.py", wav, "--spans", f"0-{duracion:.2f}", "--density", "max", "--json", cwd=trabajo)
    rangos = json.loads(salida[salida.index("{"):])["ranges"]
    # Pausas naturales: el detector deja 50 ms; añado aire para evitar cortes bruscos.
    res = []
    for a, b in rangos:
        a, b = max(0, a - 0.03), b + 0.07
        if res and a - res[-1][1] < 0.07:
            res[-1][1] = b
        else:
            res.append([a, b])
    for i in range(len(res) - 1):
        res[i][1] = min(res[i][1], res[i + 1][0] - 0.034)
    res[-1][1] = min(duracion - 0.03, res[-1][1] + 0.3)   # el último gesto respira
    for ini, fin in eliminar:
        ta, tb = palabras[int(ini)]["start"] - 0.02, palabras[int(fin)]["end"] + 0.02
        nuevo = []
        for a, b in res:
            if b <= ta or a >= tb:
                nuevo.append([a, b])
                continue
            if a < ta - 0.05:
                nuevo.append([a, ta])
            if b > tb + 0.05:
                nuevo.append([tb, b])
        res = nuevo
    return [[round(a, 3), round(b, 3)] for a, b in res]


def tiempo_salida(t, segmentos):
    for s in segmentos:
        if s["src_start"] - 0.001 <= t < s["src_end"]:
            return s["out_start"] + (t - s["src_start"]) / s.get("speed", 1.0)
    return None


def palabras_finales(palabras, plan, segmentos):
    """Aplica correcciones y lleva cada palabra a la línea de tiempo final. Une '$4' + ',700'."""
    fix = {int(c["i"]): c["texto"] for c in plan.get("correcciones", [])}
    acentos = {int(i) for i in plan.get("acentos", [])}
    salida = {}
    lista = []
    for i, w in enumerate(palabras):
        mid = (w["start"] + w["end"]) / 2
        t = tiempo_salida(mid, segmentos)
        if t is None:
            continue
        dur = max(0.05, w["end"] - w["start"])
        s = max(0.0, t - dur / 2)
        txt = fix.get(i, w["text"].strip())
        if lista and txt.startswith(",") and re.search(r"\d", lista[-1]["t"]):
            lista[-1]["t"] += txt
            lista[-1]["e"] = s + dur
            salida[i] = lista[-1]
            continue
        p = {"t": txt, "s": s, "e": s + dur, "k": i in acentos, "i": i}
        lista.append(p)
        salida[i] = p
    return lista, salida


def agrupar(lista):
    solos = {p["t"] for p in lista if re.search(r"\d", p["t"]) or (len(p["t"]) > 2 and p["t"].upper() == p["t"])}
    grupos, cur = [], []
    for i, w in enumerate(lista):
        if w["t"] in solos and cur:
            grupos.append(cur)
            cur = []
        cur.append(w)
        nxt = lista[i + 1] if i + 1 < len(lista) else None
        gap = nxt["s"] - w["e"] if nxt else 9
        duro = not nxt or gap >= 0.15 or w["t"][-1] in ",.?!" or w["t"] in solos or nxt["t"] in solos or nxt["k"] != w["k"]
        if duro:
            grupos.append(cur)
            cur = []
        elif len(cur) >= 3 or (len(cur) == 2 and nxt["t"].lower() in FUNC and w["t"].lower() not in FUNC):
            lleva = []
            while len(cur) > 1 and cur[-1]["t"].lower() in FUNC:
                lleva.insert(0, cur.pop())
            grupos.append(cur)
            cur = lleva
    return grupos


# ---------- escenas ----------

def resolver_escenas(plan, mapa, palabras, D):
    def t_de(i, defecto):
        try:
            p = mapa.get(int(i))
        except (TypeError, ValueError):
            p = None
        return p["s"] if p else defecto

    escenas = []
    for s in plan["escenas"]:
        s = dict(s)
        ini = next((mapa[k]["s"] for k in range(int(s["desde"]), int(s["hasta"]) + 1) if k in mapa), None)
        if ini is None:
            continue   # toda la escena quedó cortada
        s["_t0"] = ini
        escenas.append(s)
    if not escenas:
        raise Error("Ninguna escena quedó dentro del corte.")
    escenas[0]["_t0"] = 0.0
    for i, s in enumerate(escenas):
        s["_t_fin"] = escenas[i + 1]["_t0"] if i + 1 < len(escenas) else D
    for s in escenas:
        t0, tf = s["_t0"], s["_t_fin"]
        lim = lambda t: min(max(t0, t), max(t0, tf - 0.3))  # noqa: E731
        hay_linea2 = bool(s.get("linea2"))
        if s["tipo"] in ("onda", "barras", "secuencia", "pasos", "titulo"):
            s["_t1"] = lim(t0 + .03)
            s["_t2"] = lim(t0 + (.15 if hay_linea2 else .03))
        if s["tipo"] == "onda":
            for c in s.get("chips", []):
                c["_t"] = lim(t_de(c.get("palabra"), t0 + .4))
            a = lim(t_de(s.get("trazo_desde"), t0 + .4))
            b = lim(t_de(s.get("trazo_hasta"), tf - .4))
            s["_trazo"] = (a, max(b, a + .4))
        elif s["tipo"] == "barras":
            for j, b in enumerate(s.get("barras", [])):
                b["_t"] = lim(t_de(b.get("palabra"), t0 + .3 + j * .8))
        elif s["tipo"] == "secuencia":
            s["_ti"] = lim(t_de(s.get("palabra"), t0 + .6))
            s["_tp"] = lim(t_de(s.get("palabra_personas"), s["_ti"] + .7))
        elif s["tipo"] == "pasos":
            for j, p in enumerate(s.get("pasos", [])):
                p["_t"] = lim(t_de(p.get("palabra"), t0 + .4 + j * .7))
            if s.get("nota"):
                s["nota"]["_t"] = lim(t_de(s["nota"].get("palabra"), tf - 1))
        elif s["tipo"] == "cifra":
            s["_t_cifra"] = lim(t_de(s.get("palabra"), t0 + .6))
            s["_t_antes"] = lim(t_de(s.get("palabra_antes"), s["_t_cifra"] - .4))
            s["_t_despues"] = lim(t_de(s.get("palabra_despues"), s["_t_cifra"] + .6))
        elif s["tipo"] == "cta":
            s["_t_etiqueta"] = lim(t_de(s.get("palabra"), t0 + .4))
            s["_t_linea2"] = lim(t_de(s.get("palabra_linea2"), s["_t_etiqueta"] + .4))
            if s.get("nota"):
                s["nota"]["_t"] = lim(t_de(s["nota"].get("palabra"), tf - 1))
    return escenas


def efectos(escenas, D):
    a = os.path.join(RAIZ, "assets/audio")
    lista, turno = [], 0
    for s in escenas:
        t = s["_t0"]
        if t > 0.2:
            lista.append({"file": f"{a}/{'whoosh' if turno % 2 == 0 else 'whoosh2'}.mp3", "at": round(t - .1, 3), "what": "cambio de escena", "_p": 1})
            turno += 1
        if s["tipo"] == "pasos":
            lista += [{"file": f"{a}/click.mp3", "at": round(p["_t"], 3), "what": "paso", "_p": 2} for p in s.get("pasos", [])]
        elif s["tipo"] == "cifra":
            lista.append({"file": f"{a}/impact.mp3", "at": round(s["_t_cifra"], 3), "start": 0.358, "what": "cifra", "_p": 0})
        elif s["tipo"] == "cta":
            lista.append({"file": f"{a}/pop.mp3", "at": round(s["_t_etiqueta"], 3), "what": "llamada a la acción", "_p": 0})
            if s.get("nota"):
                lista.append({"file": f"{a}/pop.mp3", "at": round(s["nota"]["_t"], 3), "what": "nota", "_p": 3})
    tope = max(4, int(round(D / 30 * 12)))        # guía: máximo 12 por cada 30 s
    lista = sorted(lista, key=lambda x: x["_p"])[:tope]
    for x in lista:
        x.pop("_p")
    return {"below_voice_db": 15, "sounds": sorted(lista, key=lambda x: x["at"])}


def texto_plan(escenas, D, plan, n_cortes, dur_ori, musica, n_sfx, crudo):
    fil = []
    for s in escenas:
        if s["tipo"] == "persona":
            desc = "Persona a pantalla completa"
        elif s["tipo"] == "cifra":
            desc = f'Cifra {s.get("cifra")}'
        elif s["tipo"] == "cta":
            desc = f'Llamada a la acción: {s.get("linea1", "")} {s.get("etiqueta", "")} {s.get("linea2", "")}'.strip()
        else:
            desc = f'{s["tipo"].capitalize()}: {s.get("linea1", "")} / {s.get("linea2", "")}'
        fil.append(f'| {s["_t0"]:.1f}–{s["_t_fin"]:.1f} s | {desc} |')
    dudas = "\n".join(f"- {d}" for d in plan.get("dudas", [])) or "- Ninguna"
    cor = "\n".join(f'- {c["texto"]} (palabra {c["i"]})' for c in plan.get("correcciones", [])) or "- Ninguna"
    return f"""# Plan de edición: {os.path.basename(crudo)}

- Duración: {dur_ori:.1f} s → {D:.1f} s ({n_cortes} cortes de pausa)
- Repeticiones eliminadas: {len(plan.get('eliminar', []))}
- Música: {musica}
- Efectos de sonido: {n_sfx}

| Tiempo | Escena |
|---|---|
{chr(10).join(fil)}

## Correcciones de texto
{cor}

## Por confirmar
{dudas}

Puedes editar `plan.json` en la carpeta de trabajo y volver a ejecutar videoia.
"""


# ---------- flujo principal ----------

def musica_elegida(trabajo):
    propias = [f for f in glob.glob(ruta("Material-Crudo", "*")) if f.lower().endswith((".mp3", ".wav", ".m4a", ".aac", ".ogg"))]
    if propias:
        import numpy as np
        f = max(propias, key=os.path.getmtime)
        x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", "8000", "-f", "f32le", "-"],
                                         capture_output=True).stdout, dtype=np.float32)
        e = np.array([np.sqrt(np.mean(x[i:i + 8000] ** 2)) for i in range(0, max(0, len(x) - 8000), 8000)])
        db = 20 * np.log10(e + 1e-6)
        inicio = 0
        if len(db) > 40:
            inicio = min(range(0, len(db) - 32), key=lambda s: db[s:s + 30].max() - db[s:s + 30].min())
        return f, inicio, os.path.basename(f) + " (tuya)"
    return os.path.join(RAIZ, "assets/audio/musica.mp3"), 22, "Plathe (Beatless Ambient Mix), de POA (CC BY 3.0)"


def editar(a):
    crudo = buscar_crudo(a.video)
    vid = slug(os.path.splitext(os.path.basename(crudo))[0])
    trabajo = ruta(".videoia", vid)
    edit = os.path.join(trabajo, "edit/video")
    os.makedirs(edit, exist_ok=True)
    os.makedirs(ruta("Resultados"), exist_ok=True)
    guia_p = ruta("Editor IA", "Guia-de-estilo.md")
    if not os.path.exists(guia_p):
        paso("No hay guía de estilo: la creo con tus referencias")
        estilo(a)
    guia = open(guia_p, encoding="utf-8").read()
    est = json.load(open(ruta("Editor IA", "estilo.json"))) if os.path.exists(ruta("Editor IA", "estilo.json")) \
        else json.load(open(os.path.join(RAIZ, "Editor IA/estilo.json")))

    paso(f"Video: {os.path.basename(crudo)}")
    fuente = normalizar(crudo, trabajo)
    stem = os.path.splitext(os.path.basename(fuente))[0]
    dur_ori = float(ffprobe_json(fuente)["format"]["duration"])

    paso("Transcribiendo en local (la primera vez tarda)")
    reels("transcribe.py", "edit/video", fuente, cwd=trabajo)
    palabras = palabras_fuente(trabajo, stem)
    if not palabras:
        raise Error("La transcripción salió vacía: ¿el video tiene voz?")

    plan_p = os.path.join(trabajo, "plan.json")
    if os.path.exists(plan_p) and not a.replan:
        paso("Uso el plan existente (--replan para rehacerlo)")
        plan = json.load(open(plan_p, encoding="utf-8"))
        validar_plan(plan, palabras)
    else:
        if a.sin_ia or not shutil.which("claude"):
            paso("Creando plan básico, sin Claude")
            plan = plan_basico(palabras)
        else:
            paso("Claude está planeando las escenas")
            plan = plan_con_ia(palabras, guia, a.modelo)
        json.dump(plan, open(plan_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    paso("Cortando silencios y repeticiones")
    wav_out = reels("transcribe.py", "audio", "edit/video", fuente, cwd=trabajo)
    wav = os.path.join(edit, f"audio16k-{stem}.wav")
    if not os.path.exists(wav):
        raise Error(f"No se generó el audio de trabajo: {wav_out}")
    rangos = calcular_rangos(wav, trabajo, palabras, plan.get("eliminar", []), dur_ori)
    cut_p = os.path.join(edit, "cut.json")
    previo = json.load(open(cut_p)) if os.path.exists(cut_p) else {}
    cut = {"fps": 30, "speed": 1.0,
           "sources": {"main": {"file": fuente, "transcript": f"edit/video/transcripts/{stem}.json"}},
           "ranges": [{"start": x, "end": y, "beat": f"t{i}"} for i, (x, y) in enumerate(rangos)]}
    for clave in ("look", "balance"):
        if clave in previo:
            cut[clave] = previo[clave]
    json.dump(cut, open(cut_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    reels("cut.py", "edit/video", cwd=trabajo)
    r = subprocess.run([PY, os.path.join(REELS, "speech_mask.py"), "--edl", "edit/video/edl.json"], cwd=trabajo, capture_output=True, text=True, env=ENV)
    linea = [l for l in r.stdout.splitlines() if "edges with warnings" in l]
    if r.returncode != 0 and linea:
        print("Aviso: revisa estos cortes al escuchar la vista previa →", linea[-1])

    caps = json.load(open(os.path.join(edit, "captions.json")))
    D = round(caps["duration"], 3)
    lista, mapa = palabras_finales(palabras, plan, caps["segments"])
    grupos = agrupar(lista)
    escenas = resolver_escenas(plan, mapa, palabras, D)

    paso("Midiendo el encuadre")
    final_corte = os.path.join(edit, "final.mp4")
    caras = json.loads(correr([PY, os.path.join(RAIZ, "videoia/caras.py"), final_corte, os.path.join(RAIZ, "assets/vendor/face_detection_yunet_2023mar.onnx")], salida=True).strip().splitlines()[-1])
    y0, cap_full = 500, composicion.CAP_Y
    alto_ventana = (1866 - composicion.PANEL_TOP) / composicion.PANEL_ESCALA
    if caras["encontrada"]:
        y0 = int(min(max(0, caras["arriba"] - 130 / composicion.PANEL_ESCALA), 1920 - alto_ventana))
        if caras["abajo"] > composicion.CAP_Y - 30:
            cap_full = 290   # la cara baja mucho: en pantalla completa el subtítulo va arriba
    else:
        print("Aviso: no detecté una cara; uso un encuadre estándar.")

    paso("Componiendo y renderizando en alta calidad")
    reel = os.path.join(trabajo, "reel")
    if os.path.isdir(os.path.join(reel, "assets")):
        shutil.rmtree(os.path.join(reel, "assets"))
    os.makedirs(os.path.join(reel, "assets/vendor"), exist_ok=True)
    shutil.copytree(os.path.join(RAIZ, "assets/fonts"), os.path.join(reel, "assets/fonts"))
    shutil.copy(os.path.join(RAIZ, "assets/vendor/gsap.min.js"), os.path.join(reel, "assets/vendor"))
    shutil.copy(final_corte, os.path.join(reel, "assets/video.mp4"))
    json.dump({"paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}, "media": {"autoProxy": True}},
              open(os.path.join(reel, "hyperframes.json"), "w"))
    json.dump({"id": vid, "name": vid}, open(os.path.join(reel, "meta.json"), "w"))
    open(os.path.join(reel, "index.html"), "w", encoding="utf-8").write(composicion.generar(escenas, grupos, D, est, y0, cap_full))
    chk = subprocess.run(HF + ["check", "--json"], cwd=reel, capture_output=True, text=True, env=ENV)
    try:
        cj = json.loads(chk.stdout[chk.stdout.find("{"):])
        if not cj.get("ok"):
            raise Error("La composición no pasó la revisión de HyperFrames:\n" + chk.stdout[:1500])
    except ValueError:
        raise Error("No pude leer la revisión de HyperFrames:\n" + (chk.stderr or chk.stdout)[-800:])
    render = os.path.join(reel, "render.mp4")
    correr(HF + ["render", "--quality", "delivery", "--output", render], cwd=reel)

    paso("Mezclando voz, música y efectos a −14 LUFS")
    voz = os.path.join(trabajo, "con_voz.mp4")
    correr(["ffmpeg", "-v", "error", "-y", "-i", render, "-i", final_corte, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", voz])
    sfx = efectos(escenas, D)
    sfx_p = os.path.join(trabajo, "sfx.json")
    json.dump(sfx, open(sfx_p, "w"), ensure_ascii=False, indent=1)
    musica, ini_m, nombre_m = musica_elegida(trabajo)
    master = os.path.join(trabajo, "master.mp4")
    mezcla = reels("master_audio.py", voz, "-o", master, "--music", musica, "--music-start", ini_m, "--gap", 18, "--sfx", sfx_p, cwd=trabajo)
    resumen = [l for l in mezcla.splitlines() if l.startswith("output:")]
    if resumen:
        print(resumen[-1].split(" → ")[0])

    plan_md = texto_plan(escenas, D, plan, max(0, len(rangos) - 1), dur_ori, nombre_m, len(sfx["sounds"]), crudo)
    open(ruta("Resultados", f"{vid}-plan.md"), "w", encoding="utf-8").write(plan_md.replace("`plan.json` en la carpeta de trabajo", f"`.videoia/{vid}/plan.json`"))
    vista = ruta("Resultados", f"{vid}-vista-previa.mp4")
    shutil.copy(master, vista)
    print("\n" + plan_md)
    print(f"Vista previa: {vista}")
    if not a.no_abrir and sys.platform == "darwin":
        subprocess.run(["open", vista], check=False)

    if a.si:
        aprobar = True
    elif sys.stdin.isatty():
        aprobar = input("\n¿Exportar la versión final? [s/N] ").strip().lower() in ("s", "si", "sí", "y")
    else:
        aprobar = False
    if aprobar:
        final = ruta("Resultados", f"{vid}-final.mp4")
        shutil.copy(master, final)
        creditos = open(os.path.join(RAIZ, "CREDITOS.md"), encoding="utf-8").read()
        open(ruta("Resultados", f"{vid}-creditos.md"), "w", encoding="utf-8").write(creditos)
        print(f"Listo: {final}")
    else:
        print(f"No exporté la versión final. Cuando la apruebes: videoia --final --video \"{os.path.basename(crudo)}\"")


def exportar_final(a):
    crudo = buscar_crudo(a.video)
    vid = slug(os.path.splitext(os.path.basename(crudo))[0])
    master = ruta(".videoia", vid, "master.mp4")
    if not os.path.exists(master):
        raise Error("Aún no hay vista previa de ese video. Ejecuta primero: videoia")
    final = ruta("Resultados", f"{vid}-final.mp4")
    shutil.copy(master, final)
    shutil.copy(os.path.join(RAIZ, "CREDITOS.md"), ruta("Resultados", f"{vid}-creditos.md"))
    print(f"Listo: {final}")


def estilo(a):
    """Analiza Referencias/ y reescribe la guía y la paleta con Claude."""
    videos = sorted(f for f in glob.glob(ruta("Referencias", "*")) if f.lower().endswith(EXT))
    if not videos:
        raise Error("No hay videos en Referencias/. Pon ahí tus videos de inspiración.")
    if not shutil.which("claude"):
        raise Error("Crear la guía necesita Claude Code instalado.")
    trabajo = ruta(".videoia", "estilo")
    os.makedirs(trabajo, exist_ok=True)
    resumen = []
    for f in videos:
        n = slug(os.path.splitext(os.path.basename(f))[0])
        paso(f"Analizando {os.path.basename(f)}")
        d = os.path.join(trabajo, n)
        os.makedirs(d, exist_ok=True)
        dur = float(ffprobe_json(f)["format"]["duration"])
        paso_s = 2 if dur <= 60 else 3
        filas = int(dur / paso_s / 8) + 1
        correr(["ffmpeg", "-v", "error", "-y", "-i", f, "-vf", f"fps=1/{paso_s},scale=200:-2,tile=8x{filas}:padding=4", "-frames:v", "1", os.path.join(d, "hoja.png")])
        correr(["ffmpeg", "-v", "error", "-y", "-i", f, "-t", "3", "-vf", "fps=4,scale=270:-2,tile=6x2:padding=4", "-frames:v", "1", os.path.join(d, "gancho.png")])
        edit = os.path.join(d, "edit/video")
        os.makedirs(edit, exist_ok=True)
        reels("transcribe.py", "edit/video", f, cwd=d)
        t = json.load(open(os.path.join(edit, "transcripts", os.path.splitext(os.path.basename(f))[0] + ".json")))
        ws = [w for w in t["words"] if w.get("type", "word") == "word"]
        lufs = re.search(r"Input Integrated:\s*(-?[\d.]+)", subprocess.run(["ffmpeg", "-hide_banner", "-i", f, "-af", "loudnorm=print_format=summary", "-f", "null", "-"], capture_output=True, text=True).stderr)
        cortes = subprocess.run(["ffmpeg", "-hide_banner", "-i", f, "-vf", "scdet=threshold=12,metadata=print:file=-", "-an", "-f", "null", "-"], capture_output=True, text=True).stdout.count("lavfi.scd.time")
        pausas = [b["start"] - x["end"] for x, b in zip(ws, ws[1:])]
        resumen.append({"video": os.path.basename(f), "duracion_s": round(dur, 1), "palabras_por_minuto": round(len(ws) / dur * 60), "pausa_maxima_s": round(max(pausas), 2) if pausas else 0,
                        "cambios_de_plano": cortes, "lufs": lufs.group(1) if lufs else None, "transcripcion": t.get("text", " ".join(w["text"] for w in ws))[:1500],
                        "hoja": os.path.join(d, "hoja.png"), "gancho": os.path.join(d, "gancho.png")})
    actual_p = ruta("Editor IA", "Guia-de-estilo.md")
    actual = open(actual_p, encoding="utf-8").read() if os.path.exists(actual_p) else "(sin guía previa)"
    prompt = f"""Crea una guía de estilo de edición en español para videos verticales, a partir de estos referentes.

Lee con la herramienta Read TODAS las imágenes "hoja" y "gancho" indicadas (fotogramas de cada video). Encuentra lo que se repite: gancho, ritmo, subtítulos, colores, animaciones y sonido. Señala qué video es la excepción. Usa solo datos observados o medidos.

Datos medidos:
{json.dumps(resumen, ensure_ascii=False, indent=1)}

Guía actual:
{actual}

Mantén las reglas de la guía actual sobre el encuadre (panel sin zoom, zona segura de anuncios en Reels y lista final), porque el sistema de render depende de ellas. Las tipografías disponibles son Inter Tight, Instrument Serif Italic y JetBrains Mono.

Responde exactamente con:
<guia>
(guía en Markdown con: lo que se repite, paleta, tipografías, reglas de edición, lo que no hago, lista antes de exportar)
</guia>
<estilo>
{{"fondo":"#…","superficie":"#…","borde":"#…","texto":"#FFFFFF","secundario":"#…","acento":"#…","acento_texto":"#…","brillo":"#…","positivo":"#…"}}
</estilo>"""
    paso("Claude está escribiendo la guía")
    cmd = ["claude", "-p", "--output-format", "text", "--tools", "Read", "--allowedTools", "Read", "--add-dir", trabajo, "--no-session-persistence"]
    if a.modelo:
        cmd += ["--model", a.modelo]
    r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=trabajo)
    g = re.search(r"<guia>\s*(.*?)\s*</guia>", r.stdout, re.S)
    e = re.search(r"<estilo>\s*(\{.*?\})\s*</estilo>", r.stdout, re.S)
    if r.returncode != 0 or not g or not e:
        raise Error("Claude no devolvió una guía válida:\n" + (r.stderr or r.stdout)[-800:])
    paleta = json.loads(e.group(1))
    faltan = {"fondo", "superficie", "borde", "texto", "secundario", "acento", "acento_texto", "brillo", "positivo"} - set(paleta)
    if faltan or not all(re.fullmatch(r"#[0-9A-Fa-f]{6}", str(v)) for v in paleta.values()):
        raise Error("La paleta de Claude no es válida.")
    if paleta["acento_texto"].upper() == paleta["texto"].upper():
        paleta["acento_texto"] = paleta["acento"]   # si no, las palabras clave no se distinguen
    os.makedirs(ruta("Editor IA"), exist_ok=True)
    if os.path.exists(actual_p):
        marca = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        shutil.copy(actual_p, ruta("Editor IA", f"Guia-de-estilo.anterior-{marca}.md"))
    open(actual_p, "w", encoding="utf-8").write(g.group(1) + "\n")
    json.dump(paleta, open(ruta("Editor IA", "estilo.json"), "w"), ensure_ascii=False, indent=2)
    print(f"Guía guardada: {actual_p}")


def main():
    p = argparse.ArgumentParser(prog="videoia", description="Del video crudo al anuncio vertical con un solo comando.")
    p.add_argument("accion", nargs="?", default="editar", choices=["editar", "estilo"], help="editar (por defecto) o estilo: rehace la guía con Referencias/")
    p.add_argument("--video", help="video de Material-Crudo/ (por defecto, el más reciente)")
    p.add_argument("--si", action="store_true", help="exporta la versión final sin preguntar")
    p.add_argument("--final", action="store_true", help="exporta la última vista previa como versión final")
    p.add_argument("--replan", action="store_true", help="rehace el plan de escenas")
    p.add_argument("--sin-ia", action="store_true", help="plan básico, sin Claude")
    p.add_argument("--modelo", help="modelo de Claude para el plan")
    p.add_argument("--no-abrir", action="store_true", help="no abre la vista previa")
    a = p.parse_args()
    try:
        if a.accion == "estilo":
            estilo(a)
        elif a.final:
            exportar_final(a)
        else:
            editar(a)
    except Error as e:
        print(f"\n✗ {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
