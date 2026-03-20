# HuggingFace Model Downloader

互動式 HuggingFace 模型下載工具，支援斷點續傳、Proxy、Token 驗證。

---

## 功能

- 輸入模型名稱自動列出所有可下載檔案
- 逐檔下載並顯示進度條
- 斷點續傳（中途中斷重跑不需從頭來）
- 支援 HTTP Proxy
- 支援 HuggingFace Token（需授權的模型）
- 純 Python 標準庫，不需安裝額外套件

---

## 環境需求

- Python 3.10+

---

## 安裝

```bash
git clone https://github.com/Reiyu01/HuggingFace-By-Wget.git
cd Huggingface-By-Wget
```

---

## 設定

複製範例設定檔並填入你的環境：

```bash
cp .env.example .env
nano .env
```

`.env` 內容說明：

| 變數 | 說明 | 必填 |
|---|---|---|
| `HTTP_PROXY` | Proxy 位址，例如 `http://your-proxy:3128` | 否 |
| `HTTPS_PROXY` | Proxy 位址 | 否 |
| `SAVE_BASE` | 模型儲存根目錄，預設為 `./models` | 否 |
| `HF_TOKEN` | HuggingFace Token，需授權的模型才需要 | 否 |

載入環境變數：

```bash
export $(cat .env | xargs)
```

---

## 使用方式

```bash
python3 download_model.py
```

執行後依提示操作：

```
=======================================================
  HuggingFace 模型下載工具
  Proxy : http://your-proxy:3128
  儲存至: /data/model_hf
=======================================================

請輸入模型全名（例如 nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4）：
> nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-NVFP4

正在取得檔案清單...

找到 35 個檔案：
----------------------------------------
   1. config.json
   2. model-00001-of-00017.safetensors
   ...
----------------------------------------

是否開始下載全部檔案？(Y/n)：Y

[1/35] config.json
  [##################################################] 100.0%  0.0/0.0 MB
[2/35] model-00001-of-00017.safetensors
  [###########################-----------------------]  54.2%  2341.1/4318.0 MB
```

---

## 背景執行（推薦）

下載大模型時建議用 `nohup` 背景執行，終端機關掉也不影響：

```bash
nohup python3 download_model.py > download.log 2>&1 &

# 監控進度
tail -f download.log
```

---

## 斷點續傳

中途中斷後直接重跑即可，已下載完成的檔案會自動跳過，未完成的從中斷點繼續：

```bash
python3 download_model.py
# 輸入相同模型名稱，選 Y 繼續
```

---

## 需要 Token 的模型

部分模型需要先到 HuggingFace 同意授權條款並取得 Token：

1. 登入 [huggingface.co](https://huggingface.co)
2. 到模型頁面點擊 **Agree and access repository**
3. 到 [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) 建立 Token
4. 填入 `.env` 的 `HF_TOKEN` 欄位

---

## 專案結構

```
.
├── download_model.py   # 主程式
├── .env.example        # 環境變數範本
├── .gitignore
└── README.md
```

---

## License

MIT
