from Procedure import procedure
import Procedures_Motion
import Procedures_Pumps
import Procedures_A3200
import Procedures_InkCal
import Procedures_TouchProbe
import Procedures_Camera

class StartofMotion(procedure): 
    def Prepare(self):
        self.name = 'StartofMotion'
        self.requirements['motion'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'motion to start'}
        self.pmove = Procedures_Motion.RefRelPriorityLineMotion(self.apparatus, self.executor)
        self.pumpon = Procedures_Pumps.PumpOn(self.apparatus, self.executor)
        self.motionset = Procedures_A3200.A3200SetMotonType(self.apparatus, self.executor)
        self.calUpdate = Procedures_InkCal.Cal_Calulation(self.apparatus, self.executor)

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

class EndofMotion(procedure):
  
    def Prepare(self):
        self.name = 'EndofMotion'
        self.requirements['motion']={'source':'apparatus', 'address':'', 'value':'', 'desc':'motion to start'}
        self.pumpoff = Procedures_Pumps.PumpOff(self.apparatus, self.executor)
        self.motionset = Procedures_A3200.A3200SetMotonType(self.apparatus, self.executor)        
    
    def Plan(self):
        #Renaming useful pieces of informaiton
        materialname = self.requirements['motion']['value']['material']
        
        #Retreiving necessary device names
        pumpname = self.apparatus.findDevice({'descriptors':['pump', materialname] })
        motionname = self.apparatus.findDevice({'descriptors':'motion' })
        nozzlename = self.apparatus.findDevice({'descriptors':['nozzle', materialname] })
        
        #Getting necessary eprocs
        runmove = self.apparatus.GetEproc(motionname, 'Run')
        move = self.apparatus.GetEproc(motionname, 'Move')
        
        #Assign apparatus addresses to procedures
        self.pumpoff.requirements['pumpoff_time']['address']=['devices',pumpname,'pumpoff_time']
        self.pumpoff.requirements['mid_time']['address']=['devices',pumpname,'mid_time']
        ##Assumes that the +Z axis is the safe direction
        axismask = self.apparatus['devices'][motionname][nozzlename]['axismask']
        if 'Z' in axismask:
            move.requirements['point']['address']=['information','alignments','safe'+axismask['Z']]
        else:
            self.move.requirements['spepoint']['address']=['information','alignments','safeZ']
        move.requirements['speed']['address']=['devices',motionname, 'default', 'speed']

        # Doing stuff
        runmove.Do()  # Run the motion up to this point
        if pumpname != 'No devices met requirments':
            self.pumpoff.Do({'name': pumpname})
        self.motionset.Do({'Type': 'default'})
        move.Do()
        runmove.Do()


