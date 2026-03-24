# 快速上手 (Quickstart)

若您已經完成 [INSTALL.md](./INSTALL.md) 中的安裝步驟，您可以使用內建的 Sample Data 快速驗證整個 DeepAorta 的分析流程。

## 步驟一：下載範例資料
1. 開啟 3D Slicer。
2. 點擊上方的 `Module Selector` 下拉選單 (預設為 Welcome to Slicer)。
3. 在左方的 `Data` 類別或搜尋框中找到並打開 **Sample Data** 模組。
4. 向下滾動，找到 **DeepAorta** 分類。
5. 單擊一次 **DeepAorta1** 或 **DeepAorta2**。系統將開始在背景下載該測試資料（請耐心等待，由於 3D 醫學影像較大，依賴網路速度）。

> [!TIP]
> 📸 **加入截圖建議**: 請在此處加入一張點擊下載 Sample Data `DeepAorta1` 的模組區塊截圖。
> `![Sample Data Module](DeepAorta/Resources/Screenshots/sample_data.png)`

6. 下載完成後，影像會自動載入到您的 3D Slicer 視窗中。

## 步驟二：執行 DeepAorta 模組
1. 切換至 **DeepAorta** 模組（同樣從 Module Selector 的搜尋框中尋找，或置於 `DeepAorta` 類別內）。
2. 在左側的設定面板中，確認：
   - **Input volume**: 是否已自動選中您剛下載的 `DeepAorta1` 影像。如果沒有，請手動選擇。
   - **Model**: 從下拉選單中選擇 `TotalSegmentator` 或 `MONAI-Aorta`。
3. 點擊面板最下方的 **Apply** (執行) 按鈕。

## 步驟三：觀看結果
此過程約需數分鐘（需經過分割、中心線萃取、截面曲面重構、定量統計等多個步驟）。
執行完成會彈出對話框提示 "Operation completed successfully!"，此時您可以在 Slicer 的介面看見：
1. **渲染畫面**: 主動脈已被拉直展平 (Straightened Volume)，並顯示出紅色外框的標籤。
2. **統計圖表 (Plot)**: 自動彈出繪製完成折線圖，顯示主動脈沿著長軸的截面積 (Area) 與直徑 (Diameter) 變化，並帶有一條標明 "40mm" 的虛線參考線。
3. **數據表格 (Table)**: 出現名為 `Aorta Statistics with Thresholds and AUC` 的統計表，顯示包含最大直徑 (`Diameter_Max`) 等臨床意義數值。

> [!TIP]
> 📸 **加入截圖建議**: 請在此處加入一張 Slicer 滿版介面截圖，包含左側列表、3D展平主動脈、折線圖以及統計表。
> `![Final Result Dashboard](DeepAorta/Resources/Screenshots/final_result.png)`

---
**導覽 (Navigation):**
[⬅️ 上一步: 安裝指南](INSTALL.md) | [🏠 回首頁](../../README_zh-TW.md) | [➡️ 下一步: 完整操作教學](WORKFLOW_TUTORIAL.md)
