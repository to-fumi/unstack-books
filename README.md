# unstack-books
積んである本解消したい

FastAPI + PostgreSQL + SQLAlchemy(async) + Alembic / Python 3.14 / uv

## セットアップ

```bash
make setup      # uv sync / .env 作成 / husky インストール
make up         # api + db を起動 (local/compose.yaml)
make db-upgrade # マイグレーション適用
open http://localhost:8000/docs
```

`make help` でコマンド一覧を表示。

| コマンド | 内容 |
| --- | --- |
| `make up` / `make down` / `make logs` | コンテナ起動 / 停止 / ログ |
| `make dev` | db だけコンテナ、api はホストで起動 |
| `make db-current` | 現在の DB リビジョン |
| `make db-history` | マイグレーション履歴 |
| `make db-check` | モデルと DB の差分チェック |
| `make db-revision m="..."` | マイグレーション自動生成（`0003_xxx.py` のように連番で採番） |
| `make db-upgrade [rev=head]` | 適用 |
| `make db-downgrade [rev=-1]` | 取り消し (`rev=base` で全部) |
| `make lint` / `make format` | ruff |

Alembic はデフォルトで api コンテナ内で実行。ホストで実行するなら `RUN=local` を付ける。
ただし `db-revision` はファイルを生成するため常にホストで実行する。
環境は `ENV=local`（既定）で `local/compose.yaml` を使用。将来 `cloud/` を追加したら `ENV=cloud`。

## ディレクトリ構成

```
local/                 ローカル用 Dockerfile / compose.yaml
migrations/            Alembic
src/
├── main.py            FastAPI のエントリーポイント
├── app/               設定・DI の組み立て
│   ├── settings.py        環境変数を一括読み込み (DB 設定もここ)
│   ├── dependencies.py    Protocol と実装を結びつける (Composition Root)
│   └── exception_handlers.py  ドメイン例外 → HTTP
├── controller/        HTTP の入出力
│   ├── routers/           エンドポイント
│   ├── requests/          リクエストスキーマ (pydantic)
│   └── responses/         レスポンススキーマ (pydantic)
├── services/          ユースケース (ビジネスロジック)
├── domain/            どこにも依存しない中心
│   ├── models/            エンティティ (Book)
│   ├── value_objects/     Isbn, ReadingStatus
│   ├── dto/               レイヤー間のデータ受け渡し
│   ├── repositories/      リポジトリの Protocol
│   └── exceptions.py
└── external/          外部サービスの実装
    └── db/
        ├── client.py          engine / session
        ├── entities/          SQLAlchemy の ORM モデル
        └── repositories/      Protocol の SQLAlchemy 実装
```

依存の向き: `controller → services → domain ← external`（`app` がそれらを組み立てる）
