#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
codificar_documental.py - Codificación documental por reglas fijas (determinista).

Aplica a cada institución del censo las definiciones operativas del libro de
códigos (Sección 3.3 y Apéndice C del manuscrito) mediante reglas explícitas:
expresiones regulares fijas, sin modelos de lenguaje ni inteligencia artificial.
Con la misma entrada produce siempre la misma salida.

Es un instrumento de verificación POSTERIOR, escrito en noviembre de 2026. No
reproduce ni sustituye la compilación del 11 de agosto de 2026; su propósito es
medir, con un procedimiento reproducible, cuánto coincide la matriz publicada
con lo que dan unas reglas fijas. Debe declararse así en el manuscrito.

Regla de profundidad uno: solo se considera el material enlazado desde la
portada (igual que en el estudio). No se ejecuta JavaScript (igual que en el
estudio): lo que se genera dinámicamente no se lee.

Códigos: si | no | parcial | nv   (nv = no verificable por este método)

Uso (PowerShell, desde esta carpeta):
    py -m pip install requests beautifulsoup4 pypdf
    py codificar_documental.py                      # sitios en vivo, hoy
    py codificar_documental.py --wayback 20260811   # instantáneas archivadas
    py codificar_documental.py --ids 1 2 64         # solo algunos sitios

