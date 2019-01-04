from Procedure import procedure
import Procedures_Motion
import Procedures_Parses

class Generate_Toolpath(procedure):
    def Prepare(self):
        self.name = 'Generate_Toolpath'
        self.requirements['parameters']={'source':'apparatus', 'address':'', 'value':'', 'desc':'parameters used to generate toolpath'}
        self.requirements['generator']={'source':'apparatus', 'address':'', 'value':'', 'desc':'pointer to generator'}
        self.requirements['target']={'source':'apparatus', 'address':'', 'value':'', 'desc':'where to store the toolpath'}
        self.requirements['parameters']['address']=['information','toolpaths','parameters']
        self.requirements['generator']['address']=['information','toolpaths','generator']
        self.requirements['target']['address']=['information','toolpaths','toolpath']
        self.printTP = Plot_Toolpath(self.apparatus, self.executor)
    
    def Plan(self):
        parameters = self.requirements['parameters']['value']
        generator = self.requirements['generator']['value']
        target = self.requirements['target']['value']        
        
        systemname = self.apparatus.findDevice({'descriptors':'system'})
        
        runprog = self.apparatus.GetEproc(systemname, 'Run')
        
        runprog.Do({'address':generator, 'addresstype':'pointer', 'arguments':[parameters, target]})
        self.printTP.Do({'newfigure': True})
        
class Print_Toolpath(procedure):
  
    def Prepare(self):
        self.name = 'Print_Toolpath'
        self.requirements['toolpath'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'toolpath to be printed'}
        self.move = Procedures_Motion.RefRelLinearMotion(self.apparatus, self.executor)
        self.start = Procedures_Parses.Start(self.apparatus, self.executor)
        self.startmotion = Procedures_Parses.StartofMotion(self.apparatus, self.executor)
        self.endmotion = Procedures_Parses.EndofMotion(self.apparatus, self.executor)
        self.changemat = Procedures_Parses.ChangeMat(self.apparatus, self.executor)
        self.endoflayer = Procedures_Parses.EndofLayer(self.apparatus, self.executor)
        self.end = Procedures_Parses.End(self.apparatus, self.executor)

          
    
    def Plan(self):
        #Renaming useful pieces of informaiton
        toolpath = self.requirements['toolpath']['value'][0]

        #Retreiving necessary device names
        
        #Getting necessary eprocs
        
        #Assign apparatus addresses to procedures
        
        #Doing stuff
        for line in toolpath:
            if 'parse' in line:
                if line['parse']=='start':
                    self.start.Do()
                if line['parse']=='startofmotion':
                    self.startmotion.Do({'motion':line['motion']})
                if line['parse']=='endofmotion':
                    self.endmotion.Do({'motion':line['motion']})
                if line['parse']=='changemat':
                    self.changemat.Do({'startmotion':line['startmotion'],'endmotion':line['endmotion']})
                if line['parse']=='endoflayer':
                    self.endoflayer.Do({'layernumber':line['number']})
                if line['parse']=='end':
                    self.end.Do()
            else:
                motionname = self.apparatus.findDevice({'descriptors': 'motion' })
                nozzlename = self.apparatus.findDevice({'descriptors':['nozzle', line['material']] })
                refpoint = self.apparatus['information']['alignments'][nozzlename+'@start']
                speed = self.apparatus['devices'][motionname][nozzlename]['speed']
                axismask = self.apparatus['devices'][motionname][nozzlename]['axismask']
                self.move.Do({'refpoint':refpoint,'relpoint':line['endpoint'], 'speed':speed, 'axismask':axismask})

class Plot_Toolpath(procedure):
    def Prepare(self):
        self.name = 'Plot_Toolpath'
        self.requirements['parameters'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'parameters used to generate toolpath'}
        self.requirements['target'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'where to store the toolpath'}
        self.requirements['newfigure'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'Make a new figure?'}
        self.requirements['parameters']['address'] = ['information', 'toolpaths', 'parameters']
        self.requirements['target']['address'] = ['information', 'toolpaths', 'toolpath']
        

    def Plan(self):
        materials = self.requirements['parameters']['value']['materials']
        paths = self.requirements['target']['value'][0]
        newfigure = self.requirements['newfigure']['value']
    
        # Assumes toolpath is a standard toolpath structure 2D or 3D
        # is of form [identifier, color designator, line style designator, linewidth, alpha]
        import matplotlib.pyplot as plt
        import time
        #Determine toolpath dimension
        dim = 0
        n = 0
        while dim == 0:
            if n > len(paths)-1:
                dim = 'none'
            else:
                linekeys = str(paths[n].keys())
                if 'startpoint' in linekeys:
                    dim = len(paths[n]['startpoint'])
                n += 1
        # Fail out if nothing is a recognized motion
        if dim == 'none':
            return 'No motions'
        # Create a new figure of appropriate dimensions
        if newfigure:
            if dim == 2:
                plt.figure()
            if dim == 3:
                plt.figure().add_subplot(111, projection='3d')
        # Go line by line in toolpath and plot it with the formatting from 'materials'
        for line in paths:
            linekeys = str(line.keys())
            if 'startpoint' in linekeys:
                #get formatting
                for material in materials:
                    if line['material'] == material['material']:
                        # 'color': colorcode, 'linestyle': lscode, 'linewidth': linewdith, 'alpha':alphavalue}
                        gcolor = material['color']
                        gls = material['linestyle']
                        gwidth = material['linewidth']
                        galpha = material['alpha']
                        if dim == 2:
                            tempx = [line['startpoint']['X'],line['endpoint']['X']]
                            tempy = [line['startpoint']['Y'],line['endpoint']['Y']]
                            plt.plot(tempx, tempy, color=gcolor, ls=gls, linewidth=gwidth, alpha =galpha)
                        if dim == 3:
                            tempx = [line['startpoint']['X'],line['endpoint']['X']]
                            tempy = [line['startpoint']['Y'],line['endpoint']['Y']]
                            tempz = [line['startpoint']['Z'],line['endpoint']['Z']]               
                            plt.plot(tempx, tempy, tempz, color=gcolor, ls=gls, linewidth=gwidth, alpha =galpha)
        logimagefilename = 'Logs/' + str(int(round(time.time(), 0))) + 'image.png'
        plt.savefig(logimagefilename, dpi=600)
        plt.close()
        plt.clf()