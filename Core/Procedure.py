class Procedure():
    def __init__(self, apparatus, executor, **kwargs):
        self.requirements = {}
        self.apparatus = apparatus
        self.executor = executor
        self.name = 'Undefined Name'
        #dictionary of entries for the form
        #'requirement':{'desc':'Describe the requirement', 'source':'apparatus' or 'direct', 'value':14 or '', 'address'= ApparatusAdress }
        self.Prepare(**kwargs)
        
    def Prepare(self, **kwargs):
        #Set up the requirements
        #Initialize the procedures that make up this procedure
        #Propigate any information necessary for set up of this proceedure
        pass
    
    def Plan(self):
        #Get the procedures that you want
        pass

    def Do(self, values={}):
        self.GetRequirements(values)
        #self.CheckRequirements()
        self.Report(string='start')
        self.Report()
        self.Plan()
        self.Report(string='end')

    def Report(self, string=''):
        if string=='':
            self.apparatus.LogProc(self.name, self.requirements)
        else:
            self.apparatus.LogProc(self.name, string)
            
    def GetRequirements(self, values):
        #Fills in the the requirements from the apparatus and given values
        #Given values override apparatus values
        #Once set, values are held until changed
        
        #Handle apparatus values
        for req in self.requirements:
            if self.requirements[req]['source']=='apparatus':
                tempvalue = self.apparatus.getValue(self.requirements[req]['address'])
                if tempvalue!='Invalid ApparatusAddress':
                    self.requirements[req]['value']=tempvalue
                else:
                    raise Exception('ApparatusAddress ' + str(self.requirements[req]['address']) + ' was not found.')
        
        for value in values:
            if value in self.requirements:
                self.requirements[value]['value']=values[value]
    
    def CheckRequirements(self):
        Reqs_Met = True
        UnmetReqs = []
        for req in self.requirements:
            #print (req)
            if self.requirements[req]['value']=='':
                UnmetReqs.append(req)
                Reqs_Met = False
        
        if not Reqs_Met:
            raise Exception('Requirements ' + str(UnmetReqs) + ' where not met.')
        
    def GetDetails(self):
        details = {}
        for req in self.requirements:
            details[req] = self.requirements[req]['value']
        return details




