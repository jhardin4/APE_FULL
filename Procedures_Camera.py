from Procedure import procedure
import Procedures_Motion
import Procedures_A3200

        
class Capture_Image(procedure): 
    def Prepare(self):
        self.name = 'Capture_Image'
        self.requirements['file'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'path to store image'}
        self.requirements['settle_time'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'time to weight before taking picture'}
        self.requirements['camera_name'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of the camera to be used'}

    def Plan(self):
        # Renaming useful pieces of informaiton
        file = self.requirements['file']['value']
        stime = self.requirements['settle_time']['value']
        cname = self.requirements['camera_name']['value']
        
        # Retreiving necessary device names
        systemname = self.apparatus.findDevice({'descriptors': 'system'})
        
        # Retrieving information from apparatus

        # Getting necessary eprocs
        capture = self.apparatus.GetEproc(cname, 'Measure')
        dwell = self.apparatus.GetEproc(systemname, 'Dwell')

        # Assign apparatus addresses to procedures
        
        
        # Doing stuff
        dwell.Do({'dtime':stime})
        capture.Do({'file':file})

class Capture_ImageXY(procedure): 
    def Prepare(self):
        self.name = 'Capture_ImageXY'
        self.requirements['point'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'XY point to measure relative to start'}
        self.requirements['file'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'path to store image'}
        self.requirements['camera_name'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of the camera to be used'}
        self.move = Procedures_Motion.RefRelLinearMotion(self.apparatus, self.executor)
        self.motionset = Procedures_A3200.A3200SetMotonType(self.apparatus, self.executor)
        self.pmove = Procedures_Motion.RefRelPriorityLineMotion(self.apparatus, self.executor)
        self.measure = Capture_Image(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful pieces of informaiton
        point = self.requirements['point']['value']
        file = self.requirements['file']['value']
        cname = self.requirements['camera_name']['value']
        
        # Retreiving necessary device names
        motionname = self.apparatus.findDevice({'descriptors': 'motion'})
        
        # Retrieving information from apparatus
        zaxis = self.apparatus.getValue(['devices', motionname, cname, 'axismask'])['Z']

        # Getting necessary eprocs
        runmove = self.apparatus.GetEproc(motionname, 'Run')

        # Assign apparatus addresses to procedures
        self.move.requirements['speed']['address'] = ['devices',motionname, 'default', 'speed']
        self.move.requirements['axismask']['address'] = ['devices', motionname, cname, 'axismask']
        self.move.requirements['refpoint']['address'] = ['information', 'alignments', 'safe'+zaxis]

        self.measure.requirements['settle_time']['address']=['devices', cname, 'settle_time']

        self.pmove.requirements['speed']['address'] = ['devices',motionname, 'default', 'speed']
        self.pmove.requirements['axismask']['address'] = ['devices', motionname, cname, 'axismask']
        self.pmove.requirements['refpoint']['address'] = ['information', 'alignments', cname + '@start']
        
        # Doing stuff
        self.motionset.Do({'Type': 'default'})
        self.move.Do()
        self.pmove.Do({'relpoint': {'X': point['X'], 'Y': point['Y']}, 'priority': [['X', 'Y'],['Z']]})
        runmove.Do()
        self.measure.Do({'file': file, 'camera_name': cname})
        
class Configure_Settings(procedure): 
    def Prepare(self):
        self.name = 'Configure_Settings'
        self.requirements['camera_name'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of the camera to be used'}
        self.requirements['gain'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'values for master and RGB gains (0-100)'}
        
        
    def Plan(self):
        # Renaming useful pieces of informaiton
        cname = self.requirements['camera_name']['value']
        gain = self.requirements['gain']['value']

        # Getting necessary eprocs
        configure = self.apparatus.GetEproc(cname, 'Configure')
        
        # Doing stuff
        configure.Do({'gain': gain, 'camera_name': cname})
        