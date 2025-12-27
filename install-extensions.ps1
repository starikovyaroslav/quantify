# Скрипт автоматической установки расширений Cursor для QuantTxt
# Запуск: .\install-extensions.ps1

Write-Host "🚀 Установка расширений Cursor для QuantTxt..." -ForegroundColor Green
Write-Host ""

$extensions = @(
    # Python
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "ms-python.isort",
    "ms-python.flake8",
    "ms-python.mypy-type-checker",

    # TypeScript/React
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",

    # Docker
    "ms-azuretools.vscode-docker",

    # Git
    "eamodio.gitlens",

    # Code Quality
    "usernamehw.errorlens",
    "streetsidesoftware.code-spell-checker",
    "streetsidesoftware.code-spell-checker-russian",

    # Productivity
    "formulahendry.auto-rename-tag",
    "christian-kohler.path-intellisense",
    "ms-vscode.vscode-json",

    # API Development
    "humao.rest-client",

    # Markdown
    "yzhang.markdown-all-in-one",

    # Environment Files
    "mikestead.dotenv"
)

$installed = 0
$failed = 0
$skipped = 0

foreach ($ext in $extensions) {
    Write-Host "📦 Установка: $ext" -ForegroundColor Cyan

    # Проверяем, установлено ли уже расширение
    $result = cursor --list-extensions 2>$null | Select-String -Pattern $ext

    if ($result) {
        Write-Host "   ✓ Уже установлено" -ForegroundColor Yellow
        $skipped++
    } else {
        # Устанавливаем расширение
        $installResult = cursor --install-extension $ext 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Установлено успешно" -ForegroundColor Green
            $installed++
        } else {
            Write-Host "   ❌ Ошибка установки" -ForegroundColor Red
            Write-Host "   $installResult" -ForegroundColor Red
            $failed++
        }
    }

    Write-Host ""
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "📊 Итоги установки:" -ForegroundColor Green
Write-Host "   ✅ Установлено: $installed" -ForegroundColor Green
Write-Host "   ⏭️  Пропущено (уже установлено): $skipped" -ForegroundColor Yellow
Write-Host "   ❌ Ошибок: $failed" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($failed -eq 0) {
    Write-Host "🎉 Все расширения успешно установлены!" -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 Совет: Перезапустите Cursor для применения всех изменений" -ForegroundColor Cyan
} else {
    Write-Host "⚠️  Некоторые расширения не удалось установить" -ForegroundColor Yellow
    Write-Host "   Попробуйте установить их вручную через панель расширений (Ctrl+Shift+X)" -ForegroundColor Yellow
}




