# Version Compatibility Matrix

*Read this in other languages: [繁體中文](docs/zh-TW/version_compatibility_matrix.md).*

## Recommended Configuration
| Software/Package | Recommended Version | Details |
| :--- | :--- | :--- |
| **3D Slicer** | **5.4.x - 5.6.x** | This is the most stable and heavily supported timeframe for TotalSegmentator, MONAI, and VMTK dependencies. The 5.6.x tier is strongly advised to benefit from mature Python 3.9+ environments. |
| **TotalSegmentator**| Latest via Extension Manager | Always automatically pulls model weights on the fly natively. |
| **SlicerVMTK** | Latest via Extension Manager | Critical for Extract Centerline routines. |
| **Python** | Bundled inside Slicer (3.9+) | Slicer isolates its own environment. Native system Python installs are unnecessary. |

## Compatibility Risk Assessment
1. **Legacy Slicer Versions (< 5.2.x)**:
   - **High Risk**: Older versions may possess erratic Extension Managers. Some pip-installed packages (specifically updated `pandas` and `scikit-image`) often collide with the outdated legacy backend in Slicer 4.x/5.1.
2. **Mac/Linux vs Windows OS Differences**:
   - **Low Risk**: The entire module relies predominantly on standard Slicer Python API, ITK/VTK integrations, and isolated pip bounds. There are very minimal hardcoded logic bounds tied directly to Windows (`\\` pathing vs `/`).
3. **Memory / GPU (VRAM) Bounds**:
   - **High Risk**: Utilizing `TotalSegmentator` triggers intensive graphical loads. Workstations operating without a dedicated GPU, or containing < 8GB VRAM will persistently run into "Out of Memory" (OOM) failures or experience UI thread freezing.
