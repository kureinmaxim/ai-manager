# 🚀 Быстрое руководство по созданию релиза v5.6.0

## 📌 Стратегия двухэтапного релиза

**Релиз создается в два этапа:**
1. **Этап 1 (Windows)**: Коммит → Тег → Push → Сборка → GitHub Release (pre-release) с Windows EXE
2. **Этап 2 (macOS)**: Pull → Сборка DMG → Добавление DMG к релизу → Снятие pre-release

**Почему так:** 
- Git commits и теги не зависят от платформы
- `.venv` не в git - каждая платформа создает свой
- Один тег, один релиз - просто добавляем файлы
- Pre-release показывает, что релиз не полный (нет обеих версий)

## ✅ Что уже сделано

- [x] Обновлена версия до 5.6.0 во всех файлах
- [x] Обновлен CHANGELOG.md с описанием изменений
- [x] Создана документация по сборке Windows (Inno Setup)
- [x] Создана документация по сборке macOS
- [x] Создан автоматический скрипт для macOS (build_macos.sh)
- [x] Обновлены все команды для работы с .venv
- [x] Добавлен раздел "Решение проблем" в README
- [x] Добавлен скрипт проверки окружения (check_env.py)
- [x] Добавлен масштаб 70% в интерфейс

## 📋 Измененные файлы

### Основные файлы с версией:
- `config.json` - версия 5.6.0 ✅
- `AllManagerC.iss` - версия 5.6.0 ✅
- `app.py` - версия по умолчанию 5.6.0 ✅
- `run_app.py` - версия по умолчанию 5.6.0 ✅

### Документация:
- `README.md` - обновлена информация о релизе ✅
- `CHANGELOG.md` - добавлена версия 5.6.0 ✅
- `CONTRIBUTING.md` - обновлены команды и версия ✅
- `BUILD_MACOS.md` - новый файл ✅
- `RELEASE_NOTES_v5.6.0.md` - новый файл ✅

### Скрипты сборки:
- `build_windows.py` - готов к использованию ✅
- `build_macos.sh` - новый скрипт ✅

## 🎯 ЭТАП 1: Windows (сейчас) 🪟

### Шаг 1.1: Проверка окружения

```powershell
# Проверка всех компонентов
python check_env.py

# Должно показать:
# - Python 3.13+
# - Виртуальное окружение активно
# - Все зависимости установлены
# - Версия в config.json: 5.6.0
```

### Шаг 1.2: Коммит всех изменений

```powershell
# Проверка статуса
git status

# Добавить все файлы
git add .

# Создать коммит
git commit -m "Release v5.6.0: Improved documentation, cross-platform support, and UI enhancements"
```

### Шаг 1.3: Создать тег версии

```powershell
# Создать аннотированный тег
git tag -a v5.6.0 -m "Release version 5.6.0"

# Проверка тега
git tag -l -n1 v5.6.0
```

### Шаг 1.4: Отправить на GitHub

```powershell
# Отправить изменения
git push origin main

# Отправить тег
git push origin v5.6.0
```

### Шаг 1.5: Сборка Windows инсталлятора

```powershell
# Сборка с PyInstaller (если еще не сделали)
python build_windows.py
# Результат: dist\AllManagerC\AllManagerC.exe

# Сборка инсталлятора с Inno Setup
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" AllManagerC.iss
# Результат: dist\AllManagerC_Installer.exe
```

### Шаг 1.6: Создать GitHub Release (pre-release)

**Вариант A: Через веб-интерфейс** ⭐ Рекомендуется

1. Откройте https://github.com/kureinmaxim/ai-manager/releases
2. Нажмите **"Draft a new release"**
3. Выберите тег: **`v5.6.0`**
4. Название: **`AllManagerC v5.6.0`**
5. Описание: Скопируйте содержимое из `RELEASE_NOTES_v5.6.0.md`
6. Загрузите файл: **`dist\AllManagerC_Installer.exe`**
7. ✅ **Отметьте "Set as a pre-release"** ← ВАЖНО! (пока нет macOS версии)
8. Нажмите **"Publish release"**

**Вариант B: Через GitHub CLI**

