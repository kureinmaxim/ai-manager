#!/usr/bin/env python3
"""
Модуль для проверки целостности данных в AI Manager.
"""

import json
import hashlib
import uuid
from pathlib import Path

def calculate_data_hash(data):
    """Вычисляет хеш данных для проверки целостности."""
    # Сортируем данные для стабильного хеша
    sorted_data = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(sorted_data.encode('utf-8')).hexdigest()

def verify_data_integrity(servers):
    """Проверяет целостность данных серверов."""
    errors = []
    warnings = []
    
    if not isinstance(servers, list):
        return False, ["Data is not a list"]
    
    for i, server in enumerate(servers):
        # Проверяем обязательные поля
        required_fields = ['id', 'name', 'provider']
        for field in required_fields:
            if field not in server:
                errors.append(f"Server {i}: Missing required field '{field}'")
        
        # Проверяем формат UUID
        if 'id' in server:
            try:
                uuid.UUID(server['id'])
            except ValueError:
                errors.append(f"Server {i}: Invalid UUID format '{server['id']}'")
        
        # Проверяем типы данных
        if 'name' in server and not isinstance(server['name'], str):
            errors.append(f"Server {i}: 'name' must be string, got {type(server['name'])}")
        
        if 'provider' in server and not isinstance(server['provider'], str):
            errors.append(f"Server {i}: 'provider' must be string, got {type(server['provider'])}")
        
        # Проверяем структуру credentials
        if 'credentials' in server:
            creds = server['credentials']
            if not isinstance(creds, dict):
                errors.append(f"Server {i}: 'credentials' must be dict")
            else:
                # Проверяем зашифрованные поля
                encrypted_fields = ['username', 'password', 'additional_info']
                for field in encrypted_fields:
                    if field in creds:
                        value = creds[field]
                        if value and not isinstance(value, str):
                            errors.append(f"Server {i}: 'credentials.{field}' must be string")
        
        # Проверяем subscription
        if 'subscription' in server:
            sub = server['subscription']
            if not isinstance(sub, dict):
                errors.append(f"Server {i}: 'subscription' must be dict")
            else:
                if 'cost_monthly' in sub and not isinstance(sub['cost_monthly'], (int, float)):
                    warnings.append(f"Server {i}: 'subscription.cost_monthly' should be number")
        
        # Проверяем features
        if 'features' in server:
            features = server['features']
            if isinstance(features, list):
                for j, feature in enumerate(features):
                    if not isinstance(feature, str):
                        errors.append(f"Server {i}: feature {j} must be string")
            elif not isinstance(features, str):
                errors.append(f"Server {i}: 'features' must be string or list")
    
    return len(errors) == 0, errors, warnings

def add_integrity_hash(servers):
    """Добавляет хеш целостности к данным."""
    # Удаляем старый хеш, если есть
    servers_clean = [s for s in servers if not s.get('_integrity_hash')]
    
    # Вычисляем новый хеш
    data_hash = calculate_data_hash(servers_clean)
    
    # Добавляем хеш как отдельный объект
    integrity_record = {
        '_integrity_hash': data_hash,
        '_integrity_timestamp': str(datetime.now()),
        '_integrity_version': '1.0'
    }
    
    servers_clean.append(integrity_record)
    return servers_clean

def verify_integrity_hash(servers):
    """Проверяет хеш целостности данных."""
    # Ищем запись с хешем
    integrity_record = None
    servers_clean = []
    
    for server in servers:
        if server.get('_integrity_hash'):
            integrity_record = server
        else:
            servers_clean.append(server)
    
    if not integrity_record:
        return False, "No integrity hash found"
    
    # Вычисляем хеш текущих данных
    current_hash = calculate_data_hash(servers_clean)
    stored_hash = integrity_record.get('_integrity_hash')
    
    if current_hash == stored_hash:
        return True, "Data integrity verified"
    else:
        return False, f"Data integrity check failed. Expected: {stored_hash}, Got: {current_hash}"

def repair_data_integrity(servers):
    """Исправляет проблемы целостности данных."""
    repaired = []
    fixed_count = 0
    
    for i, server in enumerate(servers):
        if server.get('_integrity_hash'):
            continue  # Пропускаем записи целостности
        
        # Создаем копию сервера
        fixed_server = server.copy()
        
        # Исправляем UUID
        if 'id' not in fixed_server or not is_valid_uuid(fixed_server['id']):
            fixed_server['id'] = str(uuid.uuid4())
            fixed_count += 1
        
        # Исправляем обязательные поля
        if 'name' not in fixed_server:
            fixed_server['name'] = f"Unknown Service {i+1}"
            fixed_count += 1
        
        if 'provider' not in fixed_server:
            fixed_server['provider'] = "Unknown"
            fixed_count += 1
        
        # Исправляем типы данных
        if 'name' in fixed_server and not isinstance(fixed_server['name'], str):
            fixed_server['name'] = str(fixed_server['name'])
            fixed_count += 1
        
        if 'provider' in fixed_server and not isinstance(fixed_server['provider'], str):
            fixed_server['provider'] = str(fixed_server['provider'])
            fixed_count += 1
        
        # Исправляем credentials
        if 'credentials' in fixed_server and not isinstance(fixed_server['credentials'], dict):
            fixed_server['credentials'] = {}
            fixed_count += 1
        
        # Исправляем subscription
        if 'subscription' in fixed_server and not isinstance(fixed_server['subscription'], dict):
            fixed_server['subscription'] = {}
            fixed_count += 1
        
        repaired.append(fixed_server)
    
    return repaired, fixed_count

def is_valid_uuid(uuid_string):
    """Проверяет, является ли строка валидным UUID."""
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    # Тестирование функций целостности
    from datetime import datetime
    
    # Создаем тестовые данные
    test_servers = [
        {
            "id": str(uuid.uuid4()),
            "name": "Test Service 1",
            "provider": "Test Provider",
            "credentials": {
                "username": "test@example.com",
                "password": "encrypted_password"
            },
            "features": ["Feature 1", "Feature 2"]
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Test Service 2",
            "provider": "Test Provider 2",
            "subscription": {
                "cost_monthly": 29.99,
                "currency": "USD"
            }
        }
    ]
    
    print("🔍 Тестирование целостности данных...")
    
    # Проверяем целостность
    is_valid, errors, warnings = verify_data_integrity(test_servers)
    print(f"Целостность: {'✅ OK' if is_valid else '❌ FAILED'}")
    
    if errors:
        print("Ошибки:")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print("Предупреждения:")
        for warning in warnings:
            print(f"  - {warning}")
    
    # Добавляем хеш целостности
    servers_with_hash = add_integrity_hash(test_servers)
    print(f"Добавлен хеш целостности: {servers_with_hash[-1]['_integrity_hash'][:16]}...")
    
    # Проверяем хеш
    hash_valid, hash_message = verify_integrity_hash(servers_with_hash)
    print(f"Проверка хеша: {'✅ OK' if hash_valid else '❌ FAILED'}")
    print(f"Сообщение: {hash_message}")
    
    print("✅ Тестирование завершено")
