# DeepAorta 🫀

*Read this in other languages: [繁體中文](README_zh-TW.md).*

**DeepAorta** is an open-source extension module built on top of 3D Slicer, specializing in fully automated segmentation, centerline extraction, vessel straightening (CPR), and geometric quantification (area and max diameter) of the aorta.

<img src="Resources/Icons/DeepAorta.png" alt="DeepAorta" width="50">

## Key Features
* **One-Click Workflow**: After inputting a CT image, it automatically executes multi-model segmentation (based on TotalSegmentator / MONAI), extracts the vessel centerline, and performs straightened reconstruction.
* **Precise Geometric Quantification**: Calculates the area ($mm^2$) and maximum diameter ($mm$) of each cross-section.
* **Interactive Data Visualization**: Generates interactive line plots and a detailed statistical table (Max, Min, Median, Mean, IQR).
* **Batch Inference Mode**: Capable of loading a large directory of DICOM folders for automated background analysis, outputting unified `.mrb` Slicer project files.

## Directory Structure
```text
DeepAorta/
├── README.md                      # Project Homepage
├── README_zh-TW.md                # 繁體中文版本首頁
├── INSTALL.md                     # 🌱 Installation Guide
├── QUICKSTART.md                  # 🚀 Quickstart using Sample Data
├── WORKFLOW_TUTORIAL.md           # 🧰 Detailed Workflow Tutorial
├── TROUBLESHOOTING.md             # 🚑 Troubleshooting Common Errors
├── dependency_inventory.md        # 📦 Dependency List
├── version_compatibility_matrix.md# ⏳ Version Compatibility
├── CHANGELOG.md                   # 📝 Release Changelog
├── LICENSE                        # Open Source License (MIT)
├── CITATION.cff                   # Academic Citation Format
├── CMakeLists.txt                 # Slicer External Module Build Script
├── docs/zh-TW/                    # Traditional Chinese Documentation
└── DeepAorta/                     # Main Module Source Code
```

## Documentation
We have prepared comprehensive documentation to help you install and use this extension module in clinical or research environments:

1. **[Installation Guide (INSTALL.md)](./INSTALL.md)**: How to configure 3D Slicer 5.4+ and required external extensions.
2. **[Quickstart (QUICKSTART.md)](./QUICKSTART.md)**: Download built-in sample data to quickly verify module functionality.
3. **[Workflow Tutorial (WORKFLOW_TUTORIAL.md)](./WORKFLOW_TUTORIAL.md)**: Detailed instructions covering both single-case and batch inference modes.
4. **[Troubleshooting (TROUBLESHOOTING.md)](./TROUBLESHOOTING.md)**: Solutions for common issues like OOM (Out of Memory) crashes or missing dependencies.

## Support & Feedback
If you encounter issues or have suggestions for code improvements:
- Please ensure you have read `TROUBLESHOOTING.md`.
- If the issue persists, feel free to open an Issue on the GitHub repository.

## License
This project is released under the **[MIT License](./LICENSE)**. You are free to use it in commercial or non-commercial environments, provided the original copyright notice is retained.

## Citation
If you use the DeepAorta module in your academic research, please refer to the format in `CITATION.cff` to cite this tool, or use the example below:
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
