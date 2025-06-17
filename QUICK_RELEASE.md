# 🚀 今夜中リリースガイド

## 1. GitHubリポジトリ作成（2分）

1. https://github.com/new にアクセス
2. Repository name: `chathmd` または `texttolora`  
3. Description: `Privacy-first AI assistant with Text-to-LoRA learning technology`
4. Public を選択
5. **Initialize options はすべて空のまま**
6. Create repository

## 2. リモートリポジトリ設定（1分）

```bash
# GitHubリポジトリのURLに置き換えてください
git remote add origin https://github.com/YOUR_USERNAME/chathmd.git
git branch -M main
git push -u origin main
```

## 3. GitHub Pages 有効化（1分）

1. GitHub リポジトリページで Settings をクリック
2. 左サイドバーで Pages をクリック  
3. Source: "Deploy from a branch"
4. Branch: main
5. Folder: / (docs)
6. Save をクリック

## 4. Actions 有効化確認（1分）

1. GitHub リポジトリで Actions タブをクリック
2. "I understand my workflows, go ahead and enable them" をクリック
3. ワークフローが表示されることを確認

## 5. 最初のリリース作成（5分）

```bash
# v1.0.0 タグ作成
git tag v1.0.0
git push origin v1.0.0
```

リリースタグをpushすると、GitHub Actionsが自動で：
- Mac用DMGファイル作成
- Windows用ZIPファイル作成  
- Linux用TAR.GZ・DEBファイル作成
- GitHub Releasesページに公開

## 6. 確認事項（3分）

✅ GitHub Actions が正常実行中か確認
✅ GitHub Pages サイトが表示されるか確認
✅ リリースファイルが作成されているか確認

## 🎯 合計所要時間: 約12分

エラーが発生した場合は、GitHub Actionsログを確認してデバッグします。

---
**注意**: 初回ビルドは依存関係ダウンロードで時間がかかる場合があります（10-15分程度）