from Procedure import procedure

class A3200SetMotonType(procedure):
    def Prepare(self):
        self.name = 'A3200SetMotonType'
        self.requirements['Type']={'source':'apparatus', 'address':'', 'value':'', 'desc':'name of the full description of A3200 movement stored under the motion devices in the apparatus'}

    def Plan(self):
        motionname = self.apparatus.findDevice({'type': 'A3200Dev'})
        setmotion = self.apparatus.GetEproc(motionname, 'Set_Motion')
        settinglist = {}
        if not self.requirements['Type']['value'] in self.apparatus['devices'][motionname]:
            raise Exception(str(self.requirements['Type']['value']) + ' not found under ' + motionname)
        for req in setmotion.requirements:
            if req in self.apparatus['devices'][motionname][self.requirements['Type']['value']]:
                settinglist[req]=self.apparatus['devices'][motionname][self.requirements['Type']['value']][req]
            
        setmotion.Do(settinglist)

