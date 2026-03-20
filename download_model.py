#!/usr/bin/env python3
"""
互動式 HuggingFace 模型下載工具
用法: python download_model.py

環境變數（選填）:
  HTTP_PROXY   - Proxy 位址，例如 http://your-proxy:3128
  HTTPS_PROXY  - Proxy 位址
  SAVE_BASE    - 模型儲存根目錄，預設為當前目錄下的 models/
  HF_TOKEN     - HuggingFace Token（需要授權的模型才需要）
"""

import os
import sys
import urllib.request
import urllib.error
import json

# ── 設定（優先讀取環境變數，沒有則用預設值）──────────────
HTTP_PROXY  = os.environ.get("HTTP_PROXY", "")
HTTPS_PROXY = os.environ.get("HTTPS_PROXY", "")
SAVE_BASE   = os.environ.get("SAVE_BASE", os.path.join(os.getcwd(), "models"))
HF_TOKEN    = os.environ.get("HF_TOKEN", "")
# ────────────────────────────────────────────────────────

if HTTP_PROXY:
    os.environ["http_proxy"]  = HTTP_PROXY
if HTTPS_PROXY:
    os.environ["https_proxy"] = HTTPS_PROXY


def fetch_file_list(repo_id: str) -> list[str]:
    """從 HuggingFace API 取得檔案清單"""
    api_url = f"https://huggingface.co/api/models/{repo_id}"
    req = urllib.request.Request(api_url)
    if HF_TOKEN:
        req.add_header("Authorization", f"Bearer {HF_TOKEN}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return [f["rfilename"] for f in data.get("siblings", [])]
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print("\n[錯誤] 此模型需要 HuggingFace Token（403 Forbidden）")
            print("       請設定環境變數: export HF_TOKEN=hf_你的token")
        else:
            print(f"\n[錯誤] HTTP {e.code}: {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[錯誤] 無法取得檔案清單: {e}")
        sys.exit(1)


def download_file(url: str, dest: str) -> bool:
    """下載單一檔案，支援斷點續傳"""
    os.makedirs(os.path.dirname(dest) if os.path.dirname(dest) else ".", exist_ok=True)

    existing_size = os.path.getsize(dest) if os.path.exists(dest) else 0
    req = urllib.request.Request(url)
    if HF_TOKEN:
        req.add_header("Authorization", f"Bearer {HF_TOKEN}")
    if existing_size > 0:
        req.add_header("Range", f"bytes={existing_size}-")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            total = int(resp.headers.get("Content-Length", 0)) + existing_size
            total_mb = total / (1024 * 1024)
            mode = "ab" if existing_size > 0 else "wb"
            downloaded = existing_size

            with open(dest, mode) as f:
                while True:
                    chunk = resp.read(1024 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

                    if total > 0:
                        pct = downloaded / total * 100
                        dl_mb = downloaded / (1024 * 1024)
                        bar = "#" * int(pct / 2) + "-" * (50 - int(pct / 2))
                        print(f"\r  [{bar}] {pct:5.1f}%  {dl_mb:.1f}/{total_mb:.1f} MB", end="", flush=True)

        print()
        return True

    except urllib.error.HTTPError as e:
        if e.code == 416:
            print("  (已存在，跳過)")
            return True
        print(f"\n  [失敗] HTTP {e.code}")
        return False
    except Exception as e:
        print(f"\n  [失敗] {e}")
        return False


def main():
    print("=" * 55)
    print("  HuggingFace 模型下載工具")
    if HTTP_PROXY:
        print(f"  Proxy : {HTTP_PROXY}")
    if HF_TOKEN:
        print(f"  Token : {HF_TOKEN[:8]}...")
    print(f"  儲存至: {SAVE_BASE}")
    print("=" * 55)
    print()

    repo_id = input("請輸入模型全名（例如 nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4）：").strip()
    if not repo_id or "/" not in repo_id:
        print("[錯誤] 格式應為 owner/model-name")
        sys.exit(1)

    print(f"\n正在取得 {repo_id} 的檔案清單...")
    files = fetch_file_list(repo_id)

    if not files:
        print("[錯誤] 找不到任何檔案")
        sys.exit(1)

    print(f"\n找到 {len(files)} 個檔案：")
    print("-" * 40)
    for i, f in enumerate(files, 1):
        print(f"  {i:2}. {f}")
    print("-" * 40)

    confirm = input("\n是否開始下載全部檔案？(Y/n)：").strip().lower()
    if confirm not in ("y", "yes", ""):
        print("已取消。")
        sys.exit(0)

    model_name = repo_id.split("/")[-1]
    save_dir = os.path.join(SAVE_BASE, model_name)
    print(f"\n儲存路徑：{save_dir}")
    os.makedirs(save_dir, exist_ok=True)

    print("\n開始下載...\n")
    base_url = f"https://huggingface.co/{repo_id}/resolve/main"
    success, failed = 0, []

    for i, fname in enumerate(files, 1):
        dest = os.path.join(save_dir, fname)
        print(f"[{i}/{len(files)}] {fname}")
        ok = download_file(f"{base_url}/{fname}", dest)
        if ok:
            success += 1
        else:
            failed.append(fname)

    print("\n" + "=" * 55)
    print(f"  下載完成：{success}/{len(files)} 個檔案")
    total_size = sum(
        os.path.getsize(os.path.join(save_dir, f))
        for f in os.listdir(save_dir)
        if os.path.isfile(os.path.join(save_dir, f))
    )
    print(f"  總大小：{total_size / (1024**3):.2f} GB")
    print(f"  路徑：{save_dir}")
    if failed:
        print(f"\n  失敗的檔案（{len(failed)} 個）：")
        for f in failed:
            print(f"    - {f}")
    print("=" * 55)


if __name__ == "__main__":
    main()