Salida: salida_<modo>/sitios/<id>.json (códigos + evidencia) y
salida_<modo>/crudo/<id>/ (páginas descargadas, para auditoría).
No guarda direcciones de correo: el indicador de contacto registra solo si
existe un contacto de privacidad identificado.
"""
import argparse, hashlib, io, json, re, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup

VERSION = "1.1.0"
# 1.1.0 (11-nov-2026): solo cambia la DESCARGA, no las reglas de codificación.
#   Un error transitorio (HTTP 429/5xx, tiempo agotado, conexión cortada) ya no se
#   codifica como «nv»: se reintenta con espera creciente y, si persiste, el sitio
#   queda pendiente sin resultado. Pausa mínima de 5 s con --wayback (límite de
#   web.archive.org). Se registra la fecha de la instantánea archivada usada.
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36 "
      "LODP-WebAcc-Univ-documentary-check/" + VERSION)
TIMEOUT = 30
MIN_PALABRAS_AVISO = 150   # menos texto legible que esto = no legible por máquina

F = re.IGNORECASE

# --------------------------------------------------------------------------
# 1. Enlaces de portada (profundidad uno)
# --------------------------------------------------------------------------
RX_PRIVACIDAD = re.compile(
    r"privacidad|protecci[oó]n\s+de\s+datos|datos\s+personales|tratamiento\s+de\s+datos|"
    r"privacy|data\s+protection|personal\s+(data|information)|datenschutz|"
    r"confidentialit[eé]|donn[eé]es\s+personnelles|protection\s+des\s+donn[eé]es|"
    r"integritet|personuppgift|privacyverklaring|privacybeleid|gegevensbescherming|"
    r"隐私|个人信息|隱私|私隱|プライバシー|個人情報|개인정보", F)
RX_PRIV_HREF = re.compile(r"privac|datenschutz|data-?protection|proteccion-?de-?datos|"
                          r"datos-?personales|donnees-?personnelles|personuppgift|gdpr|rgpd", F)
RX_COOKIE = re.compile(r"cookie|kakor|쿠키|クッキー", F)
RX_ACCESIBILIDAD = re.compile(
    r"accesibilidad|accessibilit|barrierefrei|toegankelijkheid|tillg[aä]nglighet|"
    r"无障碍|無障礙|アクセシビリティ|접근성", F)
RX_ACC_HREF = re.compile(r"accessib|accesibilidad|barrierefrei|toegankelijk|tillganglighet", F)
# Barras de accesibilidad reconocibles en el HTML de la portada
RX_BARRA_ACC = re.compile(r"userway|acsbapp|accessibe|equalweb|recite\.?me|pojo-a11y|"
                          r"one-click-accessibility|wp-accessibility|accessibility-toolbar|"
                          r"readspeaker|reciteme|audioeye|sienna", F)
RX_TRANSPARENCIA = re.compile(r"transparencia|lotaip", F)

# Alcance parcial del aviso (solo en título o encabezado principal)
RX_ALCANCE_PARCIAL = re.compile(
    r"admisi[oó]n|admisiones|posgrado|postgrado|maestr[ií]a|aplicaci[oó]n\s+m[oó]vil|"
    r"\bapp\b|admissions|mobile\s+app|graduate\s+school|alumni|biblioteca|library", F)

# --------------------------------------------------------------------------
# 2. Marco jurídico aplicable por jurisdicción (Apéndice C del manuscrito)
#    Revisar y fijar ANTES de ejecutar; no modificar después de ver resultados.
# --------------------------------------------------------------------------
UE = r"\bGDPR\b|\bRGPD\b|\bDSGVO\b|General\s+Data\s+Protection\s+Regulation|" \
     r"Reglamento\s+General\s+de\s+Protecci[oó]n\s+de\s+Datos|" \
     r"R[eè]glement\s+g[eé]n[eé]ral\s+sur\s+la\s+protection|Datenschutz-Grundverordnung|" \
     r"(EU|UE)\s*\)?\s*2016\s*/\s*679|dataskyddsf[oö]rordning|(?-i:\bAVG\b)"
MARCO_APLICABLE = {
    "EC": r"\bLOPDP\b|Ley\s+Org[aá]nica\s+de\s+Protecci[oó]n\s+de\s+Datos\s+Personales",
    "DE": UE + r"|\bBDSG\b|Bundesdatenschutzgesetz|\bLDSG\b|Landesdatenschutzgesetz|BayDSG",
    "FR": UE + r"|Informatique\s+et\s+Libert[eé]s|loi\s+n[°o]?\s*78-17",
    "NL": UE + r"|\bUAVG\b|Uitvoeringswet",
    "BE": UE + r"|loi\s+du\s+30\s+juillet\s+2018|wet\s+van\s+30\s+juli\s+2018",
    "SE": UE + r"|dataskyddslagen|2018:218",
    "GB": r"UK\s+GDPR|Data\s+Protection\s+Act\s+2018|" + UE,
    "CH": r"\b(n|rev)?FADP\b|(?-i:\b(n|rev)?DSG\b)|Datenschutzgesetz|Federal\s+Act\s+on\s+Data\s+Protection|"
          r"(?-i:\bIDG\b)|Informations-\s+und\s+Datenschutzgesetz|(?-i:\bLPD\b|\bLIPAD\b)",
    "US": r"\bCCPA\b|\bCPRA\b|California\s+Consumer\s+Privacy\s+Act|\bCalOPPA\b|\bFERPA\b|"
          r"Family\s+Educational\s+Rights\s+and\s+Privacy\s+Act|\bHIPAA\b|\bGLBA\b|Gramm-Leach-Bliley|\bCOPPA\b|"
          r"(?-i:[A-Z][a-z]+)\s+(Consumer\s+)?(Data\s+)?Privacy\s+Act|" + UE,
    "CA": r"\bPIPEDA\b|\bFIPPA\b|\bFOIPPA\b|Freedom\s+of\s+Information\s+and\s+Protection\s+of\s+Privacy\s+Act|"
          r"Law\s*25|Loi\s*25|Act\s+respecting\s+Access\s+to\s+documents|Privacy\s+Act",
    "CN": r"\bPIPL\b|个人信息保护法|Personal\s+Information\s+Protection\s+Law|网络安全法|数据安全法",
    "HK": r"\bPDPO\b|Personal\s+Data\s+\(Privacy\)\s+Ordinance|個人資料\s*\(私隱\)\s*條例|Cap\.?\s*486",
    "JP": r"\bAPPI\b|個人情報の保護に関する法律|個人情報保護法|Act\s+on\s+the\s+Protection\s+of\s+Personal\s+Information",
    "KR": r"\bPIPA\b|개인정보\s*보호법|Personal\s+Information\s+Protection\s+Act",
    "SG": r"\bPDPA\b|Personal\s+Data\s+Protection\s+Act",
    "AU": r"Privacy\s+Act\s+1988|Australian\s+Privacy\s+Principles|"
          r"Privacy\s+and\s+Data\s+Protection\s+Act\s+2014|Information\s+Privacy\s+Act\s+2009|"
          r"Privacy\s+and\s+Personal\s+Information\s+Protection\s+Act|PPIP\s+Act|Health\s+Records\s+Act",
}
# Cualquier instrumento de protección de datos con nombre (para el código parcial:
# instrumento nombrado que no gobierna a la institución)
MARCO_CUALQUIERA = "|".join(set(MARCO_APLICABLE.values())) + \
    r"|Ley\s+de\s+Comercio\s+Electr[oó]nico|Ley\s+del\s+Sistema\s+Nacional\s+de\s+Registro\s+de\s+Datos\s+P[uú]blicos"
RX_MARCO_CUALQUIERA = re.compile(MARCO_CUALQUIERA, F)

# --------------------------------------------------------------------------
# 3. Derechos del interesado (al menos tres de seis + vía de ejercicio)
# --------------------------------------------------------------------------
DERECHOS = {
    "acceso": r"derecho\s+(de|a)l?\s+acceso|acceso\s+a\s+(sus|los|tus)\s+datos|right\s+(of|to)\s+access|"
              r"access\s+(to\s+)?(your|the)\s+(personal\s+)?(data|information)|Auskunft|droit\s+d.acc[eè]s|"
              r"recht\s+op\s+inzage|r[aä]tt\s+till\s+tillg[aå]ng|r[aä]tt\s+att\s+f[aå]\s+tillg[aå]ng|"
              r"查阅|查询|開示|열람",
    "rectificacion": r"rectificaci[oó]n|right\s+to\s+(rectif|correct)|rectif(y|ication)|"
                     r"correct(ion\s+of)?\s+(your\s+)?(inaccurate|incorrect)|Berichtigung|"
                     r"recht\s+op\s+rectificatie|r[aä]ttelse|更正|訂正|정정",
    "supresion": r"supresi[oó]n|eliminaci[oó]n\s+de\s+(sus|los)\s+datos|cancelaci[oó]n|erasure|"
                 r"delet(e|ion)\s+(of\s+)?(your|personal|the)|right\s+to\s+be\s+forgotten|L[oö]schung|"
                 r"effacement|recht\s+op\s+(gegevens)?wissing|radering|删除|削除|消去|삭제",
    "limitacion": r"(limitaci[oó]n|restricci[oó]n)\s+(del?\s+)?(su\s+)?tratamiento|"
                  r"restrict(ion\s+of)?\s+(the\s+)?process|Einschr[aä]nkung\s+der\s+Verarbeitung|"
                  r"limitation\s+du\s+traitement|beperking\s+van\s+de\s+verwerking|begr[aä]nsning|"
                  r"利用停止|처리\s*정지|限制处理",
    "oposicion": r"oposici[oó]n|right\s+to\s+object|object\s+to\s+(the\s+)?process|Widerspruch|"
                 r"droit\s+d.opposition|recht\s+van\s+bezwaar|inv[aä]ndning|拒绝|撤回",
    "portabilidad": r"portabilidad|portability|[UÜ]bertragbarkeit|portabilit[eé]|overdraagbaarheid|"
                    r"dataportabilitet|可搬|转移",
}
RX_DERECHOS = {k: re.compile(v, F) for k, v in DERECHOS.items()}
RX_VIA_EJERCICIO = re.compile(
    r"@|formulario|solicitud|ejercer|ejercicio\s+de\s+(sus|los)\s+derechos|form\b|request|"
    r"exercise\s+(your|these|any)|contact\s+(us|the)|Antrag|Kontakt|formulaire|demande|"
    r"申请|请求|請求|신청|문의", F)

# --------------------------------------------------------------------------
# 4. Contacto de privacidad o delegado de protección de datos
# --------------------------------------------------------------------------
RX_DPO_ROL = re.compile(
    r"data\s+protection\s+officer|\bDPO\b|privacy\s+officer|chief\s+privacy|privacy\s+office\b|"
    r"delegad[oa]\s+de\s+protecci[oó]n\s+de\s+datos|oficial\s+de\s+protecci[oó]n\s+de\s+datos|"
    r"responsable\s+de\s+protecci[oó]n\s+de\s+datos|Datenschutzbeauftragte|"
    r"d[eé]l[eé]gu[eé]\s+[aà]\s+la\s+protection\s+des\s+donn[eé]es|\bDPD\b|"
    r"functionaris\s+gegevensbescherming|dataskyddsombud|"
    r"个人信息保护负责人|個人情報保護管理者|개인정보\s*보호\s*책임자|"
    r"Data\s+Protection\s+(Office|Team)|Privacy\s+(Team|Unit)", F)
RX_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
RX_EMAIL_PRIV = re.compile(r"privac|dpo|datos|datenschutz|dataprotection|data\.protection|"
                           r"protecciondatos|gdpr|rgpd|dsb|dpd|personvern|privacy", F)

ESTADOS_UE = {"DE", "FR", "NL", "BE", "SE"}


# --------------------------------------------------------------------------
# Utilidades de descarga
# --------------------------------------------------------------------------
ESTADOS_TRANSITORIOS = {429, 500, 502, 503, 504, 520, 522, 524}
ESPERAS = [30, 60, 120, 240, 480]   # segundos entre reintentos


class ErrorTransitorio(Exception):
    """La descarga falló por una causa pasajera; el sitio no se codifica en esta corrida."""


class Descargador:
    def __init__(self, wayback=None, pausa=1.0):
        self.wayback = wayback
        self.pausa = pausa
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": UA, "Accept-Language": "es,en;q=0.8,*;q=0.5"})

    def url_efectiva(self, url):
        if self.wayback:
            return f"https://web.archive.org/web/{self.wayback}id_/{url}"
        return url

    def get(self, url):
        """Devuelve dict con status, contenido, tipo, url_final, tls_ok, error.
        Lanza ErrorTransitorio si tras los reintentos la causa sigue siendo pasajera."""
        u = self.url_efectiva(url)
        for intento, espera in enumerate([0] + ESPERAS):
            if espera:
                print(f"      reintento {intento} en {espera} s ({url})", flush=True)
                time.sleep(espera)
            time.sleep(self.pausa)
            r = {"url_solicitada": url, "url_consultada": u, "status": None, "tls_ok": None,
                 "contenido": b"", "tipo": "", "url_final": None, "error": None, "instantanea": None,
                 "fecha_hora_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
            transitorio = False
            for verificar in (True, False):
                try:
                    resp = self.s.get(u, timeout=TIMEOUT, verify=verificar, allow_redirects=True)
                    r.update(status=resp.status_code, contenido=resp.content,
                             tipo=resp.headers.get("Content-Type", ""), url_final=resp.url,
                             tls_ok=verificar)
                    transitorio = resp.status_code in ESTADOS_TRANSITORIOS
                    if transitorio and resp.headers.get("Retry-After", "").isdigit():
                        time.sleep(min(int(resp.headers["Retry-After"]), 600))
                    break
                except requests.exceptions.SSLError as e:
                    r["error"] = "SSL: " + str(e)[:200]
                    continue
                except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                    r["error"] = type(e).__name__ + ": " + str(e)[:200]
                    # sin conexión con el archivo es transitorio; con el sitio, se reintenta igual
                    transitorio = True
                    break
                except Exception as e:
                    r["error"] = type(e).__name__ + ": " + str(e)[:200]
                    break
            if not transitorio:
                m = re.search(r"/web/(\d{8,14})", r["url_final"] or "")
                r["instantanea"] = m.group(1) if (self.wayback and m) else None
                return r
        raise ErrorTransitorio(f"{url}: estado {r['status']} {r['error'] or ''}".strip())


def url_original(u):
    """Quita el prefijo de Wayback si lo hay, para resolver enlaces."""
    m = re.match(r"https?://web\.archive\.org/web/\d+[a-z_]*/(.+)", u or "")
    return m.group(1) if m else u


def texto_html(contenido):
    soup = BeautifulSoup(contenido, "html.parser")
    for t in soup(["script", "style", "noscript", "template"]):
        t.decompose()
    return soup, re.sub(r"\s+", " ", soup.get_text(" ")).strip()


def texto_pdf(contenido):
    try:
        from pypdf import PdfReader
        lector = PdfReader(io.BytesIO(contenido))
        return re.sub(r"\s+", " ", " ".join((p.extract_text() or "") for p in lector.pages)).strip()
    except Exception:
        return ""


def palabras(t):
    # Para escrituras sin espacios (chino, japonés) se cuentan caracteres CJK / 2
    lat = len(re.findall(r"\w+", t))
    cjk = len(re.findall(r"[぀-ヿ一-鿿가-힯]", t))
    return max(lat, cjk // 2)


def enlaces(soup, base):
    out = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        txt = " ".join(filter(None, [a.get_text(" ", strip=True), a.get("title", ""),
                                     a.get("aria-label", "")]))
        absu = urldefrag(urljoin(base, url_original(href)))[0]
        out.append({"texto": re.sub(r"\s+", " ", txt)[:200], "url": absu})
    return out


def sha(b):
    return hashlib.sha256(b).hexdigest()


# --------------------------------------------------------------------------
# Codificación de un sitio
# --------------------------------------------------------------------------
def codificar(sitio, d, dir_crudo):
    pais = sitio["pais"]
    grupo = sitio["grupo"]
    ev = {"descargas": [], "coincidencias": {}}
    cod = {}

    portada = d.get(sitio["url"])
    ev["descargas"].append({k: portada[k] for k in ("url_consultada", "status", "tls_ok", "url_final",
                                                     "fecha_hora_utc", "error", "instantanea")} |
                           {"sha256": sha(portada["contenido"])})
    if portada["status"] != 200 or not portada["contenido"]:
        indicadores = ["privacy_notice", "legal_framework", "data_subject_rights", "dpo_contact",
                       "accessibility_statement"] + \
                      (["cookie_policy"] if grupo == "mundo" else ["lotaip_transparency"])
        motivo = ("sin instantánea archivada" if d.wayback and portada["status"] == 404
                  else "portada no recuperable")
        return {k: "nv" for k in indicadores}, ev | {"motivo_nv": motivo}

    (dir_crudo / "portada.html").write_bytes(portada["contenido"])
    base = url_original(portada["url_final"] or sitio["url"])
    soup, _ = texto_html(portada["contenido"])
    ls = enlaces(soup, base)
    html_portada = portada["contenido"].decode("utf-8", "ignore")

    # --- enlaces candidatos ---
    def prioridad_priv(l):
        t, u = l["texto"], l["url"]
        if RX_COOKIE.search(t) and not RX_PRIVACIDAD.search(t):
            return None
        if RX_PRIVACIDAD.search(t):
            return 0
        if RX_PRIV_HREF.search(u) and not RX_COOKIE.search(u):
            return 1
        return None
    cand = sorted([(p, i, l) for i, l in enumerate(ls) if (p := prioridad_priv(l)) is not None],
                  key=lambda x: (x[0], x[1]))
    vistos, candidatos = set(), []
    for _, _, l in cand:
        if l["url"] not in vistos:
            vistos.add(l["url"]); candidatos.append(l)
    ev["candidatos_aviso"] = candidatos[:5]

    acc = [l for l in ls if RX_ACCESIBILIDAD.search(l["texto"]) or RX_ACC_HREF.search(l["url"])]
    barra = RX_BARRA_ACC.search(html_portada)
    cod["accessibility_statement"] = "si" if (acc or barra) else "no"
    ev["coincidencias"]["accesibilidad"] = (acc[:1] and acc[0]) or (barra and {"barra": barra.group(0)}) or None

    if grupo == "ecuador":
        tr = [l for l in ls if RX_TRANSPARENCIA.search(l["texto"]) or RX_TRANSPARENCIA.search(l["url"])]
        cod["lotaip_transparency"] = "si" if tr else "no"
        ev["coincidencias"]["transparencia"] = tr[0] if tr else None

    # --- aviso de privacidad ---
    aviso_txt, aviso_url, titulo, aviso_soup = None, None, "", None
    intentos_fallidos = 0
    for l in candidatos[:3]:
        r = d.get(l["url"])
        ev["descargas"].append({k: r[k] for k in ("url_consultada", "status", "tls_ok", "url_final",
                                                   "fecha_hora_utc", "error", "instantanea")} | {"sha256": sha(r["contenido"])})
        if r["status"] != 200 or not r["contenido"]:
            intentos_fallidos += 1
            continue
        es_pdf = "pdf" in r["tipo"].lower() or l["url"].lower().endswith(".pdf")
        if es_pdf:
            t = texto_pdf(r["contenido"]); s = None
            (dir_crudo / "aviso.pdf").write_bytes(r["contenido"])
        else:
            s, t = texto_html(r["contenido"])
            (dir_crudo / "aviso.html").write_bytes(r["contenido"])
        if palabras(t) < MIN_PALABRAS_AVISO:
            intentos_fallidos += 1
            continue
        aviso_txt, aviso_url, aviso_soup = t, l["url"], s
        if s is not None:
            h1 = s.find("h1")
            titulo = " ".join(filter(None, [s.title.get_text(" ", strip=True) if s.title else "",
                                            h1.get_text(" ", strip=True) if h1 else ""]))
        else:
            titulo = t[:200]
        titulo = (titulo + " " + l["texto"])[:400]
        break

    ev["aviso_url"] = aviso_url
    if aviso_txt is None:
        estado = "nv" if (candidatos and intentos_fallidos) else "no"
        cod["privacy_notice"] = estado
        # Sin aviso legible los indicadores que dependen de él no pueden ser «sí»
        for k in ("legal_framework", "data_subject_rights", "dpo_contact"):
            cod[k] = "nv" if estado == "nv" else "no"
        if grupo == "mundo":
            ck = [l for l in ls if RX_COOKIE.search(l["texto"]) or RX_COOKIE.search(l["url"])]
            cod["cookie_policy"] = "si" if ck else "no"
            ev["coincidencias"]["cookies"] = ck[0] if ck else None
        return cod, ev

    (dir_crudo / "aviso.txt").write_text(aviso_txt, encoding="utf-8")
    ev["aviso_palabras"] = palabras(aviso_txt)
    ev["aviso_sha256_texto"] = sha(aviso_txt.encode("utf-8"))

    m = RX_ALCANCE_PARCIAL.search(titulo)
    cod["privacy_notice"] = "parcial" if m else "si"
    ev["coincidencias"]["alcance_parcial"] = m.group(0) if m else None

    # --- marco jurídico ---
    rx_apl = re.compile(MARCO_APLICABLE.get(pais, "(?!)"), F)
    m_apl = rx_apl.search(aviso_txt)
    if m_apl:
        cod["legal_framework"] = "si"
    else:
        m_otro = RX_MARCO_CUALQUIERA.search(aviso_txt)
        cod["legal_framework"] = "parcial" if m_otro else "no"
        m_apl = m_otro
    ev["coincidencias"]["marco"] = m_apl.group(0) if m_apl else None

    # --- derechos ---
    enc = {k for k, rx in RX_DERECHOS.items() if rx.search(aviso_txt)}
    if re.search(r"\bARCO\b", aviso_txt):  # acceso, rectificación, cancelación, oposición
        enc |= {"acceso", "rectificacion", "supresion", "oposicion"}
    enc = sorted(enc)
    via = RX_VIA_EJERCICIO.search(aviso_txt)
    if len(enc) >= 3:
        cod["data_subject_rights"] = "si" if via else "parcial"
    else:
        cod["data_subject_rights"] = "no"
    ev["coincidencias"]["derechos"] = enc
    ev["coincidencias"]["via_ejercicio"] = bool(via)

    # --- contacto de privacidad (sin guardar direcciones) ---
    rol = RX_DPO_ROL.search(aviso_txt)
    correos_priv = [e for e in RX_EMAIL.findall(aviso_txt) if RX_EMAIL_PRIV.search(e.split("@")[0])]
    cod["dpo_contact"] = "si" if (rol or correos_priv) else "no"
    ev["coincidencias"]["contacto"] = {"rol": rol.group(0) if rol else None,
                                       "correo_dedicado": bool(correos_priv)}

    # --- política de cookies (solo grupo de referencia): documento distinto del aviso ---
    if grupo == "mundo":
        ls_aviso = enlaces(aviso_soup, aviso_url) if aviso_soup is not None else []
        ck = [l for l in ls + ls_aviso
              if (RX_COOKIE.search(l["texto"]) or RX_COOKIE.search(l["url"]))
              and urldefrag(l["url"])[0].rstrip("/") != aviso_url.rstrip("/")]
        cod["cookie_policy"] = "si" if ck else "no"
        ev["coincidencias"]["cookies"] = ck[0] if ck else None

    return cod, ev


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--censo", default="entrada/universities.json")
    ap.add_argument("--wayback", help="fecha AAAAMMDD de la instantánea de web.archive.org")
    ap.add_argument("--ids", nargs="*", type=int)
    ap.add_argument("--pausa", type=float, default=1.0,
                    help="segundos entre solicitudes (mínimo 5 con --wayback)")
    ap.add_argument("--salida")
    ap.add_argument("--rehacer", action="store_true", help="recodificar aunque ya exista el JSON")
    a = ap.parse_args()

    censo = json.loads(Path(a.censo).read_text(encoding="utf-8"))
    if a.ids:
        censo = [s for s in censo if s["id"] in set(a.ids)]
    modo = f"wayback_{a.wayback}" if a.wayback else "vivo"
    out = Path(a.salida or f"salida_{modo}")
    (out / "sitios").mkdir(parents=True, exist_ok=True)
    reglas_sha = sha(Path(__file__).read_bytes())
    d = Descargador(a.wayback, max(a.pausa, 5.0) if a.wayback else a.pausa)
    pendientes, seguidos = [], 0

    for i, s in enumerate(censo, 1):
        destino = out / "sitios" / f"{s['id']:03d}.json"
        if destino.exists() and not a.rehacer:
            continue
        dir_crudo = out / "crudo" / f"{s['id']:03d}"
        dir_crudo.mkdir(parents=True, exist_ok=True)
        try:
            cod, ev = codificar(s, d, dir_crudo)
            seguidos = 0
        except ErrorTransitorio as e:
            pendientes.append(s["sigla"]); seguidos += 1
            print(f"[{i:3d}/{len(censo)}] {s['sigla']:<14} PENDIENTE (error transitorio: {e})", flush=True)
            if seguidos >= 3:
                print("\nTres sitios seguidos con error transitorio: el servidor está limitando las "
                      "solicitudes o no hay conexión.\nSe detiene la corrida. Espere al menos 1 hora y "
                      "vuelva a ejecutar el mismo comando: continúa con los sitios pendientes.")
                return 2
            continue
        except Exception as e:  # un fallo de un sitio no detiene la corrida
            cod, ev = {}, {"error_script": f"{type(e).__name__}: {e}"}
        reg = {"id": s["id"], "grupo": s["grupo"], "sigla": s["sigla"], "pais": s["pais"],
               "url": s["url"], "modo": modo, "codigos": cod, "evidencia": ev,
               "script": "codificar_documental.py", "version": VERSION, "sha256_script": reglas_sha,
               "fecha_ejecucion_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        destino.write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"[{i:3d}/{len(censo)}] {s['sigla']:<14} " +
              " ".join(f"{k[:6]}={v}" for k, v in cod.items()), flush=True)
    print(f"\nListo. Resultados en {out / 'sitios'}")
    if pendientes:
        print(f"Pendientes por error transitorio ({len(pendientes)}): {', '.join(pendientes)}. "
              "Vuelva a ejecutar el mismo comando más tarde.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
