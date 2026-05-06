import os
import sys
import zipfile
import urllib.request
import shutil

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pocketfish", "assets")

def download_stockfish():
    os.makedirs(ASSETS_DIR, exist_ok=True)

    out_path = os.path.join(ASSETS_DIR, "stockfish.exe")

    if os.path.isfile(out_path):
        print("Stockfish already installed, skipping.")
        return

    archive_path = os.path.join(ASSETS_DIR, "stockfish.zip")

    print(f"Downloading Stockfish...")

    def reporthook(block, block_size, total):
        if total > 0:
            pct = min(100, block * block_size * 100 // total)
            print(f"\r  {pct}%", end="", flush=True)

    urllib.request.urlretrieve("https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-windows-x86-64-avx2.zip", archive_path, reporthook)
    print()

    print("Extracting...")
    with zipfile.ZipFile(archive_path, "r") as z:
        for member in z.namelist():
            if os.path.basename(member) == "stockfish-windows-x86-64-avx2.exe":
                with z.open(member) as src, open(out_path, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                break

    os.remove(archive_path)

    if os.path.isfile(out_path):
        print(f"Stockfish installed to {out_path}")
    else:
        print("ERROR: Could not find Stockfish binary in the archive.")
        print("Please download manually from https://stockfishchess.org/download/")
        sys.exit(1)


def install_dependencies():
    print("Installing Python dependencies...")
    os.system(f"{sys.executable} -m pip install -r requirements.txt")


if __name__ == "__main__":
    install_dependencies()
    download_stockfish()
    print("\nAll done!")