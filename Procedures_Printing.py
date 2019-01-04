from Procedure import procedure
import Procedures_Motion
import Procedures_Pumps

class PrintLine(procedure):
    def Prepare(self):
        self.name = 'PrintLine'
        self.requirements['startpoint']={'source':'apparatus', 'address':'', 'value':'', 'desc':'Reference point'}
        self.requirements['endpoint']={'source':'apparatus', 'address':'','value':'', 'desc':'Point relative to reference position'}
        self.requirements['material']={'source':'apparatus', 'address':'','value':'', 'desc':'material to be printed'}
        self.testmove = Procedures_Motion.RefRelLinearMotion(self.apparatus, self.executor)
        self.testpumpon = Procedures_Pumps.PumpOn(self.apparatus, self.executor)
        self.testpumpoff = Procedures_Pumps.PumpOff(self.apparatus, self.executor)         
    
    def Plan(self):
        pumpname = self.apparatus.findDevice({'descriptors':['pump',self.requirements['material']['value']] })
        motionname = self.apparatus.findDevice({'descriptors':'motion'})
        runmove = self.apparatus.GetEproc(motionname, 'Run')
        
        self.testmove.Do({'relpoint':self.requirements['startpoint']['value'], 'refpoint':self.apparatus['information']['alignments']['startpoint'], 'speed':10})
        runmove.Do()
        self.testpumpon.Do({'mid_time':1, 'pumpon_time':2, 'name':pumpname})
        
        self.testmove.Do({'relpoint':self.requirements['endpoint']['value'], 'refpoint':self.apparatus['information']['alignments']['startpoint'], 'speed':10})
        runmove.Do()
        self.testpumpoff.Do({'mid_time':1, 'pumpoff_time':3, 'name':pumpname})
        

        