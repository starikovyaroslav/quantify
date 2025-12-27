# Руководство по развертыванию QuantTxt

## Локальное развертывание

### Требования
- Docker & Docker Compose
- 4GB+ RAM
- 10GB+ свободного места на диске

### Быстрый старт

```bash
# Клонировать репозиторий
git clone <repository-url>
cd quanttxt

# Создать .env файл (опционально, есть значения по умолчанию)
cp .env.example .env

# Запустить все сервисы
docker-compose up -d

# Проверить статус
docker-compose ps

# Просмотр логов
docker-compose logs -f api
```

### Проверка работы

```bash
# Health check
curl http://localhost:8000/health

# API документация
open http://localhost:8000/docs
```

## Продакшен развертывание

### Kubernetes

#### 1. Создание namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: quanttxt
```

#### 2. ConfigMap для конфигурации

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: quanttxt-config
  namespace: quanttxt
data:
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
  DATABASE_URL: "postgresql+asyncpg://user:pass@postgres-service/quanttxt"
  CELERY_BROKER_URL: "redis://redis-service:6379/0"
  CELERY_RESULT_BACKEND: "redis://redis-service:6379/0"
```

#### 3. Deployment для API

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: quanttxt-api
  namespace: quanttxt
spec:
  replicas: 3
  selector:
    matchLabels:
      app: quanttxt-api
  template:
    metadata:
      labels:
        app: quanttxt-api
    spec:
      containers:
      - name: api
        image: quanttxt:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: quanttxt-config
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

#### 4. Deployment для Workers

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: quanttxt-worker
  namespace: quanttxt
spec:
  replicas: 5
  selector:
    matchLabels:
      app: quanttxt-worker
  template:
    metadata:
      labels:
        app: quanttxt-worker
    spec:
      containers:
      - name: worker
        image: quanttxt:latest
        command: ["celery", "-A", "app.celery_app", "worker", "--loglevel=info", "--concurrency=4"]
        envFrom:
        - configMapRef:
            name: quanttxt-config
        resources:
          requests:
            memory: "1Gi"
            cpu: "1000m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
```

#### 5. Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: quanttxt-api-service
  namespace: quanttxt
spec:
  selector:
    app: quanttxt-api
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

#### 6. Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: quanttxt-ingress
  namespace: quanttxt
  annotations:
    nginx.ingress.kubernetes.io/rate-limit: "100"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.quanttxt.com
    secretName: quanttxt-tls
  rules:
  - host: api.quanttxt.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: quanttxt-api-service
            port:
              number: 80
```

#### 7. HorizontalPodAutoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: quanttxt-api-hpa
  namespace: quanttxt
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: quanttxt-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Мониторинг

#### Prometheus

```yaml
apiVersion: v1
kind: ServiceMonitor
metadata:
  name: quanttxt-metrics
  namespace: quanttxt
spec:
  selector:
    matchLabels:
      app: quanttxt-api
  endpoints:
  - port: 8000
    path: /metrics
```

#### Grafana Dashboard

Импортировать дашборд для мониторинга:
- Запросов в секунду
- Времени обработки
- Размера очереди
- Использования ресурсов
- Ошибок

## Обновление

### Rolling Update

```bash
# Обновить образ
docker build -t quanttxt:v1.1.0 .

# Обновить в Kubernetes
kubectl set image deployment/quanttxt-api api=quanttxt:v1.1.0 -n quanttxt
kubectl set image deployment/quanttxt-worker worker=quanttxt:v1.1.0 -n quanttxt

# Проверить статус
kubectl rollout status deployment/quanttxt-api -n quanttxt
```

## Резервное копирование

### Redis

```bash
# Создать снимок
redis-cli --rdb /backup/redis-$(date +%Y%m%d).rdb

# Восстановить
redis-cli --rdb /backup/redis-20240101.rdb
```

### PostgreSQL

```bash
# Бэкап
pg_dump -U quanttxt quanttxt > /backup/postgres-$(date +%Y%m%d).sql

# Восстановление
psql -U quanttxt quanttxt < /backup/postgres-20240101.sql
```

### Файлы результатов

```bash
# Синхронизация с S3
aws s3 sync /app/results s3://quanttxt-results/
```

## Масштабирование

### Увеличение количества воркеров

```bash
kubectl scale deployment quanttxt-worker --replicas=10 -n quanttxt
```

### Увеличение ресурсов

```bash
kubectl set resources deployment quanttxt-api \
  --requests=memory=1Gi,cpu=1000m \
  --limits=memory=2Gi,cpu=2000m \
  -n quanttxt
```

## Troubleshooting

### Проверка логов

```bash
# API логи
kubectl logs -f deployment/quanttxt-api -n quanttxt

# Worker логи
kubectl logs -f deployment/quanttxt-worker -n quanttxt

# Redis логи
kubectl logs -f statefulset/redis -n quanttxt
```

### Проверка очереди

```bash
# Подключиться к Redis
kubectl exec -it redis-0 -n quanttxt -- redis-cli

# Проверить размер очереди
LLEN celery

# Проверить задачи
KEYS task:*
```

### Производительность

```bash
# Проверить использование ресурсов
kubectl top pods -n quanttxt

# Проверить метрики
curl http://localhost:8000/metrics
```




