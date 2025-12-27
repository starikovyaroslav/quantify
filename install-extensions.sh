#!/bin/bash
# Скрипт автоматической установки расширений Cursor для QuantTxt
# Запуск: chmod +x install-extensions.sh && ./install-extensions.sh

echo "🚀 Установка расширений Cursor для QuantTxt..."
echo ""

extensions=(
    # Python
    "ms-python.python"
    "ms-python.vscode-pylance"
    "ms-python.black-formatter"
    "ms-python.isort"
    "ms-python.flake8"
    "ms-python.mypy-type-checker"

    # TypeScript/React
    "dbaeumer.vscode-eslint"
    "esbenp.prettier-vscode"
    "bradlc.vscode-tailwindcss"

    # Docker
    "ms-azuretools.vscode-docker"

    # Git
    "eamodio.gitlens"

    # Code Quality
    "usernamehw.errorlens"
    "streetsidesoftware.code-spell-checker"
    "streetsidesoftware.code-spell-checker-russian"

    # Productivity
    "formulahendry.auto-rename-tag"
    "christian-kohler.path-intellisense"
    "ms-vscode.vscode-json"

    # API Development
    "humao.rest-client"

    # Markdown
    "yzhang.markdown-all-in-one"

    # Environment Files
    "mikestead.dotenv"
)

installed=0
failed=0
skipped=0

for ext in "${extensions[@]}"; do
    echo "📦 Установка: $ext"

    # Проверяем, установлено ли уже расширение
    if cursor --list-extensions 2>/dev/null | grep -q "$ext"; then
        echo "   ✓ Уже установлено"
        ((skipped++))
    else
        # Устанавливаем расширение
        if cursor --install-extension "$ext" >/dev/null 2>&1; then
            echo "   ✅ Установлено успешно"
            ((installed++))
        else
            echo "   ❌ Ошибка установки"
            ((failed++))
        fi
    fi

    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Итоги установки:"
echo "   ✅ Установлено: $installed"
echo "   ⏭️  Пропущено (уже установлено): $skipped"
echo "   ❌ Ошибок: $failed"
echo ""

if [ $failed -eq 0 ]; then
    echo "🎉 Все расширения успешно установлены!"
    echo ""
    echo "💡 Совет: Перезапустите Cursor для применения всех изменений"
else
    echo "⚠️  Некоторые расширения не удалось установить"
    echo "   Попробуйте установить их вручную через панель расширений"
fi




