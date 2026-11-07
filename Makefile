.DEFAULT_GOAL := help
# 環境ごとに compose ファイルを切り替える（例: make up ENV=cloud → cloud/compose.yaml）
ENV ?= local
COMPOSE := docker compose -f $(ENV)/compose.yaml --env-file .env

# Alembic はデフォルトで api コンテナ内で実行する。
# ホストから実行したい場合は RUN=local を付ける（例: make db-current RUN=local）
ifeq ($(RUN),local)
  ALEMBIC := uv run alembic
else
  ALEMBIC := $(COMPOSE) exec api alembic
endif

.PHONY: help
help: ## コマンド一覧
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-14s\033[0m %s\n", $$1, $$2}'

# ---------- セットアップ ----------
.PHONY: setup
setup: ## 初回セットアップ（Python依存・.env・husky）
	uv sync
	@test -f .env || cp .env.example .env
	npm install

# ---------- サーバー ----------
.PHONY: up
up: ## api + db を起動（ビルド込み）
	$(COMPOSE) up -d --build

.PHONY: down
down: ## コンテナ停止
	$(COMPOSE) down

.PHONY: logs
logs: ## api のログを表示
	$(COMPOSE) logs -f api

.PHONY: dev
dev: ## db だけ compose で起動し、api はホストで起動
	$(COMPOSE) up -d db
	uv run fastapi dev src/main.py

# ---------- マイグレーション ----------
.PHONY: db-current
db-current: ## 現在の DB スキーマのリビジョンを表示
	$(ALEMBIC) current --verbose

.PHONY: db-history
db-history: ## マイグレーション履歴を表示
	$(ALEMBIC) history --verbose

.PHONY: db-check
db-check: ## モデルと DB に差分がないか確認
	$(ALEMBIC) check

.PHONY: db-revision
db-revision: ## マイグレーション自動生成  例: make db-revision m="add xxx"
	@test -n "$(m)" || (echo 'メッセージを指定してください: make db-revision m="..."' && exit 1)
	$(ALEMBIC) revision --autogenerate -m "$(m)"

.PHONY: db-upgrade
db-upgrade: ## 適用（既定: head）  例: make db-upgrade rev=+1
	$(ALEMBIC) upgrade $(or $(rev),head)

.PHONY: db-downgrade
db-downgrade: ## 取り消し（既定: -1）  例: make db-downgrade rev=base
	$(ALEMBIC) downgrade $(or $(rev),-1)

# ---------- Lint / Format ----------
.PHONY: lint
lint: ## lint + フォーマットチェック
	uv run ruff check .
	uv run ruff format --check .

.PHONY: format
format: ## 自動修正 + フォーマット
	uv run ruff check --fix .
	uv run ruff format .
