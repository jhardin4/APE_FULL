# This is the main file that calls all of the other elements of APE

# APE framework.  Procedure may not be necessary
from Apparatus import apparatus
from Procedure import procedure
from Executor import executor

# Import the procedure sets that are needed
import Procedures_SampleTray
import Procedures_Toolpath
import Procedures_Planner
import Procedures_InkCal
import Procedures_Alignments

# Import other libraries
import FlexPrinterApparatus  # This is specific to the Flex Printer at AFRL
import XlineTPGen as TPGen  # Toolpath generator
import time

# Create apparatus and executor
MyApparatus = apparatus()
MyExecutor = executor()
MyExecutor.debug = True  # Leave this as-is for now.

#____FLexPrinterApparatus____#
# Set up a basic description of the system that is later used to create an
# apparatus specific to the Flex Printer at AFRL

materials = [{'AgPMMA': 'ZZ1'}]
tools = [{'name': 'TProbe', 'axis': 'ZZ2', 'type': 'Keyence_TouchProbe'}]
tools.append({'name': 'camera', 'axis': 'ZZ4', 'type': 'Ueye_Camera'})

FlexPrinterApparatus.Build_FlexPrinter(materials, tools, MyApparatus)
mat0 = [list(materials[n])[0] for n in range(len(materials))][0]
# Define the rest of the apparatus
MyApparatus['devices']['n' + mat0]['descriptors'].append(mat0)
MyApparatus['devices']['n' + mat0]['trace_height'] = 0.1
MyApparatus['devices']['n' + mat0]['trace_width'] = 0.2
MyApparatus['devices']['aeropump0']['descriptors'].append(mat0)
MyApparatus['devices']['gantry']['default']['speed'] = 40
MyApparatus['devices']['gantry']['n' + mat0]['speed'] = 5  # Calibration is on so this is overwritten
MyApparatus['devices']['aeropump0']['pumpon_time'] = 1  # Calibration is on so this is overwritten
MyApparatus['devices']['aeropump0']['mid_time'] = 1
MyApparatus['devices']['aeropump0']['pumpoff_time'] = 0
MyApparatus['devices']['aeropump0']['pumpres_time'] = 0.3
MyApparatus['devices']['aeropump0']['pressure'] = 100
MyApparatus['devices']['pump0']['COM'] = 9

MyApparatus['information']['materials'][mat0]['density'] = 1.84
MyApparatus['information']['toolpaths'] = {}
MyApparatus['information']['toolpaths']['generator'] = TPGen.GenerateToolpath
MyApparatus['information']['toolpaths']['parameters'] = TPGen.Make_TPGen_Data(mat0)
MyApparatus['information']['toolpaths']['toolpath'] = [0]

# Connect to all the devices in the setup
MyApparatus.Connect_All(MyExecutor, simulation=True)

# Create instances of the procedures that will be used
# Procedures that will almost always be used at this level
AlignPrinter = Procedures_Alignments.Align(MyApparatus, MyExecutor)

# Procedures for doing automated experiments
BuildGrid = Procedures_SampleTray.Setup_XYGridTray(MyApparatus, MyExecutor)
SampleGrid = Procedures_SampleTray.SampleTray(MyApparatus, MyExecutor)
CalInk = Procedures_InkCal.Calibrate(MyApparatus, MyExecutor)

# Build the procedure to be done at each sample position
class PrintSample(procedure):
    def Prepare(self):
        self.name = 'PrintSample'
        self.requirements['samplename'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of this sample for logging purposes'}
        self.gentp = Procedures_Toolpath.Generate_Toolpath(MyApparatus, MyExecutor)
        self.printtp = Procedures_Toolpath.Print_Toolpath(MyApparatus, MyExecutor)
        self.planner = Procedures_Planner.Combinatorial_Planner(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful pieces of informaiton
        samplename = self.requirements['samplename']['value']
        
        # Set the plan space from tip height and anticipated trace height
        space = {'tiph': [0.01*n for n in range(8)]}
        space['trace_height'] = [0.1 * n for n in range(1, 6)]
        # Set the Apparatus addresses for tip heigh ant anticipate trace height
        addresses = {'tiph': ['information', 'toolpaths', 'parameters', 'tiph']}
        addresses['trace_height'] = ['devices', 'nAgPMMA', 'trace_height']
        # Set the priority of exploration
        priority = ['tiph', 'trace_height']
        # Set where to store the planner log
        file = 'Data//planner.json'
        self.planner.Do({'space': space, 'Apparatus_Addresses': addresses, 'file': file, 'priority': priority})
        
        # Generate Toolpath
        self.gentp.Do()
        self.printtp.Do({'toolpath': self.gentp.requirements['target']['value']})
        time.sleep(1) #Just in for demonstration

# Do the experiment
AlignPrinter.Do({'primenoz': 'n' + mat0})
CalInk.Do({'material': 'AgPMMA'})
BuildGrid.Do({'trayname': 'example_tray', 'samplename': 'sample', 'xspacing': 10, 'xsamples': 2, 'yspacing': 5, 'ysamples': 3})
SampleGrid.Do({'trayname': 'example_tray', 'procedure': PrintSample(MyApparatus, MyExecutor)})
MyApparatus.Disconnect_All()
