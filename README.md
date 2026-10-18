# Share Hub

公開してよい資料・スライド・画像・短い動画の共有専用リポジトリ。

- サイト: https://taaaaryu.github.io/share-hub/
- スライド: `slides/<slug>/index.html` と `deck.json`
- 動画・デモ: `videos/<slug>/` / `demos/<slug>/`
- 共通テンプレート: `templates/analysis.json`、`assets/theme-terminal.css`
- 出典: 共通テンプレートは taaaaryu/slide-share を継承。

## 資料の追加

```sh
python3 scripts/new_deck.py <slug> "<title>"
python3 scripts/validate_decks.py
node --check assets/deck.js
node --check assets/home.js
```

動画はH.264/MP4、`<video controls playsinline preload="metadata">` を基本にする。
短い動画のみ直接配置し、大きい動画は別配信先を利用する。公開前に動画の全体を確認する。
GitHubの通常Gitは100MiB超のファイルを拒否、Pagesサイト全体は1GB以内。

## 公開範囲

このリポジトリとPagesは全世界に公開される。秘密情報・個人情報・未承認の非公開資料・原動画を追加しない。
名前やチャットを隠した場合も、内容・音声・メタデータの公開可否を確認する。
既存のslide-shareや非公開開発リポジトリを自動で移行しない。

## 公開済み
- [3D Fight Replay](https://taaaaryu.github.io/share-hub/videos/fight-replay-20261018/): 元動画・想定3D版・コーチング。2026-10-18にユーザーがプレイヤー名を含めマスキングなしの公開を許可。
