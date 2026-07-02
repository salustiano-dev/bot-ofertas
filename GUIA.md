# Guia — Bot de Ofertas para Telegram

Este projeto cria um canal/grupo no Telegram que posta promoções
automaticamente, com imagem do produto, preço "De/Por", desconto e o seu
link de afiliado (Amazon, Mercado Livre e Shopee).

---

## 1. Instalar o necessário

Você precisa do **Python 3** instalado. Depois, na pasta do projeto:

```
pip install -r requirements.txt
```

---

## 2. Criar o bot no Telegram (pega o TOKEN)

1. No Telegram, abra a conversa com **@BotFather**.
2. Envie `/newbot` e siga: escolha um nome e um usuário (tem que terminar em `bot`).
3. O BotFather te devolve um **token** parecido com
   `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxx`. Guarde.

---

## 3. Criar o canal e adicionar o bot

1. Crie um **canal** no Telegram (recomendado para divulgação) ou um grupo.
2. Vá em **Administradores → Adicionar administrador** e adicione o seu bot.
   Dê permissão de **Publicar mensagens**.
3. Descubra o `CHAT_ID`:
   - Canal **público**: use `@nomedocanal`.
   - Canal/grupo **privado**: adicione o bot **@userinfobot** temporariamente,
     ou encaminhe uma mensagem do canal para **@getidsbot**. O ID começa com
     `-100...`.

---

## 4. Pegar seus links de afiliado

### Amazon (automático)
1. Cadastre-se no **Amazon Associados** (associados.amazon.com.br).
2. Pegue sua **tag** (algo como `arthur-20`).
3. Coloque essa tag no `config.py` em `AMAZON_TAG`.
   → Para produtos da Amazon, basta colar a URL normal no `ofertas.json`
   que o bot adiciona a sua tag sozinho.

### Mercado Livre e Shopee (link pronto)
Nesses dois, o link de afiliado é gerado no painel de cada programa — não dá
para montar só trocando a URL. Então:
1. **Mercado Livre**: entre na Central de Afiliados, cole a URL do produto,
   gere o link e copie.
2. **Shopee**: entre no Shopee Afiliados, gere o link do produto e copie.
3. Cole o link gerado no campo **`link_afiliado`** da oferta no `ofertas.json`.

> Se `link_afiliado` estiver preenchido, o bot sempre usa ele. Isso vale para
> qualquer loja.

---

## 5. Configurar

Abra `config.py` e preencha:
- `BOT_TOKEN` → token do passo 2
- `CHAT_ID` → do passo 3
- `AMAZON_TAG` → do passo 4
- `INTERVALO_MINUTOS` → de quanto em quanto tempo postar (ex: 30)

---

## 6. Cadastrar ofertas

Edite `ofertas.json`. Cada oferta tem:

| Campo | O que é |
|-------|---------|
| `titulo` | Nome do produto |
| `imagem` | URL da imagem do produto |
| `preco_de` | Preço antigo (ex: 299.90) |
| `preco_por` | Preço com desconto (ex: 179.90) |
| `cupom` | Código do cupom (deixe "" se não tiver) |
| `url` | Link do produto (usado se não houver link de afiliado) |
| `link_afiliado` | Link de afiliado pronto (ML/Shopee, ou qualquer loja) |

O desconto em % é calculado automaticamente.

---

## 7. Busca automática de ofertas

O bot pode encher a fila de ofertas sozinho, lendo **feeds RSS** de sites e
blogs de promoção.

1. No `.env`, coloque em `FEEDS` as URLs dos feeds que você quer seguir,
   separadas por vírgula. Muitos sites de oferta e blogs têm RSS (procure por
   "/feed" ou "/rss" no site, ou o ícone de RSS).
2. Ajuste se quiser: `DESCONTO_MINIMO` (só aceita ofertas com X% ou mais) e
   `BUSCAR_A_CADA_HORAS` (de quanto em quanto tempo procurar).

O que o buscador faz: lê cada feed, pega título, preço ("De R$X por R$Y"),
imagem e link, adiciona a tag da Amazon quando o link é da Amazon, ignora o que
já foi pego antes (não repete) e joga tudo no `ofertas.json`.

