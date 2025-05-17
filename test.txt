1. Bash-скрипт резервного копирования каталога
bash
КопироватьРедактировать
#!/usr/bin/env bash
# backup.sh — создаёт .tar.gz-архив и пишет лог

SRC_DIR="$1"                       # что бэкапить
DEST_DIR="/var/backups"            # куда класть архивы
LOG="/var/log/backup.log"          # файл лога
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
ARCHIVE="${DEST_DIR}/$(basename "$SRC_DIR")_${DATE}.tar.gz"

mkdir -p "$DEST_DIR"
{
  echo "[$DATE] Starting backup of $SRC_DIR"
  tar -czf "$ARCHIVE" -C "$(dirname "$SRC_DIR")" "$(basename "$SRC_DIR")"
  echo "[$DATE] Backup finished: $ARCHIVE (exit $?)"
} >>"$LOG" 2>&1

Использование: bash backup.sh /etc

2. Email-уведомление при падении GitLab CI
.gitlab-ci.yml (фрагмент):
yaml
КопироватьРедактировать
stages: [test]

test:
  image: python:3.12
  script: pytest -q
  after_script:
    # если job завершилась с ошибкой ($CI_JOB_STATUS == failed), шлём письмо
    - |
      if [ "$CI_JOB_STATUS" = "failed" ]; then
        echo -e "Subject: ❌ CI failed\nJob: $CI_JOB_URL" | \
        sendmail -S smtp.example.com -f ci@example.com dev-team@example.com
      fi

Предполагается, что runner-image содержит sendmail или msmtp.

3. Настройка удалённого репозитория и push
bash
КопироватьРедактировать
git init
git remote add origin git@github.com:your-org/your-proj.git
git add .
git commit -m "initial commit"
git push -u origin main


4. Dockerfile для минимального Flask-приложения
dockerfile
КопироватьРедактировать
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 8080
CMD ["python", "app.py"]

app.py
python
КопироватьРедактировать
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from Flask inside Docker!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

requirements.txt
ini
КопироватьРедактировать
Flask==3.0.3


5. docker-compose.yml: веб + Postgres
yaml
КопироватьРедактировать
version: "3.9"
services:
  web:
    build: .
    ports: ["8080:8080"]
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/app
    depends_on: [db]

  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: postgres
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:

Запуск: docker compose up -d.

6. Манифест Kubernetes (Deployment + Service)
yaml
КопироватьРедактировать
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-deploy
spec:
  replicas: 2
  selector:
    matchLabels: {app: flask}
  template:
    metadata:
      labels: {app: flask}
    spec:
      containers:
        - name: flask
          image: your-registry/flask:1.0.0
          ports: [{containerPort: 8080}]
          readinessProbe:
            httpGet: {path: /, port: 8080}
            initialDelaySeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: flask-svc
spec:
  type: ClusterIP
  selector: {app: flask}
  ports:
    - port: 80
      targetPort: 8080


7. .gitlab-ci.yml для Python-проекта
yaml
КопироватьРедактировать
stages: [lint, test, build]

lint:
  image: python:3.12
  script:
    - pip install flake8
    - flake8 .

test:
  image: python:3.12
  script:
    - pip install -r requirements.txt pytest
    - pytest -q

build:
  stage: build
  image: docker:26-dind
  services: [docker:26-dind]
  variables:
    DOCKER_TLS_CERTDIR: ""
  script:
    - docker build -t "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA" .
    - docker push "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA"


8. Jenkins Pipeline (Declarative) для Java-Maven
groovy
КопироватьРедактировать
pipeline {
  agent any
  tools { maven 'maven-3.9' }   // настроено в Jenkins Global Tools
  stages {
    stage('Build & Test') {
      steps {
        sh 'mvn -B clean verify'
      }
      post {
        success { junit '**/target/surefire-reports/*.xml' }
      }
    }
    stage('Docker Build') {
      when { branch 'main' }
      steps {
        script {
          docker.build("registry.example.com/app:${env.BUILD_ID}").push()
        }
      }
    }
  }
}


9. Terraform: ВМ в AWS EC2
hcl
КопироватьРедактировать
provider "aws" {
  region = "eu-central-1"
}

