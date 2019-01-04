from Procedure import procedure
import Procedures_Motion
import Procedures_A3200

class Initialize_TouchProbe(procedure): 
    def Prepare(self):
        self.name = 'Initialize_TouchProbe'
        self.move = Procedures_Motion.RefRelLinearMotion(self.apparatus, self.executor)
        self.pmove = Procedures_Motion.RefRelPriorityLineMotion(self.apparatus, self.executor)
        self.motionset = Procedures_A3200.A3200SetMotonType(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful pieces of informaiton

        # Retreiving necessary device names
        motionname = self.apparatus.findDevice({'descriptors': 'motion'})

        # Getting necessary eprocs
        initialize = self.apparatus.GetEproc('TProbe', 'Initialize')
        runmove = self.apparatus.GetEproc(motionname, 'Run')

        # Assign apparatus addresses to procedures
        self.move.requirements['speed']['address'] = ['devices',motionname, 'default', 'speed']
        self.move.requirements['axismask']['address'] = ['devices', motionname, 'TProbe', 'axismask']
        zaxis = self.apparatus.getValue(['devices', motionname, 'TProbe', 'axismask'])['Z']
        self.move.requirements['refpoint']['address'] = ['information', 'alignments', 'safe' + zaxis]

        self.pmove.requirements['speed']['address'] = ['devices',motionname, 'default', 'speed']
        self.pmove.requirements['axismask']['address'] = ['devices', motionname, 'TProbe', 'axismask']
        self.pmove.requirements['refpoint']['address'] = ['information', 'alignments', 'TProbe@TP_init']
        
        # Doing stuff
        self.motionset.Do({'Type': 'default'})
        self.pmove.Do({'priority': [['Z'], ['X', 'Y']]})
        runmove.Do()
        initialize.Do()
        self.motionset.Do({'Type': 'default'})
        self.move.Do()
        
class Measure_TouchProbe(procedure): 
    def Prepare(self):
        self.name = 'Measure_TouchProbe'
        self.requirements['address'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'where to store result'}
        self.requirements['zreturn'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'how high to return after measurement'}
        self.requirements['retract'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'retract probe after measurement'}

    def Plan(self):
        # Renaming useful pieces of informaiton
        retract = self.requirements['retract']['value']
        zreturn = self.requirements['zreturn']['value']
        address = self.requirements['address']['value']
        
        # Retreiving necessary device names
        motionname = self.apparatus.findDevice({'descriptors': 'motion'})
        
        # Retrieving information from apparatus
        zaxis = self.apparatus.getValue(['devices', motionname, 'TProbe', 'axismask'])['Z']
        speed = self.apparatus.getValue(['devices', motionname, 'default', 'speed'])

        # Getting necessary eprocs
        measure = self.apparatus.GetEproc('TProbe', 'Measure')
        setmove = self.apparatus.GetEproc(motionname, 'Set_Motion')
        move = self.apparatus.GetEproc(motionname, 'Move')

        # Assign apparatus addresses to procedures
        
        # Doing stuff
        measure.Do({'address':address, 'addresstype':'pointer', 'retract':retract})
        setmove.Do({'RelAbs': 'Rel', 'motionmode':'cmd'})
        move.Do({'motiontype':'linear', 'motionmode':'cmd', 'point': {zaxis: zreturn}, 'speed':speed})
        setmove.Do({'RelAbs': 'Abs', 'motionmode':'cmd'})

class Measure_TouchProbeXY(procedure): 
    def Prepare(self):
        self.name = 'Measure_TouchProbeXY'
        self.requirements['point'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'XY point to measure relative to start'}
        self.move = Procedures_Motion.RefRelLinearMotion(self.apparatus, self.executor)
        self.motionset = Procedures_A3200.A3200SetMotonType(self.apparatus, self.executor)
        self.pmove = Procedures_Motion.RefRelPriorityLineMotion(self.apparatus, self.executor)
        self.measure = Measure_TouchProbe(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful pieces of informaiton
        point = self.requirements['point']['value']
        
        # Retreiving necessary device names
        motionname = self.apparatus.findDevice({'descriptors': 'motion'})
        
        # Retrieving information from apparatus
        zaxis = self.apparatus.getValue(['devices', motionname, 'TProbe', 'axismask'])['Z']

        # Getting necessary eprocs
        runmove = self.apparatus.GetEproc(motionname, 'Run')


        # Assign apparatus addresses to procedures
        self.move.requirements['speed']['address'] = ['devices',motionname, 'default', 'speed']
        self.move.requirements['axismask']['address'] = ['devices', motionname, 'TProbe', 'axismask']
        self.move.requirements['refpoint']['address'] = ['information', 'alignments', 'safe'+zaxis]
        
        self.measure.requirements['address']['address']=['information', 'height_data']
        self.measure.requirements['zreturn']['address']=['devices', 'TProbe', 'zreturn']
        self.measure.requirements['retract']['address']=['devices', 'TProbe', 'retract']

        self.pmove.requirements['speed']['address'] = ['devices',motionname, 'default', 'speed']
        self.pmove.requirements['axismask']['address'] = ['devices', motionname, 'TProbe', 'axismask']
        self.pmove.requirements['refpoint']['address'] = ['information', 'alignments', 'TProbe@start']
        
        # Doing stuff
        self.motionset.Do({'Type': 'default'})
        self.move.Do()
        self.pmove.Do({'relpoint': {'X': point['X'], 'Y': point['Y']}, 'priority': [['X', 'Y'],['Z']]})
        runmove.Do()
        self.measure.Do()
