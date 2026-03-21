# 變更日誌 (Changelog)

所有關於本專案的重大變更，將會記錄於此文件中。
本文件的格式參考 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，且此專案遵循 [語意化版本 (Semantic Versioning)](https://semver.org/spec/v2.0.0.html)。

## [Unreleased]

### Added
- 將 DeepAorta 開源化所需的一系列說明文件建置完成 (`README.md`, `INSTALL.md`, `QUICKSTART.md`, `WORKFLOW_TUTORIAL.md`, `TROUBLESHOOTING.md`)。
- 專案依賴相容性與清單整理 (`version_compatibility_matrix.md`, `dependency_inventory.md`)。
- 添加 `LICENSE` (MIT) 與 `CITATION.cff` 標準引用文件。
- 新增 `DeepAorta1` 與 `DeepAorta2` Slicer Sample Data 快速下載介接。

### Changed
- 註解並關閉了原本 `Aneurysm` 判斷的功能與圖表字眼，將模組聚焦於 Aorta 特徵萃取本身。
