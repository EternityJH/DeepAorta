# DeepAorta 🫀

*Read this in other languages: [English](README.md).*

**DeepAorta** 是一款建構於 3D Slicer 之上的開源擴充模組，專精於主動脈 (Aorta) 的全自動分割、中心線萃取、血管拉直 (Straightening) 以及其沿長軸特徵的自動化幾何量化 (面積與最大直徑計算)。

<img src="Resources/Icons/DeepAorta.png" alt="DeepAorta" width="50">

## 核心特徵 (Key Features)
* **一鍵化流程**: 輸入 CT 影像後自動執行多模型分割 (基於 TotalSegmentator / MONAI)、模型萃取成血管中心線與拉直重構。
* **精準幾何量化**: 計算各橫截面的面積 (Area, $mm^2$) 及直徑 (Diameter, $mm$)。
* **資料與視覺互動**: 產生視覺化交互折線圖以及詳細統計量 (Max, Min, Median, Mean, IQR) 表格。
* **批次推論模式 (Batch Inference)**: 能夠一鍵載入大量 DICOM 資料夾進行背景自動分析，並以 `.mrb` Slicer 專案檔格式統一輸出。

## 文件導覽 (Documentation)
我們準備了非常詳盡的中文文件來幫助您將此擴充模組安裝至臨床或研究環境中：

1. **[安裝指南 (INSTALL.md)](docs/zh-TW/INSTALL.md)**: 了解如何配置 3D Slicer 5.4+ 以及必要的外部 Extensions。
2. **[快速上手 (QUICKSTART.md)](docs/zh-TW/QUICKSTART.md)**: 下載內建 Sample Data，快速驗證模組功能。
3. **[完整操作教學 (WORKFLOW_TUTORIAL.md)](docs/zh-TW/WORKFLOW_TUTORIAL.md)**: 從單例到批次推論的使用完整說明。
4. **[錯誤排除 (TROUBLESHOOTING.md)](docs/zh-TW/TROUBLESHOOTING.md)**: OOM 或缺套件等常見錯誤及解法。
5. **[依賴清單 (Dependency Inventory)](docs/zh-TW/dependency_inventory.md)**: Slicer 內建模組與 Python 套件依賴解析。
6. **[版本相容性 (Version Compatibility)](docs/zh-TW/version_compatibility_matrix.md)**: 推薦的 Slicer 版本與硬體風險評估。

## 支援與回報 (Support & Feedback)
如果您在使用此模組時遇到問題，或是對於代碼有改善建議：
- 請確保您已詳讀 `TROUBLESHOOTING.md`。
- 若問題依然存在，歡迎在 GitHub 儲存庫提出 Issue。

## 授權聲明 (License)
本專案採用 **[MIT License](./LICENSE)** 開源釋出。您可以自由使用於商業或非商業環境，但需保留原始版權聲明。

## 引用本專案 (Citation)
若您在學術研究中使用了 DeepAorta 模組輔助分析，請參考 `CITATION.cff` 中的格式引述此工具，或見下方範例：
```bibtex
@article{Hong_2026,
  author = {Hong, Jia-Sheng and Tzeng, Yun-Hsuan and Wu, Kuan-Ting and Huang, Shih-Yu and Wang, Ting Wei and Li, Guan-Yu and Lin, Chun-Yi and Liu, Ho-Ren and Fu, Hai-Neng and Lee, Yung-Tsai and Yin, Wei-Hsian and Wu, Yu-Te},
  title = {Automated Aortic Quantification Based on Artificial Intelligence: Validation Using Contrast-Enhanced and Non-Contrast CT Scans from the Same Session},
  journal = {Preprints},
  year = {2026},
  doi = {10.20944/preprints202602.1599.v1},
  url = {https://www.preprints.org/manuscript/202602.1599}
}
```
