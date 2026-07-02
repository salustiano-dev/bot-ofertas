FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Roda o bot em modo automatico (busca ofertas + posta)
CMD ["python", "bot.py"]