```powershell
# Установите GitHub CLI: https://cli.github.com/
gh release create v5.6.0 `
    dist/AllManagerC_Installer.exe `
    --title "AllManagerC v5.6.0" `
    --notes-file RELEASE_NOTES_v5.6.0.md `
    --prerelease
```

### ✅ Чек-лист Этапа 1 (Windows):

- [ ] Проверено окружение: `python check_env.py`
- [ ] Закоммичены изменения: `git commit`
- [ ] Создан тег: `git tag -a v5.6.0`
- [ ] Отправлено в GitHub: `git push origin main` и `git push origin v5.6.0`
- [ ] Собран EXE: `python build_windows.py`
- [ ] Создан инсталлятор: Inno Setup → `AllManagerC_Installer.exe`
- [ ] Создан GitHub Release как **pre-release** с Windows EXE

---

## 🎯 ЭТАП 2: macOS (на Mac) 🍎

> **🔴 Важно:** Выполняйте этот этап ТОЛЬКО на машине с macOS, ПОСЛЕ завершения Этапа 1!

### Шаг 2.1: Скачать проект на macOS

```bash
# Перейдите в директорию проектов
cd ~/Projects  # или где вы храните проекты

# ВАРИАНТ A: Если проект еще не клонирован
git clone https://github.com/kureinmaxim/ai-manager.git
cd ai-manager

# ВАРИАНТ B: Если проект уже клонирован
cd ai-manager
git pull origin main
git fetch --tags
git checkout v5.6.0  # Переключиться на тег релиза
```

### Шаг 2.2: Проверить окружение

```bash
# Скрипт автоматически обнаружит Windows .venv и пересоздаст для macOS
python3 check_env.py

# Должно показать предупреждение о несовместимости .venv (это нормально)
```

### Шаг 2.3: Запустить сборку macOS

```bash
# Сделать скрипт исполняемым (один раз)
chmod +x build_macos.sh

# Запустить автоматическую сборку
./build_macos.sh
```

**Скрипт автоматически:**
- ⚠️ Обнаружит Windows `.venv` и пересоздаст для macOS
- 📦 Установит все зависимости
- 🔨 Соберет `dist/AllManagerC.app`
- 💿 Создаст `dist/AllManagerC_Installer_v5.6.0.dmg`
- 🔐 Вычислит и покажет **SHA256 хеш**

### Шаг 2.4: Сохранить SHA256 хеш

```bash
# SHA256 уже показан в выводе скрипта, но можно вычислить вручную:
shasum -a 256 dist/AllManagerC_Installer_v5.6.0.dmg

# Скопируйте хеш - он понадобится для README.md
```

### Шаг 2.5: Протестировать DMG

```bash
# Открыть DMG для проверки
open dist/AllManagerC_Installer_v5.6.0.dmg

# Проверить размер
du -sh dist/AllManagerC_Installer_v5.6.0.dmg
```

### Шаг 2.6: Добавить macOS DMG к существующему релизу

**Вариант A: Через веб-интерфейс** ⭐ Рекомендуется

1. Откройте https://github.com/kureinmaxim/ai-manager/releases/tag/v5.6.0
2. Нажмите **"Edit release"**
3. Загрузите файл: **`dist/AllManagerC_Installer_v5.6.0.dmg`**
4. В описании добавьте SHA256 для DMG
5. ❌ **Снимите галочку "Set as a pre-release"** ← ВАЖНО! (теперь есть обе платформы)
6. Нажмите **"Update release"**

**Вариант B: Через GitHub CLI**

```bash
# Добавить DMG к существующему релизу
gh release upload v5.6.0 dist/AllManagerC_Installer_v5.6.0.dmg

# Снять флаг pre-release
gh release edit v5.6.0 --prerelease=false
```

### Шаг 2.7: Обновить README.md с SHA256

```bash
# Отредактируйте README.md
# Замените "будет обновлен после сборки" на реальный SHA256

# Пример:
# - SHA256(DMG): `abc123def456...`

# Коммит и пуш
git add README.md
git commit -m "Update macOS DMG SHA256 for v5.6.0"
git push origin main
```

### ✅ Чек-лист Этапа 2 (macOS):

