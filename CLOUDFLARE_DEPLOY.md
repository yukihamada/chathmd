# 🌐 Cloudflare Pages デプロイメントガイド

## 🚀 クイックデプロイ

### 1. Cloudflare Pages セットアップ

1. **Cloudflare Pages に移動**
   - https://pages.cloudflare.com/
   - 「Create a project」をクリック

2. **GitHubリポジトリ接続**
   - 「Connect to Git」を選択
   - `yukihamada/chathmd` リポジトリを選択
   - 「Begin setup」をクリック

3. **ビルド設定**
   - **Project name**: `chathmd`
   - **Production branch**: `main`
   - **Build command**: 空のまま
   - **Build output directory**: `web`
   - **Root directory**: `/web`

4. **Deploy** をクリック

### 2. RunPod インテグレーション設定

#### RunPod セットアップ
1. **RunPod アカウント作成**
   - https://runpod.io/ でアカウント作成
   - GPU ポッドを起動（推奨: RTX 4090 または A100）

2. **モデルデプロイ**
   ```bash
   # RunPod ポッドで実行
   git clone https://github.com/ggerganov/llama.cpp
   cd llama.cpp
   make LLAMA_CUBLAS=1
   
   # モデルダウンロード（例：Qwen2.5-7B）
   wget https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf
   
   # サーバー起動
   ./llama-server -m Qwen2.5-7B-Instruct-Q4_K_M.gguf --port 8080 --host 0.0.0.0
   ```

3. **エンドポイント作成**
   - RunPod ダッシュボードでエンドポイント作成
   - エンドポイントIDを記録

#### Cloudflare環境変数設定
1. **Cloudflare Pages 設定**
   - Pages プロジェクト → Settings → Environment variables

2. **変数を追加**
   ```
   RUNPOD_API_KEY=your-runpod-api-key
   RUNPOD_ENDPOINT=your-runpod-endpoint-id
   ```

### 3. カスタムドメイン設定（オプション）

1. **ドメイン追加**
   - Pages プロジェクト → Custom domains
   - 「Set up a custom domain」をクリック
   - ドメイン名を入力（例：chat.yourdomain.com）

2. **DNS設定**
   - ドメインのDNSでCNAMEレコード追加
   - `chat` → `chathmd.pages.dev`

### 4. Analytics 設定（オプション）

1. **KV Namespace 作成**
   ```bash
   # Wrangler CLI使用
   npm install -g wrangler
   wrangler login
   wrangler kv:namespace create "ANALYTICS"
   ```

2. **環境変数に追加**
   ```
   ANALYTICS_KV_ID=your-kv-namespace-id
   ```

## 📊 監視とメンテナンス

### パフォーマンス監視
- Cloudflare Analytics でトラフィック確認
- RunPod メトリクスでGPU使用率監視
- API レスポンス時間の追跡

### コスト最適化
- **RunPod**: 使用量ベース課金
  - アイドル時間を最小化
  - 適切なGPUタイプ選択
- **Cloudflare**: 
  - Pages: 無料枠（月100万リクエスト）
  - Functions: 無料枠（月10万リクエスト）

### トラブルシューティング

#### よくある問題
1. **API エラー**
   - RunPod エンドポイントの状態確認
   - API キーの有効性確認

2. **デプロイ失敗**
   - ビルドログの確認
   - Functions の構文エラーチェック

3. **CORS エラー**
   - Functions でのCORSヘッダー確認
   - ドメイン設定の確認

## 🎯 完成後のURL

- **メインサイト**: `https://chathmd.pages.dev`
- **カスタムドメイン**: `https://chat.yourdomain.com`
- **API エンドポイント**: `https://chathmd.pages.dev/api/chat`

## 🔧 開発者向け

### ローカル開発
```bash
cd web
npx wrangler pages dev . --compatibility-date=2024-06-17
```

### Functions テスト
```bash
curl -X POST https://chathmd.pages.dev/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "model": "runpod"}'
```

この設定により、プライバシーを重視したクラウドAIサービスが完成します！