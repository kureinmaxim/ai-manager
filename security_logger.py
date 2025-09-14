#!/usr/bin/env python3
"""
Модуль для логирования событий безопасности в AI Manager.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Добавлена кроссплатформенная функция определения директории данных приложения
def _resolve_app_data_dir() -> Path:
    if getattr(sys, 'frozen', False):
        if sys.platform == 'win32':
            return Path(os.environ.get('APPDATA', str(Path.home()))) / 'AllManagerC'
        elif sys.platform == 'darwin':
            return Path.home() / 'Library' / 'Application Support' / 'AllManagerC'
        else:
            return Path.home() / '.local' / 'share' / 'AllManagerC'
    # Режим разработки — текущая директория проекта
    return Path.cwd()

def setup_security_logger():
    """Настраивает логгер для событий безопасности."""
    # Определяем директорию для логов (кроссплатформенно)
    app_data_dir = _resolve_app_data_dir()
    
    # Создаем директорию для логов
    log_dir = app_data_dir / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Настройка логгера безопасности
    security_logger = logging.getLogger('security')
    security_logger.setLevel(logging.INFO)
    
    # Удаляем существующие обработчики
    for handler in security_logger.handlers[:]:
        security_logger.removeHandler(handler)
    
    # Создаем файловый обработчик
    log_file = log_dir / 'security.log'
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # Форматтер для логов
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    # Добавляем обработчик к логгеру
    security_logger.addHandler(file_handler)
    
    return security_logger

def log_security_event(event_type, details, ip_address=None, user_agent=None):
    """Логирует событие безопасности."""
    logger = logging.getLogger('security')
    
    # Формируем сообщение
    message_parts = [f"EVENT: {event_type}", f"DETAILS: {details}"]
    
    if ip_address:
        message_parts.append(f"IP: {ip_address}")
    
    if user_agent:
        message_parts.append(f"USER_AGENT: {user_agent}")
    
    message = " | ".join(message_parts)
    
    # Логируем событие
    logger.info(message)
    
    # Также выводим в консоль для отладки (исправлен символ)
    print(f"🔒 SECURITY: {message}")

def log_login_attempt(success, username=None, ip_address=None):
    status = "SUCCESS" if success else "FAILED"
    details = f"Login {status}"
    if username:
        details += f" - User: {username}"
    log_security_event("LOGIN_ATTEMPT", details, ip_address)

def log_data_export(filename, ip_address=None):
    log_security_event("DATA_EXPORT", f"File: {filename}", ip_address)

def log_data_import(filename, ip_address=None):
    log_security_event("DATA_IMPORT", f"File: {filename}", ip_address)

def log_key_change(operation, ip_address=None):
    log_security_event("KEY_CHANGE", f"Operation: {operation}", ip_address)

def log_service_operation(operation, service_name, ip_address=None):
    log_security_event("SERVICE_OPERATION", f"{operation}: {service_name}", ip_address)

def log_error(error_type, error_message, ip_address=None):
    log_security_event("ERROR", f"{error_type}: {error_message}", ip_address)

def get_security_stats():
    """Возвращает статистику безопасности."""
    # Определяем директорию для логов (кроссплатформенно)
    app_data_dir = _resolve_app_data_dir()
    
    log_file = app_data_dir / 'logs' / 'security.log'
    if not log_file.exists():
        return {"total_events": 0, "events_by_type": {}}
    
    stats = {"total_events": 0, "events_by_type": {}}
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if 'EVENT:' in line:
                    stats["total_events"] += 1
                    # Извлекаем тип события
                    event_start = line.find('EVENT:') + 6
                    event_end = line.find(' |', event_start)
                    if event_end == -1:
                        event_end = line.find('DETAILS:', event_start)
                    
                    if event_end != -1:
                        event_type = line[event_start:event_end].strip()
                        stats["events_by_type"][event_type] = stats["events_by_type"].get(event_type, 0) + 1
    except Exception as e:
        print(f"Ошибка чтения статистики безопасности: {e}")
    
    return stats

if __name__ == "__main__":
    setup_security_logger()
    log_security_event("TEST", "Testing security logger")
    log_login_attempt(True, "test_user", "127.0.0.1")
    log_data_export("test_export.enc", "127.0.0.1")
    print("Тестирование завершено. Проверьте файл logs/security.log")
