<p align="center">
      <img src="https://i.ibb.co/d9mzMtH/Logo-Geo-Rinch.png" alt="Project logo" width="400">
</p>

<p align="center">
  <a href="https://github.com/DevBrain888/GeoRinch/stargazers"><img src="https://img.shields.io/github/stars/DevBrain888/GeoRinch" alt="Stars Badge"/></a>
  <a href="https://github.com/DevBrain888/GeoRinch/network/members"><img src="https://img.shields.io/github/forks/DevBrain888/GeoRinch" alt="Forks Badge"/></a>
  <a href="https://github.com/DevBrain888/GeoRinch/pulls"><img src="https://img.shields.io/github/issues-pr/DevBrain888/GeoRinch" alt="Pull Requests Badge"/></a>
  <a href="https://github.com/DevBrain888/GeoRinch/issues"><img src="https://img.shields.io/github/issues/DevBrain888/GeoRinch" alt="Issues Badge"/></a>
  <a href="https://github.com/DevBrain888/GeoRinch/graphs/contributors"><img alt="GitHub contributors" src="https://img.shields.io/github/contributors/DevBrain888/GeoRinch?color=2b9348"></a>
  <a href="https://github.com/DevBrain888/GeoRinch/blob/master/LICENSE"><img src="https://img.shields.io/github/license/DevBrain888/GeoRinch?color=2b9348" alt="License Badge"/></a>

</p>
<p align="center">
  <img src="https://img.shields.io/badge/python_3.12%2B-blue" alt="Python Version">
  <img src="https://img.shields.io/badge/version-v_1.0.0-violet" alt="GeoRinch Version">
</p>

## About

🏛 Бот Навигация ФЭК РГЭУ (РИНХ):
местонахождение аудиторий, ближайшая концелярия 📌, место для вашего перекуса😋

## Documentation

### Local launch (for development)

Вариант A — Polling (просто и без внешнего URL):

1. Клонировать и установить зависимости
   ```bash
   git clone https://github.com/DevBrain888/GeoRinch.git
   cd GeoRinch
   python -m venv .venv
   # Windows
   .venv\Scripts\Activate.ps1
   # Linux/Mac
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Создать локальный `.env` (рекомендуется отдельный тестовый токен):
   ```env
   BOT_TOKEN=your_dev_bot_token
   USE_WEBHOOK=false
   ```
3. Запуск
   ```bash
   python main.py
   ```
   Откройте чат с dev-ботом в Telegram и отправьте /start.

Вариант B — Локальный Webhook через туннель (ngrok/Cloudflare Tunnel):

1. `.env` для локального webhook
   ```env
   BOT_TOKEN=your_dev_bot_token
   USE_WEBHOOK=true
   WEBHOOK_HOST=127.0.0.1
   WEBHOOK_PORT=8000
   ```
2. Запуск приложения
   ```bash
   python main.py
   # Локальная проверка
   curl.exe http://127.0.0.1:8000/health
   ```
3. Поднять туннель и получить публичный https URL
   - ngrok: `ngrok http 8000`
   - возьмите выданный URL вида `https://....ngrok-free.app`
4. Установить webhook на публичный URL (обязательно добавить токен в конец пути и разрешить callback_query):
   ```bash
   curl "https://api.telegram.org/bot<DEV_TOKEN>/setWebhook?url=https://<NGROK_URL>/webhook/<DEV_TOKEN>&allowed_updates=%5B%22message%22,%22callback_query%22%5D"
   curl "https://api.telegram.org/bot<DEV_TOKEN>/getWebhookInfo"
   ```
   При смене URL туннеля — переустановите webhook.

Примечание: для разработки удобнее использовать отдельного бота (DEV_TOKEN), чтобы не мешать продакшену.

---

### Продакшен на Ubuntu VPS (Nginx + HTTPS + Webhook)

Требования: Ubuntu 22.04+, домен, публичный IPv4.

1) Базовая подготовка сервера
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3-venv python3-pip nginx ufw curl
sudo ufw status # Проверте работает ли увас в принципе ufw
sudo ufw allow OpenSSH 
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