class Start(procedure):
    def Prepare(self):
        self.name = 'Start'
        self.motionset = Procedures_A3200.A3200SetMotonType(self.apparatus, self.executor)
        self.pmove = Procedures_Motion.RefRelPriorityLineMotion(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful pieces of informaiton
        matList = list(self.apparatus['information']['materials'])

        # Retreiving necessary device names
        motionname = self.apparatus.findDevice({'descriptors': 'motion'})

        # Getting necessary eprocs
        runmove = self.apparatus.GetEproc(motionname, 'Run')

        # Assign apparatus addresses to procedures
        self.pmove.requirements['speed']['address'] = ['devices', motionname, 'default', 'speed']
        self.pmove.requirements['refpoint']['address'] = ['information', 'alignments', 'initial']

        # Doing stuff
        self.motionset.Do({'Type': 'default'})
        self.pmove.Do({'priority': [['ZZ1', 'ZZ2', 'ZZ3', 'ZZ4'], ['X', 'Y']]})
        runmove.Do()
        
class ChangeMat(procedure):
    def Prepare(self):
        self.name = 'ChangeMat'
        self.requirements['startmotion']={'source':'apparatus', 'address':'', 'value':'', 'desc':'motion before change'}
        self.requirements['endmotion']={'source':'apparatus', 'address':'', 'value':'', 'desc':'motion afterchange'}
        self.startofmotion=StartofMotion(self.apparatus, self.executor)
        self.endofmotion=EndofMotion(self.apparatus, self.executor)
        self.motionset = Procedures_A3200.A3200SetMotonType(self.apparatus, self.executor)
        self.pumpon = Procedures_Pumps.PumpOn(self.apparatus, self.executor)
        self.pumpoff = Procedures_Pumps.PumpOff(self.apparatus, self.executor)

    def Plan(self):
        #Renaming useful pieces of informaiton
        startmotion = self.requirements['startmotion']['value']
        endmotion = self.requirements['endmotion']['value']
        
        #Retreiving necessary device names
        motionname = self.apparatus.findDevice({'descriptors':'motion' })
        endnozzle = self.apparatus.findDevice({'descriptors':['nozzle', endmotion['material']] })
        startpump = self.apparatus.findDevice({'descriptors':['pump', startmotion['material']] })
        endpump = self.apparatus.findDevice({'descriptors':['pump', endmotion['material']] })
        
        #Getting necessary eprocs
        runmove = self.apparatus.GetEproc(motionname, 'Run')
        
        #Assign apparatus addresses to procedures
        self.pumpon.requirements['pumpon_time']['address']=['devices',endpump,'pumpon_time']
        self.pumpon.requirements['mid_time']['address']=['devices',endpump,'mid_time']
        self.pumpoff.requirements['pumpoff_time']['address']=['devices',startpump,'pumpoff_time']
        self.pumpoff.requirements['mid_time']['address']=['devices',startpump,'mid_time']        
        
        # Doing stuff
        # Handling Print-Slide behavior
        if startmotion['material']==endmotion['material'].replace('slide','') or endmotion['material']==startmotion['material'].replace('slide',''):
            if startmotion['material'].endswith('slide'):
                self.motionset.Do({'Type':endnozzle})
                runmove.Do()
                self.pumpon.Do({'name':endpump})
            else:
                runmove.Do()
                self.pumpoff.Do({'name':startpump})
                self.motionset.Do({'Type':endnozzle})
                runmove.Do()
        else:
            self.endofmotion.Do({'motion':startmotion})
            self.startofmotion.Do({'motion':endmotion})

class EndofLayer(procedure):
    def Prepare(self): 
        self.name = 'EndofLayer'
        self.requirements['layernumber']={'source':'apparatus', 'address':'', 'value':'', 'desc':'number of the layer'}
        self.calink = Procedures_InkCal.Calibrate(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful pieces of informaiton
        matList = list(self.apparatus['information']['materials'])
        lnumber = self.requirements['layernumber']['value']
        
        # Doing stuff
        if lnumber != 0 and lnumber % 4 == 0:
            for material in matList:
                if 'PDMS' in material:
                    self.calink.Do({'material':material})


class End(procedure):
    def Prepare(self):
        self.name = 'End'
        self.motionset = Procedures_A3200.A3200SetMotonType(self.apparatus, self.executor)
        self.pmove = Procedures_Motion.RefRelPriorityLineMotion(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful pieces of informaiton

        # Retreiving necessary device names
        motionname = self.apparatus.findDevice({'descriptors': 'motion'})

        # Getting necessary eprocs
        runmove = self.apparatus.GetEproc(motionname, 'Run')

        # Assign apparatus addresses to procedures
        self.pmove.requirements['speed']['address'] = ['devices', motionname, 'default', 'speed']
        self.pmove.requirements['refpoint']['address'] = ['information', 'alignments', 'initial']

        # Doing stuff
        self.motionset.Do({'Type': 'default'})
        self.pmove.Do({'priority': [['ZZ1', 'ZZ2', 'ZZ3', 'ZZ4'], ['X', 'Y']]})
        runmove.Do()
           