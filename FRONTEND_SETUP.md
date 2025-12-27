# Настройка фронтенда QuantTxt

## Быстрый старт

### 1. Установка зависимостей

```bash
cd frontend
npm install
```

### 2. Настройка переменных окружения

Создайте файл `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Запуск dev сервера

```bash
npm run dev
```

Фронтенд будет доступен на `http://localhost:3000`

## Структура проекта

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout с Toaster
│   ├── page.tsx            # Главная страница (Editor)
│   ├── gallery/
│   │   └── page.tsx        # Галерея готовых файлов
│   ├── pricing/
│   │   └── page.tsx        # Страница тарифов
│   ├── profile/
│   │   └── page.tsx        # Профиль пользователя
│   └── globals.css         # Глобальные стили + утилиты
├── components/
│   ├── SpatialBackground.tsx  # 3D фон с плавающими орбами
│   ├── GlassCard.tsx          # Универсальный glassmorphism контейнер
│   ├── UploadZone.tsx         # Drag & Drop зона загрузки
│   ├── LivePreview.tsx         # Предпросмотр результата
│   ├── ControlsPanel.tsx      # Панель управления параметрами
│   └── Navigation.tsx         # Навигационное меню
├── lib/
│   ├── api.ts              # API клиент для интеграции с бэкендом
│   └── utils.ts             # Утилиты (cn для classnames)
└── package.json
```

## Особенности реализации

### Glassmorphism 2.0
- `backdrop-filter: blur(40px) saturate(120%)`
- Полупрозрачные фоны `rgba(255, 255, 255, 0.08)`
- Градиентные границы `rgba(255, 255, 255, 0.2)`

### Spatial Layers
- 3 плавающих градиентных орба с анимацией
- Grid pattern overlay для глубины
- Fixed position с z-index: -1

### AI Micro-UI
- Пульсирующие индикаторы статуса
- Анимированные прогресс-бары
- Плавные переходы состояний через Framer Motion

### Адаптивность
- Mobile-first подход
- Responsive grid layouts
- Адаптивные размеры компонентов

## Интеграция с бэкендом

Фронтенд интегрирован с FastAPI через:

1. **POST /api/v1/quantize/** - Загрузка и создание задачи
2. **GET /api/v1/quantize/status/{task_id}** - Проверка статуса
3. **GET /api/v1/quantize/result/{task_id}** - Получение результата

### Пример использования

```typescript
import { quantizeImage, getTaskStatus, getTaskResult } from '@/lib/api'

// Загрузка изображения
const response = await quantizeImage(file, 200, 200, 5)

// Polling статуса
const status = await getTaskStatus(response.task_id)

// Получение результата
const text = await getTaskResult(response.task_id)
```

## Компоненты

### SpatialBackground
3D фон с:
- Радиальным градиентом
- 3 плавающими орбами (разные размеры и цвета)
- Grid pattern overlay
- Анимацией через Framer Motion

### GlassCard
Универсальный контейнер:
- Glassmorphism эффект
- Настраиваемый padding
- Hover эффекты (опционально)
- Адаптивные размеры

### UploadZone
Drag & Drop зона:
- Поддержка drag & drop
- Предпросмотр изображения
- Валидация размера и типа
- Анимированные состояния

### LivePreview
Предпросмотр результата:
- Отображение текста в стиле Notepad
- Индикаторы статуса (idle/processing/completed/error)
- Скроллируемая область
- Анимации переходов

### ControlsPanel
Панель управления:
- Слайдеры для width/height/quality
- Кастомные стили (chrome-none)
- Кнопка квантования с градиентом
- Состояния загрузки

## Стилизация

### Цветовая палитра
- Primary: `#667eea` → `#764ba2` (градиент)
- Accent: `#10b981` (emerald)
- Glass: `rgba(255, 255, 255, 0.08)`
- Background: `slate-950`

### Анимации
Все анимации через Framer Motion:
- `whileHover`: масштабирование при наведении
- `whileTap`: уменьшение при клике
- `animate`: плавающие элементы
- `transition`: плавные переходы

## Сборка для продакшена

```bash
# Сборка
npm run build

# Запуск продакшен сервера
npm start
```

## Деплой

### Vercel (рекомендуется)
```bash
npm i -g vercel
vercel
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

## Troubleshooting

### Проблемы с API
- Проверьте `NEXT_PUBLIC_API_URL` в `.env.local`
- Убедитесь, что бэкенд запущен на указанном порту
- Проверьте CORS настройки на бэкенде

### Проблемы со стилями
- Убедитесь, что Tailwind правильно настроен
- Проверьте `tailwind.config.ts`
- Очистите кэш: `rm -rf .next`

### Проблемы с изображениями
- Для preview используется обычный `<img>` (не Next.js Image)
- Это позволяет отображать blob URLs

## Дальнейшие улучшения

1. **Аутентификация**
   - Добавить страницу логина/регистрации
   - Интегрировать с бэкендом auth

2. **Реальное API**
   - Подключить реальные endpoints
   - Добавить обработку ошибок

3. **Оптимизация**
   - Code splitting
   - Lazy loading компонентов
   - Image optimization

4. **Дополнительные функции**
   - Сохранение в галерею
   - Экспорт в разные форматы
   - История операций




