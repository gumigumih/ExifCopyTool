EXIF Copy Tool
================

Windows の画像右クリックメニューから、EXIF情報を好きな形式でコピーする小さなツールです。

できること
----------
- フォーマット登録・編集
- 画像右クリックメニューへの登録/解除
- 右クリックからクリップボードへコピー
- 複数フォーマット対応

使い方（開発中にそのまま使う）
------------------------------
1. Python がある環境で requirements.txt をインストール
2. exif_context_app.py を起動
3. 「右クリックメニューに登録/更新」を押す

exe化
-----
Windowsで build_windows.bat を実行してください。

出力:
  dist\ExifCopyTool.exe

配布時は dist フォルダを配布してください。
ExifToolを同梱したい場合は、build前に exiftool.exe をこのフォルダへ置いてください。
同梱しない場合も Pillow fallback で JPEG等の基本EXIFは読めますが、レンズ名やメーカー独自タグはExifToolの方が強いです。

右クリック登録について
----------------------
HKCU 配下に登録するため、通常は管理者権限不要です。
Windows 11 では「その他のオプションを表示」側に出る場合があります。

テンプレート例
--------------
{Make} {Model}
{LensModel}
{FocalLength} / F{FNumber} / {ExposureTime} / ISO{ISO}
{DateTimeOriginal}

主なタグ
--------
{Make}
{Model}
{LensModel}
{FocalLength}
{FNumber}
{ExposureTime}
{ISO}
{DateTimeOriginal}
{CreateDate}
{Artist}
{Copyright}
{FileName}

保存場所
--------
%APPDATA%\ExifCopyTool\formats.json
%APPDATA%\ExifCopyTool\settings.json
