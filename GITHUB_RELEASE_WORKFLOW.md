# Руководство: публикация изменений и выпуск релиза через GitHub CLI (gh)

Это краткая инструкция из двух частей:
- Теория — что происходит при публикации изменений и релиза.
- Практика — готовые команды, повторяющие наш реальный сценарий в этом проекте.

---

## 1) Теория (что делаем и зачем)

- **Git-репозиторий**: локальная история коммитов. Изменения фиксируются `git add` → `git commit`, затем публикуются в удалённый репозиторий `git push`.
- **Ветка**: основная ветка — `main`. Мы коммитим и пушим в неё изменения UI.
- **Теги**: пометки конкретной версии кода. Для релизов используют аннотированные теги `vX.Y.Z` (например, `v5.5.7`).
- **Релиз GitHub**: объект на GitHub, привязанный к тегу. Содержит заголовок, заметки (release notes) и, при желании, файлы-артефакты. Управляем через `gh`.
- **Источник версии**: в этом проекте номер версии хранится в `config.json` → `app_info.version`. Мы читаем его, формируем тег `v<version>` и используем для релиза.
- **Заметки релиза**: формируем из секции `[Неопубликовано]` файла `CHANGELOG.md`.

Итого поток работ:
1. Зафиксировать изменения (`git add` → `git commit`).
2. Опубликовать их (`git push`).
3. Прочитать версию → создать и отправить тег (`git tag` → `git push origin <tag>`).
4. Создать релиз `gh release create <tag>` с заметками.

---

## 2) Практика (готовые команды)

Команды рассчитаны на macOS и встроенный терминал Cursor (добавляем `| cat` там, где возможен пейджер/длинный вывод; используем `python3`). Выполняйте их из корня проекта.

### Проверка окружения
```bash
# Версия GitHub CLI
gh --version | cat

# Авторизация gh (должно показать Logged in)
gh auth status | cat

# Текущее состояние репозитория
git status | cat
```

### Коммит и пуш изменений
```bash
# Зафиксировать изменённые файлы (пример)
git add CHANGELOG.md templates/layout.html templates/yubikey_login.html

# Коммит с сообщением
git commit -m "UI: доступ к настройке YubiKey при 0 ключей; кнопка перехода со страницы входа; обновлен CHANGELOG"

# Публикация в origin/main
git push origin main | cat
```

### Тег версии из config.json
```bash
# Считать версию из config.json (app_info.version)
VERSION=$(python3 - <<'PY'
import json
print(json.load(open('config.json'))['app_info']['version'])
PY
)
TAG="v${VERSION}"
echo "Готовим тег: $TAG" | cat

# Создать аннотированный тег и отправить его
git tag -a "$TAG" -m "Release $TAG: UI improvements for YubiKey setup access"
git push origin "$TAG" | cat
```

### Заметки релиза из CHANGELOG и публикация
```bash
# Вытянуть текст из секции [Неопубликовано] CHANGELOG.md
REL_NOTES=$(awk '/^## \[Неопубликовано\]/{flag=1;next}/^## \[/{flag=0}flag' CHANGELOG.md | sed 's/^#\{1,\}//')

# Создать релиз на GitHub, привязанный к тегу
gh release create "$TAG" \
  --title "AllManagerC $TAG" \
  --notes "$REL_NOTES" | cat
```

### Полезные команды после релиза
```bash
# Просмотреть релиз
gh release view "$TAG" | cat

# Открыть релиз в браузере
gh release view "$TAG" --web

# Загрузить артефакты (пример: dmg или zip)
# gh release upload "$TAG" dist/AllManagerC_Installer.dmg --clobber | cat
```

### Откат (при необходимости)
```bash
# Удалить релиз (тег останется)
gh release delete "$TAG" --yes | cat

# Удалить локальный и удалённый тег
git tag -d "$TAG"
git push origin :refs/tags/"$TAG" | cat
```

---

## Работа через интерфейс gh (интерактивно и с открытием браузера)

Ниже — способы сделать то же самое с минимальным числом флагов, используя интерактивные подсказки `gh` и встроенный редактор.

### Вход в аккаунт (через браузер)
```bash
gh auth login --hostname github.com --web --git-protocol ssh | cat
```

### Настроить редактор для заметок релиза
```bash
# Пример для VS Code
export GH_EDITOR="code --wait"
# или для nano
export GH_EDITOR="nano"
```

### Интерактивное создание релиза
```bash
TAG=v5.5.7  # замените на вашу версию

# Откроется интерактивный ввод и редактор для заметок
gh release create "$TAG"
```
- Чтобы сгенерировать заметки автоматически на основе коммитов/PR:
```bash
gh release create "$TAG" --generate-notes
```
- Чтобы использовать локальный файл и сначала сохранить как черновик:
```bash
gh release create "$TAG" --notes-file CHANGELOG.md --draft
```

### Редактирование уже созданного релиза (интерактивно)
```bash
gh release edit "$TAG"
```

### Открыть страницы в браузере
```bash
# Домашняя страница репозитория
gh repo view --web

# Страница конкретного релиза
gh release view "$TAG" --web

# Раздел кода на нужной ветке
gh browse --branch main
```

### Интерактивная загрузка файлов-артефактов
```bash
# При конфликте версии файла используйте --clobber
gh release upload "$TAG" dist/AllManagerC_Installer.dmg --clobber | cat
```

Подсказка: многие команды `gh` без обязательных флагов работают в диалоговом режиме (задают вопросы и/или открывают редактор), что удобно для ручного выпуска релиза.
