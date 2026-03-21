# Quickstart

If you have completed the setup steps in [INSTALL.md](./INSTALL.md), you can use the built-in Sample Data to quickly verify the entire DeepAorta analysis pipeline.

*Read this in other languages: [繁體中文](docs/zh-TW/QUICKSTART.md).*

## Step 1: Downloading Sample Data
1. Open 3D Slicer.
2. Click the `Module Selector` dropdown at the top (defaults to Welcome to Slicer).
3. Find and open the **Sample Data** module under the `Data` category or via the search bar.
4. Scroll down to find the **DeepAorta** category.
5. Click either **DeepAorta1** or **DeepAorta2** once. The system will start downloading the test data in the background (please be patient, as 3D medical images can be large depending on internet speed).

> [!TIP]
> 📸 **Screenshot**: Please insert an image showing the Sample Data module with DeepAorta1 clicked.
> `![Sample Data Module](DeepAorta/Resources/Screenshots/sample_data.png)`

6. Once downloaded, the volume will automatically load into your 3D Slicer views.

## Step 2: Running the DeepAorta Module
1. Switch to the **DeepAorta** module (using the Module Selector search bar, or finding it under the `AItewan` category).
2. In the left configuration panel, verify:
   - **Input volume**: Ensure your downloaded image (e.g., `DeepAorta1`) is automatically selected. If not, manually select it.
   - **Model**: Select `TotalSegmentator` or `MONAI-Aorta` from the dropdown.
3. Click the **Apply** button at the bottom of the panel.

## Step 3: Viewing Results
This process will take a few minutes (involving segmentation, centerline extraction, curved planar reformatting, and quantitative statistics).
When finished, a dialog box will pop up saying "Operation completed successfully!". In the Slicer interface, you will see:
1. **Render Views**: The aorta has been straightened and flattened (`StraightenedVolume`), displayed with red outline labels.
2. **Statistical Plot**: A line chart is automatically drawn showing the cross-sectional area and diameter variations along the aorta's long axis, complete with a "40mm" dotted reference line.
3. **Data Table**: A table named `Aorta Statistics with Thresholds and AUC` is generated, housing clinically significant metrics such as maximum diameter (`Diameter_Max`).

> [!TIP]
> 📸 **Screenshot**: Please insert an image showing the final result dashboard (Straightened Volume, the chart, and the table).
> `![Final Result Dashboard](DeepAorta/Resources/Screenshots/final_result.png)`
