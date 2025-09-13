#!/usr/bin/env python3
"""
Скрипт для сборки macOS-приложения AllManagerC.
Создает .app бандл и .dmg образ для распространения.
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import json
from datetime import datetime
import sysconfig

# Основные директории и файлы проекта
PROJECT_ROOT = Path.cwd()
DIST_DIR = PROJECT_ROOT / 'dist'
BUILD_DIR = PROJECT_ROOT / 'build'
ICON_FILE = PROJECT_ROOT / 'static' / 'images' / 'icon.icns'  # Иконка в формате .icns для macOS
CONFIG_FILE = PROJECT_ROOT / 'config.json'

# Создаем директории для сборки если их нет
DIST_DIR.mkdir(exist_ok=True)
BUILD_DIR.mkdir(exist_ok=True)

# Удаляем предыдущие сборки
def cleanup_previous_builds():
    print("Очистка предыдущих сборок...")
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR, ignore_errors=True)
    
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR, ignore_errors=True)

    spec_file = PROJECT_ROOT / f"AllManagerC.spec"
    if spec_file.exists():
        print(f"Удаление старого файла .spec: {spec_file}")
        spec_file.unlink()

# Обновление даты в config.json и получение текущей версии
def update_config_and_get_version():
    """
    Читает config.json, обновляет дату сборки, сохраняет файл
    и возвращает номер текущей версии.
    """
    print("Обновление даты сборки в config.json и чтение версии...")
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Получаем версию
        version = config_data.get('app_info', {}).get('version')
        if not version:
            print("ОШИБКА: Версия не найдена в config.json.")
            return None

        # Обновляем дату
        config_data['app_info']['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
            
        print(f"Дата в config.json обновлена. Версия для сборки: {version}")
        return version
    except FileNotFoundError:
        print(f"ОШИБКА: {CONFIG_FILE} не найден.")
        return None
    except Exception as e:
        print(f"ОШИБКА при работе с config.json: {e}")
        return None

# Проверка наличия иконки, если нет - создаем её из PNG

def check_and_create_icns():
    if not ICON_FILE.exists():
        print("Иконка .icns не найдена. Попытка создать из PNG...")
        # Используем новый исходник иконки: ALLc.png
        png_icon = PROJECT_ROOT / 'static' / 'images' / 'ALLc.png'
        
        if not png_icon.exists():
            print("PNG иконка ALLc.png не найдена. Будет использована стандартная иконка.")
            return False
        
        try:
            # Создаем временную директорию для iconset
            iconset_dir = PROJECT_ROOT / 'static' / 'images' / 'tmp.iconset'
            iconset_dir.mkdir(exist_ok=True)
            
            # Создаем иконки разных размеров
            sizes = [16, 32, 128, 256, 512]
            for size in sizes:
                size2x = size * 2
                # Генерируем обычную версию
                subprocess.call(['sips', '-z', str(size), str(size), 
                               str(png_icon), '--out', 
                               str(iconset_dir / f"icon_{size}x{size}.png")])
                                
                # Генерируем @2x версии (кроме 512x512)
                if size < 512:
                    subprocess.call(['sips', '-z', str(size2x), str(size2x), 
                                   str(png_icon), '--out', 
                                   str(iconset_dir / f"icon_{size}x{size}@2x.png")])
            
            # Для 512x512@2x используем оригинальную иконку 1024x1024
            shutil.copy(png_icon, iconset_dir / "icon_512x512@2x.png")
            
            # Конвертируем iconset в .icns - исправляем команду
            subprocess.call(['iconutil', '-c', 'icns', str(iconset_dir)])
            
            # Перемещаем созданный .icns файл в нужное место
            created_icns = iconset_dir.with_suffix('.icns')
            if created_icns.exists():
                shutil.move(created_icns, ICON_FILE)
            else:
                fallback_icns = iconset_dir.parent / "tmp.icns"
                if fallback_icns.exists():
                    shutil.move(fallback_icns, ICON_FILE)

            # Удаляем временную директорию
            shutil.rmtree(iconset_dir)
            
            print(f"Иконка .icns успешно создана: {ICON_FILE}")
            return True
        except Exception as e:
            print(f"Ошибка создания .icns: {e}")
            return False
    
    # Проверяем актуальность существующей иконки: пересобираем, если PNG новее
    try:
        png_icon = PROJECT_ROOT / 'static' / 'images' / 'ALLc.png'
        if png_icon.exists() and ICON_FILE.exists():
            if png_icon.stat().st_mtime > ICON_FILE.stat().st_mtime:
                print("ALLc.png новее, пересоздаем .icns...")
                ICON_FILE.unlink()
                return check_and_create_icns()
    except Exception:
        pass
    
    # Проверяем размер существующей иконки
    if ICON_FILE.stat().st_size < 1000:  # Если меньше 1KB, вероятно поврежден
        print("Существующая .icns иконка слишком мала, пересоздаем...")
        ICON_FILE.unlink()  # Удаляем поврежденный файл
        return check_and_create_icns()  # Рекурсивно вызываем функцию
    
    return True

# Создание файла README.txt с инструкциями
def create_readme():
    readme_content = """# All Manager

