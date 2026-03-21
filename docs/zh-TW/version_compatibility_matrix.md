# 版本相容性分析 (Version Compatibility Matrix)

## 推薦版本配置
| 軟體/套件 | 建議版本 | 說明 |
| :--- | :--- | :--- |
| **3D Slicer** | **5.4.x - 5.6.x** | 這是目前 TotalSegmentator、MONAI 以及 VMTK 最穩定支援的近代版本範圍。建議使用 5.6.x 以獲得最佳 Python 3.9+ 支援。 |
| **TotalSegmentator**| 最新版 (經由 Extension Manager) | 會隨著內部網路要求下載權重配置。 |
| **SlicerVMTK** | 最新版 (經由 Extension Manager) | 提供 Extract Centerline 所需演算法。 |
| **Python** | 隨附 Slicer (Python 3.9+)| 不需要獨立安裝 Python，使用 Slicer 內部 Python 環境即可。 |

## 相容性風險評估
1. **Slicer 舊版相容性 (< 5.2.x)**:
   - **高風險**: TotalSegmentator / MONAI 對於舊版 Slicer 支援可能不全，或者 pip 安裝套件 (如較新版 pandas/scikit-image) 時容易引發衝突。
2. **Mac/Linux vs Windows**:
   - **低風險**: 此模組絕大部分為依賴於 Slicer API 的 Python 原生腳本與 ITK/VTK 呼叫，無特殊之 OS 限定動態連結庫或硬編碼。
3. **記憶體 (VRAM) 限制**:
   - **高風險**: 若選擇 TotalSegmentator，需要較高的顯示卡 VRAM 或系統 RAM (若無 GPU 加速)，否則極易在自動分割步驟發生 "Out of memory" Crash。建議系統至少 16GB RAM，GPU VRAM 至少 8GB。
