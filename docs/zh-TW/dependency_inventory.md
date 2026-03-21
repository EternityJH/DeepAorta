# DeepAorta 依賴清單 (Dependency Inventory)

## 1. 3D Slicer 內建模組 (Built-in Modules)
DeepAorta 依賴於以下 3D Slicer 核心模組來處理資料與流程：
- **Volumes**: 用於體積資料的管理與轉換 (`CreateLabelVolumeFromVolume`, `CreateScalarVolumeFromVolume`)
- **Segmentations**: 用於處理模型輸出的分割結果 (`ExportVisibleSegmentsToLabelmapNode`, `ImportLabelmapToSegmentationNode`)
- **Markups**: 用於管理中心線的控制點 (`vtkMRMLMarkupsFiducialNode`, `vtkMRMLMarkupsCurveNode`)
- **Plots**: 用於產生與顯示量化結果折線圖 (`vtkMRMLPlotSeriesNode`, `vtkMRMLPlotChartNode`)
- **Tables**: 用於儲存與呈現統計數據 (`vtkMRMLTableNode`)

## 2. 額外擴充套件 (Extensions / External Modules)
使用 DeepAorta 前，必須透過 3D Slicer 的 Extension Manager 安裝以下擴充套件：
- **TotalSegmentator**: (選項一) 用於全自動且精準的主動脈 (Aorta) 分割。
- **MONAIAuto3DSeg**: (選項二) 提供另一個基於 MONAI 的主動脈分割模型選項 (`aorta-v1.1.0`)。
- **SlicerVMTK (Vascular Modeling Toolkit)**: 提供血管中心線萃取功能，呼叫其中的 `ExtractCenterline` 模組。
- **Sandbox (或 CurvedPlanarReformat)**: 提供將彎曲的主動脈影像與標籤展平拉直的功能 (`CurvedPlanarReformat` 模組)。

## 3. Python 套件 (Python Packages)
DeepAorta 的 Python 依賴，於載入時將會自動使用 `pip_install` 進行安裝（如未安裝）：
- **必備自動下載套件**:
  - `scikit-image`: 用於影像的平滑處理與凸包運算 (`convex_hull_image`, `morphology`)
  - `pandas`: 用於處理統計分析資料的 Dataframe 操作
- **Slicer 內建或相依自動處理套件**:
  - `numpy`, `scipy` (特別是 `ndimage` 和 `stats`), `cv2` (OpenCV)

## 4. 硬編碼與假設分析 (Hardcoded Assumptions)
- **節點命名假設**: 在分割之後會預期擷取出名稱中包含 `aorta` 的 segment (大小寫敏感需注意)。
- **路徑建立**: 在使用批量推論 (`BatchInferenceButton`) 模式時，會在原始批次資料夾的**同層路徑**自動建立一個名為 `<原始資料夾名稱>_AortaQuanBatchResult` 的目錄，並在內部以 `.mrb` 格式存檔。
- **Sample Data**: 程式內建了 `DeepAorta1` 與 `DeepAorta2` 的下載路徑，方便首次測試。
