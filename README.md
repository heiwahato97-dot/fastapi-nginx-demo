# FastAPI Nginx Demo

FastAPIアプリケーションをNginxのReverse Proxy経由で公開するデモです。

## 概要

Docker Composeを使用して、FastAPIとNginxを別々のコンテナとして起動します。

ブラウザからFastAPIへ直接アクセスするのではなく、Nginxを入口としてFastAPIへリクエストを転送します。

```text
Browser
   ↓ HTTP :80
Nginx container
   ↓ proxy_pass
FastAPI container :8000
```

## 使用技術

- Python
- FastAPI
- Uvicorn
- Nginx
- Docker
- Docker Compose

## 構成

```text
fastapi-nginx-demo/
├── nginx/
│   └── default.conf
├── main.py
├── requirements.txt
├── Dockerfile
├── compose.yaml
├── .dockerignore
├── .gitignore
└── README.md
```

## FastAPI

FastAPIはコンテナ内部の8000番ポートで動作します。

```python
@app.get("/")
def root():
    return {
        "message": "Hello through Nginx"
    }
```

ステータス確認用APIも用意しています。

```python
@app.get("/api/status")
def status():
    return {
        "status": "ok",
        "server": "FastAPI"
    }
```

## Nginx Reverse Proxy

`nginx/default.conf`:

```nginx
server {
    listen 80;

    location / {
        proxy_pass http://api:8000;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

重要なのは次の設定です。

```nginx
proxy_pass http://api:8000;
```

Docker Composeのサービス名 `api` をホスト名として使用し、NginxからFastAPIへリクエストを転送します。

## Docker Compose

`compose.yaml` では2つのサービスを定義します。

```text
api
→ FastAPI

nginx
→ Nginx Reverse Proxy
```

FastAPI側は、

```yaml
expose:
  - "8000"
```

とし、ホスト側へ8000番ポートを直接公開しません。

Nginx側だけ、

```yaml
ports:
  - "80:80"
```

として外部へ公開します。

そのため外部からの入口はNginxになります。

## 起動

設定を確認します。

```bash
docker compose config
```

コンテナをビルドして起動します。

```bash
docker compose up --build
```

コンテナの状態を確認します。

```bash
docker compose ps
```

正常時にはFastAPIとNginxの両方が起動します。

## 動作確認

### Root endpoint

```text
http://127.0.0.1/
```

Response:

```json
{
  "message": "Hello through Nginx"
}
```

### Status endpoint

```text
http://127.0.0.1/api/status
```

Response:

```json
{
  "status": "ok",
  "server": "FastAPI"
}
```

PowerShellから確認する場合:

```bash
curl.exe http://127.0.0.1/
curl.exe http://127.0.0.1/api/status
```

## リクエストの流れ

```text
Client
  ↓
localhost:80
  ↓
Nginx
  ↓
proxy_pass http://api:8000
  ↓
FastAPI
  ↓
Response
```

FastAPIを直接外部公開するのではなく、NginxがReverse ProxyとしてFastAPIの前段に配置されています。

## 停止

```bash
docker compose down
```

## 学習ポイント

- Nginx
- Reverse Proxy
- `proxy_pass`
- Docker Compose
- Multi-container application
- Docker内部ネットワーク
- サービス名による名前解決
- FastAPIのコンテナ化
- ポート公開と内部ポートの違い
- Proxy headers