2) Клонирование проекта и зависимости
```bash
cd /opt
sudo git clone https://github.com/DevBrain888/GeoRinch.git
sudo chown -R $USER:$USER GeoRinch
cd GeoRinch
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

3) DNS
— У регистратора создайте A‑запись `bot.example.com` → IP вашего VPS. Проверьте `dig +short bot.example.com`.

4) Конфигурация приложения (.env)
```env
BOT_TOKEN=your_prod_bot_token
USE_WEBHOOK=true
WEBHOOK_HOST=127.0.0.1
WEBHOOK_PORT=8000
```

5) Проверка приложения локально на сервере
```bash
python main.py
curl -I http://127.0.0.1:8000/health   # ожидается 200 OK
# Остановите Ctrl+C перед настройкой Nginx/HTTPS
```

6) Nginx (reverse‑proxy на 127.0.0.1:8000)
```bash
sudo bash -lc 'cat > /etc/nginx/sites-available/georinch << "CONF"
server {
    listen 80;
    server_name bot.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
CONF'
sudo ln -sf /etc/nginx/sites-available/georinch /etc/nginx/sites-enabled/georinch
sudo nginx -t && sudo systemctl reload nginx
```

7) HTTPS (Let’s Encrypt)
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d bot.example.com --redirect --agree-tos -m you@example.com -n
```

8) Запуск приложения в прод и установка webhook (разрешаем callback_query)
```bash
# В venv
source /opt/GeoRinch/.venv/bin/activate
python /opt/GeoRinch/main.py

# В другом окне/терминале
curl -I https://bot.example.com/health

# Важно: в webhook URL обязательно токен в конце + allowed_updates с callback_query
curl "https://api.telegram.org/bot<PROD_TOKEN>/setWebhook?url=https://bot.example.com/webhook/<PROD_TOKEN>&allowed_updates=%5B%22message%22,%22callback_query%22%5D"
curl "https://api.telegram.org/bot<PROD_TOKEN>/getWebhookInfo"
```

9) Проверка
— Откройте чат с ботом и отправьте `/start`.
— В логах должны появиться POST запросы на `/webhook/<TOKEN>` и ответ пользователю.

## 📍 Построение маршрутов между кабинетами

Бот поддерживает построение маршрутов между кабинетами на плане этажа. Для корректной работы необходимо заполнить координаты кабинетов, дверей и точек коридора.

### 📋 Как заполнить координаты

1. **Используйте готовый скрипт** (рекомендуется):
   ```bash
   python get_coordinates.py floorplans/floor_1.png
   ```
   Кликайте на изображении для получения координат точек.

2. **Или используйте графический редактор** (Paint, GIMP и т.д.):
   - Откройте план этажа в редакторе
   - Наведите курсор на нужную точку
   - Запишите координаты (X, Y)

3. **Заполните шаблон** `coordinates_template.txt`:
   - Координаты центров кабинетов
   - Координаты дверей кабинетов (точки входа в коридор)
   - Координаты точек коридора (узлы навигации)

4. **Перенесите координаты** в `pathfinder.py`:
   - Обновите словарь `COORDS_FLOOR_1`
   - Проверьте граф связей `GRAPH_FLOOR_1`

📖 **Подробное руководство:** см. [COORDINATES_GUIDE.md](COORDINATES_GUIDE.md)  
⚡ **Быстрая инструкция:** см. [SETUP_COORDINATES.md](SETUP_COORDINATES.md)

### ⚠️ Важные моменты

- **Двери должны быть в коридоре**, а не в стенах кабинетов
- **Точки коридора должны быть в центре коридора**, не в стенах
- Все точки должны образовывать **связную сеть** (можно пройти от любой точки до любой)

### 🔧 Для новых этажей

Для добавления построения маршрутов на других этажах:
1. Определите координаты для этажа (аналогично 1 этажу)
2. Добавьте их в `COORDS_BY_FLOOR` и `GRAPH_BY_FLOOR` в `pathfinder.py`
3. Обновите логику в `handlers/route.py` для поддержки новых этажей

## 🚀 Distribute

### 📦 Минимальные требования
- Python 3.12+
- pip
- git
- curl
- python3-venv (на Ubuntu)
- Nginx (для прод вебхука)
- Certbot + плагин nginx (для HTTPS в проде)
- UFW (фаервол на Ubuntu, по желанию)
- (Опционально для локальных вебхуков) ngrok или Cloudflare Tunnel

### 🔧 Troubleshooting
- Если не приходят нажатия инлайн‑кнопок в режиме webhook:
  - Переустановите webhook с `allowed_updates` (см. команды выше).
  - Убедитесь, что URL публичный HTTPS и совпадает с `/webhook/<TOKEN>`.
  - При смене адреса туннеля (ngrok) — перевыставьте webhook.

## Contributors

Спасибо этим замечательным людям:

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore -->
| [<img src="https://github.com/DevBrain888.png" width="75px;"/><br /><sub><b>DevBrain888</b></sub>]()<br />[🎨](#design-DevBrain888) [💻](https://github.com/DevBrain888/GeoRinch/commits?author=DevBrain888) [📖](https://github.com/DevBrain888/GeoRinch/commits?author=DevBrain888) [🤔](#ideas-DevBrain888) | [<img src="https://github.com/ZeroterKnows.png" width="75px;"/><br /><sub><b>ZeroterKnows</b></sub>]()<br />[🐛](https://github.com/ZeroterKnows/GeoRinch/issues?q=author%ZeroterKnows) [💻](https://github.com/ZeroterKnows/GeoRinch/commits?author=ZeroterKnows) |
| :---: | :---: |
<!-- ALL-CONTRIBUTORS-LIST:END -->


## License

[![GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Этот проект лицензирован в соответствии с [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0).

Насколько это возможно в соответствии с законом, все авторы согласились распространять эту работу под лицензией GNU GPL версии 3.0.
