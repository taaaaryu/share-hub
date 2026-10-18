# 共有用公開リポジトリ

ユーザーへの公開可能な成果物の共有先は、この `share-hub` リポジトリと https://taaaaryu.github.io/share-hub/ を使う。
ローカルの標準パスは `/Users/taaaaryu/Desktop/share-hub`。

- 調査・解析資料は `scripts/new_deck.py` と `templates/analysis.json` の共通テンプレートを使う。共通デザインは `assets/theme-terminal.css`。
- 動画・デモは必要に応じて `videos/<slug>/` / `demos/<slug>/` に置き、トップからリンクする。
- 秘密情報・個人情報・未承認の非公開データを公開しない。該当する資料や動画の公開方法はユーザーと先に決める。公開許可は元の素材全体への包括的な許可と解釈しない。
- `python3 scripts/validate_decks.py` と対象JSの構文検査を行う。動画は全フレームdecode、尺、ブラウザ再生を確認する。
- 公開後にPagesのページと素材が200で取得できることを確認し、閲覧URLをユーザーに渡す。
- 旧 `slide-share` と非公開の開発repoは自動移行しない。

## 説明資料の読みやすさ
2026-10-18のユーザー指定により、文字数に合わせて説明を無理に短縮しない。専門用語や仮定は意味と具体例を説明し、確認済みの事実・仮定・未検証事項を分ける。スライドに収まらない場合は読みやすいHTMLレポートを優先する。共有先は引き続きshare-hub。
