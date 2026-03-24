# 安裝指南 (Installation Guide)

本指南將引導您如何在一個全新的 3D Slicer 環境中部署並執行 DeepAorta 模組。

## 1. 系統要求與下載 Slicer
1. 請至 [3D Slicer 官方網站](https://download.slicer.org/) 下載 **Slicer 5.4 或更新版本**。
2. 由於 DeepAorta 依賴深度學習模型 (如 TotalSegmentator)，推薦您的電腦配備獨立顯示卡 (NVIDIA GPU 至少 8GB VRAM) 以加速運算。若無獨立顯卡，CPU 運算將耗時較長。

## 2. 安裝必需的擴充套件 (Extensions)
DeepAorta 需要幾個 Slicer 擴充套件才能正常運作。
1. 打開 3D Slicer。
2. 點擊功能表列的 `View` -> `Extension Manager` (或直接點擊介面上方的藍色擴充管理員圖示)。
3. 在 `Install Extensions` 分頁中的搜尋框，依序搜尋並安裝以下套件：
   - **TotalSegmentator** 或 **MONAIAuto3DSeg** (用於主動脈初步分割)
   - **SlicerVMTK** (Vascular Modeling Toolkit，提供中心線萃取功能)
   - **Sandbox** (或者直接搜尋 **CurvedPlanarReformat** 確保展平血管功能的套件存在)
   - **PyTorch** (讓深度學習模型能使用 GPU 進行加速運算)

> [!TIP]
> 📸 **加入截圖建議**: 請在此處加入一張 Extension Manager 已安裝這些擴充套件的截圖。
> `![Extension Manager](DeepAorta/Resources/Screenshots/extension_manager.png)`

4. 下載完成後，請**重新啟動 (Restart)** 3D Slicer。
5. **(重要) 測試 GPU 加速**: 重啟 Slicer 後，打開 **PyTorch Util** 模組（可透過 <kbd>Ctrl</kbd>+<kbd>F</kbd> 搜尋）。檢查 CUDA 是否可用；如果顯示為 CPU，請點擊安裝帶有 CUDA 支援的 PyTorch 並再次重啟。測試確認 OK 後，模組才能發揮最快的推論速度。

## 3. 載入 DeepAorta 模組
作為一個第三方模組，我們需要將 `DeepAorta` 所在資料夾加入 Slicer 的模組路徑中：
1. 將本專案存放於您固定的本機磁碟路徑中（例如解壓縮至文件夾）。
2. 打開 3D Slicer，點擊左上角的 `Edit` -> `Application Settings`。
3. 在左側清單選擇 `Modules` 標籤。
4. 找到 `Additional module paths` 區塊，點擊右側的 `>>` 添加按鈕 (Add)。
5. 瀏覽並選擇本專案內的 `DeepAorta` 資料夾（裡面必須包含 `DeepAorta.py`）。

> [!TIP]
> 📸 **加入截圖建議**: 請在此處加入一張 Application Settings 中添加模組路徑的畫面截圖。
> `![Module Path Settings](DeepAorta/Resources/Screenshots/module_path.png)`

6. 點選 OK，將會提示您需要重新啟動以套用新模組。
7. 重新啟動 3D Slicer。

## 4. 驗證模組正確載入
重啟後：
1. 點擊主畫面的模組選擇下拉選單 (Module Selector, 通常預設為 Welcome to Slicer)。
2. 在 `All Modules` 下，或是在 `DeepAorta` 分類下，您應該會看到名為 **DeepAorta** 的圖示。
3. 點擊進入。如果你看到：
   - 有個 `Input volume` 的選單
   - 看到 `Model` 的下拉選單 (TotalSegmentator 或 MONAI-Aorta)
   - 看到畫面下方有 `Batch Inference` 與 `Apply` 按鈕
**這代表您已經成功安裝並掛載了 DeepAorta 模組！**
