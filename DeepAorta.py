import logging
import os
from typing import Annotated, Optional

import vtk

import qt
import traceback

import slicer
from slicer.i18n import tr as _
from slicer.i18n import translate
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from slicer.parameterNodeWrapper import (
    parameterNodeWrapper,
    WithinRange,
)

from slicer import vtkMRMLScalarVolumeNode, \
                    vtkMRMLSegmentationNode, \
                    vtkMRMLMarkupsFiducialNode, \
                    vtkMRMLMarkupsCurveNode, \
                    vtkMRMLTransformNode

import numpy as np
import scipy.ndimage as ndimage
import vtk.util.numpy_support as nps
from skimage import measure, morphology, draw
from scipy.ndimage import gaussian_filter
import cv2

##### Install required modules #####
# basic module
pip_modules = ['skimage','pandas']
install_modules = ['scikit-image','pandas']
for i in range(len(pip_modules)):    
    try:
        module_obj = __import__(pip_modules[i])
    except:
        slicer.util.pip_install('pip install ' + install_modules[i])

#
# DeepAorta
#

class DeepAorta(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = _("DeepAorta")  # TODO: make this more human readable by adding spaces
        # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.categories = [translate("qSlicerAbstractCoreModule", "DeepAorta")]
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["DeepAorta Contributors"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        # _() function marks text as translatable to other languages
        self.parent.helpText = _("""
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#DeepAorta">module documentation</a>.
""")
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = _("""
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""")

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#

def registerSampleData():
    """
    Add data sets to Sample Data module.
    """
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData
    iconsPath = os.path.join(os.path.dirname(__file__), "Resources/Icons")

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # DeepAorta1
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category="DeepAorta",
        sampleName="DeepAorta1",
        # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
        # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
        thumbnailFileName=os.path.join(iconsPath, "DeepAorta1.png"),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        fileNames="DeepAorta1.nrrd",
        # Checksum to ensure file integrity. Can be computed by this command:
        #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
        checksums="SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        # This node name will be used when the data set is loaded
        nodeNames="DeepAorta1"
    )

    # DeepAorta2
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category="DeepAorta",
        sampleName="DeepAorta2",
        thumbnailFileName=os.path.join(iconsPath, "DeepAorta2.png"),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        fileNames="DeepAorta2.nrrd",
        checksums="SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        # This node name will be used when the data set is loaded
        nodeNames="DeepAorta2"
    )


#
# DeepAortaParameterNode
#

@parameterNodeWrapper
class DeepAortaParameterNode:
    """
    The parameters needed by module.

    inputVolume - The volume to threshold.
    imageThreshold - The value at which to threshold the input volume.
    invertThreshold - If true, will invert the threshold.
    thresholdedVolume - The output volume that will contain the thresholded volume.
    invertedVolume - The output volume that will contain the inverted thresholded volume.
    """
    inputVolume: vtkMRMLScalarVolumeNode
    imageThreshold: Annotated[float, WithinRange(-100, 500)] = 100
    invertThreshold: bool = False
    thresholdedVolume: vtkMRMLScalarVolumeNode
    invertedVolume: vtkMRMLScalarVolumeNode


#
# DeepAortaWidget
#

class DeepAortaWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None) -> None:
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._parameterNodeGuiTag = None

    def setup(self) -> None:
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath("UI/DeepAorta.ui"))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = DeepAortaLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # Buttons
        self.ui.applyButton.connect("clicked(bool)", self.onApplyButton)
        self.ui.BatchInferenceButton.connect("clicked(bool)", self.onBatchInferenceButton)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()
        
    def initialize_progressDialog(self):
        # Initialize the progress dialog if it doesn't already exist
        if not hasattr(self, 'progressDialog'):
            self.progressDialog = qt.QProgressDialog()
            self.progressDialog.setWindowTitle("Processing")
            self.progressDialog.setLabelText("Processing...")
            self.progressDialog.setCancelButtonText("Cancel")
            self.progressDialog.setMinimum(0)
            self.progressDialog.setMaximum(100)
            self.progressDialog.setWindowModality(qt.Qt.WindowModal)
            self.progressDialog.canceled.connect(self.onCancel)       
        

    def cleanup(self) -> None:
        """
        Called when the application closes and the module widget is destroyed.
        """
        self.removeObservers()

    def enter(self) -> None:
        """
        Called each time the user opens this module.
        """
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self) -> None:
        """
        Called each time the user opens a different module.
        """
        # Do not react to parameter node changes (GUI will be updated when the user enters into the module)
        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self._parameterNodeGuiTag = None
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)

    def onSceneStartClose(self, caller, event) -> None:
        """
        Called just before the scene is closed.
        """
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event) -> None:
        """
        Called just after the scene is closed.
        """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self) -> None:
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        if not self._parameterNode.inputVolume:
            firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
            if firstVolumeNode:
                self._parameterNode.inputVolume = firstVolumeNode

    def setParameterNode(self, inputParameterNode: Optional[DeepAortaParameterNode]) -> None:
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
        self._parameterNode = inputParameterNode
        if self._parameterNode:
            # Note: in the .ui file, a Qt dynamic property called "SlicerParameterName" is set on each
            # ui element that needs connection.
            self._parameterNodeGuiTag = self._parameterNode.connectGui(self.ui)
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
            self._checkCanApply()

    def _checkCanApply(self, caller=None, event=None) -> None:
        if self._parameterNode and self._parameterNode.inputVolume and self._parameterNode.thresholdedVolume:
            self.ui.applyButton.toolTip = _("Compute output volume")
            self.ui.applyButton.enabled = True
        else:
            self.ui.applyButton.toolTip = _("Select input and output volume nodes")
            self.ui.applyButton.enabled = True # tmp
    
    def onApplyButton(self, show_message=True, case_index=None, total_cases=None, batch_mode=False) -> None:
        """
        Run processing when user clicks "Apply" button.
        """
        if not batch_mode:
            show_message = True
        
        if not batch_mode:
            self.ui.applyButton.setEnabled(False)
            self.ui.BatchInferenceButton.setEnabled(False)  # Disable Batch button as well during processing

            # Initialize the progress dialog if it's not already created
            self.initialize_progressDialog()

            # Set the initial progress based on the case index and total cases
            if case_index is not None and total_cases is not None:
                self.progressDialog.setValue(int((case_index / total_cases) * 100))
            else:
                self.progressDialog.setValue(0)

            self.progressDialog.show()
            slicer.app.processEvents()

        try:
            with slicer.util.tryWithErrorDisplay(_("Failed to compute results."), waitCursor=True):
                # create output nodes if they don't exist yet
                if not self.ui.outputSegmentationSelector.currentNode():
                    segNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
                    segNode.SetName("AortaSegmentation")
                    self.ui.outputSegmentationSelector.setCurrentNode(segNode)

                if not self.ui.outputCenterlineEndpointsSelector.currentNode():
                    pointsNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")
                    pointsNode.SetName("CenterlineEndpoints")
                    self.ui.outputCenterlineEndpointsSelector.setCurrentNode(pointsNode)

                if not self.ui.outputCenterlineCurveSelector.currentNode():
                    curveNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsCurveNode")
                    curveNode.SetName("CenterlineCurve")
                    self.ui.outputCenterlineCurveSelector.setCurrentNode(curveNode)

                if not self.ui.outputStraightenedTransformSelector.currentNode():
                    transformNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")
                    transformNode.SetName("StraightenedTransform")
                    self.ui.outputStraightenedTransformSelector.setCurrentNode(transformNode)

                if not self.ui.outputStraightenedVolumeSelector.currentNode():
                    volNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
                    volNode.SetName("StraightenedVolume")
                    self.ui.outputStraightenedVolumeSelector.setCurrentNode(volNode)

                if not self.ui.outputStraightenedLabelVolumeSelector.currentNode():
                    vollabNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
                    vollabNode.SetName("StraightenedLabelVolume")
                    self.ui.outputStraightenedLabelVolumeSelector.setCurrentNode(vollabNode)

                if not self.ui.outputStraightenedSegmentationSelector.currentNode():
                    StraightenedsegNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
                    StraightenedsegNode.SetName("StraightenedAortaSegmentation")
                    self.ui.outputStraightenedSegmentationSelector.setCurrentNode(StraightenedsegNode)

                # Compute output
                self.logic.process(
                    self.ui.inputSelector.currentNode(),
                    self.ui.outputSegmentationSelector.currentNode(),
                    self.ui.outputCenterlineEndpointsSelector.currentNode(),
                    self.ui.outputCenterlineCurveSelector.currentNode(),
                    self.ui.outputStraightenedVolumeSelector.currentNode(),
                    self.ui.outputStraightenedTransformSelector.currentNode(),
                    self.ui.outputStraightenedLabelVolumeSelector.currentNode(),
                    self.ui.outputStraightenedSegmentationSelector.currentNode(),
                    self.ui.ModelComboBox.currentText,
                    self.progressDialog,  # Pass the progress dialog to the process method
                    case_index,
                    total_cases,
                    batch_mode
                )
                if self.logic.cancelled:
                    qt.QMessageBox.warning(slicer.util.mainWindow(), "Cancelled", "Operation was cancelled.")                

        except Exception as e:
            qt.QMessageBox.critical(slicer.util.mainWindow(), "Failure", f"Operation failed: {e}")
            traceback.print_exc()
        finally:
            if not batch_mode:
                if show_message:
                    qt.QMessageBox.information(slicer.util.mainWindow(), "Success", "Operation completed successfully!")
                self.progressDialog.hide()
                self.ui.applyButton.setEnabled(True)
                self.ui.BatchInferenceButton.setEnabled(True)  # Re-enable Batch button

    
    def onBatchInferenceButton(self):
        self.ui.BatchInferenceButton.setEnabled(False)
        self.ui.applyButton.setEnabled(False)  # Disable Apply button as well during processing

        self.initialize_progressDialog()

        self.progressDialog.setValue(0)
        self.progressDialog.show()
        slicer.app.processEvents()

        try:
            from DICOMLib import DICOMUtils
            print('Start batch process...')
            BatchRootPath = self.ui.BatchInferenceDirectoryButton.directory
            CaseList = os.listdir(BatchRootPath)
            BatchRootPath_0 = os.path.split(BatchRootPath)[0]
            BatchRootPath_1 = os.path.split(BatchRootPath)[1]
            Save_root = os.path.join(BatchRootPath_0, BatchRootPath_1 + '_AortaQuanBatchResult')
            if not os.path.exists(Save_root):
                os.makedirs(Save_root)
            error_ = []
            total_cases = len(CaseList)
            for i, case in enumerate(CaseList):
                print('Processing case: ' + case)
                self.progressDialog.setValue(int((i / total_cases) * 100))
                self.progressDialog.setLabelText(f"Processing case {i + 1}/{total_cases}: {case}")
                slicer.app.processEvents()
                slicer.mrmlScene.Clear(0)
                try:
                    dicomDataDir = os.path.join(BatchRootPath, case)
                    loadedNodeIDs = []
                    with DICOMUtils.TemporaryDICOMDatabase() as db:
                        DICOMUtils.importDicom(dicomDataDir, db)
                        patientUIDs = db.patients()
                        for patientUID in patientUIDs:
                            loadedNodeIDs.extend(DICOMUtils.loadPatientByUID(patientUID))
                    InputVolumeNode = slicer.mrmlScene.GetNodeByID(loadedNodeIDs[0])
                    self.onApplyButton(show_message=False, case_index=i, total_cases=total_cases, batch_mode=True)  # Use the apply button logic for individual case processing
                    save_MRB = os.path.join(Save_root, 'MRB', f'{case}.mrb')
                    slicer.util.saveScene(save_MRB)
                except Exception as e:
                    error_message = str(e)
                    print(error_message)
                    error_.append(f"{case}: {error_message}")
                print('Processing: ', i + 1, '/', total_cases)

            slicer.mrmlScene.Clear(0)
            from datetime import datetime
            now = datetime.now()
            with open(os.path.join(Save_root, 'log.txt'), 'a') as f:
                f.write(f'Batch inference finished. > {now}\n\n')
                f.write(f'There were {total_cases} cases in total.\n\n')
                f.write('The error cases were:\n')
                for error in error_:
                    f.write(f'{BatchRootPath}/{error}\n\n')

            if self.logic.cancelled:
                qt.QMessageBox.warning(slicer.util.mainWindow(), "Cancelled", "Operation was cancelled.")
            else:
                qt.QMessageBox.information(slicer.util.mainWindow(), "Success", "Operation completed successfully!")

        except Exception as e:
            qt.QMessageBox.critical(slicer.util.mainWindow(), "Failure", f"Operation failed: {e}")
        finally:
            self.progressDialog.hide()
            self.ui.BatchInferenceButton.setEnabled(True)
            self.ui.applyButton.setEnabled(True)  # Re-enable Apply button

            
    def onCancel(self):
        self.logic.cancelled = True

        
