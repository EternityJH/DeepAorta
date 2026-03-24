# Troubleshooting & Validation Guide

If you encounter unexpected errors or crashes while installing or using DeepAorta, please refer to the following guide for common solutions.

*Read this in other languages: [繁體中文](docs/zh-TW/TROUBLESHOOTING.md).*

## 1. Common Errors and Solutions

### 🔴 Error 1: `ModuleNotFoundError: No module named 'skimage'` or `pandas`
* **Symptom**: Red text errors in the Python Console complaining about missing packages upon loading the module.
* **Cause**: To eliminate manual steps, the module initiates `pip install scikit-image pandas` in the background. If you are behind a hospital firewall or require a proxy, this download will fail.
* **Solution**: 
  1. Open Slicer's built-in Python Console (press `Ctrl + 3`).
  2. Manually execute the following command (adding your proxy if needed):
     ```python
     slicer.util.pip_install('pip install scikit-image pandas --proxy http://your-proxy-address:port')
     ```
  3. Restart Slicer once successfully installed.

### 🔴 Error 2: TotalSegmentator Crashes or Quits Mid-Execution (OOM)
* **Symptom**: Slicer abruptly closes or the progress bar gets hopelessly stuck at 0% right after clicking `Apply`.
* **Cause**: TotalSegmentator is heavily reliant on Graphical Memory (VRAM). If your environment lacks a dedicated GPU, or has less than 8GB VRAM, PyTorch often crashes due to Out of Memory (OOM) exceptions.
* **Solution**: 
  - Ensure all other memory-consuming software is closed before running.
  - Switch the `Model` dropdown from TotalSegmentator to `MONAI-Aorta`, which generally has a lighter neural network footprint.

### 🔴 Error 3: Cannot find 'ExtractCenterline' or 'CurvedPlanarReformat'
* **Symptom**: Slicer throws an `AttributeError` like `module 'slicer.modules' has no attribute 'extractcenterline'`.
* **Cause**: You did not install the prerequisite extensions, or you installed them but **forgot to restart 3D Slicer**.
* **Solution**: Navigate back to the Extension Manager. Ensure the **SlicerVMTK** and **Sandbox** extensions display a blue "Installed" tag, then restart the application.

### 🔴 Error 4: Batch Inference Fails or Cases Go Missing
* **Symptom**: The resulting `AortaQuanBatchResult` directory skips many patients or pops up a sudden error dialog.
* **Cause**: The provided directory structure does not meet standard DICOM Database reading logic.
* **Solution**: 
  1. Inspect the generated error log (`Save_root/log.txt`) for specifics on what cases failed.
  2. Ensure the batch directory directly contains patient subfolders, and those subfolders directly contain DICOM `.dcm` files. Extraneous nesting may confuse Slicer's DICOM importer, causing it to lose the Patient UID.

## 2. Clean Environment Validation Checklist

To help onboard new developers or users, use this checklist to verify a successful installation from a clean slate:

- [ ] Download a freshly installed 3D Slicer (v5.6.x recommended).
- [ ] Install via Extension Manager: **TotalSegmentator**, **MONAIAuto3DSeg**, **SlicerVMTK**, **Sandbox**.
- [ ] Add the DeepAorta folder to Settings -> Modules -> Additional Module Paths.
- [ ] In Slicer, navigate to the `Sample Data` module and download `DeepAorta1`.
- [ ] Open the `DeepAorta` module. Ensure Input volume defaults heavily to DeepAorta1.
- [ ] Click `Apply`. Ensure the progress bar finishes without a console error.
- [ ] Verify the scene properly displays: **1. Flattened Straightened Volume, 2. Area/Diameter Line Chart, 3. The statistical table including thresholding numbers.**
- [ ] Validation complete.

---
**Navigation:**
[⬅️ Previous: Workflow Tutorial](WORKFLOW_TUTORIAL.md) | [🏠 Main Page](README.md)