- [ ] Скачан проект: `git clone` или `git pull`
- [ ] Проверено окружение: `python3 check_env.py`
- [ ] Собран DMG: `./build_macos.sh`
- [ ] Сохранен SHA256 хеш
- [ ] Протестирован DMG: `open dist/AllManagerC_Installer_v5.6.0.dmg`
- [ ] DMG добавлен к GitHub Release
- [ ] Снят флаг **"pre-release"**
- [ ] README.md обновлен с SHA256
- [ ] Изменения отправлены: `git push`

---

## 📊 Финальная проверка релиза

После завершения ОБОИХ этапов:

- [ ] ✅ Релиз v5.6.0 существует на GitHub
- [ ] ✅ Windows инсталлятор (`AllManagerC_Installer.exe`) загружен
- [ ] ✅ macOS DMG (`AllManagerC_Installer_v5.6.0.dmg`) загружен
- [ ] ❌ Флаг "pre-release" снят
- [ ] ✅ SHA256 хеш в README.md обновлен
- [ ] ✅ Релиз протестирован на обеих платформах

## 📝 Быстрые команды

### Для Этапа 1 (Windows):

```powershell
# Полный цикл Windows
python check_env.py
git add .
git commit -m "Release v5.6.0: Improved documentation, cross-platform support, and UI enhancements"
git tag -a v5.6.0 -m "Release version 5.6.0"
git push origin main
git push origin v5.6.0
python build_windows.py
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" AllManagerC.iss

# GitHub Release (веб-интерфейс предпочтительнее)
gh release create v5.6.0 `
    dist/AllManagerC_Installer.exe `
    --title "AllManagerC v5.6.0" `
    --notes-file RELEASE_NOTES_v5.6.0.md `
    --prerelease
```

### Для Этапа 2 (macOS):

```bash
# Полный цикл macOS
cd ~/Projects/ai-manager
git pull origin main
git fetch --tags
git checkout v5.6.0
python3 check_env.py
chmod +x build_macos.sh
./build_macos.sh

# Добавить DMG к релизу
gh release upload v5.6.0 dist/AllManagerC_Installer_v5.6.0.dmg
gh release edit v5.6.0 --prerelease=false

# Обновить README
git add README.md
git commit -m "Update macOS DMG SHA256 for v5.6.0"
git push origin main
```

## 📚 Полезные ссылки

- [README.md](README.md) - Главная документация
- [CHANGELOG.md](CHANGELOG.md) - История изменений
- [BUILD_MACOS.md](BUILD_MACOS.md) - Подробная сборка macOS
- [RELEASE_NOTES_v5.6.0.md](RELEASE_NOTES_v5.6.0.md) - Заметки о релизе
- [CROSS_PLATFORM_GUIDE.md](CROSS_PLATFORM_GUIDE.md) - Работа на Windows и macOS

## 💡 Советы и лучшие практики

1. **Тестирование**: Всегда тестируйте инсталляторы на чистой системе перед публикацией
2. **Резервное копирование**: Сохраняйте старые версии инсталляторов
3. **Документация**: Обновляйте SHA256 хеши сразу после сборки
4. **Git теги**: Используйте аннотированные теги (`-a`) для релизов
5. **Changelog**: Ведите подробную историю изменений
6. **Pre-release**: Используйте для релизов с одной платформой
7. **Проверка**: Запускайте `check_env.py` перед каждой сборкой

## ⚠️ Типичные ошибки и решения

### Ошибка: "ModuleNotFoundError: No module named 'pip'"
**Решение:** `.venv` поврежден, пересоздайте:
```powershell
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Ошибка: "Unexpected token 'AllManagerC.iss'"
**Решение:** Используйте оператор `&` для путей с пробелами в PowerShell:
```powershell
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" AllManagerC.iss
```

### Ошибка: ".venv/bin/python not found" на macOS
**Решение:** Скрипт `build_macos.sh` автоматически это исправит, или:
```bash
rm -rf .venv
python3 -m venv .venv
```

## 🎯 Текущий статус релиза

Вы находитесь на **ЭТАПЕ 1** (Windows). После его завершения:
1. ✅ Все изменения будут в GitHub
2. ✅ Тег v5.6.0 создан
3. ✅ Pre-release с Windows EXE опубликован
4. ➡️ Можно переходить к ЭТАПУ 2 на macOS

---

**Готово!** Следуйте инструкциям Этапа 1, затем Этапа 2 для полного релиза v5.6.0! 🎉

