# Servico systemd para rodar o bot 24h numa VPS Linux.
# 1. Ajuste WorkingDirectory e User para o seu caso.
# 2. Copie para /etc/systemd/system/bot-ofertas.service
# 3. sudo systemctl daemon-reload
#    sudo systemctl enable --now bot-ofertas
#    sudo journalctl -u bot-ofertas -f   (ver os logs)

[Unit]
Description=Bot de Ofertas Telegram
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/bot-ofertas
ExecStart=/usr/bin/python3 /home/ubuntu/bot-ofertas/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
