# 🚀 Руководство по развертыванию

## 📋 Содержание

- [Локальное развертывание](#-локальное-развертывание)
- [Продакшн развертывание](#-продакшн-развертывание)
- [Docker развертывание](#-docker-развертывание)
- [Облачное развертывание](#-облачное-развертывание)
- [Мониторинг](#-мониторинг)

## 🏠 Локальное развертывание

### Требования

- Python 3.8+
- pip
- Git

### Быстрая установка

```bash
# Клонирование репозитория
git clone https://github.com/your-username/ai-manager.git
cd ai-manager

# Создание виртуального окружения
python3 -m venv venv

# Активация окружения
source venv/bin/activate  # macOS/Linux
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt

# Настройка окружения
cp .env.example .env
# Отредактируйте .env файл

# Запуск приложения
python3 run_app.py
```

### Подробная настройка

#### 1. Настройка переменных окружения

Создайте файл `.env`:

```bash
# Конфигурация YubiKey
YUBIKEY_STATIC_PASSWORDS=demo123,test123,admin123

# Секретный ключ для Flask
SECRET_KEY=ваш_сгенерированный_ключ

# Настройки приложения
FLASK_ENV=development
FLASK_DEBUG=True

# Настройки шифрования
ENCRYPTION_KEY_FILE=.env

# Настройки базы данных (опционально)
DATABASE_URL=sqlite:///data/app.db

# Настройки логирования
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

#### 2. Генерация секретного ключа

```bash
python3 -c "from cryptography.fernet import Fernet; print('SECRET_KEY=' + Fernet.generate_key().decode())"
```

#### 3. Создание необходимых директорий

```bash
mkdir -p data logs uploads temp
```

#### 4. Настройка прав доступа

```bash
# Установка прав на выполнение
chmod +x run_app.py
chmod +x app.py

# Установка прав на директории
chmod 755 data logs uploads
```

## 🌐 Продакшн развертывание

### Требования

- Linux сервер (Ubuntu 20.04+)
- Python 3.8+
- Nginx
- Gunicorn
- Supervisor

### Установка на сервере

#### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python
sudo apt install python3 python3-pip python3-venv

# Установка Nginx
sudo apt install nginx

# Установка Supervisor
sudo apt install supervisor
```

#### 2. Настройка пользователя

```bash
# Создание пользователя для приложения
sudo adduser ai-manager
sudo usermod -aG sudo ai-manager

# Переключение на пользователя
sudo su - ai-manager
```

#### 3. Развертывание приложения

```bash
# Клонирование репозитория
git clone https://github.com/your-username/ai-manager.git
cd ai-manager

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
pip install gunicorn

# Настройка окружения
cp .env.example .env
nano .env  # Настройте переменные окружения
```

#### 4. Настройка Gunicorn

Создайте файл `gunicorn.conf.py`:

```python
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True
```

#### 5. Настройка Supervisor

Создайте файл `/etc/supervisor/conf.d/ai-manager.conf`:

```ini
[program:ai-manager]
command=/home/ai-manager/ai-manager/venv/bin/gunicorn -c gunicorn.conf.py app:app
directory=/home/ai-manager/ai-manager
user=ai-manager
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/ai-manager/app.log
```

#### 6. Настройка Nginx

Создайте файл `/etc/nginx/sites-available/ai-manager`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/ai-manager/ai-manager/static;
        expires 30d;
    }
}
```

#### 7. Активация конфигураций

```bash
# Активация Nginx
sudo ln -s /etc/nginx/sites-available/ai-manager /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Активация Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ai-manager
```

## 🐳 Docker развертывание

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.9-slim

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка зависимостей Python
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Создание необходимых директорий
RUN mkdir -p data logs uploads

# Установка прав доступа
RUN chmod +x run_app.py app.py

# Открытие порта
EXPOSE 5050

# Команда запуска
CMD ["python3", "run_app.py"]
```

### Docker Compose

Создайте файл `docker-compose.yml`:

```yaml
version: '3.8'

services:
  ai-manager:
    build: .
    ports:
      - "5050:5050"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - YUBIKEY_STATIC_PASSWORDS=${YUBIKEY_STATIC_PASSWORDS}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./static:/app/static
    depends_on:
      - ai-manager
    restart: unless-stopped
```

### Запуск с Docker

```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

## ☁️ Облачное развертывание

### Heroku

#### 1. Создание Procfile

```bash
# Procfile
web: gunicorn app:app
```

#### 2. Настройка переменных окружения

```bash
# Установка Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Логин в Heroku
heroku login

# Создание приложения
heroku create your-ai-manager

# Настройка переменных окружения
heroku config:set SECRET_KEY=ваш_ключ
heroku config:set YUBIKEY_STATIC_PASSWORDS=demo123,test123,admin123
heroku config:set FLASK_ENV=production
```

#### 3. Деплой

```bash
# Деплой на Heroku
git push heroku main

# Открытие приложения
heroku open
```

### AWS EC2

#### 1. Создание EC2 инстанса

```bash
# Подключение к инстансу
ssh -i your-key.pem ubuntu@your-ip

# Обновление системы
sudo apt update && sudo apt upgrade -y
```

#### 2. Установка зависимостей

```bash
# Установка Python и зависимостей
sudo apt install python3 python3-pip python3-venv nginx

# Создание пользователя
sudo adduser ai-manager
sudo usermod -aG sudo ai-manager
```

#### 3. Развертывание приложения

```bash
# Переключение на пользователя
sudo su - ai-manager

# Клонирование репозитория
git clone https://github.com/your-username/ai-manager.git
cd ai-manager

# Настройка виртуального окружения
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn
```

#### 4. Настройка systemd

Создайте файл `/etc/systemd/system/ai-manager.service`:

```ini
[Unit]
Description=AI Manager
After=network.target

[Service]
User=ai-manager
WorkingDirectory=/home/ai-manager/ai-manager
Environment="PATH=/home/ai-manager/ai-manager/venv/bin"
ExecStart=/home/ai-manager/ai-manager/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 5. Активация сервиса

```bash
# Активация сервиса
sudo systemctl enable ai-manager
sudo systemctl start ai-manager

# Проверка статуса
sudo systemctl status ai-manager
```

## 📊 Мониторинг

### Логирование

```bash
# Просмотр логов приложения
tail -f logs/app.log

# Просмотр логов безопасности
tail -f logs/security.log

# Просмотр логов Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Мониторинг производительности

```bash
# Установка инструментов мониторинга
pip install psutil

# Проверка использования ресурсов
htop
df -h
free -h
```

### Алерты

Настройте алерты для:
- Высокого использования CPU (>80%)
- Высокого использования памяти (>90%)
- Ошибок в логах
- Недоступности приложения

## 🔧 Устранение неполадок

### Частые проблемы

#### 1. Порт занят
```bash
# Проверка занятых портов
sudo netstat -tulpn | grep :5050

# Остановка процесса
sudo kill -9 PID
```

#### 2. Проблемы с правами доступа
```bash
# Исправление прав доступа
sudo chown -R ai-manager:ai-manager /home/ai-manager/ai-manager
sudo chmod -R 755 /home/ai-manager/ai-manager
```

#### 3. Проблемы с зависимостями
```bash
# Переустановка зависимостей
pip install --force-reinstall -r requirements.txt
```

### Отладка

```bash
# Запуск в режиме отладки
FLASK_ENV=development FLASK_DEBUG=True python3 app.py

# Проверка конфигурации
python3 -c "import app; print('Конфигурация загружена')"
```

---

**Примечание:** Это базовое руководство по развертыванию. Для продакшн окружения рекомендуется дополнительная настройка безопасности и мониторинга. 