import json
from pathlib import Path
from flask import session, redirect, url_for, flash, request
from yubico_client import Yubico
from yubico_client.yubico_exceptions import YubicoError, InvalidClientIdError, SignatureVerificationError
from datetime import datetime
import socket
import re

def check_internet_connection(host="api.yubico.com", port=443, timeout=3):
    """Проверяет наличие интернет-соединения, пытаясь подключиться к хосту Yubico."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except (socket.error, socket.timeout) as ex:
        print(f"🔌 Интернет-соединение отсутствует: {ex}")
        return False

class YubiKeyAuth:
    def __init__(self, app_data_dir, static_passwords=None):
        self.config_file = Path(app_data_dir) / 'yubikey_config.json'
        self.keys = []  # Список ключей вместо одного
        self.enabled = False
        self.static_passwords = static_passwords or []
        
        # Система защиты от перебора секретного входа

        
        self.load_config()
    
    def load_config(self):
        """Загружает конфигурацию YubiKey с улучшенной обработкой ошибок."""
        try:
            # Убеждаемся, что директория существует
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            if self.config_file.exists():
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        # Поддержка старого формата (один ключ)
                        if 'client_id' in config and 'secret_key' in config:
                            self.keys = [{
                                'client_id': config.get('client_id'),
                                'secret_key': config.get('secret_key'),
                                'name': 'Основной ключ',
                                'created_at': config.get('created_at', '2024-01-01')
                            }]
                        else:
                            # Новый формат (несколько ключей)
                            self.keys = config.get('keys', [])
                        self.enabled = config.get('enabled', False)
                        print(f"✅ Конфигурация YubiKey загружена: {len(self.keys)} ключей")
                except json.JSONDecodeError as e:
                    print(f"⚠️ Ошибка парсинга JSON в {self.config_file}: {e}")
                    self.keys = []
                    self.enabled = False
                except Exception as e:
                    print(f"⚠️ Ошибка чтения файла {self.config_file}: {e}")
                    self.keys = []
                    self.enabled = False
            else:
                print(f"📄 Файл конфигурации YubiKey не найден: {self.config_file}")
                self.keys = []
                self.enabled = False
        except Exception as e:
            print(f"❌ Критическая ошибка загрузки YubiKey: {e}")
            self.keys = []
            self.enabled = False
    
    def save_config(self):
        """Сохраняет конфигурацию YubiKey с улучшенной обработкой ошибок."""
        try:
            # Убеждаемся, что директория существует
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            config = {
                'keys': self.keys,
                'enabled': self.enabled
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Конфигурация YubiKey сохранена: {len(self.keys)} ключей")
        except Exception as e:
            print(f"❌ Ошибка сохранения YubiKey: {e}")
            raise
    
    def add_key(self, client_id, secret_key, name=None):
        """Добавляет новый YubiKey."""
        if not name:
            name = f"Ключ {len(self.keys) + 1}"
        
        new_key = {
            'client_id': client_id,
            'secret_key': secret_key,
            'name': name,
            'created_at': datetime.now().isoformat()
        }
        
        self.keys.append(new_key)
        self.enabled = True
        self.save_config()
        return True
    
    def remove_key(self, key_index):
        """Удаляет YubiKey по индексу."""
        if 0 <= key_index < len(self.keys):
            removed_key = self.keys.pop(key_index)
            if not self.keys:
                self.enabled = False
            self.save_config()
            return removed_key
        return None
    
    def get_keys(self):
        """Возвращает список всех ключей."""
        return self.keys
    
    def is_authenticated(self):
        """Проверяет, аутентифицирован ли пользователь с улучшенной обработкой ошибок."""
        try:
            # Проверяем, есть ли активный контекст запроса
            from flask import has_request_context
            if not has_request_context():
                print("⚠️ is_authenticated вызван вне контекста запроса")
                return False
            
            return session.get('yubikey_authenticated', False)
        except Exception as e:
            print(f"⚠️ Ошибка в is_authenticated: {e}")
            return False
    
    def verify_otp(self, otp):
        """Гибридная проверка: сначала статические пароли, потом онлайн."""
        if not otp:
            return False, "OTP не может быть пустым"

        # Сначала проверяем статические пароли (всегда)
        if self.static_passwords and otp in self.static_passwords:
            print("✅ Статический пароль успешно проверен.")
            session['yubikey_authenticated'] = True
            session['offline_auth'] = True # Ставим флаг для отображения в UI
            return True, "Офлайн-пароль подтвержден"

        # Если статический пароль не подошел, проверяем онлайн-ключи
        if check_internet_connection():
            # Строгая проверка формата для онлайн-ключа (YubiKey OTP)
            # Он должен состоять только из 44 символов ModHex.
            if not re.match(r'^[cbdefghijklnrtuv]{44}$', otp):
                print("❌ Неверный формат онлайн OTP и неверный офлайн-пароль")
                return False, "Неверный формат онлайн OTP и неверный офлайн-пароль"

            if not self.keys:
                return False, "Онлайн-ключи не настроены"
            for key_data in self.keys:
                try:
                    if not key_data.get('client_id') or not key_data.get('secret_key'):
                        continue
                    
                    client = Yubico(key_data['client_id'], key_data['secret_key'])
                    if client.verify(otp):
                        print(f"✅ Онлайн OTP успешно проверен ключом: {key_data.get('name', 'Неизвестный')}")
                        session['yubikey_authenticated'] = True
                        return True, "Онлайн-пароль подтвержден"
                except (InvalidClientIdError, SignatureVerificationError, YubicoError) as e:
                    print(f"⚠️ Ошибка проверки ключа {key_data.get('name', 'Неизвестный')}: {e}")
                    continue
            return False, "Неверный онлайн OTP"
        else:
            if not self.static_passwords:
                return False, "Статические пароли не настроены"
            print("❌ Статический пароль неверный или не задан.")
            return False, "Неверный офлайн-пароль"
    

            print(f"⚠️ Ошибка в secret_authenticate: {e}")
            return False, f"Ошибка аутентификации: {e}"
    
    def require_auth(self, f):
        def decorated(*args, **kwargs):
            if not self.enabled:
                return f(*args, **kwargs)
            if not self.is_authenticated():
                return redirect(url_for('yubikey_login'))
            return f(*args, **kwargs)
        decorated.__name__ = f.__name__
        return decorated

yubikey_auth = None

def init_yubikey_auth(app_data_dir):
    """Инициализирует YubiKey аутентификацию с улучшенной обработкой ошибок."""
    global yubikey_auth
    try:
        print(f"🔧 Инициализация YubiKey в директории: {app_data_dir}")
        
        # Загружаем статические пароли из переменных окружения
        import os
        import sys
        from dotenv import load_dotenv
        
        # Улучшенная загрузка .env файла для работы в дистрибутиве
        def load_env_file():
            """Загружает .env файл из различных возможных мест."""
            from pathlib import Path
            
            # Список возможных путей к .env файлу
            possible_paths = []
            
            # 1. Текущая директория (для разработки)
            possible_paths.append(Path.cwd() / ".env")
            
            # 2. Директория приложения (для дистрибутива)
            if getattr(sys, 'frozen', False):
                # Если приложение запаковано
                if sys.platform == 'darwin':  # macOS
                    # В .app бандле
                    app_bundle = Path(sys.executable).parent.parent.parent
                    possible_paths.append(app_bundle / "Contents" / "Resources" / ".env")
                    
                    # В пользовательской директории
                    user_env = Path.home() / "Library" / "Application Support" / "AllManager" / ".env"
                    possible_paths.append(user_env)
                    
                    # В директории приложения
                    app_dir = Path(sys.executable).parent
                    possible_paths.append(app_dir / ".env")
            
            # 3. Директория скрипта
            script_dir = Path(__file__).parent
            possible_paths.append(script_dir / ".env")
            
            # 4. Родительская директория
            parent_dir = Path(__file__).parent.parent
            possible_paths.append(parent_dir / ".env")
            
            # Пытаемся загрузить .env из каждого возможного места
            for env_path in possible_paths:
                if env_path.exists():
                    print(f"📁 [yubikey_auth] Найден .env файл: {env_path}")
                    load_dotenv(env_path)
                    return True
            
            print(f"❌ [yubikey_auth] .env файл не найден в следующих местах:")
            for path in possible_paths:
                print(f"   - {path} {'✅' if path.exists() else '❌'}")
            return False
        
        # Загружаем .env файл
        load_env_file()
        static_passwords_str = os.getenv('YUBIKEY_STATIC_PASSWORDS')
        static_passwords = []
        if static_passwords_str:
            static_passwords = [p.strip() for p in static_passwords_str.split(',')]
            print(f"🤫 {len(static_passwords)} статических паролей YubiKey загружено.")

        yubikey_auth = YubiKeyAuth(app_data_dir, static_passwords)
        print(f"✅ YubiKey инициализирован: enabled={yubikey_auth.enabled}, keys={len(yubikey_auth.keys)}")
        return yubikey_auth 
    except Exception as e:
        print(f"❌ Ошибка инициализации YubiKey: {e}")
        return None 