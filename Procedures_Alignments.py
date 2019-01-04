#These procedures handle manual alignment where the user can move the printer to specific alignment points.
#It assumes that the printer has the ability to report its position

from Procedure import procedure
import Procedures_Motion
import json
import time


class Align(procedure):
    def Prepare(self):
        self.name = 'Align'
        self.requirements['Measured_List']={'source':'apparatus', 'address':['information','alignmentnames'], 'value':'', 'desc':'parameters used to generate toolpath'}
        self.requirements['primenoz']={'source':'apparatus', 'address':'', 'value':'', 'desc':'prime material'}
        self.requirements['filename']={'source':'apparatus', 'address':'', 'value':'', 'desc':'name of alignmentfile'}
        self.requirements['filename']['address']=['information','alignmentsfile']
        self.updatealign = UpdateAlignment(self.apparatus, self.executor)
        self.derivealign = DeriveAlignments(self.apparatus, self.executor)
    
    def Plan(self):
        measuredlist = self.requirements['Measured_List']['value']
        primenoz = self.requirements['primenoz']['value']
        filename = self.requirements['filename']['value']
        
        # Doing stuff
        
        # Check for loading file
        alignmentscollected = False
        doalignment = input('Import alignments from file?([y]/n/filename)')
        if doalignment in ['y', 'Y', 'yes', 'Yes', 'YES', '']:
            afilename = input('What filename?([' + filename + '])')
            if afilename == '':
                afilename = filename
            try:
                with open(filename, 'r') as TPjson:
                    self.apparatus['information']['alignments'] = json.load(TPjson)
                alignmentscollected = True
            except FileNotFoundError:
                print('No file loaded.  Possible error in ' + afilename)
        
        # If alignments were not collected from a file, collect them directly
        if not alignmentscollected:
            for alignment in measuredlist:
                self.updatealign.Do({'alignmentname':alignment})
        
        # Check if any alignments need to be redone
        alignmentsOK = False
        while not alignmentsOK:
            redoalignments = input('Would you like to redo any alignments?(y/[n])')
            if redoalignments in ['y', 'Y', 'yes', 'Yes', 'YES']:
                namestring = ''
                for name in measuredlist:
                    namestring += name + ' '
                which_alignment = input('Which alignment would you like to redo? (pick from list below)\n'+namestring)
                if which_alignment in measuredlist:
                    self.updatealign.Do({'alignmentname': which_alignment})
                else:
                    print('Alignment is not in list.')
            else:
                alignmentsOK = True

        # Use the measured alignments to derive the remaining needed alignments
        self.derivealign.Do({'Measured_List': measuredlist, 'primenoz': primenoz})

        # Save a copy of the alignments to the main folder and to the log folder
        with open(filename, 'w') as TPjson:
            json.dump(self.apparatus['information']['alignments'], TPjson)

        with open('Logs/'+str(int(round(time.time(), 0)))+filename, 'w') as TPjson:
            json.dump(self.apparatus['information']['alignments'], TPjson)


class UpdateAlignment(procedure):
    def Prepare(self):
        self.name = 'GetAlignment'
        self.requirements['alignmentname'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'parameters used to generate toolpath'}

    def Plan(self):
        alignmentname = self.requirements['alignmentname']['value']
        alignment = self.apparatus['information']['alignments'][alignmentname]

        motionname = self.apparatus.findDevice({'descriptors': 'motion'})

        getpostion = self.apparatus.GetEproc(motionname, 'getPosition')
        
        #Doing stuff
        input('Move to ' + alignmentname + ',and press ENTER when there.')
        dimlist = list(alignment)
        if self.apparatus.simulation:
            tempposition = input('What is the simulated value of the form ' + str(dimlist) + '?')
            tempposition = tempposition.replace('[','')
            tempposition = tempposition.replace(']','')
            tempposition = tempposition.split(',')
            tempposition = [float(x) for x in tempposition]   
        else:
            datavessel = [0]
            getpostion.Do({'addresstype':'pointer','address':datavessel, 'axislist':dimlist})
            tempposition = datavessel[0]

        n=0
        for dim in dimlist:
            alignment[dim] = tempposition[n]
            n += 1

class DeriveAlignments(procedure):
    def Prepare(self):
        self.name = 'DeriveAlignments'
        self.requirements['Measured_List']={'source':'apparatus', 'address':'', 'value':'', 'desc':'list of measurements'}
        self.requirements['primenoz']={'source':'apparatus', 'address':'', 'value':'', 'desc':'prime material'}
    
    def Plan(self):
        measuredlist = self.requirements['Measured_List']['value']
        primenoz = self.requirements['primenoz']['value']
        alignments = self.apparatus['information']['alignments']
        
        motionname = self.apparatus.findDevice({'descriptors':'motion'})
        
        toollist = [n.partition('@')[0] for n in measuredlist]
        
        #Doing stuff 
        alignments['safeZZ1'] = {'ZZ1':alignments['initial']['ZZ1']}
        alignments['safeZZ2'] = {'ZZ2':alignments['initial']['ZZ2']}
        alignments['safeZZ3'] = {'ZZ3':alignments['initial']['ZZ3']}
        alignments['safeZZ4'] = {'ZZ4':alignments['initial']['ZZ4']}
        
        toollist.remove('initial')
        
        paxismask = self.apparatus['devices'][motionname][primenoz]['axismask']
        pzaxis = 'Z'
        if 'Z' in paxismask:
            pzaxis =paxismask['Z']

        for tool in toollist:
            zaxis = 'Z'
            axismask = self.apparatus['devices'][motionname][tool]['axismask']
            if 'Z' in axismask:
                zaxis =axismask['Z']

            for name in [tool+'@start',tool+'slide@start',tool+'@cal']:
                if name not in alignments:
                    alignments[name]={}
            alignments[tool+'@start']['X']=alignments[primenoz+'@start']['X'] -(alignments[primenoz+'@mark']['X'] - alignments[tool+'@mark']['X'])
            alignments[tool+'@start']['Y']=alignments[primenoz+'@start']['Y'] -(alignments[primenoz+'@mark']['Y'] - alignments[tool+'@mark']['Y'])
            alignments[tool+'@start'][zaxis]=alignments[primenoz+'@start'][pzaxis] -(alignments[primenoz+'@mark'][pzaxis] - alignments[tool+'@mark'][zaxis])
            alignments[tool+'slide@start'] = alignments[tool+'@start']
            alignments[tool+'@cal']['X']=alignments[primenoz+'@cal']['X'] -(alignments[primenoz+'@mark']['X'] - alignments[tool+'@mark']['X'])
            alignments[tool+'@cal']['Y']=alignments[primenoz+'@cal']['Y'] -(alignments[primenoz+'@mark']['Y'] - alignments[tool+'@mark']['Y'])
            alignments[tool+'@cal'][zaxis]=alignments[primenoz+'@cal'][pzaxis] -(alignments[primenoz+'@mark'][pzaxis] - alignments[tool+'@mark'][zaxis])
            
def PrintAlignments(alignments):
    printstr = ''
    alignlist = list(alignments.keys())
    for alignment in alignlist:
        printstr = printstr + alignment + '\n'+ ' '
        dimlist = list(alignments[alignment].keys())
        for dim in dimlist:
            printstr += dim + ' ' + str(alignments[alignment][dim])
        printstr += '\n\n'
    print(printstr)
        


