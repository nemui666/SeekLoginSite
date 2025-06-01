# SeekLoginSite

SeekLoginSiteは、Seleniumを利用してWeb上のログインページを自動的に検索・検出するためのシンプルなスクリプトです。検索クエリを指定すると、Google検索結果から取得したURLを巡回し、パスワード入力欄とログイン関連キーワードの有無を判定してログインページをリストアップします。

## 主な機能

- Google検索を用いたサイトの自動収集
- ログインページ判定（パスワードフィールドとキーワードの検出）
- デバッグモードによる詳細なログ出力

## 使い方

1. 依存パッケージをインストールします。
   ```bash
   pip install selenium webdriver-manager
   ```

2. `web_login_finder.py` を実行します。検索クエリは `main` 関数内で指定されています。
   ```bash
   python web_login_finder.py
   ```

3. 実行後、検出されたログインページのURLが表示されます。

## 注意点

- 本スクリプトはGoogle検索を利用するため、実行環境によってはアクセス制限やCAPTCHAが発生する場合があります。
- `webdriver-manager` がChromeDriverをダウンロードする際、インターネット接続が必要です。

## ライセンス

MIT License