resource "aws_instance" "demo" {
  ami           = "ami-0c02fb55956c7d316" # Ubuntu 22.04
  instance_type = "t3.micro"

  tags = {
    Name = "demo-vm"
  }
}

Команды:
bash
КопироватьРедактировать
terraform init
terraform apply -auto-approve


10. Ansible playbook — установка Apache
yaml
КопироватьРедактировать
---
- name: Install & start Apache
  hosts: webservers
  become: true
  tasks:
    - name: Install package
      ansible.builtin.package:
        name: apache2
        state: present
    - name: Ensure service is running
      ansible.builtin.service:
        name: apache2
        state: started
        enabled: true

inventory.ini
ini
КопироватьРедактировать
[webservers]
10.0.0.11
10.0.0.12

11. Prometheus + Grafana: метрики CPU и памяти
docker-compose.yml
yaml
КопироватьРедактировать
version: "3.9"
services:
  prometheus:
    image: prom/prometheus:v2.53.0
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports: ["9090:9090"]

  node-exporter:
    image: prom/node-exporter:v1.8.1
    network_mode: host   # скрапит собственный хост

  grafana:
    image: grafana/grafana:11.0.0
    ports: ["3000:3000"]
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

prometheus.yml
yaml
КопироватьРедактировать
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'node'
    static_configs:
      - targets: ['host.docker.internal:9100']   # или IP-ноды