## Важно: Первый запуск

При первом запуске приложения может появиться предупреждение безопасности macOS о том, 
что приложение получено не из App Store. Для решения:

1. В Finder щелкните по приложению правой кнопкой мыши (или Control+клик)
2. Выберите "Открыть" в контекстном меню
3. В появившемся диалоге нажмите "Открыть"
4. После этого приложение будет запускаться без предупреждений

## Хранение данных

Приложение автоматически сохраняет все данные в вашей пользовательской директории:
~/Library/Application Support/AllManager/

В этой директории хранятся:
- Файлы конфигурации
- Зашифрованные данные AI сервисов
- Загруженные иконки сервисов

## Резервное копирование

Для создания резервной копии данных, сохраните директорию:
~/Library/Application Support/AllManager/

## Проблемы с запуском

Если приложение не запускается, проверьте:
1. Наличие файла .env с ключом шифрования
2. Наличие прав доступа к директории данных

Для технической поддержки обратитесь к разработчику.
"""
    
    readme_path = DIST_DIR / "README.txt"
    with open(readme_path, "w") as f:
        f.write(readme_content)
    
    return readme_path

# Команда для создания .app файла с помощью PyInstaller
def build_app():
    """
    Создает .app файл из app.py с помощью PyInstaller.
    Включает все необходимые файлы: templates, static, config.json и другие.
    """
    print("Запуск PyInstaller для создания .app бундла...")
    
    icon_arg = f"--icon={ICON_FILE}" if ICON_FILE.exists() else ""
    
    # Определяем все файлы, которые нужно включить в сборку
    datas = [
        "templates:templates",          # HTML шаблоны
        "static:static",                # CSS, изображения, иконки
        "config.json:.",                # Файл конфигурации
        "data:data",                    # Директория с данными (если есть)
    ]
    
    # Если существует файл ai_services.json, добавляем его
    services_file = Path("data/ai_services.json")
    if services_file.exists():
        datas.append("data/ai_services.json:data")
    
    # Формируем аргументы для PyInstaller
    datas_args = [f"--add-data={data}" for data in datas]
    
    # Добавляем скрытые импорты для Flask и других зависимостей
    hidden_imports = [
        "--hidden-import=flask",
        "--hidden-import=flask.app",
        "--hidden-import=flask.blueprints",
        "--hidden-import=flask.cli",
        "--hidden-import=flask.config",
        "--hidden-import=flask.ctx",
        "--hidden-import=flask.debughelpers",
        "--hidden-import=flask.helpers",
        "--hidden-import=flask.json",
        "--hidden-import=flask.logging",
        "--hidden-import=flask.sessions",
        "--hidden-import=flask.signals",
        "--hidden-import=flask.templating",
        "--hidden-import=flask.testing",
        "--hidden-import=flask.views",
        "--hidden-import=werkzeug",
        "--hidden-import=werkzeug.datastructures",
        "--hidden-import=werkzeug.debug",
        "--hidden-import=werkzeug.exceptions",
        "--hidden-import=werkzeug.filesystem",
        "--hidden-import=werkzeug.formparser",
        "--hidden-import=werkzeug.http",
        "--hidden-import=werkzeug.local",
        "--hidden-import=werkzeug.middleware",
        "--hidden-import=werkzeug.middleware.proxy_fix",
        "--hidden-import=werkzeug.middleware.shared_data",
        "--hidden-import=werkzeug.routing",
        "--hidden-import=werkzeug.security",
        "--hidden-import=werkzeug.serving",
        "--hidden-import=werkzeug.test",
        "--hidden-import=werkzeug.testapp",
        "--hidden-import=werkzeug.urls",
        "--hidden-import=werkzeug.utils",
        "--hidden-import=werkzeug.wrappers",
        "--hidden-import=werkzeug.wsgi",
        "--hidden-import=jinja2",
        "--hidden-import=jinja2.async_utils",
        "--hidden-import=jinja2.bccache",
        "--hidden-import=jinja2.compiler",
        "--hidden-import=jinja2.debug",
        "--hidden-import=jinja2.defaults",
        "--hidden-import=jinja2.environment",
        "--hidden-import=jinja2.ext",
        "--hidden-import=jinja2.filters",
        "--hidden-import=jinja2.lexer",
        "--hidden-import=jinja2.loaders",
        "--hidden-import=jinja2.meta",
        "--hidden-import=jinja2.nativetypes",
        "--hidden-import=jinja2.nodes",
        "--hidden-import=jinja2.optimizer",
        "--hidden-import=jinja2.parser",
        "--hidden-import=jinja2.runtime",
        "--hidden-import=jinja2.sandbox",
        "--hidden-import=jinja2.tests",
        "--hidden-import=jinja2.utils",
        "--hidden-import=jinja2.visitor",
        "--hidden-import=cryptography",
        "--hidden-import=requests",
        "--hidden-import=webview",
        "--hidden-import=webview.platforms.cocoa",
        "--hidden-import=webview.platforms.cef",
        "--hidden-import=webview.platforms.gtk",
        "--hidden-import=webview.platforms.winforms",
        "--hidden-import=webview.platforms.edgechromium",
        "--hidden-import=webview.platforms.edgehtml",
        "--hidden-import=webview.platforms.mshtml",
        "--hidden-import=webview.platforms.qt",
        "--hidden-import=yubico_client",
        "--hidden-import=yubico_client.yubico_exceptions",
        "--exclude-module=PyQt6",
        "--exclude-module=PyQt5",
        "--exclude-module=PySide6",
        "--exclude-module=PySide2",
        "--exclude-module=_tkinter",
        "--exclude-module=tkinter",
        "--exclude-module=tcl",
        "--exclude-module=tk"
    ]
    
    pyinstaller_cmd = [
        "python3",                      # Используем python3 для запуска модуля
        "-m", "PyInstaller",            # Явно вызываем модуль PyInstaller
        "--onedir",                     # Создать директорию с файлами (совместимо с .app)
        "--windowed",                   # GUI приложение (не консольное)
        "--name=AllManagerC",             # Имя приложения
        icon_arg,                       # Иконка (если есть)
        "--clean",                      # Очистить кэш PyInstaller
        "--noconfirm",                  # Не запрашивать подтверждение
        "--distpath=dist",              # Явно указываем директорию вывода
        "--workpath=build",             # Явно указываем рабочую директорию
        "--noupx",                      # Отключаем UPX для стабильности
        "--strip",                      # Удаляем отладочную информацию
        # "--target-architecture=x86_64", # Убираем принудительное указание архитектуры
        "--osx-bundle-identifier=com.allmanagerc.app", # Bundle ID для macOS
        "--debug=all",                  # Добавляем отладочную информацию
        *datas_args,                    # Добавляемые файлы и директории
        *hidden_imports,                # Скрытые импорты
        "app.py"                        # Основной файл приложения
    ]
    
    # Убираем пустые аргументы (например, если иконки нет)
    pyinstaller_cmd = [arg for arg in pyinstaller_cmd if arg]
    
    # Запуск PyInstaller
    result = subprocess.run(pyinstaller_cmd, capture_output=False, text=True)
    
    if result.returncode != 0:
        print(f"ОШИБКА: PyInstaller завершился с кодом {result.returncode}")
        return False
    
    app_path = DIST_DIR / "AllManagerC.app"
    if not app_path.exists():
        print("ОШИБКА: .app файл не был создан.")
        return False
    
    print(f"✅ .app бундл создан: {app_path}")
    
    # Копируем .env файл в Resources приложения
    env_source = PROJECT_ROOT / ".env"
    if env_source.exists():
        env_dest = app_path / "Contents" / "Resources" / ".env"
        env_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(env_source, env_dest)
        print(f"Файл .env скопирован в {env_dest}")
    
    # Обновляем Info.plist с правильной версией
    update_info_plist(app_path)
    
    return app_path

def update_info_plist(app_path):
    """
    Обновляет Info.plist с правильной версией из config.json
    """
    info_plist_path = app_path / "Contents" / "Info.plist"
    if not info_plist_path.exists():
        print("ПРЕДУПРЕЖДЕНИЕ: Info.plist не найден")
        return
    
    try:
        # Читаем версию из config.json
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        version = config_data.get('app_info', {}).get('version', '4.0.0')
        
        # Читаем Info.plist
        with open(info_plist_path, 'r', encoding='utf-8') as f:
            plist_content = f.read()
        
        # Обновляем версии в Info.plist с более надежными регулярными выражениями
        import re
        
        # Обновляем CFBundleShortVersionString
        if '<key>CFBundleShortVersionString</key>' in plist_content:
            plist_content = re.sub(
                r'(<key>CFBundleShortVersionString</key>\s*<string>)[^<]*(</string>)',
                lambda m: m.group(1) + version + m.group(2),
                plist_content
            )
        
        # Обновляем CFBundleVersion
        if '<key>CFBundleVersion</key>' in plist_content:
            plist_content = re.sub(
                r'(<key>CFBundleVersion</key>\s*<string>)[^<]*(</string>)',
                lambda m: m.group(1) + version + m.group(2),
                plist_content
            )
        
        # Записываем обновленный Info.plist
        with open(info_plist_path, 'w', encoding='utf-8') as f:
            f.write(plist_content)
        
        print(f"✅ Info.plist обновлен с версией {version}")
        
    except Exception as e:
        print(f"ОШИБКА при обновлении Info.plist: {e}")

# Создание DMG образа
def create_dmg(app_path):
    app_name = app_path.name.split('.')[0]
    dmg_name = f"{app_name}_Installer.dmg"
    dmg_path = DIST_DIR / dmg_name
    
    # Удаляем старый DMG если есть
    if os.path.exists(dmg_path):
        os.remove(dmg_path)
    
    # Создаем README файл
    readme_path = create_readme()
    
    # Готовим команду для создания DMG
    # hdiutil используется для создания DMG в macOS
    try:
        print("Создание DMG образа...")
        
        # Создаем временную папку для монтирования
        tmp_dir = DIST_DIR / "tmp_dmg"
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        tmp_dir.mkdir(parents=True)
        
        # Копируем .app в эту папку
        shutil.copytree(app_path, tmp_dir / app_path.name)
        
        # Копируем README.txt
        shutil.copy(readme_path, tmp_dir / "README.txt")
        
        # Создаем символьную ссылку на Applications
        os.symlink('/Applications', tmp_dir / 'Applications')
        
        # Создаем DMG
        subprocess.call([
            'hdiutil', 'create', '-volname', app_name, 
            '-srcfolder', str(tmp_dir), 
            '-ov', '-format', 'UDZO', str(dmg_path)
        ])
        
        # Удаляем временную папку
        shutil.rmtree(tmp_dir)
        
        print(f"DMG образ создан: {dmg_path}")
        return dmg_path
    except Exception as e:
        print(f"Ошибка создания DMG: {e}")
        return None

# Основная функция сборки
def main():
    print("Сборка AllManagerC для macOS")
    print("===========================")
    
    cleanup_previous_builds()
    
    # 0. Обновляем конфиг и получаем версию
    print("\n[0/3] Обновление файла конфигурации...")
    app_version = update_config_and_get_version()
    if not app_version:
        sys.exit(1) # Прерываем, если не удалось получить версию
    
    # 0.5. Проверяем и создаем иконку .icns
    print("\n[0.5/3] Проверка и создание иконки приложения...")
    if not check_and_create_icns():
        print("ПРЕДУПРЕЖДЕНИЕ: Не удалось создать .icns, будет использована стандартная иконка.")

    # 1. Сборка .app
    print(f"\n[1/3] Сборка .app бундла для версии {app_version}...")
    app_path = build_app()
    
    # Проверяем успешность создания приложения
    if not app_path:
        print("❌ ОШИБКА: Не удалось создать .app бундл!")
        sys.exit(1)
    
    # 2. Создание .dmg
    print(f"\n[2/3] Создание .dmg образа для версии {app_version}...")
    dmg_path = create_dmg(app_path)
    
    if dmg_path:
        print("\nСборка завершена успешно!")
        print(f"- Приложение: {app_path}")
        print(f"- DMG образ: {dmg_path}")
        
        print("\n=== ВАЖНАЯ ИНФОРМАЦИЯ ДЛЯ ЗАПУСКА ===")
        print("Приложение хранит все данные в директории пользователя:")
        print("~/Library/Application Support/AllManagerC/")
        print("\nПри первом запуске:")
        print("1. Щелкните по приложению правой кнопкой мыши")
        print("2. Выберите 'Открыть'")
        print("3. В диалоге безопасности нажмите 'Открыть'")
    else:
        print("\nСборка завершена с ошибками.")

if __name__ == "__main__":
    main() 