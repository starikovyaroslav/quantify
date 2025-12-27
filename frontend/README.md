# QuantTxt Frontend

Современный фронтенд для QuantTxt с премиум дизайном в стиле Stripe/RunwayML.

## Технологии

- **Next.js 14** - React фреймворк
- **TypeScript** - Типизация
- **Tailwind CSS** - Стилизация
- **Framer Motion** - Анимации
- **React Dropzone** - Drag & Drop загрузка
- **Axios** - HTTP клиент

## Установка

```bash
# Установить зависимости
npm install

# Запустить dev сервер
npm run dev

# Собрать для продакшена
npm run build

# Запустить продакшен сервер
npm start
```

## Переменные окружения

Создайте `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Структура проекта

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Главная страница
│   └── globals.css         # Глобальные стили
├── components/
│   ├── SpatialBackground.tsx  # 3D фон
│   ├── GlassCard.tsx          # Стеклянная карточка
│   ├── UploadZone.tsx         # Зона загрузки
│   ├── LivePreview.tsx        # Предпросмотр
│   └── ControlsPanel.tsx      # Панель управления
├── lib/
│   ├── api.ts              # API клиент
│   └── utils.ts             # Утилиты
└── package.json
```

## Особенности дизайна

### Glassmorphism 2.0

- `backdrop-filter: blur(40px) saturate(120%)`
- Полупрозрачные фоны с размытием
- Градиентные границы

### Spatial Layers

- 3D глубина через blur и scale
- Плавающие орбы с анимацией
- Перспективные трансформации

### AI Micro-UI

- Пульсирующие индикаторы
- Анимированные прогресс-бары
- Плавные переходы состояний

## Компоненты

### SpatialBackground

3D фон с плавающими градиентными орбами и сеткой.

### GlassCard

Универсальный контейнер с glassmorphism эффектом.

### UploadZone

Drag & Drop зона для загрузки изображений с предпросмотром.

### LivePreview

Предпросмотр результата квантования в реальном времени.

### ControlsPanel

Панель управления параметрами квантования.

## API Интеграция

Фронтенд интегрирован с FastAPI бэкендом через:

- `/api/v1/quantize/` - Загрузка и квантование
- `/api/v1/quantize/status/{task_id}` - Статус задачи
- `/api/v1/quantize/result/{task_id}` - Результат

## Адаптивность

- **Mobile (320px+):** Одноколоночный layout
- **Tablet (768px+):** Двухколоночная сетка
- **Desktop (1200px+):** Полный layout с боковой панелью
- **4K:** Увеличенный масштаб и тени

## Анимации

Все анимации реализованы через Framer Motion:

- Hover эффекты
- Переходы состояний
- Плавающие элементы
- Загрузочные индикаторы



