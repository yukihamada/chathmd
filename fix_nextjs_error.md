# Next.js TypeError 修正方法

## エラーの原因

```typescript
// 問題のあるコード (24行目)
const [learningQueue, setLearningQueue] = useState<Array<{messageId: string, correction: string}>([])
```

このエラーは以下の理由で発生している可能性があります：

1. **TypeScript型定義の問題**
2. **useState の初期値が正しく設定されていない**
3. **配列の型推論エラー**

## 修正方法

### 1. 型定義を明確にする

```typescript
// app/page.tsx の修正版
interface LearningQueueItem {
  messageId: string;
  correction: string;
}

const [learningQueue, setLearningQueue] = useState<LearningQueueItem[]>([]);
```

### 2. より安全な初期化

```typescript
// 安全な初期化方法
const [learningQueue, setLearningQueue] = useState(() => {
  return [] as Array<{messageId: string, correction: string}>;
});
```

### 3. デフォルト値の確実な設定

```typescript
// null チェック付きの初期化
const [learningQueue, setLearningQueue] = useState<Array<{messageId: string, correction: string}> | null>(null);

// 使用時
useEffect(() => {
  if (learningQueue === null) {
    setLearningQueue([]);
  }
}, []);
```

## 完全な修正例

```typescript
'use client'

import { useState, useEffect } from 'react'

// 型定義
interface LearningQueueItem {
  messageId: string;
  correction: string;
}

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

export default function ChatPage() {
  // State の修正
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState('');
  
  // 修正: 型定義を明確にして初期化
  const [learningQueue, setLearningQueue] = useState<LearningQueueItem[]>([]);
  
  const [isTraining, setIsTraining] = useState(false);
  const [currentModel, setCurrentModel] = useState('default');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // 学習キューに追加する関数
  const addToLearningQueue = (messageId: string, correction: string) => {
    setLearningQueue(prev => [
      ...prev,
      { messageId, correction }
    ]);
  };

  // 学習キューをクリア
  const clearLearningQueue = () => {
    setLearningQueue([]);
  };

  // LoRA 学習実行
  const trainModel = async () => {
    if (learningQueue.length === 0) return;
    
    setIsTraining(true);
    try {
      // Text-to-LoRA 学習ロジック
      const response = await fetch('/api/train-lora', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          learningData: learningQueue
        })
      });
      
      if (response.ok) {
        setCurrentModel(`trained-${Date.now()}`);
        clearLearningQueue();
      }
    } catch (error) {
      console.error('Training failed:', error);
    } finally {
      setIsTraining(false);
    }
  };

  return (
    <div className="flex h-screen">
      {/* サイドバー */}
      <div className={`${isSidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 overflow-hidden bg-gray-100`}>
        <div className="p-4">
          <h2 className="text-lg font-semibold mb-4">Learning Queue</h2>
          
          {learningQueue.length > 0 ? (
            <div className="space-y-2">
              {learningQueue.map((item, index) => (
                <div key={index} className="p-2 bg-white rounded border">
                  <p className="text-sm text-gray-600">Message: {item.messageId}</p>
                  <p className="text-sm">{item.correction}</p>
                </div>
              ))}
              
              <button
                onClick={trainModel}
                disabled={isTraining}
                className="w-full mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
              >
                {isTraining ? 'Training...' : `Train LoRA (${learningQueue.length})`}
              </button>
            </div>
          ) : (
            <p className="text-gray-500">No learning data yet</p>
          )}
        </div>
      </div>

      {/* メインチャット */}
      <div className="flex-1 flex flex-col">
        {/* ヘッダー */}
        <div className="flex items-center justify-between p-4 border-b">
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="px-3 py-1 bg-gray-200 rounded"
          >
            {isSidebarOpen ? 'Hide' : 'Show'} Learning
          </button>
          
          <div className="text-sm text-gray-600">
            Model: {currentModel}
          </div>
        </div>

        {/* メッセージエリア */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div key={message.id} className="flex flex-col">
              <div className={`p-3 rounded-lg max-w-2xl ${
                message.role === 'user' 
                  ? 'bg-blue-100 self-end' 
                  : 'bg-gray-100 self-start'
              }`}>
                {editingMessageId === message.id ? (
                  <div className="space-y-2">
                    <textarea
                      value={editContent}
                      onChange={(e) => setEditContent(e.target.value)}
                      className="w-full p-2 border rounded"
                      rows={3}
                    />
                    <div className="flex space-x-2">
                      <button
                        onClick={() => {
                          addToLearningQueue(message.id, editContent);
                          setEditingMessageId(null);
                        }}
                        className="px-3 py-1 bg-green-500 text-white rounded text-sm"
                      >
                        Save Correction
                      </button>
                      <button
                        onClick={() => setEditingMessageId(null)}
                        className="px-3 py-1 bg-gray-500 text-white rounded text-sm"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <div>
                    <p>{message.content}</p>
                    {message.role === 'assistant' && (
                      <button
                        onClick={() => {
                          setEditingMessageId(message.id);
                          setEditContent(message.content);
                        }}
                        className="mt-2 text-xs text-blue-600 hover:underline"
                      >
                        Improve this response
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* 入力エリア */}
        <div className="border-t p-4">
          <div className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
              placeholder="Type your message..."
              className="flex-1 p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  async function handleSend() {
    if (!input.trim()) return;
    
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      content: input,
      role: 'user',
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    
    try {
      // API呼び出し（実装に応じて調整）
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          model: currentModel
        })
      });
      
      const data = await response.json();
      
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        content: data.response,
        role: 'assistant',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  }
}
```

## 追加の修正ポイント

### package.json の確認
```json
{
  "dependencies": {
    "next": "^14.0.4",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "@types/react": "^18.0.0"
  }
}
```

### tsconfig.json の確認
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}
```

この修正により、TypeScript の型エラーが解決され、学習キューが正常に動作するはずです。