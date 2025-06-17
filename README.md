# Text-to-LoRA with jan-mini-14B Q4_K_XS

jan-mini-14B-qwen3 の Q4_K_XS 量子化モデルを Text-to-LoRA (T2L) で動かすための実装です。

## 特徴

- **Q4_K_XS 量子化**: 26GB → 7.5GB にモデルサイズを削減
- **Text-to-LoRA**: 自然言語の説明から LoRA アダプタを自動生成
- **ホットスワップ**: 推論中に LoRA を動的に切り替え可能
- **低メモリ**: 16GB GPU や M1/M2 Mac で動作

## セットアップ

### 1. 環境準備

```bash
# リポジトリをクローン
git clone <your-repo> && cd texttolora

# セットアップスクリプトを実行
chmod +x setup.sh
./setup.sh
```

要件:
- Python 3.10+
- git, cmake, clang (または gcc)
- 16GB 以上の RAM
- (オプション) CUDA 対応 GPU

### 2. モデルの準備

```bash
# jan-mini-14B を Q4_K_XS に量子化
python scripts/download_and_quantize.py

# 完了すると models/jan-mini-14b-q4_k_xs.gguf が生成されます
```

### 3. ハイパーネットの準備

Text-to-LoRA のハイパーネットモデルを `trained_t2l/` に配置してください。

```bash
# 例: 事前学習済みハイパーネットをダウンロード
mkdir -p trained_t2l/jan_qwen_t2l
# ... ハイパーネットファイルを配置 ...
```

## 使い方

### LoRA の生成

自然言語のタスク説明から LoRA を生成:

```bash
# 高校入試レベルの要約タスク用 LoRA を生成
python scripts/generate_lora.py \
  trained_t2l/jan_qwen_t2l \
  "高校入試レベルの長文を80語以内で要約する" \
  --out loras/hs_summary \
  --convert-gguf

# カスタムランクで生成
python scripts/generate_lora.py \
  trained_t2l/jan_qwen_t2l \
  "技術文書を初心者向けに説明し直す" \
  --out loras/tech_simplifier \
  --rank 16 \
  --convert-gguf
```

### 推論の実行

#### シンプルな推論

```bash
# ベースモデルで推論
python scripts/inference.py \
  --prompt "Explain quantum computing in simple terms."

# LoRA を適用して推論
python scripts/inference.py \
  --lora loras/hs_summary.gguf \
  --prompt "Summarize this text: [your long text here]"
```

#### インタラクティブモード

LoRA をホットスワップしながら対話:

```bash
python scripts/inference.py --interactive

# コマンド:
# /lora loras/hs_summary.gguf  - LoRA をロード
# /nolora                      - LoRA を解除
# /exit                        - 終了
```

#### ベンチマーク

複数の LoRA を比較:

```bash
python scripts/inference.py \
  --benchmark loras/hs_summary.gguf loras/tech_simplifier.gguf \
  --prompt "Your test prompt here"
```

## ディレクトリ構造

```
texttolora/
├── scripts/
│   ├── download_and_quantize.py  # モデル量子化
│   ├── generate_lora.py          # LoRA 生成
│   └── inference.py              # 推論実行
├── models/                       # 量子化モデル
├── loras/                        # 生成した LoRA
├── trained_t2l/                  # ハイパーネット
└── llama.cpp/                    # llama.cpp (自動クローン)
```

## パフォーマンス

| 設定 | メモリ使用量 | 推論速度 |
|------|------------|---------|
| FP16 | 24-26 GB | ベースライン |
| Q4_K_XS | 7-9 GB | 1.5-2x 高速 |
| Q4_K_XS + LoRA | 8-10 GB | 1.3-1.8x 高速 |

## トラブルシューティング

### 量子化エラー

```bash
# FP32 経由で変換
python scripts/download_and_quantize.py --outtype f32
```

### LoRA 変換エラー

llama.cpp を最新版に更新:

```bash
cd llama.cpp && git pull && make clean && make
```

### メモリ不足

- `--threads` を減らす
- より小さい `--ctx-size` を使用
- CPU オフロードを有効化

## 注意事項

- jan-mini-14B は 40 層構成（通常の Llama は 32 層）
- ハイパーネットは jan-mini 用に調整が必要
- 初回実行時は HuggingFace からモデルをダウンロード（約 26GB）

## ライセンス

このプロジェクトは MIT ライセンスで公開されています。
使用するモデルのライセンスも確認してください。