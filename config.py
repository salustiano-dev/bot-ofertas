"""
Configuracoes do bot.
Preencha pelo arquivo .env (recomendado) ou direto aqui embaixo.
"""

import os

# Carrega variaveis do arquivo .env, se existir (nao quebra se nao tiver a lib).
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


# ---- Telegram ----
# Token que o @BotFather te da ao criar o bot.
BOT_TOKEN = os.getenv("BOT_TOKEN", "COLE_SEU_TOKEN_AQUI")

# ID do canal/grupo. Ex: "@meucanaldeofertas" (canal publico)
# ou "-1001234567890" (grupo/canal privado, numero negativo).
CHAT_ID = os.getenv("CHAT_ID", "@seucanaldeofertas")


# ---- Afiliados ----
# Sua tag da Amazon Associados (ex: "arthur-20").
AMAZON_TAG = os.getenv("AMAZON_TAG", "")


# ---- Agendamento ----
# Intervalo entre posts, em minutos (modo automatico).
INTERVALO_MINUTOS = int(os.getenv("INTERVALO_MINUTOS", "30"))

# Buscar ofertas novas automaticamente de tempos em tempos?
BUSCAR_AUTOMATICO = os.getenv("BUSCAR_AUTOMATICO", "true").lower() == "true"

# De quantas em quantas horas buscar ofertas novas.
BUSCAR_A_CADA_HORAS = int(os.getenv("BUSCAR_A_CADA_HORAS", "3"))


# ---- Busca de ofertas (buscar_ofertas.py) ----
# Feeds RSS de sites/canais de promocao. Troque pelos que voce quiser seguir.
# Muitos sites e blogs de ofertas publicam RSS. Cole aqui as URLs dos feeds.
FEEDS = [
    u.strip() for u in os.getenv(
        "FEEDS",
        # exemplos - substitua pelos feeds reais que voce usa:
        "https://www.exemplo-ofertas.com/feed,"
        "https://outro-site-de-promo.com/rss"
    ).split(",") if u.strip()
]

# So aceita ofertas com desconto igual ou maior que isso (%). 0 = aceita tudo.
DESCONTO_MINIMO = int(os.getenv("DESCONTO_MINIMO", "0"))

# Quantas ofertas novas pegar por busca (limite por feed).
MAX_POR_FEED = int(os.getenv("MAX_POR_FEED", "10"))


# ---- Mercado Livre (fonte_mercadolivre.py) ----
# Liga/desliga a busca no ML.
ML_ATIVO = os.getenv("ML_ATIVO", "true").lower() == "true"

# Credenciais da sua aplicacao (developers.mercadolivre.com.br).
# A SECRET fica so aqui/no .env, nunca compartilhe.
ML_APP_ID = os.getenv("ML_APP_ID", "")
ML_SECRET = os.getenv("ML_SECRET", "")

# Termos/produtos que o bot vai procurar no ML.
ML_TERMOS = [
    t.strip() for t in os.getenv(
        "ML_TERMOS",
        "celular,notebook,fone bluetooth,smart tv,air fryer,"
        "console playstation,monitor,cadeira gamer,perfume,tenis"
    ).split(",") if t.strip()
]

# Quantos itens olhar por termo.
ML_LIMITE_POR_TERMO = int(os.getenv("ML_LIMITE_POR_TERMO", "20"))

# So considera ofertas com desconto igual/maior que isso (%). Ex: 10.
ML_DESCONTO_MINIMO = int(os.getenv("ML_DESCONTO_MINIMO", "10"))

# A partir deste desconto (%), marca como "POSSIVEL BUG".
ML_BUG_DESCONTO = int(os.getenv("ML_BUG_DESCONTO", "70"))


# ---- Geral ----
# Rodar em modo teste (nao posta de verdade, so mostra na tela).
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
