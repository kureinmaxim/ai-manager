# 🚀 Быстрое руководство по созданию релиза v5.6.0

## ✅ Что уже сделано

- [x] Обновлена версия до 5.6.0 во всех файлах
- [x] Обновлен CHANGELOG.md с описанием изменений
- [x] Создана документация по сборке Windows (Inno Setup)
- [x] Создана документация по сборке macOS
- [x] Создан автоматический скрипт для macOS (build_macos.sh)
- [x] Обновлены все команды для работы с .venv
- [x] Добавлен раздел "Решение проблем" в README

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

## 🎯 Следующие шаги

### 1. Сборка для Windows

```powershell
# В вашем текущем терминале (уже в .venv)
(.venv) PS> python build_windows.py

# После успешной сборки:
# Откройте AllManagerC.iss в Inno Setup Compiler
# Нажмите Build → Compile (или F9)
# Инсталлятор будет в dist\AllManagerC_Installer.exe
```

### 2. Сборка для macOS (если у вас есть доступ к Mac)

> **⚠️ Важно:** Если вы работали на Windows, `.venv` от Windows не будет работать на macOS.  
> Скрипт `build_macos.sh` автоматически обнаружит это и пересоздаст `.venv` для macOS.

```bash
# На macOS:
chmod +x build_macos.sh
./build_macos.sh

# Скрипт автоматически:
# - Обнаружит Windows .venv и пересоздаст для macOS (если нужно)
# - Установит все зависимости
# - Создаст dist/AllManagerC.app
# - Создаст dist/AllManagerC_Installer_v5.6.0.dmg
# - Покажет SHA256 хеш
```

### 3. Коммит изменений

```bash
# Добавить все файлы
git add .

# Создать коммит
git commit -m "Release v5.6.0: Improved documentation and Windows support"

# Создать тег
git tag -a v5.6.0 -m "Release version 5.6.0"

# Отправить изменения
git push origin main
git push origin v5.6.0
```

### 4. Создание GitHub Release

#### Вариант A: Через веб-интерфейс GitHub

1. Перейдите на https://github.com/kureinmaxim/ai-manager/releases
2. Нажмите "Draft a new release"
3. Выберите тег: `v5.6.0`
4. Название: `AllManagerC v5.6.0`
5. Описание: скопируйте содержимое из `RELEASE_NOTES_v5.6.0.md`
6. Загрузите файлы:
   - `AllManagerC_Installer.exe` (Windows)
   - `AllManagerC_Installer_v5.6.0.dmg` (macOS)
7. Нажмите "Publish release"

#### Вариант B: Через GitHub CLI

```bash
# Установите GitHub CLI: https://cli.github.com/

# Создайте релиз
gh release create v5.6.0 \
    dist/AllManagerC_Installer.exe \
    dist/AllManagerC_Installer_v5.6.0.dmg \
    --title "AllManagerC v5.6.0" \
    --notes-file RELEASE_NOTES_v5.6.0.md
```

### 5. Обновление README с SHA256

После создания macOS DMG, обновите README.md:

```bash
# Получите SHA256 хеш (macOS/Linux)
shasum -a 256 dist/AllManagerC_Installer_v5.6.0.dmg

# Windows PowerShell
Get-FileHash dist\AllManagerC_Installer_v5.6.0.dmg -Algorithm SHA256

# Вставьте хеш в README.md вместо "будет обновлен после сборки"
```

### 6. Финальная проверка

- [ ] Протестирован Windows инсталлятор
- [ ] Протестирован macOS DMG
- [ ] Проверены все ссылки в README
- [ ] Обновлен SHA256 хеш в README
- [ ] Создан GitHub Release
- [ ] Опубликованы изменения

## 📝 Быстрые команды

```bash
# Полный цикл релиза (после сборки инсталляторов)
git add .
git commit -m "Release v5.6.0"
git tag -a v5.6.0 -m "Release version 5.6.0"
git push origin main --tags

# Создание релиза
gh release create v5.6.0 \
    dist/AllManagerC_Installer.exe \
    dist/AllManagerC_Installer_v5.6.0.dmg \
    --title "AllManagerC v5.6.0" \
    --notes-file RELEASE_NOTES_v5.6.0.md
```

## 🔍 Проверка перед релизом

```bash
# Проверка окружения
python check_env.py

# Проверка версий
grep -r "5.6.0" config.json AllManagerC.iss app.py run_app.py

# Проверка сборки Windows
python build_windows.py

# Проверка файлов
ls -lh dist/
```

## 📚 Полезные ссылки

- [README.md](README.md) - Главная документация
- [CHANGELOG.md](CHANGELOG.md) - История изменений
- [BUILD_MACOS.md](BUILD_MACOS.md) - Подробная сборка macOS
- [RELEASE_NOTES_v5.6.0.md](RELEASE_NOTES_v5.6.0.md) - Заметки о релизе
- [CROSS_PLATFORM_GUIDE.md](CROSS_PLATFORM_GUIDE.md) - Работа на Windows и macOS

## 💡 Советы

1. **Тестирование**: Всегда тестируйте инсталляторы на чистой системе
2. **Резервное копирование**: Сохраняйте старые версии инсталляторов
3. **Документация**: Обновляйте SHA256 хеши сразу после сборки
4. **Git теги**: Используйте аннотированные теги (-a) для релизов
5. **Changelog**: Ведите подробную историю изменений

---

**Готово!** Теперь у вас есть все необходимое для создания релиза v5.6.0! 🎉

