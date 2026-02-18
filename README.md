# contextcast（Step A + Step B プロトタイプ）

以下を対象とした最小構成のモノレポです。

- FastAPI バックエンド API
- Python ワーカー
- PostgreSQL（Docker）
- Alembic マイグレーション
- ローカルファイルストレージ（`storage/`）と、DB には S3 キー相当のパスのみ保存

> 現在は Step B まで対応しています。OAuth / LLM / TTS / iOS本実装は引き続きスコープ外です。

## リポジトリ構成

```
contextcast/
  apps/
    api/
    worker/
    ios/
  infra/
    docker-compose.yml
  docs/
  storage/
  Makefile
  .env.example
```

## 前提条件

- Docker + Docker Compose
- Make

## クイックスタート

```bash
cd contextcast
make bootstrap
make up
make migrate
make seed
```

ヘルスチェック:

```bash
curl http://localhost:8000/health
```

期待レスポンス例:

```json
{
  "status": "ok",
  "service": "contextcast-api",
  "version": "0.1.0",
  "database": "up"
}
```

## Makeコマンド

- `make bootstrap` - `.env` が存在しない場合に `.env.example` から作成
- `make up` - コンテナのビルドと起動
- `make down` - コンテナ停止
- `make logs` - Composeログを追跡表示
- `make ps` - 実行中サービス一覧表示
- `make migrate` - Alembicマイグレーション適用
- `make seed` - 最小サンプルデータ投入
- `make worker-run` - ダミーワーカーパイプラインを1回実行
- `make test` - docker-compose上でAPI/Workerのpytestを実行
- `make test-api` - API系テストのみ実行
- `make test-worker` - worker + media統合テストのみ実行

## テスト実行（docker-compose）

テストは **apiコンテナ内で実行** されます。pytest から DB 作成は行わず、`POSTGRES_DB=contextcast_test` を使って compose 側で test DB を用意する前提です。

```bash
cd contextcast
cp .env.test.example .env.test
make up
make migrate
make test
```

補足:
- テスト中は `STORAGE_ROOT` を一時ディレクトリへ差し替えて隔離します。
- DB隔離は原則 transaction + rollback、worker統合テストのみ局所的にTRUNCATEを使います。

## 環境変数

詳細は `.env.example` を参照してください。

- `DATABASE_URL`
- `POSTGRES_*`
- `API_HOST`, `API_PORT`
- `LOG_LEVEL`
- `STORAGE_ROOT`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_DAYS`
- `MEDIA_BASE_URL`

## Step B APIフロー（mock login -> generate -> play）

1) ログイン（モック）

```bash
curl -s -X POST http://localhost:8000/auth/mock_login \
  -H 'Content-Type: application/json' \
  -d '{"handle":"yusuke"}'
```

レスポンスから `access_token` を控えてください。

2) 当日Episode生成

```bash
TOKEN="<access_token>"

curl -s -X POST http://localhost:8000/episodes/generate_today \
  -H "Authorization: Bearer ${TOKEN}"
```

3) 当日Episode取得

```bash
curl -s http://localhost:8000/episodes/today \
  -H "Authorization: Bearer ${TOKEN}"
```

4) 音声URL取得

```bash
EPISODE_ID="<episode_id>"

curl -s http://localhost:8000/episodes/${EPISODE_ID}/audio_url \
  -H "Authorization: Bearer ${TOKEN}"
```

5) 音声再生URLを開く

`audio_url`（例: `http://localhost:8000/media/episodes/<episode_id>/audio.mp3`）へアクセスすると、ローカル保存されたダミーmp3を取得できます。

## ストレージ方針

- 生成物はローカル `storage/` 配下にファイルとして保存します。
- DB には生成物の本体を保存せず、キー/パス文字列（S3キー相当）のみ保存します。

## 将来のAWS移行マッピング

- `postgres` -> RDS PostgreSQL
- ローカルワーカー直接実行 -> SQS + ECSワーカー
- `storage/` -> S3バケット
