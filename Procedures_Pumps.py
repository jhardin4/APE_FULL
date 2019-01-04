from Procedure import procedure

class PumpOn(procedure):
    def Prepare(self):
        self.name = 'PumpOn'
        self.requirements['mid_time']={'source':'apparatus', 'address':'', 'value':'', 'desc':'time to allow things to settle'}
        self.requirements['pumpon_time']={'source':'apparatus', 'address':'','value':'', 'desc':'Point relative to reference position'}
        self.requirements['name']={'source':'apparatus', 'address':'','value':'', 'desc':'name of the pump'}
    
    def Plan(self):
        pumpname = self.requirements['name']['value']
        pumpon = self.apparatus.GetEproc(pumpname, 'On')
        systemname = self.apparatus.findDevice({'descriptors':'system'})
        systemdwell = self.apparatus.GetEproc(systemname, 'Dwell')
        
        mid_time = self.requirements['mid_time']['value']
        pumpon_time = self.requirements['pumpon_time']['value']
        
        systemdwell.Do({'dtime':mid_time})
        pumpon.Do()
        systemdwell.Do({'dtime':pumpon_time})
        
class PumpOff(procedure):
    def Prepare(self):
        self.name = 'PumpOff'
        self.requirements['mid_time']={'source':'apparatus', 'address':'', 'value':'', 'desc':'time to allow things to settle'}
        self.requirements['pumpoff_time']={'source':'apparatus', 'address':'','value':'', 'desc':'Point relative to reference position'}
        self.requirements['name']={'source':'apparatus', 'address':'','value':'', 'desc':'name of the pump'}
    
    def Plan(self):
        pumpname = self.requirements['name']['value']
        pumpoff = self.apparatus.GetEproc(pumpname, 'Off')
        systemname = self.apparatus.findDevice({'descriptors':'system'})
        systemdwell = self.apparatus.GetEproc(systemname, 'Dwell')
        
        mid_time = self.requirements['mid_time']['value']
        pumpoff_time = self.requirements['pumpoff_time']['value']
        
        systemdwell.Do({'dtime':pumpoff_time})
        pumpoff.Do()
        systemdwell.Do({'dtime':mid_time})