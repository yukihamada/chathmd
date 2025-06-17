# Learning Data Format for Text-to-LoRA

## 最適な学習データ形式

Text-to-LoRAで効果的な学習を行うため、以下の形式でデータを保存します：

### 1. Training Pairs Format (JSON)

```json
{
  "id": "a1b2c3d4",
  "timestamp": "2024-01-15T10:30:00",
  "task_type": "📚 より詳しく・具体的に",
  "input": {
    "context": "User: 機械学習について教えて\nAssistant: 機械学習は...",
    "original_response": "機械学習は、コンピュータがデータから学習する技術です。",
    "user_feedback": "具体例や詳細な説明を追加して、より理解しやすくする",
    "rating": 4,
    "qualities": ["正確", "簡潔"]
  },
  "target_style": {
    "improvement_direction": "📚 より詳しく・具体的に",
    "specific_guidance": "具体例や詳細な説明を追加して、より理解しやすくする",
    "ideal_example": "画像認識やレコメンデーションシステムなどの例を含めた説明",
    "desired_qualities": ["正確", "簡潔", "詳しい"]
  },
  "metadata": {
    "is_custom_feedback": false,
    "conversation_length": 25,
    "response_length": 15
  }
}
```

### 2. Task Description Format (Plain Text)

各フィードバックに対応する自然言語タスク記述：

```
具体例やデータを含めた詳細な説明を提供する。特に具体例や詳細な説明を追加して、より理解しやすくするを重視して回答する。正確、簡潔な特徴を保ちながら改善する
```

### 3. Master Index Format (JSON)

```json
{
  "total_feedback": 15,
  "by_type": {
    "📚 より詳しく・具体的に": 7,
    "🎯 簡潔で要点を絞って": 5,
    "💡 初心者向けに優しく": 3
  },
  "by_rating": {
    "3": 2,
    "4": 8,
    "5": 5
  },
  "entries": [
    {
      "id": "a1b2c3d4",
      "timestamp": "2024-01-15T10:30:00",
      "type": "📚 より詳しく・具体的に",
      "rating": 4,
      "is_custom": false
    }
  ]
}
```

### 4. Export Format for Text-to-LoRA Training

```json
{
  "dataset_info": {
    "name": "chatHMD_feedback_dataset",
    "description": "User feedback data for Text-to-LoRA training",
    "total_samples": 15,
    "created_at": "2024-01-15T10:30:00"
  },
  "training_samples": [
    {
      "task": "具体例やデータを含めた詳細な説明を提供する",
      "input": "機械学習は、コンピュータがデータから学習する技術です。",
      "target_style": "📚 より詳しく・具体的に",
      "guidance": "具体例や詳細な説明を追加して、より理解しやすくする",
      "context": "User: 機械学習について教えて..."
    }
  ]
}
```

## データ品質の基準

### 高品質なフィードバック（推奨）
- 評価: 4-5星
- 具体的な改善提案
- 明確な期待される成果
- 会話コンテキストが豊富

### 使用されるデータ
- 最低評価: 3星以上
- 重複排除済み
- 最新のものを優先
- バランスの取れた改善タイプ

## ファイル構造

```
learning_data/
├── conversations/          # 会話履歴
├── feedback/              # 生のフィードバックデータ
├── training_pairs/        # 学習用ペアデータ (JSON)
│   ├── a1b2c3d4.json
│   ├── e5f6g7h8.json
│   └── ...
├── task_descriptions/     # タスク記述 (TXT)
│   ├── a1b2c3d4_task.txt
│   ├── e5f6g7h8_task.txt
│   └── ...
├── master_index.json      # マスターインデックス
└── text_to_lora_dataset.json  # エクスポート用データセット
```

## 使用方法

1. **フィードバック収集**: ユーザーが評価とアドバイスを提供
2. **データ保存**: 最適形式で自動保存
3. **品質フィルタ**: 3星以上のデータのみ使用
4. **データセット作成**: Text-to-LoRA用にエクスポート
5. **LoRA学習**: 生成されたタスク記述でLoRA訓練

この形式により、効率的で効果的なText-to-LoRA学習が可能になります。