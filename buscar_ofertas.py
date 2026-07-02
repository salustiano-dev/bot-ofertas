"""
Bot de ofertas para Telegram.

O que faz:
- Le as ofertas do arquivo ofertas.json
- Monta o link de afiliado (Amazon automatico; ML/Shopee com link pronto)
- Monta um post com: imagem, titulo, "De R$X por R$Y", % de desconto, cupom e link
- Posta no seu canal/grupo automaticamente, uma oferta por vez, no intervalo definido

Como rodar:
    pip install -r requirements.txt
    python bot.py            # roda automatico (busca ofertas + posta)
    python bot.py --agora    # posta UMA oferta agora e sai (bom pra testar)
    python bot.py --buscar   # so busca ofertas novas e sai

Dica: coloque DRY_RUN=true no ambiente para simular sem postar de verdade.
"""

import json
import sys
import time

import requests
import schedule

import config
from afiliados import montar_link

try:
    import buscar_ofertas
except Exception:
    buscar_ofertas = None

OFERTAS_ARQUIVO = "ofertas.json"
INDICE_ARQUIVO = ".ultimo_indice"  # lembra qual oferta ja foi postada


def carregar_ofertas():
    with open(OFERTAS_ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)


def ler_indice():
    try:
        with open(INDICE_ARQUIVO, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def salvar_indice(i):
    with open(INDICE_ARQUIVO, "w") as f:
        f.write(str(i))


def reais(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def montar_texto(oferta):
    de = float(oferta["preco_de"])
    por = float(oferta["preco_por"])
    desconto = round((1 - por / de) * 100) if de > 0 else 0
    link = montar_link(oferta)

    linhas = []
    linhas.append(f"🔥 <b>{oferta['titulo']}</b>")
    linhas.append("")
    linhas.append(f"❌ De: <s>{reais(de)}</s>")
    linhas.append(f"✅ Por: <b>{reais(por)}</b>  (-{desconto}%)")
    if oferta.get("cupom"):
        linhas.append(f"🏷️ Cupom: <code>{oferta['cupom']}</code>")
    linhas.append("")
    linhas.append(f"🛒 <a href=\"{link}\">COMPRAR AGORA</a>")
    linhas.append("")
    linhas.append("⚠️ Promoções por tempo limitado, o preço pode mudar.")
    return "\n".join(linhas)


def postar(oferta):
    texto = montar_texto(oferta)
    imagem = oferta.get("imagem", "").strip()

    if config.DRY_RUN:
        print("----- SIMULACAO (DRY_RUN) -----")
        print("Imagem:", imagem or "(sem imagem)")
        print(texto)
        print("-------------------------------")
        return True

    if imagem:
        url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendPhoto"
        dados = {"chat_id": config.CHAT_ID, "photo": imagem,
                 "caption": texto, "parse_mode": "HTML"}
    else:
        url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage"
        dados = {"chat_id": config.CHAT_ID, "text": texto,
                 "parse_mode": "HTML", "disable_web_page_preview": False}

    r = requests.post(url, data=dados, timeout=30)
    if r.status_code == 200:
        print(f"[OK] Postado: {oferta['titulo']}")
        return True
    print(f"[ERRO] {r.status_code}: {r.text}")
    return False


def _pode_postar(oferta):
    """Nao posta ofertas que ainda esperam link de afiliado (ex: ML)."""
    if oferta.get("precisa_link") and not oferta.get("link_afiliado", "").strip():
        return False
    return True


def postar_proxima():
    ofertas = carregar_ofertas()
    if not ofertas:
        print("Nenhuma oferta no ofertas.json")
        return

    n = len(ofertas)
    inicio = ler_indice() % n
    # procura a proxima oferta que pode ser postada (pula as sem link)
    for passo in range(n):
        i = (inicio + passo) % n
        if _pode_postar(ofertas[i]):
            postar(ofertas[i])
            salvar_indice((i + 1) % n)
            return
    print("Nenhuma oferta pronta para postar (todas aguardando link de afiliado).")


def buscar_novas():
    if buscar_ofertas is None:
        print("[AVISO] buscar_ofertas indisponivel (instale feedparser).")
        return
    try:
        buscar_ofertas.atualizar()
    except Exception as e:
        print(f"[ERRO] Falha ao buscar ofertas: {e}")


def listar_pendentes():
    """Mostra as ofertas que esperam link de afiliado (ex: Mercado Livre)."""
    ofertas = carregar_ofertas()
    pend = [o for o in ofertas
            if o.get("precisa_link") and not o.get("link_afiliado", "").strip()]
    if not pend:
        print("Nenhuma oferta aguardando link. Tudo pronto pra postar!")
        return
    print(f"{len(pend)} oferta(s) esperando link de afiliado:\n")
    for o in pend:
        print(f"- {o['titulo']}")
        print(f"  Produto: {o['url']}")
        print(f"  Gere o link em: https://www.mercadolivre.com.br/afiliados "
              f"e cole no campo 'link_afiliado' desta oferta no ofertas.json\n")


def main():
    if "--pendentes" in sys.argv:
        listar_pendentes()
        return

    if "--buscar" in sys.argv:
        buscar_novas()
        return

    if "--agora" in sys.argv:
        postar_proxima()
        return

    print(f"Bot iniciado. Postando a cada {config.INTERVALO_MINUTOS} min.")
    if config.BUSCAR_AUTOMATICO:
        print(f"Buscando ofertas novas a cada {config.BUSCAR_A_CADA_HORAS}h.")
        buscar_novas()  # busca uma vez ao iniciar
        schedule.every(config.BUSCAR_A_CADA_HORAS).hours.do(buscar_novas)
    print("Pressione Ctrl+C para parar.")

    postar_proxima()  # posta uma logo ao iniciar
    schedule.every(config.INTERVALO_MINUTOS).minutes.do(postar_proxima)
    while True:
        schedule.run_pending()
        time.sleep(5)


if __name__ == "__main__":
    main()
