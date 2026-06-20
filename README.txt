ExifCopyTool v10
================

Windowsの右クリックメニューから画像のEXIF情報をテンプレート形式でコピーするツールです。

■ 普通に使う場合
1. build_windows.bat を実行
2. dist\ExifCopyTool.exe を起動
3. 「有効にする」にチェック
4. 「表示する拡張子」に右クリックメニューを出したい拡張子を入力
   例: .jpg, .jpeg, .png, .heic, .arw, .dng
5. 「拡張子を保存して再登録」を押す

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

■ v10変更点
- インストーラー作者名を「ぐみ ( meggumi.com )」に変更
- 「全ファイルにも表示する」を廃止
- コンテキストメニューに表示する拡張子を設定画面で指定できるように変更
- .jpg/.heic/.arw/.dng など、指定した拡張子ごとに右クリックメニューを登録
- v7/v8で登録した全ファイル用メニューは再登録時に削除
