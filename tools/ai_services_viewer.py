#!/usr/bin/env python3
"""
Инструмент для просмотра AI-сервисов
"""
import os
import json
from cryptography.fernet import Fernet
from dotenv import load_dotenv

def decrypt_data(fernet_instance, encrypted_data):
    """Расшифровывает данные"""
    if not encrypted_data:
        return "N/A"
    try:
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
        return fernet_instance.decrypt(encrypted_data).decode('utf-8')
    except Exception:
        return "Ошибка расшифровки"

def view_ai_services():
    """Просматривает AI-сервисы"""
    load_dotenv()
    secret_key = os.getenv("SECRET_KEY")
    
    if not secret_key:
        print("❌ SECRET_KEY не найден в .env")
        return
        
    try:
        fernet = Fernet(secret_key.encode())
    except Exception as e:
        print(f"❌ Ошибка Fernet: {e}")
        return
    
    data_file = "data/ai_services.json.enc"
    if not os.path.exists(data_file):
        print(f"❌ Файл {data_file} не найден")
        return
    
    try:
        with open(data_file, 'rb') as f:
            encrypted_data = f.read()
            
        decrypted_json = fernet.decrypt(encrypted_data).decode('utf-8')
        services = json.loads(decrypted_json)
        
    except Exception as e:
        print(f"❌ Ошибка расшифровки: {e}")
        return
    
    print("🤖 === AI SERVICES MANAGER - ДАННЫЕ ===")
    print(f"📊 Всего сервисов: {len(services)}")
    print("=" * 50)
    
    for i, service in enumerate(services, 1):
        print(f"\n🔸 СЕРВИС #{i}: {service.get('name', 'N/A')}")
        print(f"   Тип: {service.get('service_type', 'N/A')}")
        print(f"   Провайдер: {service.get('provider', 'N/A')}")
        print(f"   Статус: {service.get('status', 'N/A')}")
        
        # Доступ
        print(f"\n   🔗 Доступ:")
        print(f"   URL входа: {service.get('login_url', 'N/A')}")
        
        creds = service.get('credentials', {})
        if creds:
            username = decrypt_data(fernet, creds.get('username', ''))
            password = decrypt_data(fernet, creds.get('password', ''))
            print(f"   Логин: {username}")
            print(f"   Пароль: {password}")
        
        # Подписка
        sub = service.get('subscription', {})
        if sub:
            print(f"\n   💳 Подписка:")
            print(f"   План: {sub.get('plan_name', 'N/A')}")
            print(f"   Стоимость: {sub.get('cost_monthly', 0)} {sub.get('currency', 'USD')}/мес")
            print(f"   Следующий платеж: {sub.get('next_payment_date', 'N/A')}")
            print(f"   Автопродление: {'Да' if sub.get('auto_renewal') else 'Нет'}")
        
        # Дополнительно
        notes = service.get('notes', '')
        if notes:
            print(f"\n   📝 Заметки: {notes}")
            
        print(f"   📅 Создан: {service.get('created_at', 'N/A')}")
        print("-" * 40)
    
    print("\n✅ Просмотр завершен")

if __name__ == "__main__":
    view_ai_services()
