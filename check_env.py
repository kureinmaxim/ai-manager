#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для проверки окружения разработки AllManagerC
Проверяет платформу, Python версию, виртуальное окружение и зависимости
"""

import sys
import platform
import os
from pathlib import Path

# Для корректной работы с кириллицей и эмодзи в Windows
if platform.system() == 'Windows':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def print_header(text):
    """Красивый заголовок"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def check_platform():
    """Проверка платформы"""
    print_header("🖥️  ПЛАТФОРМА")
    print(f"  ОС: {platform.system()} {platform.release()}")
    print(f"  Архитектура: {platform.machine()}")
    print(f"  Процессор: {platform.processor()}")
    
def check_python():
    """Проверка Python"""
    print_header("🐍 PYTHON")
    print(f"  Версия: {sys.version}")
    print(f"  Исполняемый файл: {sys.executable}")
    print(f"  Префикс: {sys.prefix}")
    print(f"  Base префикс: {sys.base_prefix}")
    
def check_venv():
    """Проверка виртуального окружения"""
    print_header("📦 ВИРТУАЛЬНОЕ ОКРУЖЕНИЕ")
    
    in_venv = sys.prefix != sys.base_prefix
    print(f"  В виртуальном окружении: {'✅ ДА' if in_venv else '❌ НЕТ'}")
    
    if in_venv:
        print(f"  Путь к venv: {sys.prefix}")
    
    # Проверка .venv в текущей директории
    venv_dir = Path('.venv')
    if venv_dir.exists():
        print(f"  Папка .venv: ✅ Существует")
        
        # Проверка для какой платформы создан .venv
        if platform.system() == 'Windows':
            python_exe = venv_dir / 'Scripts' / 'python.exe'
            activate_ps1 = venv_dir / 'Scripts' / 'Activate.ps1'
            if python_exe.exists() and activate_ps1.exists():
                print(f"  Тип .venv: ✅ Windows (Scripts/python.exe)")
            else:
                print(f"  Тип .venv: ⚠️  Похоже на Unix, но вы на Windows!")
                print(f"  Рекомендация: Пересоздайте .venv командой:")
                print(f"    Remove-Item -Recurse -Force .venv")
                print(f"    python -m venv .venv")
        else:
            python_bin = venv_dir / 'bin' / 'python'
            activate_sh = venv_dir / 'bin' / 'activate'
            if python_bin.exists() and activate_sh.exists():
                print(f"  Тип .venv: ✅ Unix (bin/python)")
            else:
                print(f"  Тип .venv: ⚠️  Похоже на Windows, но вы на Unix!")
                print(f"  Рекомендация: Пересоздайте .venv командой:")
                print(f"    rm -rf .venv")
                print(f"    python3 -m venv .venv")
    else:
        print(f"  Папка .venv: ❌ Не найдена")
        if platform.system() == 'Windows':
            print(f"  Создайте: python -m venv .venv")
        else:
            print(f"  Создайте: python3 -m venv .venv")
    
def check_dependencies():
    """Проверка ключевых зависимостей"""
    print_header("📚 ЗАВИСИМОСТИ")
    
    packages = {
        'flask': 'Flask',
        'cryptography': 'cryptography',
        'requests': 'requests',
        'webview': 'pywebview',
        'yubico_client': 'yubico-client',
    }
    
    for module_name, package_name in packages.items():
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'неизвестна')
            print(f"  ✅ {package_name}: {version}")
        except ImportError:
            print(f"  ❌ {package_name}: НЕ УСТАНОВЛЕН")
    
def check_config():
    """Проверка конфигурации"""
    print_header("⚙️  КОНФИГУРАЦИЯ")
    
    import json
    config_file = Path('config.json')
    
    if config_file.exists():
        print(f"  ✅ config.json: Существует")
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                version = config.get('app_info', {}).get('version', 'не указана')
                print(f"  Версия приложения: {version}")
        except Exception as e:
            print(f"  ⚠️  Ошибка чтения: {e}")
    else:
        print(f"  ❌ config.json: Не найден")
    
    env_file = Path('.env')
    if env_file.exists():
        print(f"  ✅ .env: Существует")
    else:
        print(f"  ⚠️  .env: Не найден (может быть в %APPDATA%)")
    
def check_git():
    """Проверка git статуса"""
    print_header("🔀 GIT")
    
    git_dir = Path('.git')
    if git_dir.exists():
        print(f"  ✅ Git репозиторий: Инициализирован")
        
        # Проверка .venv в gitignore
        gitignore = Path('.gitignore')
        if gitignore.exists():
            try:
                with open(gitignore, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if '.venv' in content or 'venv' in content:
                        print(f"  ✅ .venv в .gitignore: Да")
                    else:
                        print(f"  ⚠️  .venv в .gitignore: Нет (ДОБАВЬТЕ!)")
            except Exception as e:
                print(f"  ⚠️  Ошибка чтения .gitignore: {e}")
        else:
            print(f"  ⚠️  .gitignore: Не найден")
    else:
        print(f"  ⚠️  Git репозиторий: Не инициализирован")

def print_recommendations():
    """Рекомендации"""
    print_header("💡 РЕКОМЕНДАЦИИ")
    
    in_venv = sys.prefix != sys.base_prefix
    
    if not in_venv:
        print("  ⚠️  Вы НЕ в виртуальном окружении!")
        print("  Активируйте его:")
        if platform.system() == 'Windows':
            print("    .\\venv\\Scripts\\Activate.ps1")
        else:
            print("    source .venv/bin/activate")
    
    # Проверка версии Python
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  ⚠️  Рекомендуется Python 3.8+")
        print(f"  Текущая версия: {version.major}.{version.minor}.{version.micro}")
    
    print("\n  📖 Полезные ссылки:")
    print("    - README.md - Главная документация")
    print("    - CROSS_PLATFORM_GUIDE.md - Работа на разных ОС")
    print("    - QUICK_RELEASE_GUIDE.md - Создание релиза")

def main():
    """Основная функция"""
    print("\n" + "🔍 ПРОВЕРКА ОКРУЖЕНИЯ AllManagerC".center(60))
    
    check_platform()
    check_python()
    check_venv()
    
    # Проверка зависимостей только если в venv или есть .venv
    if sys.prefix != sys.base_prefix or Path('.venv').exists():
        check_dependencies()
    
    check_config()
    check_git()
    print_recommendations()
    
    print("\n" + "="*60)
    print("  ✅ Проверка завершена!")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()

