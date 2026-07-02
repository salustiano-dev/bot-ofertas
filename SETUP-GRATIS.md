# Deploy 100% grátis no GitHub Actions

O bot vai rodar sozinho a cada 30 minutos, de graça, sem servidor e sem cartão.
Siga os passos na ordem.

## Passo 1 — Criar o bot no Telegram
1. No Telegram, fale com **@BotFather** → `/newbot` → escolha nome e usuário.
2. Guarde o **TOKEN** que ele te der.

## Passo 2 — Criar o canal
1. Crie um **canal** no Telegram.
2. Adicione seu bot como **administrador** com permissão de **Publicar**.
3. Anote o `@nome_do_canal` (público) ou o ID `-100...` (privado).

## Passo 3 — Criar a conta e o repositório no GitHub
1. Crie conta em https://github.com (grátis).
2. Clique em **New repository** → dê um nome (ex: `bot-ofertas`).
3. Recomendado: **Público** (minutos ilimitados no Actions). Crie o repositório.

## Passo 4 — Subir os arquivos
Modo fácil (pelo navegador):
1. No repositório, clique em **Add file → Upload files**.
2. Arraste **todos** os arquivos desta pasta (incluindo a pasta `.github`).
3. **NÃO suba o arquivo `.env`** (ele tem segredos e não deve ir pro GitHub).
4. Clique em **Commit changes**.

> Dica: se o GitHub não deixar arrastar a pasta `.github`, crie o arquivo
> manualmente: **Add file → Create new file**, nome
> `.github/workflows/bot.yml`, e cole o conteúdo do arquivo.

## Passo 5 — Colocar as chaves nos Secrets (seguro)
No repositório: **Settings → Secrets and variables → Actions → New repository secret**.
Crie um secret para cada item:

| Nome do Secret | Valor |
|----------------|-------|
| `BOT_TOKEN` | token do @BotFather |
| `CHAT_ID` | @seucanal ou -100... |
| `AMAZON_TAG` | sua tag Amazon (ex: arthur-20) |
| `ML_APP_ID` | App ID do Mercado Livre |
| `ML_SECRET` | Secret Key do Mercado Livre |
| `ML_TERMOS` | celular,notebook,fone bluetooth,smart tv,air fryer |
| `ML_DESCONTO_MINIMO` | 10 |
| `ML_BUG_DESCONTO` | 70 |
| `FEEDS` | (opcional) feeds RSS separados por vírgula |

As chaves ficam criptografadas — ninguém vê, nem aparecem nos logs.

## Passo 6 — Ligar o Actions
1. Aba **Actions** do repositório → se pedir, clique em **I understand... enable**.
2. Abra o workflow **"Bot de Ofertas"** → botão **Run workflow** pra testar agora.
3. Veja os logs. Se tudo ok, ele passa a rodar sozinho a cada 30 min.

## Pronto!
- O bot busca ofertas (Amazon/ML/feeds), monta o post e publica no canal.
- Ofertas do **Mercado Livre** ficam seguras até você colar o link de afiliado
  (o ML não deixa gerar por API). Rode localmente `python bot.py --pendentes`
  pra ver quais faltam, gere no painel e faça commit do `ofertas.json`.

### Observações honestas
- O horário pode atrasar 5–15 min (normal no GitHub Actions).
- Se o repositório ficar 60 dias sem nenhuma atividade, o GitHub pausa o
  agendamento — basta fazer qualquer commit pra religar.
- Cada execução posta **1 oferta**. A cada 30 min = até 48 posts/dia.
  Pra mudar o ritmo, edite o `cron` no arquivo `.github/workflows/bot.yml`.