Comandos:
```
python bot.py --buscar     # só busca ofertas novas e sai
```
No modo automático (`python bot.py`), a busca roda sozinha de tempos em tempos
se `BUSCAR_AUTOMATICO=true`.

> Importante: o preço nem sempre vem no RSS. Quando o bot não acha o preço, ele
> salva a oferta com preço 0 para você completar antes de postar. Para Mercado
> Livre e Shopee, o link de afiliado precisa ser gerado no painel deles (passo 4)
> e colado no campo `link_afiliado`.

---

## 7b. Ofertas e bugs do Mercado Livre (automático)

O bot busca produtos no Mercado Livre, lê o preço atual e o original, calcula o
desconto e marca **"⚠️ POSSIVEL BUG"** quando o desconto é muito alto.

No `.env` preencha:
- `ML_APP_ID` e `ML_SECRET` → da sua aplicação (developers.mercadolivre.com.br).
- `ML_TERMOS` → produtos que quer seguir (ex: celular, notebook, air fryer…).
- `ML_DESCONTO_MINIMO` → desconto mínimo pra entrar (padrão 10%, pega até promo/cupom pequeno).
- `ML_BUG_DESCONTO` → a partir de quanto marca como bug (padrão 70%).

**Limitação importante do ML:** o Mercado Livre **não deixa gerar o link de
afiliado por API**. Então o bot acha a oferta sozinho, mas **segura** ela até
você colar o link de afiliado. Fluxo:

1. `python bot.py --pendentes` → lista as ofertas do ML esperando link.
2. Para cada uma, gere o link em https://www.mercadolivre.com.br/afiliados
   (é rápido: cola a URL do produto, gera o link).
3. Cole o link no campo `link_afiliado` daquela oferta no `ofertas.json`.
4. Pronto — o bot passa a postar ela normalmente.

> Amazon e Shopee (quando a API for aprovada) geram o link sozinhos. Só o ML
> tem esse passo manual, por limitação deles.

---

## 8. Rodar

Testar sem postar de verdade (mostra o post na tela):
```
DRY_RUN=true python bot.py --agora
```

Postar uma oferta agora, de verdade:
```
python bot.py --agora
```

Rodar em modo automático (busca ofertas + posta em rotação):
```
python bot.py
```

---

## 9. Deixar rodando 24h

Você tem 3 opções prontas no projeto:

**A) Railway / Render (mais fácil, na nuvem)**
1. Suba os arquivos para um repositório no GitHub.
2. Crie um projeto no Railway (ou Render) apontando para esse repositório.
3. Em *Variables*, adicione as mesmas chaves do `.env` (BOT_TOKEN, CHAT_ID,
   AMAZON_TAG, FEEDS, etc.).
4. O `Procfile`/`railway.json` já dizem para rodar `python bot.py`. Pronto.

**B) Docker (qualquer servidor)**
```
cp .env.example .env   # preencha
docker compose up -d    # roda em segundo plano, reinicia sozinho
docker compose logs -f  # ver os logs
```

**C) VPS Linux com systemd**
1. Copie a pasta para a VPS (ex: `/home/ubuntu/bot-ofertas`).
2. Ajuste caminhos/usuário em `bot-ofertas.service`.
3. 
```
sudo cp bot-ofertas.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now bot-ofertas
sudo journalctl -u bot-ofertas -f
```

---

## Sobre "bugs" de preço (erros de precificação)

Grupos de promoção às vezes divulgam erros de preço. Funciona, mas:
- A loja pode **cancelar o pedido** sem obrigação de entregar.
- Some rápido — precisa de monitoramento em tempo real.
- Divulgar como "compra garantida" pode queimar a reputação do seu grupo.

Recomendo sempre postar com o aviso de que o preço pode mudar/ser cancelado
(o bot já inclui esse aviso no rodapé de cada post).

---

## Próximos passos possíveis (é só pedir)

- **Busca automática de ofertas** em sites e marketplaces, jogando direto no `ofertas.json`.
- **Monitor de preço** que avisa quando um produto cai abaixo de um valor.
- **Hospedagem 24h** para o bot rodar sem seu PC ligado.
- **Botão de link** clicável em vez de texto, e templates de imagem personalizados.
