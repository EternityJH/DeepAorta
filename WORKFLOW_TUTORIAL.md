# Workflow Tutorial

The DeepAorta module automates the segmentation and quantification of the aorta from abdominal or thoracic CT images. It supports both **Single Inference Mode** and **Batch Inference Mode**.

*Read this in other languages: [繁體中文](docs/zh-TW/WORKFLOW_TUTORIAL.md).*

## 1. Interface Overview
* **Input volume**: Select the 3D CT image currently loaded in 3D Slicer that you wish to analyze (e.g., `.nii.gz`, `.nrrd`, or an imported DICOM Volume).
* **Model**: Offers two primary backbones for initial aorta segmentation:
  1. `TotalSegmentator`: Highly accurate but requires slightly more VRAM.
  2. `MONAI-Aorta`: Based on MONAIAuto3DSeg, lightweight and specialized around the `aorta-v1.1.0` model.

## 2. Single Inference Mode
Ideal for analyzing individual patients or thoroughly inspecting intermediate steps:
1. Import the image into 3D Slicer (e.g., drag and drop a `.nii.gz` file and select `Volume`).
2. Open the **DeepAorta** module.
3. Set the `Input volume` to your scanned image.

> [!TIP]
> 📸 **Screenshot**: Please insert an image of the DeepAorta module UI showcasing the filled parameters right before hitting Apply.
> `![DeepAorta UI](DeepAorta/Resources/Screenshots/module_ui.png)`

4. Click **Apply**.
5. The module will sequentially execute the following pipeline:
   - **Model Inference**: Calls TotalSegmentator or MONAI to extract the `AortaSegmentation`.
   - **Centerline Extraction**: Uses VMTK to find the endpoints of the aorta and generates a centerline curve.
   - **Vessel Straightening**: Performs Curved Planar Reformat (`CurvedPlanarReformat`) along the centerline, producing an independent `StraightenedVolume` node.
   - **Geometric Smoothing & Calculation**: Extracts the convex hull and computes the cross-sectional area and maximum diameter slice by slice.
   - **Result Generation**: Outputs a visual chart (`ChartView`) and a detailed statistical table (`TableViewNode`).

## 3. Batch Inference Mode
For processing large cohorts (e.g., dozens of categorized DICOM folders):
1. Prepare a root directory exclusively for the batch run (e.g., `C:\MyDataset\AAA_Cases\`).
2. The directory immediately inside MUST contain individual patient folders, where each patient folder contains their raw `.dcm` files:
   ```text
   AAA_Cases/
    ├─ Patient_001/
    │   ├─ 001.dcm, 002.dcm ...
    ├─ Patient_002/
    │   └─ ...
   ```
3. Open Slicer and navigate to the DeepAorta module.
4. Find the **Batch Inference Directory** field, click the folder icon, and select your `AAA_Cases` directory.
5. Click the **Batch Inference** button.
6. The module creates a temporary virtual DICOM Database, iterates through each patient, loads the volume, analyzes it, saves the results, and **clears the scene** before moving to the next case.
7. **Output**: Once fully completed, you will find an auto-generated directory named `AAA_Cases_AortaQuanBatchResult` inside `C:\MyDataset\`. You can drag any generated `.mrb` file from this folder back into Slicer to review the full quantified analysis for that patient.

> [!TIP]
> 📸 **Screenshot**: Please insert an image of Windows Explorer or MacOS Finder showing the output `.mrb` batch results.
> `![Batch Output Folder](DeepAorta/Resources/Screenshots/batch_output.png)`

## 4. Stability Tips & Validation
* While in Batch Inference Mode, avoid moving your mouse extensively or clicking within the Slicer window. UI interactions can freeze the event loop or crash the execution thread.
* Failed cases will be logged in `Save_root/log.txt`. Open this file to trace back which specific case encountered an error.
* If your output yields an `EmptyLabelMap` or the straightened image is completely missing, ensure your chosen model (TotalSegmentator) wasn't forcefully killed by the OS due to insufficient resources (common on machines with <16GB RAM).
