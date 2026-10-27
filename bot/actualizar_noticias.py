#!/usr/bin/env python3
"""Bot de noticias de El Portal de Tlacotalpan: busca noticias de la región (Bing News RSS),
las combina con las anteriores y escribe noticias.json. Solo guarda título, resumen corto,
imagen y enlace a la fuente original."""
import json, re, html, os, urllib.request, urllib.parse
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

CONSULTAS = ["Tlacotalpan", "Papaloapan Veracruz", "Cosamaloapan", "Tlacotalpan son jarocho"]
MAX = 40
SALIDA = os.path.join(os.path.dirname(__file__), "..", "noticias.json")
UA = {"User-Agent": "Mozilla/5.0 (compatible; ElPortalBot/1.0)"}
CATS = [("Cultura", r"fiesta|candelaria|son jarocho|música|cultura|museo|festival|tradici"),
        ("Deportes", r"futbol|fútbol|béisbol|beisbol|torneo|deport"),
        ("Seguridad", r"policía|detenid|robo|accidente|seguridad|fiscal"),
        ("Comunidad", r"vecinos|comunidad|escuela|salud|obra|ayuntamiento|alcald")]

def get(url, limite=400000):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
        return r.read(limite)

def url_real(link):
    q = urllib.parse.parse_qs(urllib.parse.urlparse(link).query)
    return q.get("url", [link])[0]

def categoria(texto):
    for nombre, patron in CATS:
        if re.search(patron, texto.lower()):
            return nombre
    return "Región"

def parsear(xml):
    out = []
    for it in ET.fromstring(xml).iter("item"):
        d = {"titulo": "", "resumen": "", "fuente": "", "imagen": "", "link": "", "fecha": ""}
        for ch in it:
            t = ch.tag.split("}")[-1].lower()
            v = (ch.text or "").strip()
            if t == "title": d["titulo"] = html.unescape(v)
            elif t == "link": d["link"] = v
            elif t == "description": d["resumen"] = html.unescape(re.sub("<[^>]+>", "", v))[:220]
            elif t == "pubdate":
                try: d["fecha"] = parsedate_to_datetime(v).astimezone(timezone.utc).isoformat()
                except Exception: pass
            elif t == "source": d["fuente"] = v
            elif t == "image": d["imagen"] = v
        if d["titulo"] and d["link"]:
            u = url_real(d["link"])
            if d["imagen"].startswith("//"): d["imagen"] = "https:" + d["imagen"]
            out.append({"titulo": d["titulo"], "resumen": d["resumen"], "fuente": d["fuente"] or urllib.parse.urlparse(u).netloc,
                        "fecha": d["fecha"], "categoria": categoria(d["titulo"] + " " + d["resumen"]), "url": u, "imagen": d["imagen"]})
    return out

def og_imagen(url):
    try:
        h = get(url, 250000).decode("utf-8", "ignore")
        m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', h) or \
            re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image', h)
        return html.unescape(m.group(1)) if m else ""
    except Exception:
        return ""

def main():
    try: previas = json.load(open(SALIDA, encoding="utf-8")).get("noticias", [])
    except Exception: previas = []
    todas = [n for n in previas if n["url"] != "#"]
    for q in CONSULTAS:
        try:
            todas += parsear(get("https://www.bing.com/news/search?format=rss&mkt=es-MX&q=" + urllib.parse.quote(q)))
        except Exception as e:
            print("Error con", q, e)
    vistos, unicas = set(), []
    for n in sorted(todas, key=lambda x: x["fecha"], reverse=True):
        clave = re.sub(r"\W+", "", n["titulo"].lower())[:60]
        if n["url"] in vistos or clave in vistos: continue
        vistos |= {n["url"], clave}; unicas.append(n)
    unicas = unicas[:MAX]
    for n in [x for x in unicas if not x["imagen"]][:15]:
        n["imagen"] = og_imagen(n["url"])
    if not unicas: print("Sin resultados; no se modifica el archivo."); return
    json.dump({"actualizado": datetime.now(timezone.utc).isoformat(), "noticias": unicas},
              open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(unicas), "noticias guardadas")

if __name__ == "__main__":
    main()
