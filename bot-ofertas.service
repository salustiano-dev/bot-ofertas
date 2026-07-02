"""
Gerador de links de afiliado.

- Amazon: adiciona automaticamente sua tag (?tag=SEU-TAG-20) em qualquer link.
- Mercado Livre e Shopee: nao ha jeito confiavel de gerar o link so trocando
  parametros na URL. Voce gera o link de afiliado no painel de cada programa
  e cola pronto no ofertas.json (campo "link_afiliado"). Este modulo apenas
  repassa esse link.

Assim o bot funciona 100%: Amazon automatico, ML/Shopee com link ja gerado.
"""

from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import config


def _detectar_loja(url: str) -> str:
    u = url.lower()
    if "amazon." in u or "amzn.to" in u:
        return "amazon"
    if "mercadolivre" in u or "mercadolibre" in u or "/sec/" in u or "mercadol" in u:
        return "mercadolivre"
    if "shopee" in u or "shp.ee" in u:
        return "shopee"
    return "outro"


def _amazon_com_tag(url: str, tag: str) -> str:
    """Adiciona/atualiza o parametro tag na URL da Amazon."""
    partes = urlparse(url)
    q = parse_qs(partes.query)
    q["tag"] = [tag]
    nova_query = urlencode({k: v[0] for k, v in q.items()})
    return urlunparse(partes._replace(query=nova_query))


def montar_link(oferta: dict) -> str:
    """
    Retorna o link final que vai no post.

    Regras:
    1. Se a oferta ja tem 'link_afiliado', usa ele (caso de ML e Shopee).
    2. Se for Amazon e tiver so a URL do produto, adiciona sua tag.
    3. Senao, devolve a URL normal (sem afiliado) e avisa no log.
    """
    link_pronto = oferta.get("link_afiliado", "").strip()
    if link_pronto:
        return link_pronto

    url = oferta.get("url", "").strip()
    if not url:
        return ""

    loja = _detectar_loja(url)

    if loja == "amazon" and config.AMAZON_TAG:
        return _amazon_com_tag(url, config.AMAZON_TAG)

    # ML e Shopee exigem link gerado no painel
    if loja in ("mercadolivre", "shopee"):
        print(f"[AVISO] Oferta '{oferta.get('titulo')}' e da {loja}. "
              f"Cole o link de afiliado no campo 'link_afiliado' do ofertas.json.")
    return url


if __name__ == "__main__":
    # teste rapido
    exemplo = {"titulo": "Fone Teste",
               "url": "https://www.amazon.com.br/dp/B08XYZ123"}
    print(montar_link(exemplo))
