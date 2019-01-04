'''
These procedures are related to calibrating the ink extrusion rate and the
pump timing using a fairly simple and robust conversion from mass extrution
rate to volumetric extrusion rate to speed from target trace geometry.

'''

from Procedure import procedure
import time
import json
import Procedures_Motion
import Procedures_Pumps


class Calibrate(procedure):
    def Prepare(self):
        self.name = 'Calibrate'
        self.requirements['material'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'parameters used to generate toolpath'}
        self.requirements['filename'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of alignmentfile'}
        self.requirements['filename']['address'] = ['information', 'calibrationfile']
        self.cal_calculation = Cal_Calulation(self.apparatus, self.executor)
        self.cal_measurement = Cal_Measurement(self.apparatus, self.executor)

    def Plan(self):
        material = self.requirements['material']['value']
        filename = self.requirements['filename']['value']

        # Do stuff
        # Handle the first call of a calibration on a particular material
        # This involves choosing to calibrate or not and whether to make a new file
        if not self.apparatus['information']['materials'][material]['calibrated']:
            usecal = input('Would you like to use ink calibraton for ' + material + '?([y],n)')
            if usecal in ['Y', 'y', 'yes', 'Yes', '']:
                self.apparatus['information']['materials'][material]['calibrated'] = True
                newfile = input('Would you like to make a new file for ' + material + '?(y,[n])')
                if newfile in ['Y', 'y', 'yes', 'Yes']:
                    # Clear existing file
                    cfilename = material + filename
                    tempfile = open(cfilename, mode='w')
                    json.dump([], tempfile)
                    tempfile.close()
                    self.cal_measurement.Do({'material': material})
                else:
                    newdata = input('Would you like to make new measurement of ' + material + '?(y,[n])')
                    if newdata in ['Y', 'y', 'yes', 'Yes']:
                        self.cal_measurement.Do({'material': material})
                    else:
                        self.cal_calculation.Do({'material': material})

        else:
            self.cal_measurement.Do({'material': material})




class Cal_Measurement(procedure):
    def Prepare(self):
        self.name = 'Cal_Measurement'
        self.requirements['material'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'parameters used to generate toolpath'}
        self.requirements['filename'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of alignmentfile'}
        self.requirements['filename']['address'] = ['information', 'calibrationfile']
        self.pmotion = Procedures_Motion.RefRelPriorityLineMotion(self.apparatus, self.executor)
        self.pumpon = Procedures_Pumps.PumpOn(self.apparatus, self.executor)
        self.pumpoff = Procedures_Pumps.PumpOff(self.apparatus, self.executor)

    def Plan(self):
        # Reassignments for convienence
        material = self.requirements['material']['value']
        filename = self.requirements['filename']['value']

        # FIND devices needed for procedure
        motion = self.apparatus.findDevice({'descriptors': ['motion']})
        system = self.apparatus.findDevice({'descriptors': ['system']})
        nozzle = self.apparatus.findDevice({'descriptors': ['nozzle', material]})
        pump = self.apparatus.findDevice({'descriptors': ['pump', material]})

        #Find elemental procedures
        run = self.apparatus.GetEproc(motion, 'Run')
        dwell = self.apparatus.GetEproc(system, 'Dwell')
        pumpset = self.apparatus.GetEproc(pump, 'Set')
        
        self.pmotion.requirements['axismask']['address'] = ['devices', motion, 'n'+material, 'axismask']
        self.pmotion.requirements['refpoint']['address'] = ['information', 'alignments', 'n'+material+'@cal']
        self.pmotion.requirements['speed']['address'] = ['devices', motion, 'default', 'speed']

        # Do stuff
        # Go to calibration position
        self.pmotion.Do({'priority': [['Z'], ['X', 'Y']]})
        run.Do()

        # Get intial information
        initialweightok = False
        while not initialweightok:
            initialweightstr = input('What is the initial weight of the slide in grams?')
            try:
                initialweight = float(initialweightstr)
                qtext = 'Is ' + initialweightstr + 'g the correct value?(y/n)'
                confirmation = input(qtext)
                if confirmation == 'y':
                    initialweightok = True
            except ValueError:
                print('That is not a number.  Try again.')
        input('Put slide in place and press ENTER.')

        # turn pumps on and off
        ptime = self.apparatus['information']['ink calibration']['time']
        pumpset.requirements['pressure']['address'] = ['devices', pump, 'pressure']
        pumpset.Do()
        self.pumpon.Do({'name': pump})
        dwell.Do({'dtime': ptime})
        self.pumpoff.Do({'name': pump})

        finalweightok = False
        while not finalweightok:
            finalweightstr = input('What is the final weight of the slide in grams?')
            try:
                finalweight = float(finalweightstr)
                qtext = 'Is ' + str(finalweightstr + 'g the correct value?(y/n)')
                confirmation = input(qtext)
                if confirmation == 'y':
                    finalweightok = True
            except ValueError:
                print('That is not a number.  Try again.')

        # Construct the data entry for the calibration log
        dataline = {'delta_weight': finalweight-initialweight, 'test_time': ptime, 'time': time.time()}
        cfilename = material + filename
        # Load in the previous file
        with open(cfilename, 'r') as caljson:
            file_data = json.load(caljson)
        file_data.append(dataline)
        # Store the updated data
        with open(cfilename, 'w') as caljson:
            json.dump(file_data, caljson)
        with open('Logs/' + str(int(round(time.time(), 0))) + cfilename, 'w') as caljson:
            json.dump(file_data, caljson)


class Cal_Calulation(procedure):
    def Prepare(self):
        self.name = 'Cal_Calulation'
        self.requirements['material'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'parameters used to generate toolpath'}
        self.requirements['filename'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of alignmentfile'}
        self.requirements['filename']['address'] = ['information', 'calibrationfile']
        self.pmotion = Procedures_Motion.RefRelPriorityLineMotion(self.apparatus, self.executor)
        self.pumpon = Procedures_Pumps.PumpOn(self.apparatus, self.executor)
        self.pumpoff = Procedures_Pumps.PumpOff(self.apparatus, self.executor)

    def Plan(self):
        # Reassignments for convienence
        material = self.requirements['material']['value']
        filename = self.requirements['filename']['value']
        cfilename = material + filename

        motion = self.apparatus.findDevice({'descriptors': ['motion']})
        nozzle = self.apparatus.findDevice({'descriptors': ['nozzle', material]})
        pump = self.apparatus.findDevice({'descriptors': ['pump', material]})

        do_pumpcal = self.apparatus.getValue(['information', 'materials', material, 'do_pumpcal'])
        do_speedcal = self.apparatus.getValue(['information', 'materials', material, 'do_speedcal'])
        density = self.apparatus.getValue(['information', 'materials', material, 'density'])
        trace_width = self.apparatus.getValue(['devices', nozzle, 'trace_width'])
        trace_height = self.apparatus.getValue(['devices', nozzle, 'trace_height'])
        pumpres_time = self.apparatus.getValue(['devices', pump, 'pumpres_time'])

        with open(cfilename, 'r') as caljson:
            file_data = json.load(caljson)

        if len(file_data) == 1:
            dweight = float(file_data[0]['delta_weight'])
            exvolume = dweight / density * 1000  # mm^3
            vexrate = exvolume / file_data[0]['test_time']  # mm^3/s
            crossarea = trace_width * trace_height  # mm^2
            targetspeed = vexrate/crossarea  # m/s
        else:
            initial_time = float(file_data[len(file_data) - 2]['time'])
            final_time = float(file_data[len(file_data) - 1]['time'])
            initial_dweight = float(file_data[len(file_data) - 2]['delta_weight'])
            final_dweight = float(file_data[len(file_data) - 1]['delta_weight'])
            cur_time = time.time()
            # Assume linear change in viscosity with time
            proj_dweight = (cur_time - initial_time) / (final_time - initial_time) * (final_dweight - initial_dweight) + initial_dweight
            # Continue with calculations
            exvolume = proj_dweight / density * 1000  # mm^3
            vexrate = exvolume / file_data[0]['test_time']  # mm^3/s
            crossarea = trace_width * trace_height  # mm^2
            targetspeed = vexrate/crossarea  # m/s            
        if do_speedcal:
            self.apparatus['devices'][motion][nozzle]['speed'] = targetspeed
        if do_pumpcal:
            self.apparatus['devices'][pump]['pumpon_time'] = pumpres_time + 1.5*trace_height / targetspeed