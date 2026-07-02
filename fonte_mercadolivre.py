"""
Fonte de ofertas: Mercado Livre.

O que faz:
- Autentica na API do ML usando App ID + Secret (fluxo client_credentials).
- Busca produtos pelos termos configurados (config.ML_TERMOS).
- Le preco atual e preco original, calcula o desconto.
- Marca "possivel bug" quando o desconto passa de config.ML_BUG_DESCONTO.
- Devolve as ofertas para entrar no ofertas.json.

Importante (limitacao do ML):
- O Mercado Livre NAO libera gerar link de afiliado por API. Entao as ofertas
  do ML entram com o campo "link_afiliado" vazio e "precisa_link": true.
  O bot NAO posta essas ate voce colar o link de afiliado (gerado no painel
  https://www.mercadolivre.com.br/afiliados). Assim voce nao perde comissao.
"""

import time
import requests

import config

TOKEN_URL = "https://api.mercadolibre.com/oauth/token"
SEARCH_URL = "https://api.mercadolibre.com/sites/MLB/search"

_token_cache = {"token": None, "expira_em": 0}


def _get_token():
    """Pega (e reaproveita) um access token de aplicacao."""
    agora = time.time()
    if _token_cache["token"] and agora < _token_cache["expira_em"]:
        return _token_cache["token"]

    if not config.ML_APP_ID or not config.ML_SECRET:
        raise RuntimeError("Faltam ML_APP_ID / ML_SECRET no .env")

    resp = requests.post(TOKEN_URL, data={
        "grant_type": "client_credentials",
        "client_id": config.ML_APP_ID,
        "client_secret": config.ML_SECRET,
    }, headers={"Accept": "application/json"}, timeout=30)
    resp.raise_for_status()
    dados = resp.json()
    _token_cache["token"] = dados["access_token"]
    # renova um pouco antes de expirar
    _token_cache["expira_em"] = agora + int(dados.get("expires_in", 3600)) - 60
    return _token_cache["token"]


def _preco_original(item):
    """Tenta achar o preco 'de' (antes do desconto)."""
    for campo in ("original_price", "regular_amount"):
        v = item.get(campo)
        if v:
            return float(v)
    # as vezes vem dentro de 'sale_price'
    sp = item.get("sale_price") or {}
    if isinstance(sp, dict) and sp.get("regular_amount"):
        return float(sp["regular_amount"])
    return 0.0


def _parse_item(item):
    por = float(item.get("price") or 0)
    de = _preco_original(item)
    if de <= por:
        de = 0.0  # sem promo declarada
    desconto = round((1 - por / de) * 100) if de > por > 0 else 0

    titulo = item.get("title", "")[:120]
    if desconto >= config.ML_BUG_DESCONTO and desconto > 0:
        titulo = f"⚠️ POSSIVEL BUG ({desconto}% OFF) - {titulo}"

    return {
        "titulo": titulo,
        "imagem": (item.get("thumbnail", "") or "").replace("http://", "https://")
                  .replace("-I.jpg", "-O.jpg"),  # imagem em melhor qualidade
        "preco_de": de,
        "preco_por": por,
        "desconto": desconto,
        "cupom": "",
        "url": item.get("permalink", ""),
        "link_afiliado": "",       # ML nao gera por API -> preencher no painel
        "precisa_link": True,      # bot segura ate ter link de afiliado
        "loja": "mercadolivre",
    }


def buscar():
    """Busca ofertas no ML pelos termos configurados. Retorna lista."""
    if not config.ML_ATIVO:
        return []

    token = _get_token()
    headers = {"Authorization": f"Bearer {token}"}
    achados = []

    for termo in config.ML_TERMOS:
        try:
            r = requests.get(SEARCH_URL, headers=headers, params={
                "q": termo,
                "limit": config.ML_LIMITE_POR_TERMO,
                "sort": "price_asc",
            }, timeout=30)
            r.raise_for_status()
            resultados = r.json().get("results", [])
        except Exception as e:
            print(f"[ERRO ML] termo '{termo}': {e}")
            continue

        for item in resultados:
            oferta = _parse_item(item)
            if oferta["desconto"] >= config.ML_DESCONTO_MINIMO:
                achados.append(oferta)

        time.sleep(0.3)  # gentileza com a API

    print(f"[ML] {len(achados)} oferta(s) encontrada(s).")
    return achados


if __name__ == "__main__":
    for o in buscar():
        print(f"- {o['preco_por']:.2f} (de {o['preco_de']:.2f}) "
              f"{o['desconto']}% :: {o['titulo']}")
