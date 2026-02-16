# contextcast アーキテクチャ（Step A）

## 目的

以下を満たす、最小構成かつ将来的に本番移行しやすい骨格を提供します。

- API: FastAPI
- Worker: Python CLI
- DB: PostgreSQL
- Storage: ローカルファイルシステム（`storage/`）
  - DBにはS3キー相当のパスのみ保存

## モノレポ構成

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
```

## ローカル実行構成

- `postgres` コンテナ: リレーショナルデータを保持
- `api` コンテナ: FastAPI + Alembic を実行
- `worker` コンテナ: 擬似キューとしてワーカー処理を手動実行

## データモデル

- `users`
- `x_accounts`
- `episodes`
- `job_runs`

生成物（audio / script / summary）はDBに本体を保存せず、キー/パス文字列のみ保存します。

## AWS移行パス

- Postgresコンテナ -> RDS PostgreSQL
- ローカルワーカー直接実行 -> SQSトリガーのECS Fargateワーカー
- ローカル `storage/` パス -> S3オブジェクトキー
- API/Workerコンテナ分離構成はECSデプロイモデルにそのまま対応
