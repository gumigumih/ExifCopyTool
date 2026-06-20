ExifCopyTool v8
================

Windowsの右クリックメニューから画像のEXIF情報をテンプレート形式でコピーするツールです。

■ 普通に使う場合
1. build_windows.bat を実行
2. dist\ExifCopyTool.exe を起動
3. 「右クリックメニューを有効にする」にチェック

■ インストーラーを作る場合
1. Inno Setup 6 をインストール
   https://jrsoftware.org/isdl.php
2. build_windows.bat を実行
3. build_installer.bat を実行
4. installer\ExifCopyToolSetup.exe が作成されます

■ インストーラー版の挙動
- インストール先: %LOCALAPPDATA%\Programs\ExifCopyTool
- Python不要
- Windows起動時に常駐しません
- 右クリックした時だけ ExifCopyTool.exe が起動します
- アンインストール時に右クリックメニューも解除します

■ exiftool.exe について
レンズ名やメーカー独自EXIFを安定して読むには、exiftool.exe を同梱してください。
インストーラー作成時は、このフォルダに exiftool.exe を置いてから build_installer.bat を実行すると同梱されます。

■ v8変更点
- インストーラー用の Inno Setup スクリプトを追加
- build_installer.bat を追加
- --register-context-menu / --unregister-context-menu を追加
- 全ファイル表示時の AppliesTo 指定を修正
