"""
EXIF Copy Tool - Windows context menu utility.

Features:
- GUI for editing output formats
- Register/unregister Windows right-click menu entries under HKCU (no admin)
- Copy EXIF text to clipboard from context menu
- Uses bundled exiftool.exe when present; falls back to Pillow for common tags
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from typing import Any, Dict, List

try:
    import winreg  # type: ignore
except Exception:  # pragma: no cover
    winreg = None  # type: ignore

try:
    from PIL import Image, ExifTags  # type: ignore
except Exception:
    Image = None  # type: ignore
    ExifTags = None  # type: ignore

APP_NAME = "ExifCopyTool"
MENU_ROOT_KEY = r"Software\Classes\SystemFileAssociations\image\shell\ExifCopyTool"
SENDTO_SHORTCUT_NAME = "EXIF情報をコピー.lnk"

DEFAULT_FORMATS = [
    {
        "name": "撮影設定",
        "template": "{Make} {Model}\n{LensModel}\n{FocalLength} / F{FNumber} / {ExposureTime} / ISO{ISO}\n{DateTimeOriginal}",
    },
    {
        "name": "SNS用",
        "template": "📷 {Make} {Model}\n🔭 {LensModel}\n⚙️ {FocalLength} / F{FNumber} / {ExposureTime} / ISO{ISO}",
    },
    {
        "name": "Markdown",
        "template": "**Camera:** {Make} {Model}\n**Lens:** {LensModel}\n**Settings:** {FocalLength} / F{FNumber} / {ExposureTime} / ISO{ISO}\n**Date:** {DateTimeOriginal}",
    },
]

EXIFTOOL_TAGS = [
    "DateTimeOriginal",
    "CreateDate",
    "Make",
    "Model",
    "LensModel",
    "LensID",
    "FNumber",
    "ExposureTime",
    "ISO",
    "FocalLength",
    "FocalLengthIn35mmFormat",
    "Artist",
    "Copyright",
    "FileName",
]

PIL_TAG_ALIASES = {
    "DateTimeOriginal": "DateTimeOriginal",
    "Make": "Make",
    "Model": "Model",
    "FNumber": "FNumber",
    "ExposureTime": "ExposureTime",
    "ISOSpeedRatings": "ISO",
    "PhotographicSensitivity": "ISO",
    "FocalLength": "FocalLength",
    "LensModel": "LensModel",
    "Artist": "Artist",
    "Copyright": "Copyright",
}


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def data_dir() -> Path:
    base = os.environ.get("APPDATA")
    if base:
        p = Path(base) / APP_NAME
    else:
        p = app_dir() / "data"
    p.mkdir(parents=True, exist_ok=True)
    return p


def formats_path() -> Path:
    return data_dir() / "formats.json"


def settings_path() -> Path:
    return data_dir() / "settings.json"


def load_formats() -> List[Dict[str, str]]:
    p = formats_path()
    if not p.exists():
        save_formats(DEFAULT_FORMATS)
        return [dict(x) for x in DEFAULT_FORMATS]
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [{"name": str(x.get("name", "")), "template": str(x.get("template", ""))} for x in data]
    except Exception:
        pass
    return [dict(x) for x in DEFAULT_FORMATS]


def save_formats(formats: List[Dict[str, str]]) -> None:
    formats_path().write_text(json.dumps(formats, ensure_ascii=False, indent=2), encoding="utf-8")


def load_settings() -> Dict[str, Any]:
    p = settings_path()
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_settings(settings: Dict[str, Any]) -> None:
    settings_path().write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")


def executable_path() -> str:
    if getattr(sys, "frozen", False):
        return str(Path(sys.executable).resolve())
    return str(Path(sys.executable).resolve())


def script_arg_prefix() -> List[str]:
    if getattr(sys, "frozen", False):
        return [executable_path()]
    return [executable_path(), str(Path(__file__).resolve())]


def find_exiftool() -> str | None:
    candidates = [
        app_dir() / "exiftool.exe",
        app_dir() / "exiftool(-k).exe",
        app_dir() / "tools" / "exiftool.exe",
        app_dir() / "tools" / "exiftool(-k).exe",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return shutil.which("exiftool") or shutil.which("exiftool.exe")


def rational_to_str(v: Any) -> str:
    try:
        # Pillow IFDRational
        f = float(v)
        if f.is_integer():
            return str(int(f))
        return f"{f:g}"
    except Exception:
        return str(v)


def exposure_to_str(v: Any) -> str:
    try:
        f = float(v)
        if f and f < 1:
            denom = round(1 / f)
            return f"1/{denom}"
        return f"{f:g}"
    except Exception:
        return str(v)


def read_exif_exiftool(image_path: str) -> Dict[str, str]:
    exe = find_exiftool()
    if not exe:
        raise RuntimeError("exiftool.exe が見つかりません")
    args = [exe, "-j", "-n"] + [f"-{t}" for t in EXIFTOOL_TAGS] + [image_path]
    proc = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", creationflags=0x08000000 if os.name == "nt" else 0)
    if proc.returncode not in (0, 1):
        raise RuntimeError(proc.stderr.strip() or "ExifTool の実行に失敗しました")
    arr = json.loads(proc.stdout or "[]")
    raw = arr[0] if arr else {}
    out = {k: "" for k in EXIFTOOL_TAGS}
    for k, v in raw.items():
        if k == "SourceFile":
            continue
        out[k] = str(v)
    if not out.get("LensModel") and out.get("LensID"):
        out["LensModel"] = out["LensID"]
    return out


def read_exif_pillow(image_path: str) -> Dict[str, str]:
    if Image is None or ExifTags is None:
        raise RuntimeError("Pillow が利用できません")
    out = {k: "" for k in EXIFTOOL_TAGS}
    out["FileName"] = Path(image_path).name
    with Image.open(image_path) as img:
        exif = img.getexif()
        tag_map = ExifTags.TAGS
        for tag_id, value in exif.items():
            name = tag_map.get(tag_id, str(tag_id))
            dest = PIL_TAG_ALIASES.get(name)
            if not dest:
                continue
            if dest == "ExposureTime":
                out[dest] = exposure_to_str(value)
            elif dest == "FNumber":
                out[dest] = rational_to_str(value)
            elif dest == "FocalLength":
                out[dest] = rational_to_str(value) + " mm"
            else:
                out[dest] = str(value)
    return out


def read_exif(image_path: str) -> Dict[str, str]:
    try:
        d = read_exif_exiftool(image_path)
    except Exception:
        d = read_exif_pillow(image_path)
    d.setdefault("FileName", Path(image_path).name)
    # Pretty fixes
    if d.get("FNumber") and not str(d["FNumber"]).startswith("F"):
        pass
    if d.get("ISO") and str(d["ISO"]).lower().startswith("iso"):
        d["ISO"] = str(d["ISO"])[3:].strip()
    return d


def render_template(template: str, data: Dict[str, str]) -> str:
    class SafeDict(dict):
        def __missing__(self, key: str) -> str:
            return ""
    text = template.format_map(SafeDict(data))
    lines = [line.rstrip() for line in text.splitlines()]
    # Remove lines that became nearly empty after missing fields
    return "\n".join([line for line in lines if line.strip() and line.strip() not in {"/ /", "//"}]).strip()


def copy_to_clipboard(text: str) -> None:
    root = tk.Tk()
    root.withdraw()
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()
    root.destroy()


def copy_format(format_name: str, image_paths: List[str]) -> None:
    formats = load_formats()
    fmt = next((f for f in formats if f["name"] == format_name), formats[0] if formats else DEFAULT_FORMATS[0])
    rendered = []
    for p in image_paths:
        data = read_exif(p)
        rendered.append(render_template(fmt["template"], data))
    copy_to_clipboard("\n\n".join(rendered))


def register_context_menu() -> None:
    if winreg is None:
        raise RuntimeError("Windows専用機能です")
    formats = load_formats()
    exe_parts = script_arg_prefix()
    root = winreg.CreateKey(winreg.HKEY_CURRENT_USER, MENU_ROOT_KEY)
    winreg.SetValueEx(root, "MUIVerb", 0, winreg.REG_SZ, "EXIF情報をコピー")
    winreg.SetValueEx(root, "SubCommands", 0, winreg.REG_SZ, "")
    winreg.SetValueEx(root, "Icon", 0, winreg.REG_SZ, exe_parts[0])
    shell_key = winreg.CreateKey(root, "shell")
    for idx, fmt in enumerate(formats):
        key_name = f"format_{idx:02d}"
        k = winreg.CreateKey(shell_key, key_name)
        winreg.SetValueEx(k, "MUIVerb", 0, winreg.REG_SZ, fmt["name"])
        cmd = ' '.join([f'"{x}"' for x in exe_parts] + ["--copy", f'"{fmt["name"]}"', '"%1"'])
        ck = winreg.CreateKey(k, "command")
        winreg.SetValueEx(ck, "", 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(ck)
        winreg.CloseKey(k)
    settings_key = winreg.CreateKey(shell_key, "settings")
    winreg.SetValueEx(settings_key, "MUIVerb", 0, winreg.REG_SZ, "フォーマット設定を開く")
    cmd = ' '.join([f'"{x}"' for x in exe_parts])
    ck = winreg.CreateKey(settings_key, "command")
    winreg.SetValueEx(ck, "", 0, winreg.REG_SZ, cmd)
    winreg.CloseKey(ck)
    winreg.CloseKey(settings_key)
    winreg.CloseKey(shell_key)
    winreg.CloseKey(root)
    settings = load_settings()
    settings["context_menu_registered"] = True
    save_settings(settings)


def delete_tree(root: Any, subkey: str) -> None:
    try:
        with winreg.OpenKey(root, subkey, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:  # type: ignore
            while True:
                try:
                    child = winreg.EnumKey(key, 0)  # type: ignore
                    delete_tree(key, child)
                except OSError:
                    break
        winreg.DeleteKey(root, subkey)  # type: ignore
    except FileNotFoundError:
        return


def unregister_context_menu() -> None:
    if winreg is None:
        raise RuntimeError("Windows専用機能です")
    delete_tree(winreg.HKEY_CURRENT_USER, MENU_ROOT_KEY)
    settings = load_settings()
    settings["context_menu_registered"] = False
    save_settings(settings)


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("EXIFコピー 設定")
        self.geometry("760x560")
        self.formats = load_formats()
        self.selected_index = 0
        self._build()
        self._refresh_list()

    def _build(self) -> None:
        top = ttk.Frame(self, padding=10)
        top.pack(fill="both", expand=True)

        left = ttk.Frame(top)
        left.pack(side="left", fill="y", padx=(0, 10))
        ttk.Label(left, text="フォーマット").pack(anchor="w")
        self.listbox = tk.Listbox(left, width=24, height=18)
        self.listbox.pack(fill="y", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        btns = ttk.Frame(left)
        btns.pack(fill="x", pady=6)
        ttk.Button(btns, text="追加", command=self.add_format).pack(side="left")
        ttk.Button(btns, text="削除", command=self.delete_format).pack(side="left", padx=4)

        right = ttk.Frame(top)
        right.pack(side="left", fill="both", expand=True)
        ttk.Label(right, text="名前").pack(anchor="w")
        self.name_var = tk.StringVar()
        ttk.Entry(right, textvariable=self.name_var).pack(fill="x", pady=(0, 8))
        ttk.Label(right, text="テンプレート（使える項目: {Make}, {Model}, {LensModel}, {FocalLength}, {FNumber}, {ExposureTime}, {ISO}, {DateTimeOriginal}, {FileName} など）").pack(anchor="w")
        self.text = tk.Text(right, height=12, wrap="word")
        self.text.pack(fill="both", expand=True)

        sample_frame = ttk.Frame(right)
        sample_frame.pack(fill="x", pady=8)
        ttk.Button(sample_frame, text="保存", command=self.save_current).pack(side="left")
        ttk.Button(sample_frame, text="画像でテスト", command=self.test_image).pack(side="left", padx=6)
        ttk.Button(sample_frame, text="右クリックメニューに登録/更新", command=self.register).pack(side="left", padx=6)
        ttk.Button(sample_frame, text="登録解除", command=self.unregister).pack(side="left")

        ttk.Label(right, text="テスト出力").pack(anchor="w")
        self.preview = tk.Text(right, height=7, wrap="word")
        self.preview.pack(fill="both")

    def _refresh_list(self) -> None:
        self.listbox.delete(0, "end")
        for f in self.formats:
            self.listbox.insert("end", f["name"])
        if self.formats:
            self.listbox.selection_set(min(self.selected_index, len(self.formats)-1))
            self.load_selected()

    def on_select(self, _event: Any = None) -> None:
        sel = self.listbox.curselection()
        if sel:
            self.selected_index = sel[0]
            self.load_selected()

    def load_selected(self) -> None:
        if not self.formats:
            return
        fmt = self.formats[self.selected_index]
        self.name_var.set(fmt["name"])
        self.text.delete("1.0", "end")
        self.text.insert("1.0", fmt["template"])

    def save_current(self) -> None:
        if not self.formats:
            return
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("エラー", "名前を入力してください")
            return
        self.formats[self.selected_index] = {"name": name, "template": self.text.get("1.0", "end").strip()}
        save_formats(self.formats)
        self._refresh_list()
        messagebox.showinfo("保存しました", "フォーマットを保存しました。右クリックメニューにも反映する場合は登録/更新してください。")

    def add_format(self) -> None:
        self.formats.append({"name": "新しいフォーマット", "template": "{Make} {Model}\n{FocalLength} / F{FNumber} / {ExposureTime} / ISO{ISO}"})
        self.selected_index = len(self.formats) - 1
        save_formats(self.formats)
        self._refresh_list()

    def delete_format(self) -> None:
        if len(self.formats) <= 1:
            messagebox.showwarning("削除できません", "フォーマットは最低1つ必要です。")
            return
        del self.formats[self.selected_index]
        self.selected_index = max(0, self.selected_index - 1)
        save_formats(self.formats)
        self._refresh_list()

    def test_image(self) -> None:
        self.save_current()
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.tif *.tiff *.heic *.webp"), ("All files", "*.*")])
        if not path:
            return
        try:
            data = read_exif(path)
            text = render_template(self.formats[self.selected_index]["template"], data)
            self.preview.delete("1.0", "end")
            self.preview.insert("1.0", text)
            copy_to_clipboard(text)
            messagebox.showinfo("コピーしました", "テスト出力をクリップボードにコピーしました。")
        except Exception as e:
            messagebox.showerror("エラー", str(e))

    def register(self) -> None:
        self.save_current()
        try:
            register_context_menu()
            messagebox.showinfo("登録しました", "画像ファイルの右クリックメニューに登録しました。Windows 11では『その他のオプションを表示』側に出る場合があります。")
        except Exception as e:
            messagebox.showerror("登録失敗", str(e))

    def unregister(self) -> None:
        try:
            unregister_context_menu()
            messagebox.showinfo("解除しました", "右クリックメニューから削除しました。")
        except Exception as e:
            messagebox.showerror("解除失敗", str(e))


def main() -> None:
    try:
        if "--copy" in sys.argv:
            i = sys.argv.index("--copy")
            fmt = sys.argv[i + 1]
            paths = sys.argv[i + 2:]
            if not paths:
                raise RuntimeError("画像ファイルが指定されていません")
            copy_format(fmt, paths)
            return
        App().mainloop()
    except Exception as e:
        log = data_dir() / "error.log"
        log.write_text(traceback.format_exc(), encoding="utf-8")
        try:
            messagebox.showerror("EXIFコピー エラー", f"{e}\n\n詳細: {log}")
        except Exception:
            pass


if __name__ == "__main__":
    main()
