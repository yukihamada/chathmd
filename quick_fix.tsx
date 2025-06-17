// 🔧 即座の修正：app/page.tsx の24行目を以下に変更

// ❌ 問題のあるコード
const [learningQueue, setLearningQueue] = useState<Array<{messageId: string, correction: string}>([])

// ✅ 修正版1: 括弧の位置を修正
const [learningQueue, setLearningQueue] = useState<Array<{messageId: string, correction: string}>>([])

// ✅ 修正版2: より明確な型定義
interface LearningItem {
  messageId: string;
  correction: string;
}

const [learningQueue, setLearningQueue] = useState<LearningItem[]>([])

// ✅ 修正版3: 最も安全な方法
const [learningQueue, setLearningQueue] = useState(() => {
  return [] as Array<{messageId: string, correction: string}>;
});

// 🎯 推奨される完全な修正
'use client'

import { useState } from 'react'

// 型定義
interface LearningQueueItem {
  messageId: string;
  correction: string;
}

export default function Page() {
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null)
  const [editContent, setEditContent] = useState('')
  
  // 🔥 ここを修正！
  const [learningQueue, setLearningQueue] = useState<LearningQueueItem[]>([])
  
  const [isTraining, setIsTraining] = useState(false)
  const [currentModel, setCurrentModel] = useState('default')
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  // 残りのコンポーネントロジック...
  
  return (
    <div>
      {/* UI コンテンツ */}
    </div>
  )
}