# 錯誤排除與驗收指南 (Troubleshooting)

在安裝與使用 DeepAorta 的過程中，若您遇到非預期的錯誤或當機，請參考以下常見問題進行排除。

## 1. 常見錯誤與排除方式

### 🔴 錯誤 1: `ModuleNotFoundError: No module named 'skimage'` 或 `pandas`
* **現象**: 第一次載入此模組時，Python Console 跳出找不到套件的紅字錯誤。
* **原因**: 模組會在初始化時嘗試背景執行 `pip install scikit-image pandas`。若您的網路環境位於醫院防火牆或需要代理伺服器 (Proxy)，可能會導致下載失敗。
* **解決方案**: 
  1. 開啟 Slicer 內建的 Python Console (按 `Ctrl + 3` 叫出 Python 終端機)。
  2. 手動輸入並執行以下指令繞過 SSL 或加上 Proxy:
     ```python
     slicer.util.pip_install('scikit-image pandas --proxy http://您的代理位址:埠號')
     ```
  3. 安裝成功後重啟 Slicer。

### 🔴 錯誤 2: TotalSegmentator 執行一半崩潰或閃退 (Out of Memory)
* **現象**: 按下 `Apply` 後進度條卡在 0% 或突然整個 Slicer 關閉。
* **原因**: TotalSegmentator 非常依賴顯示卡記憶體 (VRAM)。若您的環境沒有獨立顯示卡，或是 VRAM 小於 8GB，很容易在 PyTorch 載入模型權重時記憶體不足 (OOM)。
* **解決方案**: 
  - 嘗試關閉其他佔用記憶體的應用程式。
  - 在 `Model` 選單中改選 `MONAI-Aorta` 模型，其神經網路參數量通常對系統要求較友善。

### 🔴 錯誤 3: 找不到 ExtractCenterline, CurvedPlanarReformat
* **現象**: 畫面跳出類似 `module 'slicer.modules' has no attribute 'extractcenterline'` 或當機。
* **原因**: 您未完全安裝前置依賴的 Extensions，或者安裝後**沒有重新啟動 Slicer**。
* **解決方案**: 請回到 Extension Manager，確認 **SlicerVMTK** 與 **Sandbox** (或 CurvedPlanarReformat 相關擴充) 已亮起藍色 Installed 的標籤，並確實重啟軟體。

### 🔴 錯誤 4: 批次推論 (Batch Inference) 失敗或部分檔案遺失
* **現象**: `AortaQuanBatchResult` 目錄少了很多病患，或是中途跳出錯誤提示框。
* **原因**: 提供的目錄結構不符合 DICOM Database 讀取邏輯。
* **解決方案**: 
  1. 請檢查您的錯誤記錄檔 (`Save_root/log.txt`) 了解哪些 Case 發生錯誤。
  2. 確保批次目錄下一層就是各個患者的子資料夾，子資料夾內直接是 DICOM `.dcm` 檔，切勿包了過多層級，否則匯入 Database 會找不到 Patient UID。

## 2. 乾淨環境驗收清單 (Validation Checklist)

為了幫助新團隊成員或開發者驗收，請遵循以下檢核表確保整體建置成功：

- [ ] 下載全新安裝的 3D Slicer (推薦 5.6.x 穩定版)。
- [ ] 透過 Extension Manager 安裝: **TotalSegmentator**, **MONAIAuto3DSeg**, **SlicerVMTK**, **Sandbox**。
- [ ] 將 DeepAorta 資料夾加入 Settings -> Modules -> Additional Module Paths。
- [ ] 於 Slicer 中切換至 `Sample Data` 模組，下載 `DeepAorta1`。
- [ ] 切換至 `DeepAorta` 模組，確認 Input volume 預設為 DeepAorta1。
- [ ] 按下 `Apply` 按鈕，進度條跑完無報錯。
- [ ] 驗證場景中包含：**1. 展開的血管 2. Area/Diameter 折線圖 3. 包含閾值判斷的統計 Table**。
- [ ] 驗證完畢。

---
**導覽 (Navigation):**
[⬅️ 上一步: 完整操作教學](WORKFLOW_TUTORIAL.md) | [🏠 回首頁](../../README_zh-TW.md)
