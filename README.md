ExifCopyTool
============

写真ファイルを右クリックして、EXIF情報を好きなフォーマットでクリップボードへコピーするWindows向けツールです。
カメラ、レンズ、焦点距離、F値、シャッタースピード、ISO、撮影日時などを、SNS投稿やメモ用に整えられます。

ダウンロード
------------

最新版はGitHub Releasesからダウンロードできます。

- インストーラー版: https://github.com/gumigumih/ExifCopyTool/releases/latest/download/ExifCopyToolSetup.exe
- リリースページ: https://github.com/gumigumih/ExifCopyTool/releases/latest

通常はインストーラー版を使ってください。Pythonのインストールは不要です。

使い方
------

1. `ExifCopyToolSetup.exe` をダウンロードしてインストールします。
2. 設定画面で「右クリックメニュー」を有効にします。
3. 写真ファイルを右クリックします。
4. 「EXIF情報をコピー」から使いたいフォーマットを選びます。
5. 整形されたEXIF情報がクリップボードへコピーされます。

フォーマット編集
----------------

設定画面の「フォーマット編集」タブで、コピー内容を自由に編集できます。

例:

```text
{Make} {Model}
{LensModel}
{FocalLength} / F{FNumber} / {ExposureTime} / ISO{ISO}
{DateTimeOriginal}
```

よく使うタグ:

- `{Make}`: メーカー
- `{Model}`: カメラ名
- `{LensModel}`: レンズ名
- `{FocalLength}`: 焦点距離
- `{FNumber}`: F値
- `{ExposureTime}`: シャッタースピード
- `{ISO}`: ISO感度
- `{DateTimeOriginal}`: 撮影日時
- `{FileName}`: ファイル名

設定画面にはサンプルプレビューが表示されるので、実際にコピーされる見た目を確認しながら編集できます。

対応ファイル
------------

JPEG、PNG、TIFF、HEIC、WebPに加えて、ARW、CR3、NEFなどのRAWファイルでも取得できる範囲のEXIF情報を読み取ります。
レンズ名などのメーカー独自情報を安定して取得したい場合は、ExifTool同梱版または `exiftool.exe` の利用を推奨します。

インストール先と動作
--------------------

- インストール先: `%LOCALAPPDATA%\Programs\ExifCopyTool`
- Windows起動時に常駐しません。
- 右クリックした時だけアプリが起動します。
- コピー結果はWindows通知で表示されます。
- アンインストール時に右クリックメニューも解除します。

更新確認について
----------------

設定画面の「アプリ設定」タブから更新確認できます。
GitHubリポジトリがprivateの場合、未認証のアプリから最新Releaseを取得できないため、更新確認に失敗することがあります。

開発者向け
----------

ローカルでビルドする場合:

```bat
build_windows.bat
build_installer.bat
```

`installer\ExifCopyToolSetup.exe` が作成されます。
