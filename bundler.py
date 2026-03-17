import os
import sys
import subprocess
import shutil
from pathlib import Path

def build():
    print("🚀 BRIGHTOS — EXE Construction Engine v3.0")
    print("--------------------------------------------------")
    
    # Clean old builds
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            print(f"🧹 Cleaning {folder}...")
            shutil.rmtree(folder)

    # PyInstaller Command
    # We include our custom directories as data
    # We use --onedir to keep security_vault and neural_store persistent outside the EXE
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "BrightOS",
        # We don't need avatar.png anymore as it's procedural Jarvis circles
        "--add-data", "visual_link;visual_link",
        "--add-data", "system_laws;system_laws",
        "igniter.py"
    ]
    
    print("🛠️  Starting PyInstaller build...")
    subprocess.run(cmd, check=True)

    dist_path = Path("dist/BrightOS")
    
    # Export core component folders to the EXE directory
    core_components = ["ability_core", "central_nerve", "neural_store", "security_vault"]
    
    for folder in core_components:
        src = Path(folder)
        dst = dist_path / folder
        if src.exists():
            print(f"📁 Linking System Component: {folder}")
            if dst.exists(): shutil.rmtree(dst)
            shutil.copytree(src, dst)

    print("\n" + "═"*60)
    print(" ✅ BRIGHTOS DEPLOYMENT COMPLETE")
    print(f" 📂 EXE Location: {os.path.abspath(dist_path)}")
    print(" 🚀 Launch BrightOS.exe to begin.")
    print("═"*60 + "\n")

if __name__ == "__main__":
    build()
