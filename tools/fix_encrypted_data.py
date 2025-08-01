#!/usr/bin/env python3
"""
Утилита для исправления файла данных после смены ключей.
Исправляет ситуацию, когда основной файл зашифрован новым ключом,
но отдельные поля внутри сервисов зашифрованы старым ключом.
"""

import os
import json
import sys
from cryptography.fernet import Fernet
from datetime import datetime

def load_config():
    """Загружает конфигурацию приложения."""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки конфига: {e}")
        return {}

def load_key_from_env():
    """Загружает текущий ключ из .env файла."""
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('SECRET_KEY='):
                    return line.strip().split('=', 1)[1]
        return None
    except Exception as e:
        print(f"Ошибка загрузки ключа: {e}")
        return None

def re_encrypt_service_data(service, old_fernet, new_fernet):
    """Перешифровывает зашифрованные поля сервиса."""
    import copy
    service_copy = copy.deepcopy(service)
    
    # Список полей для перешифровки
    fields_to_reencrypt = [
        ('credentials', 'username'),
        ('credentials', 'password'),
        ('credentials', 'additional_info'),
        ('personal_cabinet', 'account_email'),
        ('ssh_credentials', 'password'),
        ('ssh_credentials', 'root_password'),
        ('panel_credentials', 'user'),
        ('panel_credentials', 'password'),
        ('hoster_credentials', 'user'),
        ('hoster_credentials', 'password')
    ]
    
    fields_processed = 0
    fields_reencrypted = 0
    
    for section, field in fields_to_reencrypt:
        try:
            # Проверяем, существует ли секция и поле
            if section in service_copy and field in service_copy[section]:
                encrypted_value = service_copy[section][field]
                fields_processed += 1
                
                # Пропускаем пустые значения
                if not encrypted_value or encrypted_value == "":
                    continue
                
                # Сначала пытаемся расшифровать новым ключом
                try:
                    decrypted_value = new_fernet.decrypt(encrypted_value.encode()).decode()
                    # Если удалось, поле уже правильно зашифровано
                    continue
                except:
                    pass
                
                # Пытаемся расшифровать старым ключом
                try:
                    decrypted_value = old_fernet.decrypt(encrypted_value.encode()).decode()
                    # Зашифровываем новым ключом
                    reencrypted_value = new_fernet.encrypt(decrypted_value.encode()).decode()
                    service_copy[section][field] = reencrypted_value
                    fields_reencrypted += 1
                    print(f"  ✅ Перешифровано: {section}.{field}")
                except Exception as e:
                    print(f"  ⚠️ Не удалось обработать {section}.{field}: {e}")
                    continue
                    
        except Exception as e:
            print(f"  ❌ Ошибка с секцией {section}: {e}")
            continue
    
    return service_copy, fields_processed, fields_reencrypted

def fix_data_file(old_key, new_key, data_file_path):
    """Исправляет файл данных, перешифровывая поля с правильным ключом."""
    
    print(f"\n=== ИСПРАВЛЕНИЕ ФАЙЛА ДАННЫХ ===")
    print(f"Файл: {data_file_path}")
    print(f"Старый ключ (последние 10 символов): {old_key[-10:]}")
    print(f"Новый ключ (последние 10 символов): {new_key[-10:]}")
    
    # Создаем Fernet объекты
    old_fernet = Fernet(old_key.encode())
    new_fernet = Fernet(new_key.encode())
    
    # Создаем резервную копию
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{data_file_path}.backup_{timestamp}"
    
    try:
        import shutil
        shutil.copy2(data_file_path, backup_path)
        print(f"✅ Резервная копия создана: {backup_path}")
    except Exception as e:
        print(f"⚠️ Не удалось создать резервную копию: {e}")
        response = input("Продолжить без резервной копии? (y/N): ")
        if response.lower() != 'y':
            print("Операция отменена.")
            return False
    
    try:
        # Загружаем данные (файл должен расшифровываться новым ключом)
        with open(data_file_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = new_fernet.decrypt(encrypted_data)
        services_data = json.loads(decrypted_data.decode('utf-8'))
        
        print(f"✅ Файл загружен: {len(services_data)} сервисов")
        
        # Перешифровываем каждый сервис
        fixed_services = []
        total_fields = 0
        total_reencrypted = 0
        
        for i, service in enumerate(services_data):
            service_name = service.get('name', f'Service #{i+1}')
            print(f"\nОбработка сервиса: {service_name}")
            
            fixed_service, fields_processed, fields_reencrypted = re_encrypt_service_data(
                service, old_fernet, new_fernet
            )
            
            fixed_services.append(fixed_service)
            total_fields += fields_processed
            total_reencrypted += fields_reencrypted
            
            print(f"  Обработано полей: {fields_processed}, перешифровано: {fields_reencrypted}")
        
        # Сохраняем исправленные данные
        json_string = json.dumps(fixed_services, ensure_ascii=False, indent=2)
        encrypted_data = new_fernet.encrypt(json_string.encode('utf-8'))
        
        with open(data_file_path, 'wb') as f:
            f.write(encrypted_data)
        
        print(f"\n🎉 ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!")
        print(f"✅ Всего полей обработано: {total_fields}")
        print(f"✅ Перешифровано полей: {total_reencrypted}")
        print(f"✅ Файл сохранен: {data_file_path}")
        
        if total_reencrypted > 0:
            print(f"\n🔑 Теперь все поля зашифрованы текущим ключом!")
        else:
            print(f"\n✨ Все поля уже были корректно зашифрованы.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА ПРИ ИСПРАВЛЕНИИ: {e}")
        import traceback
        traceback.print_exc()
        
        # Пытаемся восстановить из резервной копии
        if os.path.exists(backup_path):
            try:
                shutil.copy2(backup_path, data_file_path)
                print(f"🔄 Файл восстановлен из резервной копии")
            except Exception as restore_error:
                print(f"❌ Не удалось восстановить из резервной копии: {restore_error}")
        
        return False

def main():
    print("🔧 Утилита исправления зашифрованных данных")
    print("=" * 50)
    
    # Загружаем конфигурацию
    config = load_config()
    data_file_path = config.get('active_data_file')
    
    if not data_file_path or not os.path.exists(data_file_path):
        print("❌ Активный файл данных не найден")
        return 1
    
    # Загружаем текущий ключ
    current_key = load_key_from_env()
    if not current_key:
        print("❌ Не найден текущий ключ в .env файле")
        return 1
    
    print(f"✅ Найден активный файл: {data_file_path}")
    print(f"✅ Текущий ключ загружен")
    
    # Запрашиваем старый ключ
    print(f"\nДля исправления нужен СТАРЫЙ ключ шифрования")
    print(f"(тот, которым были зашифрованы поля внутри сервисов)")
    old_key = input("Введите старый ключ: ").strip()
    
    if not old_key:
        print("❌ Старый ключ не указан")
        return 1
    
    # Проверяем формат ключей
    try:
        Fernet(old_key.encode())
        Fernet(current_key.encode())
    except Exception as e:
        print(f"❌ Неверный формат ключа: {e}")
        return 1
    
    # Выполняем исправление
    success = fix_data_file(old_key, current_key, data_file_path)
    
    if success:
        print(f"\n✅ ГОТОВО! Теперь попробуйте редактировать/удалять сервисы в приложении.")
        return 0
    else:
        print(f"\n❌ Исправление не удалось. Проверьте логи выше.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 