# 🌍 Кросс-платформенная разработка

Руководство по работе с проектом AllManagerC на разных операционных системах.

## ⚠️ Важно: Виртуальные окружения

### Главное правило

**Виртуальное окружение `.venv` НЕЛЬЗЯ использовать между разными операционными системами!**

| Платформа | Структура `.venv` | Активация |
|-----------|-------------------|-----------|
| **Windows** | `.venv\Scripts\python.exe` | `.\.venv\Scripts\Activate.ps1` |
| **macOS/Linux** | `.venv/bin/python` | `source .venv/bin/activate` |

### Почему не работает?

1. **Разные пути:** Windows использует `\`, Unix использует `/`
2. **Разные бинарники:** `.pyd` (Windows) vs `.so` (Unix)
3. **Разные скрипты:** PowerShell vs Bash
4. **Разные Python:** Возможно разные версии или сборки

## 📋 Сценарии работы

### Сценарий 1: Работа только на одной платформе

```bash
# Создайте .venv один раз
python -m venv .venv  # Windows
python3 -m venv .venv  # macOS/Linux

# Активируйте
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
source .venv/bin/activate     # macOS/Linux

# Установите зависимости
pip install -r requirements.txt
```

✅ `.venv` в `.gitignore` - не попадет в репозиторий

### Сценарий 2: Переключение между Windows и macOS

#### На Windows:
```powershell
# Создайте .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Работайте с проектом
python app.py

# Закоммитьте изменения (без .venv!)
git add .
git commit -m "My changes"
git push
```

#### На macOS:
```bash
# Клонируйте или переключитесь на ветку
git pull

# УДАЛИТЕ Windows .venv (если он как-то попал)
rm -rf .venv

# Создайте НОВЫЙ .venv для macOS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Работайте с проектом
python3 app.py
```

### Сценарий 3: Автоматизация сборки

#### Windows:
```powershell
# Используйте build_windows.py
.\.venv\Scripts\Activate.ps1
python build_windows.py

# Затем Inno Setup для инсталлятора
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" AllManagerC.iss
```

#### macOS:
```bash
# Используйте build_macos.sh (он умный!)
chmod +x build_macos.sh
./build_macos.sh

# Скрипт сам:
# 1. Обнаружит Windows .venv
# 2. Удалит его
# 3. Создаст новый для macOS
# 4. Соберет приложение
```

## 🔍 Проверка платформы .venv

### Как узнать, для какой платформы создан .venv?

#### Windows PowerShell:
```powershell
# Если существует - это Windows
Test-Path .venv\Scripts\python.exe
# True = Windows, False = macOS/Linux или не существует
```

#### macOS/Linux:
```bash
# Если существует - это macOS/Linux
test -f .venv/bin/python && echo "Unix" || echo "Windows or not exists"
```

## 🛠️ Команды для разных платформ

### Создание проекта

| Действие | Windows | macOS/Linux |
|----------|---------|-------------|
| Создать venv | `python -m venv .venv` | `python3 -m venv .venv` |
| Активировать (PowerShell) | `.\.venv\Scripts\Activate.ps1` | - |
| Активировать (CMD) | `.venv\Scripts\activate.bat` | - |
| Активировать (Bash) | - | `source .venv/bin/activate` |
| Деактивировать | `deactivate` | `deactivate` |
| Удалить venv | `Remove-Item -Recurse -Force .venv` | `rm -rf .venv` |

### Установка зависимостей

```bash
# Одинаково на всех платформах (после активации)
pip install -r requirements.txt
```

### Запуск приложения

| Режим | Windows | macOS/Linux |
|-------|---------|-------------|
| GUI | `python run_app.py` | `python3 run_app.py` |
| Web | `python app.py` | `python3 app.py` |
| С отладкой | `set FLASK_DEBUG=1 && python app.py` | `FLASK_DEBUG=1 python3 app.py` |

### Сборка

| Платформа | Команда |
|-----------|---------|
| Windows | `python build_windows.py` → Inno Setup |
| macOS | `./build_macos.sh` |

## 🚫 Типичные ошибки

### Ошибка 1: "python.exe not found" на macOS

**Причина:** Используете Windows `.venv` на macOS

**Решение:**
```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Ошибка 2: "Activate.ps1 not found" на Windows

**Причина:** Используете macOS/Linux `.venv` на Windows

**Решение:**
```powershell
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Ошибка 3: .venv в git

**Проверка:**
```bash
git status | grep .venv
```

Если показывает `.venv/`, значит он попал в git.

**Решение:**
```bash
# Убедитесь, что .venv в .gitignore
echo ".venv/" >> .gitignore

# Удалите из git (но не с диска!)
git rm -r --cached .venv
git commit -m "Remove .venv from git"
```

## ✅ Лучшие практики

### 1. Всегда используйте виртуальное окружение
```bash
# ❌ НЕ ТАК
python app.py  # глобальные пакеты

# ✅ ТАК
source .venv/bin/activate
python app.py
```

### 2. Фиксируйте версии зависимостей
```bash
# После установки всех пакетов
pip freeze > requirements.txt
```

### 3. Документируйте команды в README
- Разделяйте команды для Windows и Unix
- Указывайте PowerShell vs CMD vs Bash
- Примеры для каждой платформы

### 4. Используйте скрипты сборки
- `build_windows.py` для Windows
- `build_macos.sh` для macOS
- Они сами проверяют окружение

### 5. Тестируйте на обеих платформах
- Windows: Тестируйте в PowerShell И CMD
- macOS: Тестируйте в Terminal
- Linux: Тестируйте в Bash

## 📝 Чек-лист перед коммитом

- [ ] `.venv/` в `.gitignore`
- [ ] `.venv/` не в `git status`
- [ ] `requirements.txt` актуален
- [ ] Работает на вашей платформе
- [ ] Документация обновлена для обеих платформ
- [ ] Версия обновлена в `config.json`

## 🆘 Быстрая помощь

### Полный сброс окружения

#### Windows:
```powershell
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

#### macOS/Linux:
```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Автоматическая проверка

В проекте есть готовый скрипт `check_env.py` для диагностики окружения.

Запустите:
```bash
# Windows
python check_env.py

# macOS/Linux
python3 check_env.py
```

Скрипт покажет:
- 🖥️ Платформу и архитектуру
- 🐍 Версию Python
- 📦 Статус виртуального окружения
- ⚠️ Обнаружит несовместимость .venv (Windows на macOS или наоборот)
- 📚 Установленные зависимости
- ⚙️ Конфигурацию проекта
- 💡 Рекомендации по исправлению

---

**Помните:** `.venv` - это временный артефакт сборки, как `node_modules` или `build/`.  
Он не должен попадать в git и должен пересоздаваться на каждой платформе!

