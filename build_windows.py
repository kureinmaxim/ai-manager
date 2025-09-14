import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
import sys

PROJECT_ROOT = Path(__file__).parent.resolve()
DIST_DIR = PROJECT_ROOT / 'dist'
BUILD_DIR = PROJECT_ROOT / 'build'
CONFIG_FILE = PROJECT_ROOT / 'config.json'
ICON_ICO = PROJECT_ROOT / 'static' / 'images' / 'icon.ico'

def update_config_date():
    try:
        if CONFIG_FILE.exists():
            data = json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
            data.setdefault('app_info', {})
            data['app_info']['last_updated'] = datetime.now().strftime('%Y-%m-%d')
            CONFIG_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            return data.get('app_info', {}).get('version', '0.0.0')
    except Exception:
        pass
    return '0.0.0'

def build():
    DIST_DIR.mkdir(exist_ok=True)
    BUILD_DIR.mkdir(exist_ok=True)

    version = update_config_date()

    datas = [
        "templates;templates",
        "static;static",
        "config.json;.",
        "data;data",
    ]

    hidden = [
        "--hidden-import=flask",
        "--hidden-import=werkzeug",
        "--hidden-import=jinja2",
        "--hidden-import=cryptography",
        "--hidden-import=requests",
        "--hidden-import=webview",
        "--hidden-import=webview.platforms.cef",
        "--hidden-import=webview.platforms.winforms",
        "--hidden-import=webview.platforms.edgechromium",
        "--hidden-import=webview.platforms.edgehtml",
        "--hidden-import=webview.platforms.mshtml",
        "--hidden-import=webview.platforms.qt",
        "--hidden-import=yubico_client",
        "--hidden-import=yubico_client.yubico_exceptions",
        "--exclude-module=PyQt6",
        "--exclude-module=PyQt5",
        "--exclude-module=PySide6",
        "--exclude-module=PySide2",
        "--exclude-module=_tkinter",
        "--exclude-module=tkinter",
        "--exclude-module=tcl",
        "--exclude-module=tk",
    ]

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onedir",
        "--windowed",
        "--name=AllManagerC",
        "--noconfirm",
        "--clean",
        "--distpath=dist",
        "--workpath=build",
        "--noupx",
        "--debug=all",
        *[f"--add-data={d}" for d in datas],
        *hidden,
        "app.py"
    ]

    if ICON_ICO.exists():
        cmd.insert(-1, f"--icon={ICON_ICO}")

    print("Running:", " ".join(map(str, cmd)))
    rc = subprocess.call(cmd)
    if rc != 0:
        raise SystemExit(rc)
    print(f"✅ Build complete. Version: {version}. Output: dist\\AllManagerC\\")

if __name__ == "__main__":
    build()
