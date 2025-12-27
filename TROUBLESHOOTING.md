# Решение проблем Docker

## ❌ Ошибка: "500 Internal Server Error" при docker-compose up

### Проблема
```
unable to get image 'quanttxt-api':
request returned 500 Internal Server Error
```

### Решения

#### 1. Проверьте, запущен ли Docker Desktop

```bash
# Проверка статуса Docker
docker ps

# Если ошибка - запустите Docker Desktop
# Windows: найдите "Docker Desktop" в меню Пуск
```

**Решение:** Запустите Docker Desktop и дождитесь полной загрузки (иконка в трее должна быть зеленая).

#### 2. Перезапустите Docker Desktop

1. Закройте Docker Desktop полностью
2. Запустите снова
3. Дождитесь полной загрузки
4. Попробуйте снова: `docker-compose up -d`

#### 3. Соберите образы вручную

```bash
# Сначала соберите образы
docker-compose build

# Затем запустите
docker-compose up -d
```

#### 4. Очистите Docker кэш

```bash
# Остановите все контейнеры
docker-compose down

# Очистите неиспользуемые образы
docker system prune -a

# Пересоберите
docker-compose build --no-cache
docker-compose up -d
```

#### 5. Проверьте версию Docker

```bash
docker --version
docker-compose --version
```

**Требования:**
- Docker Desktop 4.0+
- Docker Compose 2.0+

#### 6. Обновите Docker Desktop

Если версия старая, обновите Docker Desktop до последней версии.

### Другие частые ошибки

#### Порт уже занят

```
Error: bind: address already in use
```

**Решение:**
```bash
# Найдите процесс, использующий порт
netstat -ano | findstr :8000

# Или измените порт в docker-compose.yml
ports:
  - "8001:8000"  # Вместо 8000:8000
```

#### Недостаточно памяти

```
Error: no space left on device
```

**Решение:**
```bash
# Очистите неиспользуемые данные
docker system prune -a --volumes

# Освободите место на диске
```

#### Проблемы с правами доступа

```
Error: permission denied
```

**Решение:**
- Убедитесь, что Docker Desktop запущен от имени администратора
- Проверьте настройки WSL2 (если используется)

### Пошаговая диагностика

```bash
# 1. Проверьте Docker
docker ps

# 2. Проверьте образы
docker images

# 3. Проверьте docker-compose
docker-compose config

# 4. Соберите образы
docker-compose build

# 5. Запустите
docker-compose up -d

# 6. Проверьте логи
docker-compose logs
```

### Если ничего не помогает

1. **Полная переустановка Docker Desktop:**
   - Удалите Docker Desktop
   - Перезагрузите компьютер
   - Установите заново

2. **Используйте WSL2 (рекомендуется):**
   - WSL2 не обязателен, но улучшает производительность
   - Убедитесь, что WSL2 установлен: `wsl --status`
   - В Docker Desktop Settings → General → Use WSL 2 based engine
   - Подробнее: см. [DOCKER_WSL_GUIDE.md](DOCKER_WSL_GUIDE.md)

3. **Проверьте антивирус:**
   - Некоторые антивирусы блокируют Docker
   - Добавьте Docker в исключения

### Логи для диагностики

```bash
# Логи Docker
docker info

# Логи docker-compose
docker-compose logs --tail=100

# Логи конкретного сервиса
docker-compose logs api
docker-compose logs frontend
```

