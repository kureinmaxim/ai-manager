#!/usr/bin/env python3
"""
Стабильный скрипт для запуска AI Manager с GUI
"""

import os
import sys
import threading
import time
import signal

# Устанавливаем переменные окружения для PyWebView
os.environ['PYWEBVIEW_GUI'] = 'cocoa'

# Импортируем необходимые модули
import webview
import requests

def run_flask():
    """Запускает Flask-приложение."""
    try:
        print("🚀 Запуск Flask сервера на http://127.0.0.1:5050")
        # Импортируем app здесь, чтобы избежать циклических импортов
        import app
        app.app.run(host='127.0.0.1', port=5050, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        print(f"❌ Ошибка запуска Flask сервера: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🔧 Запуск AI Manager с GUI...")
    
    # Останавливаем процессы на порту 5050
    os.system("lsof -ti:5050 | xargs kill -9 2>/dev/null || true")
    
    # Запускаем Flask в отдельном потоке
    print("🔄 Запуск Flask в отдельном потоке...")
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Ждем запуска сервера
    time.sleep(3)
    
    def on_closing():
        print("Окно закрывается, отправка запроса на выключение...")
        try:
            requests.get('http://127.0.0.1:5050/shutdown', timeout=1)
        except requests.exceptions.RequestException:
            pass
    
    # Создаем окно PyWebView
    print("🔄 Создание GUI окна...")
        # Загружаем версию из config.json
    try:
        import json
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            version = config.get('app_info', {}).get('version', '5.6.0')
    except:
        version = '5.6.0'

    window = webview.create_window(
        f'AI Manager v{version}',
        'http://127.0.0.1:5050',
        width=1280,
        height=800,
        resizable=True,
        frameless=False,
        easy_drag=True,
        fullscreen=False,
        on_top=False,
        confirm_close=False,
        background_color='#ffffff',
        transparent=False,
        text_select=True,
        focus=True
    )
    
    window.events.closing += on_closing
    
    # Запускаем GUI
    print("🚀 Запуск GUI приложения...")
    print("🌐 GUI окно должно открыться автоматически")
    print("📱 Если окно не появилось, откройте браузер: http://127.0.0.1:5050")
    
    webview.start(debug=False, gui='cocoa')
    
    print("Приложение закрыто.")

if __name__ == "__main__":
    main()