def check_cancelled(func):
    def wrapper(self, *args, **kwargs):
        if self.cancelled:
            raise Exception("Process was cancelled")
        return func(self, *args, **kwargs)
    return wrapper              
        

#
# DeepAortaLogic
#

class DeepAortaLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self) -> None:
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)
        self.cancelled = False

    def getParameterNode(self):
        return DeepAortaParameterNode(super().getParameterNode())
    
    @check_cancelled
    def OnlyAorta(self):
    
        # The name of the segment to keep
        segment_to_keep = "aorta"

        # Get all segmentation nodes in the scene
        segmentation_nodes = slicer.util.getNodesByClass("vtkMRMLSegmentationNode")

        if len(segmentation_nodes) > 0:
            # Iterate through all segmentation nodes to find the segment to keep
            for node in segmentation_nodes:
                segmentation = node.GetSegmentation()
                segment_ids = vtk.vtkStringArray()
                segmentation.GetSegmentIDs(segment_ids)
                
                for i in range(segment_ids.GetNumberOfValues()):
                    segment_id = segment_ids.GetValue(i)
                    if segment_id != segment_to_keep:
                        segmentation.RemoveSegment(segment_id)
    
    @check_cancelled
    def keepFirstAndFarthestPoint(self,markupsFiducialNode):
        if not markupsFiducialNode or markupsFiducialNode.GetNumberOfControlPoints() < 2:
            raise ValueError("The Markups Fiducial Node must have at least two points")

        maxDistance = 0
        farthestPointIndex = -1
        numPoints = markupsFiducialNode.GetNumberOfControlPoints()

        # Get the position of the first point
        firstPoint = [0, 0, 0]
        markupsFiducialNode.GetNthControlPointPosition(0, firstPoint)

        # Find the point farthest from the first point
        for i in range(1, numPoints):
            point = [0, 0, 0]
            markupsFiducialNode.GetNthControlPointPosition(i, point)
            distance = vtk.vtkMath.Distance2BetweenPoints(firstPoint, point)
            if distance > maxDistance:
                maxDistance = distance
                farthestPointIndex = i

        # Remove all points except the first and the farthest
        for i in range(numPoints - 1, -1, -1):  # Iterate backwards to avoid index shifting
            if i != 0 and i != farthestPointIndex:
                markupsFiducialNode.RemoveNthControlPoint(i)

    @check_cancelled
    def max_diameter(self, slice_):
        labeled, num_features = ndimage.label(slice_)
        max_diameter = 0
        
        for i in range(1, num_features + 1):
            # Extract the ith connected component
            component = (labeled == i)
            
            # Find the coordinates of the non-zero pixels of the component
            coords = np.column_stack(np.where(component))
            
            # Compute the pairwise Euclidean distances between all coordinates
            dists = np.linalg.norm(coords[:, np.newaxis, :] - coords[np.newaxis, :, :], axis=2)
            
            # Get the maximum distance, which corresponds to the maximum diameter of this component
            component_diameter = np.max(dists)
            
            # Update the maximum diameter if necessary
            if component_diameter > max_diameter:
                max_diameter = component_diameter
                
        return max_diameter            

    @check_cancelled
    def aorta_quan(self, volumeNode):

        image_data = volumeNode.GetImageData()
        volume_array = nps.vtk_to_numpy(image_data.GetPointData().GetScalars()).reshape(image_data.GetDimensions(), order='F')
        volume_array = np.transpose(volume_array, (2, 1, 0))  

        areas = [np.sum(slice_) for slice_ in volume_array]
        diameters = [self.max_diameter(slice_) for slice_ in volume_array]
                
        return areas, diameters

    @check_cancelled
    def createLabelMapVolumeNode(self, segNode):
        # Get the segmentation logic
        segLogic = slicer.modules.segmentations.logic()
        # Prepare an empty label map for export
        emptyLabelMap = slicer.vtkMRMLLabelMapVolumeNode()
        emptyLabelMap.SetName(segNode.GetName() + "_LabelMap")
        slicer.mrmlScene.AddNode(emptyLabelMap)
        # Export the segmentation to a label map
        segLogic.ExportVisibleSegmentsToLabelmapNode(segNode, emptyLabelMap)
        # Update the scene
        slicer.app.processEvents()

        return emptyLabelMap
    
    @check_cancelled
    def StraightenedLabelVolume2Segmentation(self, scalarVolumeNode, segmentationNode):        

        # Create a label map volume from the scalar volume
        labelMapVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
        slicer.modules.volumes.logic().CreateLabelVolumeFromVolume(slicer.mrmlScene, labelMapVolumeNode, scalarVolumeNode)

        # Import the label map into the segmentation
        slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(labelMapVolumeNode, segmentationNode)

        # Optionally, delete the label map volume node if no longer needed
        slicer.mrmlScene.RemoveNode(labelMapVolumeNode)

        # Get the segmentation
        segmentation = segmentationNode.GetSegmentation()

        # Assuming there is only one segment, get its ID
        segmentIDs = segmentation.GetSegmentIDs()
        if len(segmentIDs) > 0:
            firstSegmentId = segmentIDs[0]

            # Rename the segment
            segment = segmentation.GetSegment(firstSegmentId)
            segment.SetName("Aorta")

            # Get the display node associated with the segmentation node
            displayNode = segmentationNode.GetDisplayNode()

            # Set the segmentation display properties
            if displayNode is not None:
                # Set the slice intersection thickness
                displayNode.SetSliceIntersectionThickness(3)

                # Set display properties for the segment
                # Set color to red (R, G, B values range from 0 to 1)
                segment.SetColor(1, 0, 0)  # Red

                # Hide the fill for the segment
                displayNode.SetSegmentVisibility2DFill(firstSegmentId, False)

                # Show the outline for the segment
                displayNode.SetSegmentVisibility2DOutline(firstSegmentId, True)

                # show the segment in 3D
                displayNode.SetVisibility3D(True)

    @check_cancelled
    def createAreaDiameterPlot(self, areas, diameters):
        # Ensure the lengths of areas and diameters are the same
        if len(areas) != len(diameters):
            raise ValueError("Length of areas and diameters must be the same.")

        # Create a table node to store the data
        tableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode")
        table = tableNode.GetTable()

        # Create and populate arrays
        arrX = vtk.vtkFloatArray()
        arrX.SetName("X")
        arrAreas = vtk.vtkFloatArray()
        arrAreas.SetName("Area(mm²)")
        arrDiameters = vtk.vtkFloatArray()
        arrDiameters.SetName("Diameter(mm)")
        arrRefLine = vtk.vtkFloatArray() # Array for the reference line
        arrRefLine.SetName("40mm Line")

        for i in range(len(areas)):
            arrX.InsertNextValue(i)
            arrAreas.InsertNextValue(areas[i])
            arrDiameters.InsertNextValue(diameters[i])
            arrRefLine.InsertNextValue(40)  # Insert value at 40mm

        # Add arrays to the table
        table.AddColumn(arrX)
        table.AddColumn(arrAreas)
        table.AddColumn(arrDiameters)
        table.AddColumn(arrRefLine)  # Add the reference line column
        tableNode.SetAndObserveTable(table)
        tableNode.SetName("Aorta Area and Diameter")

        # Create plot series nodes
        plotSeriesNode1 = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode", "Area Series")
        plotSeriesNode1.SetAndObserveTableNodeID(tableNode.GetID())
        plotSeriesNode1.SetXColumnName("X")
        plotSeriesNode1.SetYColumnName("Area(mm²)")
        plotSeriesNode1.SetPlotType(slicer.vtkMRMLPlotSeriesNode.PlotTypeLine)

        plotSeriesNode2 = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode", "Diameter Series")
        plotSeriesNode2.SetAndObserveTableNodeID(tableNode.GetID())
        plotSeriesNode2.SetXColumnName("X")
        plotSeriesNode2.SetYColumnName("Diameter(mm)")
        plotSeriesNode2.SetPlotType(slicer.vtkMRMLPlotSeriesNode.PlotTypeLine)

        # Create a plot series node for the reference line
        plotSeriesNodeRef = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode", "40mm Reference Line")
        plotSeriesNodeRef.SetAndObserveTableNodeID(tableNode.GetID())
        plotSeriesNodeRef.SetXColumnName("X")
        plotSeriesNodeRef.SetYColumnName("40mm Line")
        plotSeriesNodeRef.SetPlotType(slicer.vtkMRMLPlotSeriesNode.PlotTypeLine)
        plotSeriesNodeRef.SetLineStyle(slicer.vtkMRMLPlotSeriesNode.LineStyleDash)

        # Create a plot chart node
        plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode", "Area and Diameter Chart")
        plotChartNode.AddAndObservePlotSeriesNodeID(plotSeriesNode1.GetID())
        plotChartNode.AddAndObservePlotSeriesNodeID(plotSeriesNode2.GetID())
        plotChartNode.AddAndObservePlotSeriesNodeID(plotSeriesNodeRef.GetID())  # Add the reference line

        # Create a plot view node
        plotViewNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotViewNode", "Plot View")
        plotViewNode.SetPlotChartNodeID(plotChartNode.GetID())
        # Update the scene
        slicer.app.processEvents()  

        # PlotViewNodes
        plotViewNodes = slicer.util.getNodesByClass('vtkMRMLPlotViewNode')

        # set visibility
        for plotViewNode in plotViewNodes:
            plotViewNode.SetVisibility(True)
            plotViewNode.SetPlotChartNodeID(plotChartNode.GetID())

        return plotChartNode, plotViewNode, tableNode
    
    @check_cancelled
    def LabelMapNode_to_ScalarVolumeNode(self,LabelMapVolumeNode):
        # label map to scalar volume
        scalarVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        slicer.modules.volumes.logic().CreateScalarVolumeFromVolume(slicer.mrmlScene, scalarVolumeNode, LabelMapVolumeNode)
        # rename the scalar volume
        scalarVolumeNode.SetName(LabelMapVolumeNode.GetName())
        # set value to 100 for thresholding
        scalarVolumeData = slicer.util.arrayFromVolume(scalarVolumeNode)
        scalarVolumeData = scalarVolumeData*100
        slicer.util.updateVolumeFromArray(scalarVolumeNode, scalarVolumeData)

        return scalarVolumeNode
    
    def copy_scalar_volume_node(self,volume_node_to_copy):
        """
        Copy a ScalarVolumeNode and add it to the scene as a new node.

        Parameters:
        volume_node_to_copy (vtkMRMLScalarVolumeNode): The original volume node to copy.

        Returns:
        vtkMRMLScalarVolumeNode: The new copied volume node.
        """
        # Create a new ScalarVolumeNode
        new_node = slicer.vtkMRMLScalarVolumeNode()
        new_node.SetName(volume_node_to_copy.GetName() + '_Copy')

        # Copy the image data
        new_node.SetAndObserveImageData(vtk.vtkImageData())
        new_node.GetImageData().DeepCopy(volume_node_to_copy.GetImageData())

        # Copy other properties from the original node
        new_node.Copy(volume_node_to_copy)
        new_node.SetAndObserveTransformNodeID(volume_node_to_copy.GetTransformNodeID())

        # Add the new node to the scene
        slicer.mrmlScene.AddNode(new_node)

        # Set display properties
        display_node = slicer.vtkMRMLScalarVolumeDisplayNode()
        slicer.mrmlScene.AddNode(display_node)
        new_node.SetAndObserveDisplayNodeID(display_node.GetID())
        display_node.SetAndObserveColorNodeID(volume_node_to_copy.GetDisplayNode().GetColorNodeID())

        print(f"New volume node created: {new_node.GetName()}")

        return new_node
    
    def process_binary_mask(self, input_array):
        # 確保輸入是二值的0和1
        binary_image = (input_array * 255).astype(np.uint8)
        
        # 使用 Gaussian Kernel 強化實心部分
        blurred = cv2.GaussianBlur(binary_image, (11, 11), 0)
        
        # 再次進行二值化處理
        _, enhanced_binary_image = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)
        
        # 進行形態學操作，使用閉運算（膨脹後再侵蝕）
        kernel = np.ones((5, 5), np.uint8)
        closing = cv2.morphologyEx(enhanced_binary_image, cv2.MORPH_CLOSE, kernel)
        
        # 進行連通分量標記
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(closing, connectivity=8)
        
        # 確保 stats 有預期的結構（至少有一個連通分量）
        if stats.shape[0] > 1:
            # 找到最大的連通分量（排除背景）
            largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
            
            # 創建一個空白掩膜並填充最大的連通分量
            largest_component = np.zeros_like(binary_image)
            largest_component[labels == largest_label] = 255
            
            # 將結果轉換回0和1
            result_array = (largest_component / 255).astype(np.uint8)
        else:
            # 如果沒有找到任何連通分量，返回一個空白掩膜
            result_array = np.zeros_like(binary_image)
        
        return result_array    
    
    def dilate_binary_mask(self, binary_mask, expansion_pixels=2):
        """
        對二值數組的binary mask進行圓形膨脹
        :param binary_mask: numpy array, 二值數組
        :param expansion_pixels: int, 膨脹的像素數
        :return: numpy array, 膨脹後的binary mask
        """
        # 確保輸入是二值的0和1
        binary_image = (binary_mask * 255).astype(np.uint8)
        
        # 創建圓形內核，半徑為擴展像素數
        radius = expansion_pixels
        kernel_size = 2 * radius + 1
        circular_kernel = np.zeros((kernel_size, kernel_size), dtype=np.uint8)
        cv2.circle(circular_kernel, (radius, radius), radius, 1, -1)
        
        # 進行膨脹操作
        dilated_image = cv2.dilate(binary_image, circular_kernel)
        
        # 將結果轉換回0和1
        dilated_mask = (dilated_image / 255).astype(np.uint8)
        
        return dilated_mask
    
    @check_cancelled
    def smooth_volume_mask(self, volume_node):
        """
        Smooths the mask within a given volume node using the convex hull method.

        Parameters:
        - volume_node: The volume node containing the mask to be smoothed.
        - cutoff_frequency: The cutoff frequency for smoothing (unused in this function).
        """
        # for debug
        _ = self.copy_scalar_volume_node(volume_node)        
        
        # Extract the 3D array from the volume node
        volume_data = slicer.util.arrayFromVolume(volume_node)

        # Initialize an array of the same size as the original volume data to store the smoothed data
        smoothed_volume_data = np.zeros_like(volume_data)

        # Process each z-axis slice
        for z in range(volume_data.shape[0]):
            # Binarization: Set values greater than 50 to 1, others to 0
            binary_slice = ((volume_data[z, :, :] >= 50) & (volume_data[z, :, :] <= 100)).astype(np.uint8)            

            # Connected component analysis
            labeled_array, num_features = ndimage.label(binary_slice)
            if num_features > 0:
                # Compute distances of each region to the center
                center_of_mass = np.array(ndimage.center_of_mass(binary_slice, labeled_array, range(1, num_features + 1)))
                image_center = np.array(binary_slice.shape) / 2
                distances = np.sqrt(np.sum((center_of_mass - image_center) ** 2, axis=1))

                # Retain the region closest to the center
                closest_region = (labeled_array == (np.argmin(distances) + 1))
                
                # Process the binary mask
                # closest_region_processed = closest_region
                closest_region_processed = self.process_binary_mask(closest_region)
                closest_region_processed = self.process_binary_mask(closest_region_processed)
                
                # Compute the convex hull
                hull = morphology.convex_hull_image(closest_region_processed)
                
                # dilate the mask
                hull = self.dilate_binary_mask(hull, 3)
                               
                # # Apply Gaussian smoothing to the slice
                # smoothed_slice = gaussian_filter(hull, sigma=1)
                smoothed_volume_data[z, :, :] = hull
                
        # Update the volume node with the smoothed data
        slicer.util.updateVolumeFromArray(volume_node, smoothed_volume_data)

    @check_cancelled
    def setSegmentationOpacity(self, segmentationNode):             
        # Get the display node
        displayNode = segmentationNode.GetDisplayNode()
        # Set opacity for all segments
        opacity = 0.3  # Adjust this value between 0 (fully transparent) and 1 (fully opaque)
        displayNode.SetOpacity3D(opacity)
        # Update the view
        slicer.app.processEvents()
    
    @check_cancelled    
    def setStatsTable(self, table_node):
        import pandas as pd
        from scipy import stats
        
        # 轉換vtkTable為Pandas DataFrame
        def vtkTableToDataFrame(table_node):
            table = table_node.GetTable()
            columns = [table.GetColumnName(i) for i in range(table.GetNumberOfColumns())]
            data = {col: slicer.util.arrayFromTableColumn(table_node, col) for col in columns}
            df = pd.DataFrame(data)
            return df

        df = vtkTableToDataFrame(table_node)

        # 計算統計數據
        area = df['Area(mm²)']
        diameter = df['Diameter(mm)']

        # Min, Max, Mean, Median, IQR
        area_min = np.min(area)
        area_max = np.max(area)
        area_mean = np.mean(area)
        area_median = np.median(area)
        area_iqr = stats.iqr(area)

        diameter_min = np.min(diameter)
        diameter_max = np.max(diameter)
        diameter_mean = np.mean(diameter)
        diameter_median = np.median(diameter)
        diameter_iqr = stats.iqr(diameter)

        # 其他計算
        area_iqr_plus_mean = area_iqr + area_mean
        diameter_max_plus_median = diameter_max + diameter_median
        diameter_max_plus_mean = diameter_max + diameter_mean
        diameter_max_times_median = diameter_max * diameter_median
        diameter_max_times_mean = diameter_max * diameter_mean
        diameter_iqr_times_mean = diameter_iqr * diameter_mean
        area_mean_times_diameter_max = area_mean * diameter_max

        # 閾值
        thresholds = {
            'Metric': [
                'Area_Min', 'Area_Max', 'Area_Mean', 'Area_Median', 'Area_IQR',
                'Diameter_Min', 'Diameter_Max', 'Diameter_Mean', 'Diameter_Median', 'Diameter_IQR',
                'Area_IQR+Area_Mean', 'Diameter_Max+Diameter_Median', 'Diameter_Max+Diameter_Mean',
                'Diameter_Max*Diameter_Median', 'Diameter_Max*Diameter_Mean', 'Diameter_IQR*Diameter_Mean',
                'Area_Mean*Diameter_Max'
            ],
            'Value': [
                area_min, area_max, area_mean, area_median, area_iqr,
                diameter_min, diameter_max, diameter_mean, diameter_median, diameter_iqr,
                area_iqr_plus_mean, diameter_max_plus_median, diameter_max_plus_mean,
                diameter_max_times_median, diameter_max_times_mean, diameter_iqr_times_mean,
                area_mean_times_diameter_max
            ],
            'Threshold': [
                268, 1198, 616, 609, 298,
                20, 42, 30, 29, 8,
                892, 70, 71, 1215, 1228, 36, 26822
            ],
            'Units': [
                'mm²', 'mm²', 'mm²', 'mm²', 'mm²',
                'mm', 'mm', 'mm', 'mm', 'mm',
                'mm²', 'mm', 'mm', 'mm²', 'mm²', 'mm', 'mm³'
            ],
            'AUC': [
                0.54, 0.85, 0.85, 0.82, 0.82,
                0.55, 0.86, 0.85, 0.83, 0.76,
                0.87, 0.88, 0.88, 0.88, 0.88, 0.87, 0.87
            ]
        }

        results_df = pd.DataFrame(thresholds)

        # 添加Aneurysm列
        # results_df['Aneurysm'] = (results_df['Value'] > results_df['Threshold']).astype(int)

        # 創建新的TableNode
        new_table_node = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLTableNode')
        new_table_node.SetName('Aorta Statistics with Thresholds and AUC')

        # 將結果DataFrame轉換為vtkTable
        def dataFrameToVtkTable(df):
            table = vtk.vtkTable()
            for col in df.columns:
                if df[col].dtype in [np.float32, np.float64]:
                    arr = vtk.vtkFloatArray()
                elif df[col].dtype in [np.int32, np.int64]:
                    arr = vtk.vtkIntArray()
                else:
                    arr = vtk.vtkStringArray()
                arr.SetName(col)
                table.AddColumn(arr)
            for i in range(len(df)):
                table.InsertNextBlankRow()
                for j, col in enumerate(df.columns):
                    if df[col].dtype in [np.float32, np.float64, np.int32, np.int64]:
                        table.GetColumn(j).SetValue(i, df[col].iloc[i])
                    else:
                        table.GetColumn(j).SetValue(i, str(df[col].iloc[i]))
            return table

        vtk_table = dataFrameToVtkTable(results_df)
        new_table_node.SetAndObserveTable(vtk_table)

        # 確認結果
        slicer.util.setSliceViewerLayers(foregroundOpacity=0.7)
        slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID(new_table_node.GetID())
        slicer.app.applicationLogic().PropagateTableSelection()

        # 找到所有 TableViewNodes
        tableViewNodes = slicer.util.getNodesByClass('vtkMRMLTableViewNode')

        # 遍歷這些節點並顯示它們
        for node in tableViewNodes:
            node.SetVisibility(True)

    def process(self,
                inputVolume: vtkMRMLScalarVolumeNode,
                outputSegmentation: vtkMRMLSegmentationNode,
                outputCenterlineEndpoints: vtkMRMLMarkupsFiducialNode,
                outputCenterlineCurve: vtkMRMLMarkupsCurveNode,
                outputStraightenedVolume: vtkMRMLScalarVolumeNode,
                outputStraightenedTransform: vtkMRMLTransformNode,
                outputStraightenedLabelVolume: vtkMRMLScalarVolumeNode,
                outputStraightenedSegmentation: vtkMRMLSegmentationNode,
                model_name: str,
                progressDialog: qt.QProgressDialog,
                case_index: int = None,
                total_cases: int = None,
                batch_mode: bool = False):

        """
        Run the processing algorithm.
        Can be used without GUI widget.
        :param inputVolume: Input volume to be processed
        :param outputSegmentation: Segmentation node to store the output segmentation
        :param outputCenterlineEndpoints: Markups fiducial node to store the endpoints of the centerline
        :param outputCenterlineCurve: Markups curve node to store the centerline curve
        :param outputStraightenedVolume: Scalar volume node to store the straightened volume
        :param outputStraightenedTransform: Transform node to store the transform to the straightened volume
        :param outputStraightenedLabelVolume: Scalar volume node to store the straightened label volume
        :param outputStraightenedSegmentation: Segmentation node to store the straightened segmentation
        :param model_name: Name of the model to be used for segmentation
        :param progressDialog: Progress dialog to display the progress
        :param case_index: Index of the current case in batch processing
        :param total_cases: Total number of cases in batch processing
        :param batch_mode: Flag indicating if it's in batch processing mode
        """

        if not inputVolume:
            raise ValueError("Input volume is invalid")

        steps = 13  # Total number of steps in the process
        currentStep = 0

        def updateProgress(step, message):
            nonlocal currentStep
            currentStep += step
            if batch_mode and case_index is not None and total_cases is not None:
                overall_progress = (case_index / total_cases) * 100
                case_progress = (currentStep / steps) * (100 / total_cases)
                progressDialog.setValue(int(overall_progress + case_progress))
                progressDialog.setLabelText(f"Case {case_index + 1}/{total_cases}: {message}")
            else:
                progressDialog.setValue(int((currentStep / steps) * 100))
                progressDialog.setLabelText(message)
            slicer.app.processEvents()
            if self.cancelled:
                raise Exception("Process was cancelled")

        updateProgress(1, 'Start processing with model: ' + model_name)

        if model_name == 'TotalSegmentator':
            # TotalSegmentator
            if 'TotalSegmentatorInstance' not in dir(slicer.modules):
                slicer.modules.totalsegmentator.widgetRepresentation().show()
                slicer.modules.totalsegmentator.widgetRepresentation().close()
            slicer.modules.TotalSegmentatorInstance.parent.widgetRepresentation().self().logic.process(
                inputVolume,
                outputSegmentation,
                fast=False
            )
            # Only keep Aorta
            self.OnlyAorta()

        elif model_name == 'MONAI-Aorta':
            # MONAI Aorta Segmentation
            if 'MONAIAuto3DSegInstance' not in dir(slicer.modules):
                slicer.modules.monaiauto3dseg.widgetRepresentation().show()
                slicer.modules.monaiauto3dseg.widgetRepresentation().close()
            slicer.modules.MONAIAuto3DSegInstance.parent.widgetRepresentation().self().logic.process(
                [inputVolume],
                outputSegmentation,
                'aorta-v1.1.0'
            )

        updateProgress(1, 'Creating label map node from segmentation...')
        LabelMapVolumeNode = self.createLabelMapVolumeNode(outputSegmentation)
        LabelMapScalarVolumeNode = self.LabelMapNode_to_ScalarVolumeNode(LabelMapVolumeNode)

        updateProgress(1, 'Detecting start and end points...')
        if 'ExtractCenterlineWidget' not in dir(slicer.modules):
            slicer.modules.extractcenterline.widgetRepresentation().show()
            slicer.modules.extractcenterline.widgetRepresentation().close()
        slicer.modules.ExtractCenterlineWidget.ui.inputSurfaceSelector.setCurrentNode(outputSegmentation)
        slicer.modules.ExtractCenterlineWidget.ui.endPointsMarkupsSelector.setCurrentNode(outputCenterlineEndpoints)
        slicer.modules.ExtractCenterlineWidget.onAutoDetectEndPoints()

        self.keepFirstAndFarthestPoint(outputCenterlineEndpoints)
        self.setSegmentationOpacity(outputSegmentation)

        updateProgress(1, 'Extracting centerline...')
        if 'ExtractCenterlineWidget' not in dir(slicer.modules):
            slicer.modules.extractcenterline.widgetRepresentation().show()
            slicer.modules.extractcenterline.widgetRepresentation().close()
        newNode = slicer.modules.ExtractCenterlineWidget.ui.outputCenterlinePropertiesTableSelector.addNode()
        newNode.SetName("CenterlineProperties")
        slicer.modules.ExtractCenterlineWidget.ui.outputCenterlineCurveSelector.setCurrentNode(outputCenterlineCurve)
        slicer.modules.ExtractCenterlineWidget.onApplyButton()

        updateProgress(1, 'Straightening the vessel...')
        if 'CurvedPlanarReformatWidget' not in dir(slicer.modules):
            slicer.modules.curvedplanarreformat.widgetRepresentation().show()
            slicer.modules.curvedplanarreformat.widgetRepresentation().close()
        slicer.modules.CurvedPlanarReformatWidget.ui.inputVolumeSelector.setCurrentNode(inputVolume)
        slicer.modules.CurvedPlanarReformatWidget.ui.inputCurveSelector.setCurrentNode(outputCenterlineCurve)
        slicer.modules.CurvedPlanarReformatWidget.ui.outputStraightenedVolumeSelector.setCurrentNode(outputStraightenedVolume)
        slicer.modules.CurvedPlanarReformatWidget.ui.outputTransformToStraightenedVolumeSelector.setCurrentNode(outputStraightenedTransform)
        slicer.modules.CurvedPlanarReformatWidget.ui.sliceSizeCoordinatesWidget.coordinates = '300,300'
        slicer.modules.CurvedPlanarReformatWidget.onApplyButton()

        slicer.modules.CurvedPlanarReformatWidget.ui.inputVolumeSelector.setCurrentNode(LabelMapScalarVolumeNode)
        slicer.modules.CurvedPlanarReformatWidget.ui.inputCurveSelector.setCurrentNode(outputCenterlineCurve)
        slicer.modules.CurvedPlanarReformatWidget.ui.outputStraightenedVolumeSelector.setCurrentNode(outputStraightenedLabelVolume)
        slicer.modules.CurvedPlanarReformatWidget.onApplyButton()

        updateProgress(1, 'Resetting camera to center the view...')
        threeDView = slicer.app.layoutManager().threeDWidget(0).threeDView()
        threeDView.resetFocalPoint()

        updateProgress(1, 'Smoothing the label volume...')
        self.smooth_volume_mask(outputStraightenedLabelVolume)

        updateProgress(1, 'Computing area and diameter...')
        areas, diameters = self.aorta_quan(outputStraightenedLabelVolume)

        updateProgress(1, 'Creating plot...')
        plotChartNode, plotViewNode, tableNode = self.createAreaDiameterPlot(areas, diameters)

        updateProgress(1, 'Setting stats table...')
        self.setStatsTable(tableNode)

        updateProgress(1, 'Creating segmentation from label volume...')
        self.StraightenedLabelVolume2Segmentation(outputStraightenedLabelVolume, outputStraightenedSegmentation)
        self.setSegmentationOpacity(outputStraightenedSegmentation)

        updateProgress(1, 'Finalizing...')
        outputSegmentation.SetDisplayVisibility(False)
        outputCenterlineEndpoints.SetDisplayVisibility(False)
        outputCenterlineCurve.SetDisplayVisibility(False)
        slicer.util.setSliceViewerLayers(background=slicer.util.getNode('StraightenedVolume'))
        slicer.util.resetSliceViews()
        slicer.app.processEvents()

        updateProgress(1, 'Processing complete.')




#
# DeepAortaTest
#

class DeepAortaTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_DeepAorta1()

    def test_DeepAorta1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")

        # Get/create input data

        import SampleData
        registerSampleData()
        inputVolume = SampleData.downloadSample("DeepAorta1")
        self.delayDisplay("Loaded test data set")

        inputScalarRange = inputVolume.GetImageData().GetScalarRange()
        self.assertEqual(inputScalarRange[0], 0)
        self.assertEqual(inputScalarRange[1], 695)

        outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        threshold = 100

        # Test the module logic

        logic = DeepAortaLogic()

        # Test algorithm with non-inverted threshold
        logic.process(inputVolume, outputVolume, threshold, True)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], threshold)

        # Test algorithm with inverted threshold
        logic.process(inputVolume, outputVolume, threshold, False)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], inputScalarRange[1])

        self.delayDisplay("Test passed")
