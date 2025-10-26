# 🍎 Создание релиза для macOS

Инструкция по сборке и публикации релиза AllManagerC для macOS.

> **⚠️ Важно о виртуальном окружении:**  
> Виртуальные окружения `.venv` **специфичны для платформы**. Если вы работали на Windows и создали там `.venv`, при переходе на macOS нужно:
> - Либо удалить `.venv` командой `rm -rf .venv` и создать заново
> - Либо использовать скрипт `build_macos.sh` - он автоматически обнаружит Windows `.venv` и пересоздаст для macOS
> 
> Виртуальное окружение **не должно** попадать в git (уже в `.gitignore`).

## 📋 Требования

- macOS 10.13+
- Python 3.8+
- Xcode Command Line Tools
- [create-dmg](https://github.com/create-dmg/create-dmg) (опционально, для красивого DMG)

## 🚀 Подготовка окружения

### 1. Установка зависимостей

```bash
# Переход в директорию проекта
cd ai-manager

# Проверка окружения (опционально, но рекомендуется)
python3 check_env.py

# Создание виртуального окружения
python3 -m venv .venv

# Активация окружения
source .venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
pip install pyinstaller

# Опционально: для создания красивого DMG
brew install create-dmg

# Повторная проверка окружения
python check_env.py
```

## 📦 Сборка приложения

### 2. Создание .app с PyInstaller

```bash
# Базовая сборка
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
    app.py

# Результат будет в dist/AllManagerC.app
```

### 3. Проверка сборки

```bash
# Запуск приложения для проверки
open dist/AllManagerC.app

# Проверка зависимостей
otool -L dist/AllManagerC.app/Contents/MacOS/AllManagerC
```

## 🎨 Создание DMG инсталлятора

### 4. Подготовка DMG

#### Вариант A: С помощью create-dmg (рекомендуется)

```bash
# Создание красивого DMG с фоном и иконками
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
    "dist/AllManagerC.app"
```

#### Вариант B: Простой DMG

```bash
# Создание папки для DMG
mkdir -p dist/dmg
cp -r dist/AllManagerC.app dist/dmg/
ln -s /Applications dist/dmg/Applications

# Создание DMG
hdiutil create -volname "AllManagerC v5.6.0" \
    -srcfolder dist/dmg \
    -ov -format UDZO \
    dist/AllManagerC_Installer_v5.6.0.dmg

# Очистка
rm -rf dist/dmg
```

## 🔐 Подписание приложения (опционально)

### 5. Подписание для распространения

```bash
# Требуется Apple Developer ID
codesign --deep --force --verify --verbose \
    --sign "Developer ID Application: Your Name (TEAM_ID)" \
    dist/AllManagerC.app

# Проверка подписи
codesign --verify --deep --strict --verbose=2 dist/AllManagerC.app
spctl -a -t exec -vv dist/AllManagerC.app
```

### 6. Нотаризация (для распространения вне App Store)

```bash
# Упаковка для нотаризации
ditto -c -k --keepParent dist/AllManagerC.app AllManagerC.zip

# Отправка на нотаризацию
xcrun notarytool submit AllManagerC.zip \
    --apple-id "your-email@example.com" \
    --team-id "TEAM_ID" \
    --password "app-specific-password"

# Проверка статуса
xcrun notarytool log <submission-id> \
    --apple-id "your-email@example.com" \
    --team-id "TEAM_ID" \
    --password "app-specific-password"

# После успешной нотаризации - прикрепить тикет
xcrun stapler staple dist/AllManagerC.app
```

## 📊 Проверка и тестирование

### 7. Финальная проверка

```bash
# Размер приложения
du -sh dist/AllManagerC.app
du -sh dist/AllManagerC_Installer_v5.6.0.dmg

# SHA256 хеш для релиза
shasum -a 256 dist/AllManagerC_Installer_v5.6.0.dmg

# Проверка на чистой системе
# Откройте DMG и перетащите приложение в Applications
open dist/AllManagerC_Installer_v5.6.0.dmg
```

## 📤 Публикация релиза

### 8. Создание GitHub Release

```bash
# Создание тега
git tag -a v5.6.0 -m "Release version 5.6.0"
git push origin v5.6.0

# Загрузка через GitHub CLI
gh release create v5.6.0 \
    dist/AllManagerC_Installer_v5.6.0.dmg \
    --title "AllManagerC v5.6.0" \
    --notes-file CHANGELOG.md
```

### 9. Обновление README.md

После публикации обновите README.md:

```markdown
## ⬇️ Скачать

- Последний релиз: [Latest Release](https://github.com/kureinmaxim/ai-manager/releases/latest)
- Прямая ссылка (v5.6.0, macOS DMG): [AllManagerC_Installer_v5.6.0.dmg](https://github.com/kureinmaxim/ai-manager/releases/download/v5.6.0/AllManagerC_Installer_v5.6.0.dmg)
- SHA256(DMG): `<вставьте хеш из шага 7>`
```

## 🔍 Решение проблем

### Ошибка "App is damaged"

Если пользователи видят ошибку "App is damaged and can't be opened":

```bash
# Удаление карантинных атрибутов
xattr -cr /Applications/AllManagerC.app
```

### Проблемы с импортом модулей

```bash
# Добавьте --collect-all для проблемных модулей
pyinstaller ... --collect-all flask --collect-all werkzeug
```

### Большой размер приложения

```bash
# Исключите ненужные модули
pyinstaller ... \
    --exclude-module=PyQt5 \
    --exclude-module=PyQt6 \
    --exclude-module=matplotlib \
    --exclude-module=numpy
```

## 📝 Чек-лист релиза

- [ ] Обновлена версия в `config.json`
- [ ] Обновлен `CHANGELOG.md`
- [ ] Проведено тестирование на чистой macOS
- [ ] Создан DMG инсталлятор
- [ ] Вычислен SHA256 хеш
- [ ] Создан git tag
- [ ] Опубликован GitHub Release
- [ ] Обновлен README.md с новой ссылкой и хешем
- [ ] Протестирована установка из DMG

## 🎉 Готово!

Ваш релиз AllManagerC v5.6.0 для macOS готов к распространению!

---

**Примечание:** Для автоматизации этого процесса можно создать скрипт `build_macos.sh` или использовать GitHub Actions.

