#!/usr/bin/env python3
"""
Скрипт для диагностики и исправления проблем с данными AI Manager
"""

import os
import json
import base64
from cryptography.fernet import Fernet
from pathlib import Path

def load_secret_key():
    """Загружает SECRET_KEY из .env файла"""
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('SECRET_KEY='):
                    return line.split('=', 1)[1].strip()
    except FileNotFoundError:
        print("❌ Файл .env не найден")
        return None
    return None

def test_decryption(file_path, secret_key):
    """Тестирует расшифровку файла"""
    try:
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        
        if not encrypted_data:
            return False, "Файл пустой"
            
        fernet = Fernet(secret_key.encode())
        decrypted_data = fernet.decrypt(encrypted_data)
        data = json.loads(decrypted_data.decode('utf-8'))
        
        return True, f"Успешно расшифровано: {len(data)} сервисов"
    except Exception as e:
        return False, str(e)

def analyze_data_files():
    """Анализирует все файлы данных"""
    print("🔍 АНАЛИЗ ФАЙЛОВ ДАННЫХ")
    print("=" * 50)
    
    secret_key = load_secret_key()
    if not secret_key:
        print("❌ Не удалось загрузить SECRET_KEY")
        return
    
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ Папка data не найдена")
        return
    
    # Находим все .enc файлы
    enc_files = list(data_dir.glob("*.enc"))
    
    print(f"Найдено файлов: {len(enc_files)}")
    print()
    
    working_files = []
    
    for file_path in enc_files:
        print(f"📁 {file_path.name}:")
        print(f"   Размер: {file_path.stat().st_size} байт")
        
        success, message = test_decryption(file_path, secret_key)
        if success:
            print(f"   ✅ {message}")
            working_files.append(file_path)
        else:
            print(f"   ❌ {message}")
        print()
    
    return working_files

def fix_active_file(working_files):
    """Исправляет активный файл в конфигурации"""
    print("🔧 ИСПРАВЛЕНИЕ КОНФИГУРАЦИИ")
    print("=" * 50)
    
    if not working_files:
        print("❌ Нет рабочих файлов данных")
        return False
    
    # Выбираем самый большой файл как наиболее полный
    best_file = max(working_files, key=lambda f: f.stat().st_size)
    print(f"Выбран файл: {best_file.name}")
    print(f"Размер: {best_file.stat().st_size} байт")
    
    # Обновляем конфигурацию
    config_path = Path("config.json")
    if not config_path.exists():
        print("❌ Файл config.json не найден")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Обновляем путь к активному файлу
        config['active_data_file'] = str(best_file.absolute())
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Конфигурация обновлена: {best_file.name}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка обновления конфигурации: {e}")
        return False

def verify_fix():
    """Проверяет, что исправление работает"""
    print("✅ ПРОВЕРКА ИСПРАВЛЕНИЯ")
    print("=" * 50)
    
    try:
        # Импортируем функцию загрузки данных
        import sys
        sys.path.append('.')
        
        # Создаем временный модуль для тестирования
        test_code = """
import os
import json
from cryptography.fernet import Fernet

def test_load():
    # Загружаем конфигурацию
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    active_file = config.get('active_data_file')
    if not active_file or not os.path.exists(active_file):
        return False, "Активный файл не найден"
    
    # Загружаем ключ
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('SECRET_KEY='):
                secret_key = line.split('=', 1)[1].strip()
                break
    else:
        return False, "SECRET_KEY не найден"
    
    # Тестируем расшифровку
    try:
        with open(active_file, 'rb') as f:
            encrypted_data = f.read()
        
        fernet = Fernet(secret_key.encode())
        decrypted_data = fernet.decrypt(encrypted_data)
        data = json.loads(decrypted_data.decode('utf-8'))
        
        return True, f"Успешно загружено {len(data)} сервисов"
    except Exception as e:
        return False, str(e)

success, message = test_load()
print(f"Результат: {message}")
"""
        
        # Выполняем тест
        result = os.popen(f'python3 -c "{test_code}"').read().strip()
        print(result)
        
        if "Успешно загружено" in result:
            print("✅ Исправление работает!")
            return True
        else:
            print("❌ Исправление не работает")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return False

def main():
    """Главная функция"""
    print("🤖 AI MANAGER - ИСПРАВЛЕНИЕ ЦЕЛОСТНОСТИ ДАННЫХ")
    print("=" * 60)
    
    # Анализируем файлы
    working_files = analyze_data_files()
    
    if not working_files:
        print("❌ Нет рабочих файлов данных для восстановления")
        return
    
    # Исправляем конфигурацию
    if fix_active_file(working_files):
        # Проверяем исправление
        if verify_fix():
            print("\n🎉 ПРОБЛЕМА ИСПРАВЛЕНА!")
            print("Теперь вы можете:")
            print("1. Запустить приложение: python3 run_app.py")
            print("2. Редактировать и удалять сервисы")
            print("3. Добавлять новые сервисы")
        else:
            print("\n⚠️ Исправление не полностью работает")
            print("Попробуйте перезапустить приложение")
    else:
        print("\n❌ Не удалось исправить проблему")

if __name__ == "__main__":
    main() 