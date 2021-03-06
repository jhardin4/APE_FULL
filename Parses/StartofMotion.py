from Core import Procedure
import Procedures.Aerotech_A3200_Set
import Procedures.Motion_RefRelPriorityLineMotion
import Procedures.Pump_PumpOn
import Procedures.User_InkCal_Calculate


class StartofMotion(Procedure): 
    def Prepare(self):
        self.name = 'StartofMotion'
        self.requirements['motion'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'motion to start'}
        self.pmove = Procedures.Motion_RefRelPriorityLineMotion(self.apparatus, self.executor)
        self.pumpon = Procedures.Pump_PumpOn(self.apparatus, self.executor)
        self.motionset = Procedures.Aerotech_A3200_Set(self.apparatus, self.executor)
        self.calUpdate = Procedures.User_InkCal_Calculate(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful pieces of informaiton
        startpoint = self.requirements['motion']['value']['startpoint']
        materialname = self.requirements['motion']['value']['material']

        # Retreiving necessary device names
        nozzlename = self.apparatus.findDevice({'descriptors': ['nozzle', materialname]})
        pumpname = self.apparatus.findDevice({'descriptors': ['pump', materialname]})
        motionname = self.apparatus.findDevice({'descriptors': 'motion'})

        # Getting necessary eprocs
        pumpset = self.apparatus.GetEproc(pumpname, 'Set')
        runmove = self.apparatus.GetEproc(motionname, 'Run')

        # Assign apparatus addresses to procedures
        self.pumpon.requirements['pumpon_time']['address'] = ['devices', pumpname, 'pumpon_time']
        self.pumpon.requirements['mid_time']['address'] = ['devices', pumpname, 'mid_time']
        self.pmove.requirements['refpoint']['address'] = ['information', 'alignments', nozzlename + '@start']
        self.pmove.requirements['speed']['address'] = ['devices',motionname, 'default', 'speed']
        self.pmove.requirements['axismask']['address'] = ['devices', motionname, nozzlename, 'axismask']

        # Doing stuff
        self.motionset.Do({'Type': 'default'})
        self.pmove.Do({'relpoint': startpoint, 'priority': [['X', 'Y'], ['Z']]})
        if materialname in self.apparatus['information']['materials']:
            self.calUpdate.Do({'material': materialname})
        self.motionset.Do({'Type': nozzlename})
        runmove.Do()
        if pumpname != 'No devices met requirments':
            pumpset.requirements['pressure']['address'] = ['devices', pumpname, 'pressure']
            pumpset.Do()
            self.pumpon.Do({'name': pumpname})
