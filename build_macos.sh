#!/bin/bash
# Скрипт для сборки AllManagerC для macOS
# Версия: 5.6.0

set -e  # Остановка при ошибке

echo "🍎 Сборка AllManagerC для macOS v5.6.0"
echo "========================================="

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Проверка виртуального окружения
if [ -d ".venv" ]; then
    # Проверка, что .venv создан для текущей платформы
    if [ ! -f ".venv/bin/activate" ]; then
        echo -e "${RED}⚠️  Обнаружено виртуальное окружение от другой платформы (Windows)${NC}"
        echo "Пересоздание виртуального окружения для macOS..."
        rm -rf .venv
        python3 -m venv .venv
    else
        echo -e "${GREEN}✅ Виртуальное окружение найдено${NC}"
    fi
else
    echo -e "${BLUE}📦 Создание виртуального окружения...${NC}"
    python3 -m venv .venv
fi

# Активация окружения
echo -e "${BLUE}📦 Активация виртуального окружения...${NC}"
source .venv/bin/activate

# Установка/обновление зависимостей
echo -e "${BLUE}📦 Установка зависимостей...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Очистка старых сборок
echo -e "${BLUE}🧹 Очистка старых сборок...${NC}"
rm -rf build dist *.spec

# Сборка приложения
echo -e "${BLUE}🔨 Сборка приложения с PyInstaller...${NC}"
pyinstaller --name="AllManagerC" \
    --windowed \
    --onedir \
    --icon=static/images/icon.ico \
    --add-data="templates:templates" \
    --add-data="static:static" \
    --add-data="config.json:." \
    --add-data="data:data" \
    --hidden-import=flask \
    --hidden-import=werkzeug \
    --hidden-import=jinja2 \
    --hidden-import=cryptography \
    --hidden-import=requests \
    --hidden-import=webview \
    --hidden-import=yubico_client \
    --exclude-module=PyQt5 \
    --exclude-module=PyQt6 \
    --exclude-module=PySide2 \
    --exclude-module=PySide6 \
    app.py

echo -e "${GREEN}✅ Приложение собрано: dist/AllManagerC.app${NC}"

# Проверка размера
APP_SIZE=$(du -sh dist/AllManagerC.app | cut -f1)
echo -e "${BLUE}📊 Размер приложения: ${APP_SIZE}${NC}"

# Создание DMG
echo -e "${BLUE}💿 Создание DMG инсталлятора...${NC}"

# Проверка наличия create-dmg
if command -v create-dmg &> /dev/null; then
    echo "Используется create-dmg для создания красивого DMG..."
    create-dmg \
        --volname "AllManagerC v5.6.0" \
        --volicon "static/images/icon.ico" \
        --window-pos 200 120 \
        --window-size 800 400 \
        --icon-size 100 \
        --icon "AllManagerC.app" 200 190 \
        --hide-extension "AllManagerC.app" \
        --app-drop-link 600 185 \
        "dist/AllManagerC_Installer_v5.6.0.dmg" \
        "dist/AllManagerC.app" || {
            echo "Ошибка с create-dmg, использую hdiutil..."
            # Fallback на hdiutil
            mkdir -p dist/dmg
            cp -r dist/AllManagerC.app dist/dmg/
            ln -s /Applications dist/dmg/Applications
            hdiutil create -volname "AllManagerC v5.6.0" \
                -srcfolder dist/dmg \
                -ov -format UDZO \
                dist/AllManagerC_Installer_v5.6.0.dmg
            rm -rf dist/dmg
        }
else
    echo "create-dmg не установлен, использую hdiutil..."
    mkdir -p dist/dmg
    cp -r dist/AllManagerC.app dist/dmg/
    ln -s /Applications dist/dmg/Applications
    hdiutil create -volname "AllManagerC v5.6.0" \
        -srcfolder dist/dmg \
        -ov -format UDZO \
        dist/AllManagerC_Installer_v5.6.0.dmg
    rm -rf dist/dmg
fi

echo -e "${GREEN}✅ DMG создан: dist/AllManagerC_Installer_v5.6.0.dmg${NC}"

# Вычисление SHA256
echo -e "${BLUE}🔐 Вычисление SHA256...${NC}"
SHA256=$(shasum -a 256 dist/AllManagerC_Installer_v5.6.0.dmg | cut -d' ' -f1)
echo -e "${GREEN}SHA256: ${SHA256}${NC}"

# Размер DMG
DMG_SIZE=$(du -sh dist/AllManagerC_Installer_v5.6.0.dmg | cut -f1)
echo -e "${BLUE}📊 Размер DMG: ${DMG_SIZE}${NC}"

# Итоговая информация
echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}✅ Сборка завершена успешно!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "📦 Файлы:"
echo -e "   App:  dist/AllManagerC.app"
echo -e "   DMG:  dist/AllManagerC_Installer_v5.6.0.dmg"
echo ""
echo -e "📊 Информация:"
echo -e "   Размер App: ${APP_SIZE}"
echo -e "   Размер DMG: ${DMG_SIZE}"
echo -e "   SHA256:     ${SHA256}"
echo ""
echo -e "🚀 Следующие шаги:"
echo -e "   1. Протестируйте: open dist/AllManagerC.app"
echo -e "   2. Протестируйте DMG: open dist/AllManagerC_Installer_v5.6.0.dmg"
echo -e "   3. Создайте тег: git tag -a v5.6.0 -m 'Release v5.6.0'"
echo -e "   4. Опубликуйте: gh release create v5.6.0 dist/AllManagerC_Installer_v5.6.0.dmg"
echo -e "   5. Обновите README.md с SHA256"
echo ""