После запуска откройте Grafana → Settings → Data Sources → Prometheus (http://prometheus:9090). Импортируйте готовый дашборд 1860 (Node Exporter Full).

12. Filebeat → Elasticsearch
filebeat.yml (минимум)
yaml
КопироватьРедактировать
filebeat.inputs:
  - type: log
    paths: [/var/log/*.log]

output.elasticsearch:
  hosts: ["https://es.example.com:9200"]
  username: "beats_writer"
  password: "${BEATS_PASS}"
  ssl.certificate_authorities: ["/etc/ssl/certs/ca.pem"]

Запуск (systemd):
bash
КопироватьРедактировать
sudo filebeat modules enable system
sudo systemctl enable --now filebeat


13. Интеграция SonarQube в GitLab CI
yaml
КопироватьРедактировать
sonar:
  image: sonarsource/sonar-scanner-cli:5
  variables:
    SONAR_HOST_URL: "https://sonar.example.com"
    SONAR_TOKEN: "$SONAR_TOKEN"
  script:
    - sonar-scanner -Dsonar.projectKey=$CI_PROJECT_NAME
  allow_failure: true        # не блокирует pipeline


14. Скан Docker-образа Trivy
bash
КопироватьРедактировать
trivy image --exit-code 1 --severity CRITICAL,HIGH registry.example.com/app:latest

В CI:
yaml
КопироватьРедактировать
container_scan:
  image: aquasec/trivy:0.50
  script: ["trivy", "image", "--exit-code", "1", "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA"]


15. Кейс DevOps-трансформации: Netflix
Кратко:
Проблема: ручные деплои → редкие релизы, высокий MTTR.


Шаги:


Переход на AWS + Spinnaker (свой CD-движок).


Контейнеризация каждого микросервиса.


Chaos Monkey → культура «выживи при сбое».


Итог: >4 000 прод-релизов / день, глобальное безотказное стриминговое ядро.



16. Модель взаимодействия Dev & Ops при релизе
mathematica
КопироватьРедактировать
Dev → PR → Code Review → Merge → CI (build+tests)
           ↑                         ↓
        Feedback ← Ops ← CD (deploy staging) ← Smoke Tests
                                      ↓
                            Manual gate / Auto-promote
                                      ↓
                                 Deploy prod
                                      ↓
                                   Monitoring
                                      ↑
                              Incident & RCA loop


17. Scrum-backlog (фичи CI/CD)
ID
User-Story
Value
Est
Sprint
1
Как Dev я хочу GitLab CI, чтобы сборка была автоматической
★★★★
8
1
2
Как PO я хочу автотесты, чтобы снизить дефекты
★★★
5
1
3
Canary-деплой 5 % трафика
★★★
8
2
4
Slack-алёрты из Prometheus
★★
3
2
5
Rollback одной командой
★★★★
5
3


18. Blue-green в Kubernetes (Service-switch)
yaml
КопироватьРедактировать
# blue deployment
apiVersion: apps/v1
kind: Deployment
metadata: {name: app-blue}
spec:
  replicas: 3
  selector: {matchLabels: {app: demo, color: blue}}
  template: {metadata: {labels: {app: demo, color: blue}}, spec: {containers:[{name: app, image: registry/app:v1}]}}

# green deployment (новая версия)
---
apiVersion: apps/v1
kind: Deployment
metadata: {name: app-green}
spec:
  replicas: 3
  selector: {matchLabels: {app: demo, color: green}}
  template: {metadata: {labels: {app: demo, color: green}}, spec: {containers:[{name: app, image: registry/app:v2}]}}

# сервис — точка переключения
---
apiVersion: v1
kind: Service
metadata: {name: app-svc}
spec:
  selector: {app: demo, color: blue}   # изменить на green при cutover
  ports: [{port: 80, targetPort: 8080}]


19. Диаграмма CI/CD (Mermaid)
mermaid
КопироватьРедактировать
graph LR
  A[Commit] --> B(Build)
  B --> C(Test)
  C -->|pass| D(Push image -> Registry)
  D --> E(Deploy Staging)
  E --> F{Smoke OK?}
  F -- No --> C
  F -- Yes --> G(Manual gate)
  G --> H(Deploy Prod)
  H --> I(Observability)


20. Grafana alert rule (YAML)
yaml
КопироватьРедактировать
apiVersion: 1
groups:
  - name: CPU-alerts
    rules:
      - uid: high-cpu
        title: High CPU > 80 %
        condition: B
        data:
          - refId: A
            expr: avg(rate(node_cpu_seconds_total{mode!="idle"}[5m])) * 100
          - refId: B
            reduce: last
            expressions: ["A"]
            evaluator: "gt"
            params: [80]
        for: 2m
        annotations: {summary: "CPU > 80 % for 2m"}
        labels: {severity: critical}


21. Авто-удаление неудачных сборок в Jenkins (Groovy)
groovy
КопироватьРедактировать
properties([
  buildDiscarder(logRotator(
      numToKeepStr: '30',
      daysToKeepStr: '',
      artifactNumToKeepStr: '',
      artifactDaysToKeepStr: '')),
  pipelineTriggers([])
])

post {
  failure {
    cleanWs()                // стираем workspace
    script {
      currentBuild.rawBuild.delete()  // удаляем сам build
    }
  }
}


22. Ansible: инвентарь + командный запуск
inventory.ini
ini
КопироватьРедактировать
[web]
web01 ansible_host=10.0.1.10
web02 ansible_host=10.0.1.11

[db]
db01 ansible_host=10.0.2.10

Запуск:
bash
КопироватьРедактировать
ansible all -i inventory.ini -m ping
ansible-playbook -i inventory.ini site.yml


23. GitHub Actions для Python
.github/workflows/ci.yml
yaml
КопироватьРедактировать
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.12"}
      - run: pip install -r requirements.txt
      - run: pytest -q


24. Автозапуск unit-тестов после коммита (pre-push hook)
.git/hooks/pre-push
bash
КопироватьРедактировать
#!/usr/bin/env bash
pytest -q
RESULT=$?
if [ $RESULT -ne 0 ]; then
  echo "Tests failed — push aborted"
  exit 1
fi

Не забудьте chmod +x .git/hooks/pre-push.

25. Kubernetes: стратегия отката
yaml
КопироватьРедактировать
apiVersion: apps/v1
kind: Deployment
metadata: {name: app}
spec:
  revisionHistoryLimit: 5
  strategy:
    type: RollingUpdate
    rollingUpdate: {maxUnavailable: 0, maxSurge: 25%}
  replicas: 3
  selector: {matchLabels: {app: demo}}
  template:
    metadata: {labels: {app: demo}}
    spec:
      containers:
        - name: app
          image: registry/app:v3

Откат до предыдущей версии
bash
КопироватьРедактировать
kubectl rollout undo deployment/app                # к v2
kubectl rollout history deployment/app             # посмотреть ревизии
kubectl rollout undo deployment/app --to-revision=5
