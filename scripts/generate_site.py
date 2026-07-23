#!/usr/bin/env python3
"""
Genera docs/index.html con los próximos conciertos/actividades musicales
de los centros cívicos que le interesan a la abuela.

Fuente principal: "Agenda d'actes i activitats de la ciutat de Barcelona"
(Open Data BCN, licencia Creative Commons Attribution 4.0):
https://opendata-ajuntament.barcelona.cat/data/ca/dataset/agenda-diaria

Fuente secundaria: data/extras.yml (curado a mano cada semana para
fuentes que no están en datos abiertos, p.ej. CaixaForum).

Si la fuente oficial falla (mantenimiento, cambios de formato, etc.)
el script NO borra la web existente: deja docs/index.html tal cual
estaba y solo avisa por consola, para que nunca se quede vacía.
"""

import json
import re
import sys
import unicodedata
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"

# Endpoint estándar del catálogo CKAN de Open Data BCN para este dataset.
CKAN_PACKAGE_URL = (
    "https://opendata-ajuntament.barcelona.cat/data/api/3/action/"
    "package_show?id=agenda-diaria"
)

DAYS_AHEAD = 12  # cuántos días hacia delante mostramos cada semana
REQUEST_TIMEOUT = 20

DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def normalize(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.lower().strip()


def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def find_json_resource_url() -> str | None:
    """Consulta el catálogo CKAN y busca el recurso en formato JSON."""
    req = urllib.request.Request(
        CKAN_PACKAGE_URL,
        headers={"User-Agent": "barcelona-musical-abuela/1.0 (proyecto personal, ver README)"},
    )
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        payload = json.load(resp)

    resources = payload.get("result", {}).get("resources", [])
    for res in resources:
        fmt = (res.get("format") or "").lower()
        if fmt == "json":
            return res.get("url")
    # si no hay JSON, probamos con el primero que haya
    return resources[0].get("url") if resources else None


def fetch_agenda_events() -> list[dict]:
    resource_url = find_json_resource_url()
    if not resource_url:
        raise RuntimeError("No se encontró ningún recurso descargable en el dataset.")

    req = urllib.request.Request(
        resource_url,
        headers={"User-Agent": "barcelona-musical-abuela/1.0 (proyecto personal, ver README)"},
    )
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        raw = json.load(resp)

    # La estructura exacta puede variar; probamos las formas más
    # habituales del feed de datos abiertos de Barcelona.
    if isinstance(raw, dict):
        for key in ("events", "result", "data"):
            if key in raw and isinstance(raw[key], list):
                return raw[key]
        # a veces viene como {"event": [...]}
        if "event" in raw:
            return raw["event"] if isinstance(raw["event"], list) else [raw["event"]]
    if isinstance(raw, list):
        return raw

    raise RuntimeError("Formato de la agenda oficial no reconocido; revisa el script.")


def event_matches_venue(ev: dict, venues: list[dict]) -> str | None:
    """Devuelve el nombre "bonito" del centro si el evento es de uno de
    nuestros centros cívicos, o None si no coincide con ninguno."""
    haystacks = []
    for key in ("location", "espai", "addresses", "adreca", "equipament", "name"):
        val = ev.get(key)
        if isinstance(val, str):
            haystacks.append(val)
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    haystacks.append(item.get("name", "") or item.get("espai", ""))
                elif isinstance(item, str):
                    haystacks.append(item)
        elif isinstance(val, dict):
            haystacks.append(val.get("name", ""))

    haystack_norm = normalize(" | ".join(h for h in haystacks if h))
    if not haystack_norm:
        return None

    for venue in venues:
        for alias in venue.get("aliases", [venue["name"]]):
            if normalize(alias) in haystack_norm:
                return venue["name"]
    return None


def event_is_musical(ev: dict, keywords: list[str]) -> bool:
    text_fields = []
    for key in ("title", "name", "categories", "tags", "description", "classification"):
        val = ev.get(key)
        if isinstance(val, str):
            text_fields.append(val)
        elif isinstance(val, list):
            text_fields.extend(str(x) for x in val)

    text_norm = normalize(" | ".join(text_fields))
    return any(normalize(kw) in text_norm for kw in keywords)


def parse_event_date(ev: dict) -> date | None:
    for key in ("from_date", "start_date", "data_inici", "date_start", "date"):
        val = ev.get(key)
        if not val:
            continue
        val = str(val)[:10]
        try:
            return datetime.strptime(val, "%Y-%m-%d").date()
        except ValueError:
            continue
    return None


def collect_official_events(venues: list[dict], keywords: list[str]) -> list[dict]:
    today = date.today()
    limit = today + timedelta(days=DAYS_AHEAD)

    events = fetch_agenda_events()
    results = []
    for ev in events:
        venue_name = event_matches_venue(ev, venues)
        if not venue_name:
            continue
        if not event_is_musical(ev, keywords):
            continue
        ev_date = parse_event_date(ev)
        if not ev_date or not (today <= ev_date <= limit):
            continue

        results.append({
            "titulo": ev.get("title") or ev.get("name") or "Actividad musical",
            "fecha": ev_date,
            "hora": (ev.get("hour") or ev.get("hora") or "").strip(),
            "lugar": venue_name,
            "descripcion": (ev.get("description") or "").strip(),
            "enlace": ev.get("link") or ev.get("url") or "",
            "fuente": "Centres Cívics / Ajuntament de Barcelona",
        })
    return results


def collect_extra_events() -> list[dict]:
    extras = load_yaml(DATA_DIR / "extras.yml").get("eventos", []) or []
    today = date.today()
    limit = today + timedelta(days=DAYS_AHEAD)

    results = []
    for ev in extras:
        try:
            ev_date = datetime.strptime(str(ev["fecha"]), "%Y-%m-%d").date()
        except (KeyError, ValueError):
            continue
        if not (today <= ev_date <= limit):
            continue
        results.append({
            "titulo": ev.get("titulo", "Actividad musical"),
            "fecha": ev_date,
            "hora": ev.get("hora", ""),
            "lugar": ev.get("lugar", ""),
            "descripcion": ev.get("descripcion", ""),
            "enlace": ev.get("enlace", ""),
            "fuente": ev.get("fuente", "Añadido a mano"),
        })
    return results


def formatear_fecha(d: date) -> str:
    return f"{DIAS_SEMANA[d.weekday()].capitalize()} {d.day} de {MESES[d.month - 1]}"


def render_html(eventos: list[dict], aviso: str | None) -> str:
    eventos = sorted(eventos, key=lambda e: (e["fecha"], e["hora"] or ""))

    dias = {}
    for ev in eventos:
        dias.setdefault(ev["fecha"], []).append(ev)

    hoy_str = formatear_fecha(date.today())

    bloques = []
    if not dias:
        bloques.append(
            '<p class="sin-eventos">Esta semana no hay conciertos nuevos '
            "confirmados en la lista de centros. Vuelve a mirar la semana que viene.</p>"
        )
    for dia, lista in dias.items():
        tarjetas = []
        for ev in lista:
            hora = f'<span class="hora">{ev["hora"]} h</span>' if ev["hora"] else ""
            desc = f'<p class="descripcion">{ev["descripcion"]}</p>' if ev["descripcion"] else ""
            enlace = (
                f'<a class="mas-info" href="{ev["enlace"]}" target="_blank" rel="noopener">Más información</a>'
                if ev["enlace"] else ""
            )
            tarjetas.append(f"""
            <article class="evento">
              <h3>{ev["titulo"]}</h3>
              <p class="lugar">📍 {ev["lugar"]} {hora}</p>
              {desc}
              {enlace}
            </article>""")
        bloques.append(f"""
        <section class="dia">
          <h2>{formatear_fecha(dia)}</h2>
          {"".join(tarjetas)}
        </section>""")

    aviso_html = f'<p class="aviso">{aviso}</p>' if aviso else ""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Conciertos de la semana</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
  <div class="mosaico" aria-hidden="true"></div>
  <header>
    <h1>Conciertos de la semana</h1>
    <p class="subtitulo">Centros cívicos de Barcelona · actualizado el {hoy_str}</p>
  </header>
  <main>
    {aviso_html}
    {"".join(bloques)}
  </main>
  <footer>
    <p>Se actualiza automáticamente cada domingo.</p>
  </footer>
</body>
</html>
"""


def main():
    venues = load_yaml(DATA_DIR / "venues.yml").get("venues", [])
    keywords = load_yaml(DATA_DIR / "venues.yml").get("music_keywords", [])

    aviso = None
    oficiales = []
    try:
        oficiales = collect_official_events(venues, keywords)
    except Exception as exc:  # noqa: BLE001
        print(f"[aviso] No se pudo leer la agenda oficial: {exc}", file=sys.stderr)
        aviso = (
            "⚠️ Esta semana no se ha podido consultar la agenda oficial del "
            "Ayuntamiento automáticamente. Estos son solo los eventos añadidos a mano."
        )

    extras = collect_extra_events()
    todos = oficiales + extras

    if not oficiales and not extras and aviso is None:
        aviso = None  # sencillamente no hay eventos esta semana, no es un error

    html = render_html(todos, aviso)

    DOCS_DIR.mkdir(exist_ok=True)
    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")
    print(f"OK: {len(todos)} eventos escritos en docs/index.html")


if __name__ == "__main__":
    main()
