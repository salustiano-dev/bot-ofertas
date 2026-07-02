# Bot de Ofertas para Telegram

Canal/grupo no Telegram que **busca promoções automaticamente** e **posta**
com imagem do produto, preço "De/Por", % de desconto, cupom e o **seu link de
afiliado** (Amazon, Mercado Livre e Shopee).

## Arquivos

| Arquivo | Para que serve |
|---------|----------------|
| `bot.py` | Programa principal: busca ofertas e posta no Telegram. |
| `buscar_ofertas.py` | Lê feeds RSS de sites de promoção e enche o `ofertas.json`. |
| `afiliados.py` | Monta o link de afiliado (Amazon automático; ML/Shopee link pronto). |
| `config.py` | Configurações (lê do arquivo `.env`). |
| `ofertas.json` | Fila de ofertas a postar. |
| `.env.example` | Modelo de configuração — copie para `.env`. |
| `requirements.txt` | Dependências Python. |
| `Dockerfile` / `docker-compose.yml` | Rodar em container. |
| `Procfile` / `railway.json` | Deploy em Railway/Render. |
| `bot-ofertas.service` | Rodar 24h numa VPS com systemd. |
| `GUIA.md` | Passo a passo completo em português. |

## Início rápido

```
pip install -r requirements.txt
cp .env.example .env      # e preencha seus dados
DRY_RUN=true python bot.py --agora   # testa sem postar
python bot.py             # roda de verdade (busca + posta 24h)
```

Comandos úteis:
- `python bot.py` — modo automático (busca ofertas + posta em rotação).
- `python bot.py --agora` — posta uma oferta agora e sai.
- `python bot.py --buscar` — só busca ofertas novas e sai.

Leia o **GUIA.md** para o passo a passo (criar bot no @BotFather, canal,
tags de afiliado e hospedagem 24h).
