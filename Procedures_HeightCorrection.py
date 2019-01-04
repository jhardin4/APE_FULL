from Procedure import procedure
import Procedures_TouchProbe
import Procedures_A3200

class Initialize_SPHeightCorrect(procedure): 
    def Prepare(self):
        self.name = 'Initialize_SPHeightCorrect'
        self.measureTouch = Procedures_TouchProbe.Measure_TouchProbeXY(self.apparatus, self.executor)
        # Setup Apparatus
        if 'SPHeightCorrect' not in self.apparatus['information']:
            self.apparatus['information']['SPHeightCorrect'] = {'touchprobe_Z@start': '', 'original @starts': {}}

    def Plan(self):
        # Renaming useful pieces of informaiton
        alignments = self.apparatus['information']['alignments']
        o_starts = self.apparatus['information']['SPHeightCorrect']['original @starts']

        # Retreiving necessary device names
        motionname = self.apparatus.findDevice({'descriptors': 'motion'})

        # Getting necessary eprocs

        # Assign apparatus addresses to procedures
        
        # Doing stuff
        for alignment in alignments:
            if '@start' in alignment:
                toolname = alignment.split('@')[0]
                if toolname in self.apparatus['devices'][motionname]:
                    if 'axismask' in self.apparatus['devices'][motionname][toolname]:
                        axismask = self.apparatus.getValue(['devices', motionname, toolname, 'axismask'])
                        o_starts[alignment] = {axismask['Z']: alignments[alignment][axismask['Z']]}

        self.measureTouch.Do({'point': {'X': 0, 'Y': 0}})

        self.apparatus.setValue(['information', 'SPHeightCorrect', 'touchprobe_Z@start'], self.apparatus.getValue(['information', 'height_data'])[0])


class SPHeightCorrect(procedure): 
    def Prepare(self):
        self.name = 'SPHeightCorrect'
        self.requirements['point'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'XY point to measure relative to start'}
        self.measureTouch = Procedures_TouchProbe.Measure_TouchProbeXY(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful pieces of informaiton
        point = self.requirements['point']['value']
        alignments = self.apparatus['information']['alignments']
        o_starts = self.apparatus['information']['SPHeightCorrect']['original @starts']
        o_z = self.apparatus['information']['SPHeightCorrect']['touchprobe_Z@start']

        # Retreiving necessary device names

        # Getting necessary eprocs

        # Assign apparatus addresses to procedures
        
        # Doing stuff
        self.measureTouch.Do({'point': point})
        new_z = self.apparatus.getValue(['information', 'height_data'])[0]
        adjustment = new_z - o_z
        for alignment in alignments:
            if '@start' in alignment:
                if alignment in o_starts:
                    for dim in o_starts[alignment]:
                        alignments[alignment][dim] = o_starts[alignment][dim]+adjustment
        self.Report(string='@start alignments adjusted by ' + str(adjustment) + '.')

class DD_SPHeightCorrect(procedure): 
    def Prepare(self):
        self.name = 'DD_SPHeightCorrect'
        self.requirements['height'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'height to use for correction'}

    def Plan(self):
        # Renaming useful pieces of informaiton
        height = self.requirements['height']['value']
        alignments = self.apparatus['information']['alignments']
        o_starts = self.apparatus['information']['SPHeightCorrect']['original @starts']
        o_z = self.apparatus['information']['SPHeightCorrect']['touchprobe_Z@start']

        # Retreiving necessary device names

        # Getting necessary eprocs

        # Assign apparatus addresses to procedures
        
        # Doing stuff
        
        new_z = height
        adjustment = new_z - o_z
        for alignment in alignments:
            if '@start' in alignment:
                if alignment in o_starts:
                    for dim in o_starts[alignment]:
                        alignments[alignment][dim] = o_starts[alignment][dim]+adjustment
        self.Report(string='@start alignments adjusted by ' + str(adjustment) + '.')