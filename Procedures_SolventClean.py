'''
These procedures are related to using a solvent bath to clean a nozzle

'''

from Procedure import procedure
import time
import json
import Procedures_Motion
import Procedures_A3200


class CleanNozzle(procedure):
    def Prepare(self):
        self.name = 'Calibrate'
        self.requirements['nozzlename'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of the nozzle being cleaned'}
        self.requirements['depth'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'how deep to go into the cleaning vessel'}
        self.requirements['delay'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'How long to wait between swirls'}
        self.requirements['swirls'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'How many swirls to do'}
        self.requirements['sradius'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'How many swirls to do'}
        
        self.move = Procedures_Motion.RefRelLinearMotion(self.apparatus, self.executor)
        self.pmove = Procedures_Motion.RefRelPriorityLineMotion(self.apparatus, self.executor)
        self.motionset = Procedures_A3200.A3200SetMotonType(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful informaiton
        nozzlename = self.requirements['nozzlename']['value']
        depth = self.requirements['depth']['value']
        delay = self.requirements['delay']['value']
        swirls = self.requirements['swirls']['value']
        sradius = self.requirements['sradius']['value']
        
        # Retreiving necessary device names
        motionname = self.apparatus.findDevice({'descriptors': 'motion'})
        pumpname = self.apparatus.findDevice({'descriptors': ['pump', nozzlename[1:]]})
        systemname = self.apparatus.findDevice({'descriptors': 'system'})

        # Getting necessary eprocs
        runmove = self.apparatus.GetEproc(motionname, 'Run')
        pumpon = self.apparatus.GetEproc(pumpname, 'On')
        pumpoff = self.apparatus.GetEproc(pumpname, 'Off')
        #pumpset = self.apparatus.GetEproc(pumpname, 'Set')
        dwell = self.apparatus.GetEproc(systemname, 'Dwell')

        # Assign apparatus addresses to procedures        
        self.move.requirements['speed']['address'] = ['devices',motionname, 'default', 'speed']
        self.move.requirements['axismask']['address'] = ['devices', motionname, nozzlename, 'axismask']
        self.move.requirements['refpoint']['address'] = ['information', 'alignments', nozzlename + '@dump']

        self.pmove.requirements['speed']['address'] = ['devices',motionname, 'default', 'speed']
        self.pmove.requirements['axismask']['address'] = ['devices', motionname, nozzlename, 'axismask']
        self.pmove.requirements['refpoint']['address'] = ['information', 'alignments', nozzlename + '@dump']
        
        # Doing stuff
        self.motionset.Do({'Type': 'default'})
        self.pmove.Do({'priority': [['X', 'Y'], ['Z']]})
        self.move.Do({'relpoint':{'Z':-depth}})
        runmove.Do()
        #pumpset.requirements['pressure']['address'] = ['devices', pumpname, 'pressure']
        #pumpset.Do()
        pumpon.Do()
        for n in range(swirls):
            self.move.Do({'relpoint':{'X': sradius/2, 'Y': sradius/2, 'Z':-depth}})
            self.move.Do({'relpoint':{'X': sradius/2, 'Y': -sradius/2, 'Z':-depth}})
            self.move.Do({'relpoint':{'X': -sradius/2, 'Y': -sradius/2, 'Z':-depth}})
            self.move.Do({'relpoint':{'X': -sradius/2, 'Y': sradius/2, 'Z':-depth}})
        self.move.Do({'relpoint':{'Z':-depth}})
        runmove.Do()
        dwell.Do({'dtime':delay})
        pumpoff.Do()
        for n in range(swirls):
            self.move.Do({'relpoint':{'X': sradius/2, 'Y': sradius/2, 'Z':-depth}})
            self.move.Do({'relpoint':{'X': sradius/2, 'Y': -sradius/2, 'Z':-depth}})
            self.move.Do({'relpoint':{'X': -sradius/2, 'Y': -sradius/2, 'Z':-depth}})
            self.move.Do({'relpoint':{'X': -sradius/2, 'Y': sradius/2, 'Z':-depth}})
        self.move.Do({'relpoint':{'Z':-depth}})
        self.move.Do({'relpoint':{'Z':0}})
        zaxis = self.apparatus.getValue(['devices', motionname, nozzlename, 'axismask'])['Z']
        self.move.requirements['refpoint']['address'] = ['information', 'alignments', 'safe' + zaxis]
        self.move.Do()

