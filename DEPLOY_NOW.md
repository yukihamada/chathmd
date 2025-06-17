# 🚀 今すぐデプロイ！

## GitHubリポジトリ作成後に実行：

```bash
# GitHub push
git push -u origin main

# 全自動デプロイ
./deploy_all.sh
```

## または手動で：

### 1. Cloudflare Pages (2分)
- https://pages.cloudflare.com/
- Connect Git → yukihamada/chathmd
- Root directory: `web`
- Deploy

### 2. 環境変数設定 (1分)
```
RUNPOD_API_KEY=[Set as GitHub Secret]
ENVIRONMENT=production
MODEL_NAME=jan-nano-xs
```

### 3. RunPod デプロイ (3分)
```bash
python3 runpod_deploy.py
```

### 4. リリース作成 (30秒)
```bash
git tag v1.0.0
git push origin v1.0.0
```

## 🎯 完了後のURL：
- **Webアプリ**: https://chathmd.pages.dev
- **ダウンロード**: https://yukihamada.github.io/chathmd  
- **GitHub**: https://github.com/yukihamada/chathmd

**今夜中リリース準備完璧！🎉**