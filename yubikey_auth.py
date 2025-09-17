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
        # Секретный PIN и антибрут-логика (в файле config.json приложения)
        self.app_data_dir = Path(app_data_dir)
        self.app_config_path = self.app_data_dir / 'config.json'
        self.secret_login_attempts = 0
        self.secret_login_blocked_until = 0
        self.secret_login_block_duration = 30  # секунд

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

    # ====== СЕКРЕТНЫЙ PIN: хранение и антибрут ======
    def _load_app_config(self):
        try:
            if not self.app_config_path.exists():
                return {}
            with open(self.app_config_path, 'r', encoding='utf-8') as f:
                return json.load(f) or {}
        except Exception:
            return {}

    def _save_app_config(self, cfg: dict):
        try:
            self.app_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.app_config_path, 'w', encoding='utf-8') as f:
                json.dump(cfg, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения config.json: {e}")
            return False

    def get_secret_pin(self) -> str:
        try:
            import os
            env_pin = os.getenv('DEV_PIN') or os.getenv('DEVELOPER_PIN')
            if env_pin and str(env_pin).strip():
                return str(env_pin).strip()
        except Exception:
            pass
        cfg = self._load_app_config()
        sec = cfg.get('security') or {}
        pin = sec.get('secret_pin', {}).get('current_pin') if isinstance(sec.get('secret_pin'), dict) else None
        if not pin:
            # fallback на security.dev_pin или '1234'
            pin = sec.get('dev_pin') or '1234'
        return str(pin)

    def change_secret_pin(self, old_pin: str, new_pin: str):
        try:
            current = self.get_secret_pin()
            if str(old_pin) != str(current):
                return False, 'Старый PIN неверен'
            cfg = self._load_app_config()
            if 'security' not in cfg or not isinstance(cfg.get('security'), dict):
                cfg['security'] = {}
            # Обновляем новую структуру
            cfg['security']['secret_pin'] = {
                'current_pin': str(new_pin),
                'updated_at': datetime.now().isoformat()
            }
            # Удаляем устаревший dev_pin, чтобы не путал
            if 'dev_pin' in cfg['security']:
                cfg['security'].pop('dev_pin', None)
            ok = self._save_app_config(cfg)
            if not ok:
                return False, 'Не удалось сохранить PIN'
            # Сбросить попытки после смены
            self.secret_login_attempts = 0
            self.secret_login_blocked_until = 0
            return True, 'PIN изменён'
        except Exception as e:
            return False, f'Ошибка: {e}'

    def is_secret_login_blocked(self) -> bool:
        try:
            import time
            return time.time() < float(self.secret_login_blocked_until or 0)
        except Exception:
            return False

    def get_secret_login_block_remaining(self) -> int:
        try:
            import time
            remaining = int((self.secret_login_blocked_until or 0) - time.time())
            return max(0, remaining)
        except Exception:
            return 0

    def block_secret_login(self):
        try:
            import time
            self.secret_login_blocked_until = time.time() + int(self.secret_login_block_duration)
        except Exception:
            pass

    def secret_authenticate(self, pin: str):
        try:
            if self.is_secret_login_blocked():
                return False, f"Блокировка {self.get_secret_login_block_remaining()} сек"
            if not pin:
                return False, 'Введите PIN'
            if str(pin).strip() == str(self.get_secret_pin()).strip():
                self.secret_login_attempts = 0
                session['yubikey_authenticated'] = True
                return True, 'Успех'
            # Неверный PIN
            self.secret_login_attempts += 1
            if self.secret_login_attempts >= 3:
                self.block_secret_login()
                self.secret_login_attempts = 0
                return False, 'Слишком много попыток. Временная блокировка.'
            return False, 'Неверный PIN'
        except Exception as e:
            return False, f'Ошибка аутентификации: {e}'

    
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
        """Гибридная проверка: сначала статические пароли, потом онлайн с понятными ошибками."""
        if not otp:
            return False, "OTP не может быть пустым"

        # Сначала проверяем статические пароли (всегда)
        if self.static_passwords and otp in self.static_passwords:
            print("✅ Статический пароль успешно проверен.")
            session['yubikey_authenticated'] = True
            session['offline_auth'] = True
            return True, "Офлайн-пароль подтвержден"

        # Если статический пароль не подошел, проверяем онлайн-ключи
        if check_internet_connection():
            # Строгая проверка формата для онлайн-ключа (YubiKey OTP): 44 символа ModHex
            if not re.match(r'^[cbdefghijklnrtuv]{44}$', otp):
                print("❌ Неверный формат онлайн OTP и неверный офлайн-пароль")
                return False, "Неверный формат онлайн OTP и неверный офлайн-пароль"

            if not self.keys:
                return False, "Онлайн-ключи не настроены"

            # Таблица расшифровки ответов Yubico в понятные сообщения
            status_to_message = {
                'REPLAYED_OTP': "Код уже был использован. Нажмите кнопку ещё раз (сгенерируйте новый).",
                'BAD_OTP': "Неверный одноразовый код. Нажмите кнопку на ключе ещё раз.",
                'NO_SUCH_CLIENT': "Неверный Client ID. Проверьте, что в настройках указан числовой Client ID из кабинета Yubico.",
                'BAD_SIGNATURE': "Неверный Secret Key. Проверьте Secret Key, скопируйте заново из кабинета Yubico.",
                'MISSING_PARAMETER': "Отсутствуют параметры запроса. Проверьте, что сохранены Client ID и Secret Key.",
                'BACKEND_ERROR': "Сбой на стороне Yubico. Повторите попытку позже.",
                'REPLAYED_REQUEST': "Повтор запроса. Попробуйте ещё раз.",
                'NOT_ENOUGH_ANSWERS': "Недостаточно ответов сервера Yubico. Повторите попытку позже.",
                'OPERATION_NOT_ALLOWED': "OTP-операция запрещена для вашего ключа. Проверьте настройку слота OTP."
            }

            for key_data in self.keys:
                try:
                    client_id = key_data.get('client_id')
                    secret_key = key_data.get('secret_key')
                    if not client_id or not secret_key:
                        continue

                    client = Yubico(client_id, secret_key)

                    # Запрашиваем подробный ответ от YubiCloud
                    response = client.verify(otp, return_response=True)
                    status = getattr(response, 'status', None) if response is not None else None

                    if status == 'OK':
                        print(f"✅ Онлайн OTP успешно проверен ключом: {key_data.get('name', 'Неизвестный')}")
                        session['yubikey_authenticated'] = True
                        return True, "Онлайн-пароль подтвержден"

                    # Если статус присутствует и не OK — вернём понятное сообщение
                    if status:
                        human_message = status_to_message.get(status, f"Ошибка Yubico: {status}")
                        print(f"⚠️ Верификация не пройдена ({status}): {human_message}")
                        return False, human_message

                    # На всякий случай: если библиотека вернула неуспех без статуса
                    print("⚠️ Верификация не удалась без кода статуса")
                    return False, "Не удалось подтвердить OTP. Попробуйте ещё раз."

                except InvalidClientIdError:
                    return False, "Неверный Client ID. Проверьте значение в настройках YubiKey."
                except SignatureVerificationError:
                    return False, "Неверный Secret Key. Проверьте значение в настройках YubiKey."
                except YubicoError as e:
                    msg = str(e) or "YubicoError"
                    lower_msg = msg.lower()
                    if 'timeout' in lower_msg or 'timed out' in lower_msg:
                        return False, "Тайм-аут соединения с YubiCloud. Проверьте интернет и повторите."
                    if 'network' in lower_msg or 'connection' in lower_msg:
                        return False, "Нет связи с YubiCloud. Проверьте интернет-соединение."
                    return False, f"Ошибка Yubico: {msg}"

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
                    user_env = Path.home() / "Library" / "Application Support" / "AllManagerC" / ".env"
                    possible_paths.append(user_env)
                    
                    # В директории приложения
                    app_dir = Path(sys.executable).parent
                    possible_paths.append(app_dir / ".env")
                elif sys.platform == 'win32':
                    from pathlib import Path as _P
                    possible_paths.append(_P(os.environ.get('APPDATA', str(Path.home()))) / 'AllManagerC' / '.env')
                    possible_paths.append(Path(sys.executable).parent / '.env')
                else:
                    possible_paths.append(Path.home() / '.local' / 'share' / 'AllManagerC' / '.env')
                    possible_paths.append(Path(sys.executable).parent / '.env')
            
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