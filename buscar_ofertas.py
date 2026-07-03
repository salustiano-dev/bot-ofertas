"""
Buscador automatico de ofertas.

Le os feeds RSS configurados em config.FEEDS (sites/blogs/canais de promocao),
extrai titulo, preco, imagem e link de cada oferta, aplica a tag da Amazon
quando o link e da Amazon, remove itens repetidos e adiciona ao ofertas.json.

Rodar sozinho:
    python buscar_ofertas.py

O bot.py tambem chama isso automaticamente se BUSCAR_AUTOMATICO=true.

Observacoes honestas:
- Precos nem sempre vem estruturados no RSS. A gente tenta achar "De R$ X por
  R$ Y" no titulo/resumo. Quando nao acha, marca preco 0 para voce revisar.
- Para Mercado Livre e Shopee o link de afiliado tem que ser gerado no painel
  deles; aqui o link entra "cru" e voce troca pelo de afiliado (ou pede pra eu
  automatizar via API quando voce tiver as credenciais).
"""

import json
import os
import re
import html

import feedparser

import config

OFERTAS_ARQUIVO = "ofertas.json"
VISTOS_ARQUIVO = ".ofertas_vistas.json"

# Regex para achar valores em reais (ex: R$ 1.299,90)
PRECO_RE = re.compile(r"R\$\s?([\d\.]+,\d{2})")


def _para_float(txt):
    return float(txt.replace(".", "").replace(",", "."))


def _extrair_precos(texto):
    """Tenta achar preco_de e preco_por num texto. Retorna (de, por)."""
    valores = [_para_float(v) for v in PRECO_RE.findall(texto or "")]
    if len(valores) >= 2:
        de, por = max(valores[0], valores[1]), min(valores[0], valores[1])
        return de, por
    if len(valores) == 1:
        return 0.0, valores[0]
    return 0.0, 0.0


def _extrair_imagem(entrada):
    # tenta varios lugares comuns onde o RSS coloca a imagem
    if "media_content" in entrada and entrada.media_content:
        return entrada.media_content[0].get("url", "")
    if "media_thumbnail" in entrada and entrada.media_thumbnail:
        return entrada.media_thumbnail[0].get("url", "")
    for enc in entrada.get("enclosures", []) or []:
        if str(enc.get("type", "")).startswith("image"):
            return enc.get("href", "")
    # procura <img src=...> no conteudo
    conteudo = ""
    if entrada.get("content"):
        conteudo = entrada["content"][0].get("value", "")
    conteudo += entrada.get("summary", "")
    m = re.search(r'<img[^>]+src="([^"]+)"', conteudo)
    return m.group(1) if m else ""


def _carregar_json(caminho, padrao):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return padrao


def _salvar_json(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def buscar():
    """Le os feeds e devolve lista de ofertas novas (ainda nao vistas)."""
    vistos = set(_carregar_json(VISTOS_ARQUIVO, []))
    novas = []

    if not config.FEEDS:
        print("[AVISO] Nenhum feed configurado. Preencha FEEDS no .env/config.")
        return novas

    for url in config.FEEDS:
        print(f"Lendo feed: {url}")
        try:
            feed = feedparser.parse(url)
        except Exception as e:
            print(f"[ERRO] Falha ao ler {url}: {e}")
            continue

        for entrada in feed.entries[: config.MAX_POR_FEED]:
            link = entrada.get("link", "").strip()
            if not link or link in vistos:
                continue

            titulo = html.unescape(entrada.get("title", "")).strip()
            texto = f"{titulo} {entrada.get('summary', '')}"
            de, por = _extrair_precos(texto)

            desconto = round((1 - por / de) * 100) if de > 0 and por > 0 else 0
            if config.DESCONTO_MINIMO and desconto < config.DESCONTO_MINIMO:
                continue

            oferta = {
                "titulo": titulo[:120],
                "imagem": _extrair_imagem(entrada),
                "preco_de": de,
                "preco_por": por,
                "cupom": "",
                "url": link,
                "link_afiliado": "",
            }
            novas.append(oferta)
            vistos.add(link)

    _salvar_json(VISTOS_ARQUIVO, list(vistos))
    return novas


def _buscar_todas_fontes():
    """Junta ofertas dos feeds RSS + Mercado Livre."""
    todas = buscar()  # feeds RSS
    try:
        import fonte_mercadolivre
        todas += fonte_mercadolivre.buscar()
    except Exception as e:
        print(f"[AVISO] Fonte Mercado Livre indisponivel: {e}")
    return todas


def atualizar():
    """Busca ofertas novas de todas as fontes e adiciona ao ofertas.json."""
    ofertas = _carregar_json(OFERTAS_ARQUIVO, [])
    urls_atuais = {o.get("url") for o in ofertas}

    novas = _buscar_todas_fontes()
    adicionadas = 0
    for o in novas:
        if o.get("url") and o["url"] not in urls_atuais:
            ofertas.append(o)
            urls_atuais.add(o["url"])
            adicionadas += 1

    _salvar_json(OFERTAS_ARQUIVO, ofertas)
    pendentes = sum(1 for o in ofertas if o.get("precisa_link"))
    print(f"[OK] {adicionadas} oferta(s) nova(s). Total: {len(ofertas)}. "
          f"Aguardando link de afiliado (ML): {pendentes}.")
    return adicionadas


if __name__ == "__main__":
    atualizar()
