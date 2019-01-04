import Procedure
import time


# Parent class of all devices bleh
class Device():
    def __init__(self, name):
        self.simulation = False
        self.connected = False
        self.name = name
        self.on = False
        self.descriptors = []
        self.driver_address = ''
        self.addresstype = 'pointer'
        self.procaddresstype = 'pointer'
        self.send_addresstype = 'direct'
        self.dependent_device = False
        self.requirements = {}
        self.log = ''

        # Description of methods that will be treated as elemental procedures
        self.requirements['On'] = {}
        self.requirements['Off'] = {}
        self.requirements['Set'] = {}
        self.requirements['Connect'] = {}
        self.requirements['Disconnect'] = {}

    def On(self):
        self.addlog(self.name + ' on')

        return self.returnlog()

    def Off(self):
        self.addlog(self.name + ' off')

        return self.returnlog()

    def Set(self):
        self.addlog(self.name + ' set')

        return self.returnlog()

    def CreateEprocs(self, apparatus, executor):
        for eleproc in self.requirements:
            eprocEntry = {'device': self.name,
                          'method': eleproc,
                          'handle': Procedure.eproc(apparatus, executor, self.name, eleproc, self.requirements[eleproc])}
            apparatus['eproclist'].append(eprocEntry)

    def returnlog(self):
        message = self.log
        self.log = ''

        return message

    def addlog(self, logstr):
        self.log += logstr + '\n'

    def ERegister(self, executer):
        executer.loadDevice(self.name, self, 'pointer')

    def Connect(self):
        self.addlog(self.name + ' is connected.')

        return self.returnlog()

    def Disconnect(self):
        self.addlog(self.name + ' is disconnected.')

        return self.returnlog()


class System(Device):
    def __init__(self, name):
        Device.__init__(self,name)

        self.descriptors.append('system')

        self.requirements['Dwell'] = {}
        self.requirements['Dwell']['dtime'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'time to wait in seconds'}

        self.requirements['Run'] = {}
        self.requirements['Run']['address'] = {'value': '', 'source': 'direct', 'address': '', 'desc': 'address of the program or pointer to it'}
        self.requirements['Run']['addresstype'] = {'value': '', 'source': 'direct', 'address': '', 'desc': 'type of address'}
        self.requirements['Run']['arguments'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'list of the arguments for the program in order. Will be decomposed with * operator'}

    def Set(self, pressure=''):
        self.pressure = pressure
        self.log = self.name + ' set to ' + self.pressure

        return self.returnlog()

    def Dwell(self, dtime=''):
        if not self.simulation and dtime != '':
            time.sleep(dtime)
        self.log = self.name + ' waited ' + str(dtime) + ' s.'

        return self.returnlog()

    def Run(self, address='', addresstype='pointer', arguments=[]):
        if addresstype == 'pointer':
            address(*arguments)
        self.log = self.name + ' ran a program'

        return self.returnlog()


class Motion(Device):
    def __init__(self, name):
        Device.__init__(self, name)

        self.descriptors.append('motion')

        self.commandlog = []
        self.motiontype = 'linear'
        self.motionmode = 'loadrun'
        self.axes = ['X', 'x', 'Y', 'y', 'Z', 'z']
        self.motionsetting = {}

        self.requirements['Move'] = {}
        self.requirements['Move']['point'] = {'value': '', 'source': 'apparatus', 'address': '',
                                              'desc': 'Dictionary with the motions sytem axes as keys and target values'}
        self.requirements['Move']['speed'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'speed of motion, typicaly in mm/s'}
        self.requirements['Move']['motiontype'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'speed of motion, typicaly in mm/s'}
        self.requirements['Move']['motionmode'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'cmd or loadrun'}

        self.requirements['Set_Motion'] = {}
        self.requirements['Set_Motion']['RelAbs'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Relative or Absolute motion'}
        self.requirements['Set_Motion']['dmotionmode'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'default motion mode'}
        self.requirements['Set_Motion']['dmotiontype'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'default motion type'}
        self.requirements['Set_Motion']['motionmode'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'cmd or loadrun'}

    def Move(self, point={}, speed=0, motiontype='', motionmode=''):
        self.commandlog.append(self.MotionCMD(point, speed, motiontype))
        self.fRun(motionmode)

        return self.returnlog()

    def Set_Motion(self, RelAbs='', dmotionmode='', dmotiontype='', motionmode=''):
        if dmotionmode != '':
            self.motionmode = dmotionmode
            self.motionsettings['motionmode'] = dmotionmode

        if dmotiontype != '':
            self.motiontype = dmotiontype
            self.motionsettings['motiontype'] = dmotiontype

        if RelAbs != '':
            self.fSet_RelAbs(RelAbs, motionmode)

        return self.returnlog()

    def fSet_RelAbs(self, RelAbs, motionmode):
        if RelAbs == 'Rel':
            self.commandlog.append('G91 \n')

        if RelAbs == 'Abs':
            self.commandlog.append('G90 \n')

        self.motionsettings['RelAbs'] = RelAbs
        self.fRun(motionmode)

    def MotionCMD(self, point, speed, motiontype):
        if motiontype == '':
            motiontype = self.motiontype
        cmdline = ''
        if motiontype == 'linear':
            cmdline += 'G01 '
            for axis in self.axes:
                if axis in point:
                    cmdline += axis + ' ' + '{0:f}'.format(point[axis]) + ' '
            cmdline += 'F ' + '{0:f}'.format(speed) + ' '
            cmdline += '\n'

        return cmdline

    def Run(self, motionmode=''):
        if motionmode == '':
            motionmode = 'cmd'
        self.fRun(motionmode)
        return self.returnlog()

    def fRun(self, motionmode):
        if motionmode == '':
            motionmode = self.motionmode
        if motionmode == 'loadrun':
            self.addlog('Commands Loaded')
        elif motionmode == 'cmd':
            cmdline = self.commandlog
            self.sendCommands(cmdline)
            self.commandlog = []

    def sendCommands(self, commands):
        message = ''

        for line in commands:
            message += line

        self.addlog(message)


class Sensor(Device):
    def __init__(self, name):
        Device.__init__(self, name)
        self.returnformat = ''
        self.result = ''

    def StoreMeasurement(self, address, addresstype, result):
        if addresstype == 'pointer':
            # this assumes that address=[0] exists when this method is used.
            address[0] = result

    def Measure(self, address='', addresstype=''):
        pass

    def Sensor_Calibrate():
        pass


class A3200Dev(Motion, Sensor):
    def __init__(self, name):
        Motion.__init__(self, name)

        self.descriptors = [*self.descriptors,
                            *['Aerotech', 'A3200', 'sensor']]

        self.tasklog = {'task1': [], 'task2': [], 'task3': [], 'task4': []}
        self.commandlog = []
        self.defaulttask = 1
        self.handle = ''

        # Possible modes are cmd and loadrun
        self.axes = ['X', 'x', 'Y', 'y',
                     'ZZ1', 'zz1', 'ZZ2', 'zz2', 'ZZ3', 'zz3', 'ZZ4', 'zz4',
                     'i', 'I', 'j', 'J', 'k', 'K']
        self.axismask = {}
        self.maxaxis = 4

        self.requirements['Set_Motion']['task'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'task being used for this operation'}
        self.requirements['Set_Motion']['length_units'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'length units for motion'}
        self.requirements['Set_Motion']['MotionRamp'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Ramp rate for a set of coordinated motions'}
        self.requirements['Set_Motion']['MaxAccel'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Maximum acceleration during coordinated motion'}
        self.requirements['Set_Motion']['LookAhead'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Activate multi-command motion planning'}
        self.requirements['Set_Motion']['axismask'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'how to convert between target and machine dimensions'}
        self.requirements['Set_Motion']['dtask'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'default task'}

        self.requirements['Move'] = {}
        self.requirements['Move']['point'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Information about where to move to'}
        self.requirements['Move']['motiontype'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'kind of path taken to point'}
        self.requirements['Move']['speed'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'speed of the motion'}
        self.requirements['Move']['task'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'task being used for this operation'}
        self.requirements['Move']['motionmode'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'cmd or loadrun to determine if it si stored in a buffer, commandlog, or run immediately'}

        self.requirements['set_DO'] = {}
        self.requirements['set_DO']['axis'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'IO axis'}
        self.requirements['set_DO']['bit'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'bit on IO axis'}
        self.requirements['set_DO']['value'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'value of that bit.  0 or 1'}

        self.requirements['Run'] = {}
        self.requirements['Run']['task'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Which task buffer to run'}

        self.requirements['getPosition'] = {}
        self.requirements['getPosition']['address'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Address of where to store result'}
        self.requirements['getPosition']['addresstype'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Type of address'}
        self.requirements['getPosition']['axislist'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'List of axes that will be reported'}

        self.requirements['getAI'] = {}
        self.requirements['getAI']['address'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Address of where to store result'}
        self.requirements['getAI']['addresstype'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Type of address'}
        self.requirements['getAI']['axis'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Axis of AI'}
        self.requirements['getAI']['channel'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Channel on that axis'}

        self.requirements['Load'] = {}
        self.requirements['Load']['cmstr'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'String of commands to load'}
        self.requirements['Load']['task'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'task being used for this operation'}
        self.requirements['Load']['mode'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'cmd or loadrun to determine if it si stored in a buffer, commandlog, or run immediately'}

        self.requirements['LogData_Start'] = {}
        self.requirements['LogData_Start']['file'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Where to store results'}
        self.requirements['LogData_Start']['points'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Maximum number of points to collect'}
        self.requirements['LogData_Start']['parameters'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': '{axis: [pc, pf, vc, vf, ac, af]...}'}
        self.requirements['LogData_Start']['interval'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'cmd or loadrun to determine if it si stored in a buffer, commandlog, or run immediately'}
        self.requirements['LogData_Start']['task'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'task being used for this operation'}
        self.requirements['LogData_Start']['mode'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'cmd or loadrun to determine if it si stored in a buffer, commandlog, or run immediately'}

        self.requirements['LogData_Stop'] = {}
        self.requirements['LogData_Stop']['task'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'task being used for this operation'}
        self.requirements['LogData_Stop']['mode'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'cmd or loadrun to determine if it si stored in a buffer, commandlog, or run immediately'}

    def Connect(self):
        if not self.simulation:
            from Drivers import A3200
            self.handle = A3200.A3200()
        self.addlog(self.name + ' is connected')

        return self.returnlog()

    def Disconnect(self):
        if not self.simulation:
            self.handle.disconnect()
        self.addlog(Device.Disconnect(self))

        return self.returnlog()

    def Set_Motion(self, dtask='', axismask='', length_units='', RelAbs='', MotionRamp='', MaxAccel='', LookAhead='', dmotionmode='', dmotiontype='', motionmode='', task=''):
        # These direct assignments are somewhat queue jumping at the moment
        if dtask != '':
            self.defaulttask = dtask

        if dmotiontype != '':
            self.motiontype = dmotiontype

        if dmotionmode != '':
            self.motionmode = dmotionmode

        if task == '':
            task = self.defaulttask

        if motionmode == '':
            motionmode = self.motiontype

        # These do not que jump
        if axismask != '':
            self.fSet_axismask(axismask, task, motionmode)

        if RelAbs != '':
            self.fSet_RelAbs(RelAbs, task, motionmode)

        if length_units != '':
            self.fSet_length_units(length_units, task, motionmode)

        if MotionRamp != '':
            self.fSet_MotionRamp(MotionRamp, task, motionmode)

        if MaxAccel != '':
            self.fSet_MaxAccel(MaxAccel, task, motionmode)

        if LookAhead != '':
            self.fSet_LookAhead(LookAhead, task, motionmode)

        return self.returnlog()

    def fSet_axismask(self, axismask, task, motionmode, update=False):
        if update:
            self.axismask = axismask
            self.addlog('Axis mask changed to ' + str(self.axismask))
        else:
            kwargs = {'axismask': axismask, 'task': task, 'motionmode': motionmode, 'update': True}
            self.tasklog['task' + str(task)].append({'function': self.fSet_axismask, 'args': kwargs})

        self.fRun(motionmode,task)

    def fSet_LookAhead(self, LookAhead, task, motionmode):
        if LookAhead:
            self.tasklog['task' + str(task)].append('VELOCITY ON \n')
        else:
            self.tasklog['task' + str(task)].append('VELOCITY OFF \n')
        self.motionsetting['LookAhead'] = LookAhead

        self.fRun(motionmode, task)

    def fSet_MaxAccel(self, MaxAccel, task, motionmode):
        self.tasklog['task' + str(task)].append('CoordinatedAccelLimit = ' + str(MaxAccel) + '\n')
        self.motionsetting['MaxAccel'] = MaxAccel
        self.fRun(motionmode, task)

    def fSet_RelAbs(self, RelAbs, task, motionmode):
        if RelAbs == 'Rel':
            self.tasklog['task' + str(task)].append('G91 \n')

        if RelAbs == 'Abs':
            self.tasklog['task' + str(task)].append('G90 \n')

        self.motionsetting['RelAbs'] = RelAbs
        self.fRun(motionmode, task)

    def fSet_MotionRamp(self, MotionRamp, task, motionmode):
        self.tasklog['task' + str(task)].append('RAMP RATE ' + str(MotionRamp) + '\n')

        self.motionsetting['MotionRamp'] = MotionRamp
        self.fRun(motionmode, task)

    def fSet_length_units(self, length_units, task, motionmode):
        if length_units == 'mm':
            self.tasklog['task' + str(task)].append('G71 \n')

        if length_units == 'inch':
            self.tasklog['task' + str(task)].append('G70 \n')

        self.motionsetting['length_units'] = length_units
        self.fRun(motionmode, task)

    def Set_DO(self, axis='', bit='', value='', task='', motionmode=''):
        if motionmode == '':
            motionmode = self.motionmode

        if task == '':
            task = self.defaulttask

        if not self.simulation:
            cmdstr = '$DO' + '['+str(bit)+'].' + axis + ' = ' + str(value) + ' \n'
            self.tasklog['task'+str(task)].append(cmdstr)
        self.addlog('Bit ' + str(bit) + ' on the ' + str(axis) + ' set to ' + str(value))

        self.fRun(motionmode, task)

        return self.returnlog()

    def Move(self, point='', motiontype='', speed='', task='', motionmode=''):
        if task == '':
            task = self.defaulttask
        self.tasklog['task' + str(task)].append({'function': self.MotionCMD, 'args': [point, speed, motiontype]})

        self.fRun(motionmode, task)

        return self.returnlog()

    def MotionCMD(self, point, speed, motiontype):
        if motiontype == '':
            motiontype = self.motiontype
        cmdline = ''

        for dim in self.axismask:
            if dim in point:
                point[self.axismask[dim]] = point[dim]
                point.pop(dim, None)

        if motiontype == 'linear':
            axescount = 0
            cmdline += 'G01 '
            for axis in self.axes:
                if axis in point:
                    axescount += 1
                    if axescount > self.maxaxis:
                        #print(cmdline)
                        raise Exception('Number of axes exceeds ITAR limit.')
                    cmdline += axis + ' ' + '{0:f}'.format(point[axis]) + ' '
            cmdline += 'F ' + '{0:f}'.format(speed) + ' '
            cmdline += '\n'
        
        if motiontype == 'incremental':
            cmdline += 'MOVEINC '
            axis = list(point)[0]
            cmdline += axis + ' ' + '{0:f}'.format(point[axis]) + ' ' + '{0:f}'.format(speed)
            cmdline += '\n'
            
        self.addlog(cmdline)

        return cmdline

    def Run(self, task=''):
        self.fRun('cmd', task)

        return self.returnlog()

    def fRun(self, motionmode, task):
        if task == '':
            task = self.defaulttask

        if motionmode == '':
            motionmode = self.motionmode
        if motionmode == 'loadrun':
            self.addlog('Commands Loaded')
        elif motionmode == 'cmd':
            self.commandlog = self.tasklog['task' + str(task)]
            self.tasklog['task' + str(task)] = []
            cmdline = self.commandlog
            self.sendCommands(cmdline, task)
            self.commandlog = []

    def getPosition(self, address='', addresstype='', axislist=''):
        # Get the postion from the driver
        if not self.simulation:
            result = self.handle.get_position(axislist)
        else:
            result = input('What are simulation values for ' + str(axislist) + '?')

        # Store it at the target location
        self.StoreMeasurement(address, addresstype, result)
        self.log += (str(axislist) + ' measured to be ' + str(result))

        return self.returnlog()

    def getAI(self, address='', addresstype='', axis='', channel=''):
        # Get the postion from the driver
        if not self.simulation:
            result = self.handle.AI(axis, channel)
        else:
            rstring = input('What is the simulated value for ' + str(axis) + ' ' + str(channel) + '?')
            result = float(rstring)

        # Store it at the target location
        self.StoreMeasurement(address, addresstype, result)
        self.log = ('AI Axis ' + str(axis) + ' channel ' + str(channel) + ' measured to be ' + str(result))

        return self.returnlog()

    def sendCommands(self, commands, task):

        cmdmessage = ''
        for line in commands:
            if type(line) == str:
                cmdmessage += line
                self.addlog(line)
            elif type(line) == dict and line['function'] == self.MotionCMD:
                cmdmessage += line['function'](*line['args'])
            elif type(line) == dict:
                line['function'](**line['args'])
        if not self.simulation:
            self.handle.cmd_exe(cmdmessage, task=task)
        
    def LogData_Start(self, file='', points='', parameters='', interval='', task='', motionmode=''):
        if task == '':
            task = self.defaulttask
        self.tasklog['task' + str(task)].append("""
                     DATACOLLECT STOP
                     DATACOLLECT ITEM RESET
                     """)
        index = 0
        for dim in parameters:
            if type(parameters[dim]) == list:
                for element in parameter[dim]:
                    temp = 'DATACOLLECT ITEM %s, %s, DATAITEM_'%(str(index), dim)
                    if element[0] == 'p':
                        temp += 'Position'
                    elif element[0] == 'v':
                        temp += 'Velocity'
                    elif element[0] == 'a':
                        temp += 'Acceleration'
                    else:
                        raise Exception(dim + str(element) + ' is an unknown parameter')
                    
                    if element[1] == 'f':
                        temp += 'Feedback'
                    elif element[1] == 'c':
                        temp += 'Command'
                    else:
                        raise Exception(dim + str(element) + ' is an unknown parameter')
                    self.tasklog['task' + str(task)].append(temp + '\n')
                    index += 1
            self.tasklog['task' + str(task)].append('$task[0] = FILEOPEN "%s" , 0\n' % (file))
            self.tasklog['task' + str(task)].append('DATACOLLECT START $task[0], %s, %s\n' % (str(points), str(interval)))
            self.fRun(motionmode, task)
            return self.returnlog()

    def LogData_Stop(self, task='', motionmode=''):
        if task == '':
            task = self.defaulttask
        self.tasklog['task' + str(task)].append("""
                     DATACOLLECT STOP
                     FILECLOSE $task[0]
                     """)
        self.fRun(motionmode, task)
        return self.returnlog()

class Pump(Device):
    def __init__(self, name):
        Device.__init__(self, name)
        self.descriptors.append('pump')
        self.requirements['Set']['pressure'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Pump pressure in kPa'}

    def Set(self, pressure=''):
        self.pressure = pressure
        self.addlog(self.name + ' set to ' + self.pressure)

        return self.returnlog()


class UltimusVDev(Pump):
    def __init__(self, name):
        Device.__init__(self, name)
        self.descriptors = [*self.descriptors,
                            *['pump', 'pressure', 'Nordson', 'Ultimus', 'UltimusV']]

        self.requirements['Connect']['COM'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Serial COM port to communcate through'}
        self.requirements['Set']['pressure'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'pressure when the pump is ON'}
        self.requirements['Set']['vacuum'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'vacuum when the pump is OFF'}

        self.pressure = 0
        self.vacuum = 0
        self.driver_address = ''

    def On(self):
        if not self.simulation:
            self.driver_address.startPump()
        self.on = True
        self.addlog(self.name + ' is on.')

        return self.returnlog()

    def Off(self):
        if not self.simulation:
            self.driver_address.stopPump()
        self.on = False
        self.addlog(self.name + ' is off.')

        return self.returnlog()

    def Connect(self, COM=''):
        if not self.simulation:
            from Drivers import Ultimus_V as UltimusV
            self.driver_address = UltimusV.Ultimus_V_Pump(COM)

        self.addlog('Ultimus ' + self.name + ' is connected on port ' + str(COM))

        return self.returnlog()

    def Set(self, pressure='', vacuum=''):
        if pressure != '':
            if not self.simulation:
                self.driver_address.set_pressure(pressure)
            self.pressure = pressure
        if vacuum != '':
            if not self.simulation:
                self.driver_address.set_vacuum(vacuum)
            self.vacuum = vacuum
        self.addlog(self.name + ' is set to ' + str(pressure) + 'kPa pressure and ' + str(vacuum) + 'kPa vacuum.')

        return self.returnlog()

    def Disconnect(self):
        if not self.simulation:
            if self.driver_address != '':
                self.driver_address.disconnect()

        self.addlog(Pump.Disconnect(self))

        return self.returnlog()


class UltimusVDev_A3200(UltimusVDev):
    def __init__(self, name):
        UltimusVDev.__init__(self, name)

        self.descriptors.append('A3200')

        self.pressure = 0
        self.vacuum = 0
        self.pumphandle = ''
        self.A3200handle = ''
        self.IOaxis = ''
        self.IObit = ''
        self.dependent_device = True
        self.defaulttask = 1
        self.dependencies = ['pump', 'A3200']

        self.requirements['Connect']['pumpname'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'name of the pump being used'}
        self.requirements['Connect']['pumpaddress'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'pointer to the pump device'}
        self.requirements['Connect']['A3200name'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'name of the A3200 controller being used'}
        self.requirements['Connect']['A3200address'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'pointer to the A3200 device'}
        self.requirements['Connect']['IOaxis'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'IO axis on A3200'}
        self.requirements['Connect']['IObit'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'bit on the IO axis being used'}

        # This entry is removed because the pump should already be connected
        self.requirements['Connect'].pop('COM', None)

    def On(self, task='', mode='cmd'):
        self.log += self.A3200handle.Set_DO(axis=self.IOaxis, bit=self.IObit, value=1, task=task, motionmode=mode)
        self.on = True
        self.addlog(self.name + ' is on.')
        return self.returnlog()

    def Off(self, task='', mode='cmd'):
        self.fOff(task, mode)
        return self.returnlog()

    def Set(self, pressure='', vacuum=''):
        self.addlog(self.pumphandle.Set(pressure=pressure, vacuum=vacuum))
        return self.returnlog()

    def fOff(self, task, mode):
        self.log += self.A3200handle.Set_DO(axis=self.IOaxis, bit=self.IObit, value=0, task=task, motionmode=mode)
        self.on = False
        self.addlog(self.name + ' is off.')

    def Connect(self, pumpname='', A3200name='', pumpaddress='', A3200address='', IOaxis = '', IObit = ''):
        self.descriptors.append(pumpname)
        self.descriptors.append(A3200name)
        self.pumphandle = pumpaddress
        self.A3200handle = A3200address
        self.IOaxis = IOaxis
        self.IObit = IObit

        self.addlog('Ultimus/A3200 ' + pumpname +
                    '/' + A3200name +
                    ' ' + self.name +
                    ' is connected using ' + str(self.IOaxis) +
                    ' bit ' + str(self.IObit))
        self.fOff(self.defaulttask, 'cmd')

        return self.returnlog()
   

class Keyence_TouchProbe(Sensor):
    def __init__(self, name):
        Sensor.__init__(self, name)
        self.returnformat=''
        self.A3200handle = ''
        self.DOaxis = '' #ZZ1
        self.DObit = '' #0
        self.AIaxis = '' #ZZ2
        self.AIchannel = '' #0
        self.axis = 'ZZ2'
        self.dependent_device = True
        self.dependencies =['A3200', 'system']
        self.extend_delay = 1
        self.extended = False
        self.def_num_points = 5

        #used during initialization, take more samples
        self.init_number = 10
        self.init_delay = 0.1
        
        #used during movement, take less samples
        self.fast_number = 3
        self.fast_delay = 0.01
        self.min_step = 0.01
        self.speed = 10
        self.step = 1 #note, bad things may happen if this gets too big
        
        #machine parameters
        self.z_window = 1
        self.v_window = 4
        self.extend_delay = 1
        self.safe_positions = dict(ZZ1 = 0, ZZ2 = 0, ZZ3 = 0, ZZ4 = 0)
        self.configured = False
        self.sampleresult = 0
        self.zresult = 0
        
        # Elemental Procedures
        self.requirements['Connect']['A3200name'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'name of the system device'}
        self.requirements['Connect']['A3200address'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'pointer to the system device'}        
        self.requirements['Connect']['systemname'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'name of the A3200 device'}
        self.requirements['Connect']['systemaddress'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'pointer to the A3200 device'}
        self.requirements['Connect']['axis'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'motion axis'}
        self.requirements['Connect']['DOaxis'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'DO axis on A3200'}
        self.requirements['Connect']['DObit'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'bit on the DO axis being used'}    
        self.requirements['Connect']['AIaxis'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'AI axis on A3200'}
        self.requirements['Connect']['AIchannel'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'channel on the AI axis being used'} 

        self.requirements['Initialize'] = {}
        self.requirements['Initialize']['num_points'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'I dont really know what this number is for'}
        
        self.requirements['Measure'] = {}
        self.requirements['Measure']['address'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'address to store value'}
        self.requirements['Measure']['addresstype'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'addres type of address'} 
        self.requirements['Measure']['retract'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'whether to retract the probe at end of measurement'}
        
    def Connect(self, A3200name='', A3200address='', axis='', DOaxis='', DObit='', AIaxis='', AIchannel='', systemname='', systemaddress=''):
        self.descriptors.append(A3200name)
        self.A3200handle = A3200address
        self.axis = axis
        self.DOaxis = DOaxis
        self.DObit = DObit
        self.AIaxis = AIaxis
        self.AIchannel = AIchannel
        self.systemname = systemname
        self.systemhandle = systemaddress
        if not self.simulation:
            import numpy as np
        
        self.addlog('Keyence Touchprobe using ' + A3200name + ' using ' + str(self.DOaxis) + ' bit ' + str(self.DObit))
        return self.returnlog()
    
    def Initialize(self, num_points = ''):
        if num_points == '':
            num_points = self.def_num_points

        if num_points < 2:
            num_points = 2
        
        # Calibration routine
        if not self.simulation:
            import numpy as np
            datavessel = [0]
            self.set_voltage_window()
            v = []
            z = []
            v_target = [self.v_low + i*(self.v_high-self.v_low)/(num_points+1) for i in range(1, num_points+1)]

            self.extend()
            self.goto_contact()
            for value in v_target:
                self.goto_voltage(value, step=self.z_window/num_points)
                self.wait_for_settle(timing='normal')
                self.sample(10, 1)
                v.append(self.sampleresult)
                self.addlog(self.A3200handle.getPosition(address=datavessel, addresstype='pointer', axislist=[self.axis]))
                z.append(datavessel[0][0])

           # use the z and v arrays to get the slope, then calculate the reference z
            p = np.polyfit(v, z, 1)
            self.dzdv = p[0]
            # loglines += self.get_z() + '\n'
            # self.ref_position[self.axis] = self.zresult

            self.configured = True
            self.addlog('Height to voltage slope is ' + str(self.dzdv))
        else:
            self.addlog('Initialization done.')
        return self.returnlog()

    def set_voltage_window(self, n = 100, t = 5):
        '''
        Extend and retract the probe to get the voltage window 
            (and test if the extension is working.)
        '''
        vi = 0
        vf = 0

        self.retract()
        self.addlog(self.systemhandle.Dwell(dtime=0.5))
        self.wait_for_settle(timing = 'slow')
        self.sample(n,t)
        vi = self.sampleresult
        self.extend()
        self.addlog(self.systemhandle.Dwell(dtime=0.5))
        self.wait_for_settle(timing = 'slow')
        self.sample(n,t)
        vf = self.sampleresult
        self.v_high = vi
        self.v_low = vf
        self.retract()
        self.addlog('Voltage window set to ' + str(vi) + ' to ' + str(vf))

            
    def Measure(self, address='', addresstype='', retract = True):
        '''
        Take a measurement.
        '''
        if not self.simulation:
            datavessel = [0]
            self.addlog(self.A3200handle.getAI(address = datavessel, addresstype = 'pointer', axis = self.AIaxis, channel = self.AIchannel))
            if datavessel[0] > 0.8 * self.v_high:
                self.extend()
                self.addlog(self.systemhandle.Dwell(dtime=0.25))
                self.wait_for_settle()
            self.sample(3, 0.05)
            if not (1.2 * self.v_low < self.sampleresult < 1.8 * self.v_high):
                self.goto_contact()
            self.goto_voltage((self.v_high+self.v_low)/2, step=self.z_window/2, diff=0.35 * (self.v_high-self.v_low))
            self.wait_for_settle()
            self.get_z()
            result = self.zresult
        else:
            result = float(input('What is the expected height?'))

        if retract:
            self.retract()
        self.StoreMeasurement(address, addresstype, result)
        return self.returnlog()

    def wait_for_settle(self, limit=0.01, timeout=5, timing='normal'):
        '''
        Wait for the probe to settle prior to a measurement.
        '''
        timing_values = {'slow': [20, 0.2],
                         'normal': [10, 0.1],
                         'fast': [5, 0.05]}
        if timing not in timing_values.keys():
            timing = 'normal'
        self.sample(*timing_values[timing], average=False)
        v = self.sampleresult
        start = time.time()
        while (max(v) - min(v) > limit) and (time.time()-start < timeout):
            self.sample(*timing_values[timing], average=False)
            v = self.sampleresult
        self.addlog('Voltage settled in ' + str((time.time()-start)*1000) + ' ms at ' + timing + ' rate')

    def sample(self, n, t, average=True):
        v = 0
        vlist = []
        datavessel = [0]
        if not self.simulation:
            for i in range(n):
                self.addlog(self.A3200handle.getAI(address = datavessel, addresstype = 'pointer', axis = self.AIaxis, channel = self.AIchannel))
                v += datavessel[0]
                vlist.append(datavessel[0])
                time.sleep(t/n)
            if average:
                self.sampleresult = v/n
            else:
                self.sampleresult = vlist
        else:
            if average:
                v_string = input('What is the average voltage reading in volts?')
                self.sampleresult = float(v_string)
            else:
                vmax_string = input('What is the max voltage reading in volts?')
                vmin_string = input('What is the min voltage reading in volts?')
                vlist = [float(vmax_string),float(vmin_string)]
                self.sampleresult = vlist
        
        self.addlog('The following voltages were measured: \n' + str(vlist))

    def goto_contact(self):
        '''
        Moves down rapidly untill the GT2 makes contact. Should be used with care to avoid collisions.
        '''
        datavessel = [0]
        self.addlog(self.A3200handle.Set_Motion(RelAbs='Rel', motionmode='cmd'))
        self.addlog(self.A3200handle.getAI(address=datavessel, addresstype='pointer', axis=self.AIaxis, channel=self.AIchannel))
        voltage = datavessel[0]
        self.addlog(self.A3200handle.getPosition(address=datavessel, addresstype='pointer', axislist=[self.axis]))
        z_current = datavessel[0][0]
        while voltage < 1.1 * self.v_low:
            #take steps until the voltage changes from the min (extended) value
            cur_position = z_current
            z_current -= self.step
           
            point = {self.axis: -self.step} 
            self.addlog(self.A3200handle.Move(point=point, motiontype='incremental', speed=self.speed, motionmode='cmd'))
            while z_current + 0.5 * self.step < cur_position:
                #wait for more than half the step to be taken
                self.addlog(self.systemhandle.Dwell(dtime = self.step / (5.0 * self.speed)))
                self.addlog(self.A3200handle.getPosition(address=datavessel, addresstype='pointer', axislist=[self.axis]))
                cur_position = datavessel[0][0]                
            self.addlog(self.A3200handle.getAI(address=datavessel, addresstype='pointer', axis=self.AIaxis, channel=self.AIchannel))
            voltage = datavessel[0]
        
        #step back up half a step to account for overshoot and to wait for the move to complete
        point = {self.axis: 0.5 * self.step}
        self.addlog(self.A3200handle.Move(point=point, motiontype='incremental', speed=self.speed, motionmode='cmd'))
        self.addlog(self.systemhandle.Dwell(dtime = self.step / (self.speed)))

    def goto_voltage(self, v, step=0.25, diff=0.05):
        '''
        Move the axis until the touch-probe output is v +/- diff.
        '''
        direction = 0
        # test the voltage first to decide on a direction
        self.addlog(self.A3200handle.Set_Motion(RelAbs='Rel', motionmode='cmd'))
        self.wait_for_settle(limit=0.005, timeout=1, timing='fast')
        self.sample(3, 0.03)
        current_v = self.sampleresult
        while not (v - diff < current_v < v + diff):
            # print(v - diff, '<', current_v, '<', v + diff)
            if v - diff > current_v:
                direction = -1
            else:
                direction = 1
            point = {self.axis: direction * step}
            self.addlog(self.A3200handle.Move(point=point, motiontype='linear', speed=self.speed, motionmode='cmd'))
            self.wait_for_settle(limit=0.005, timeout=1, timing='fast')
            self.sample(3, 0.03)
            current_v = self.sampleresult
            # check to see if we're chainging directions
            if v - diff > current_v:
                new_direction = -1
            else:
                new_direction = 1
            if direction * new_direction < 0:
                step = step / 2.0


    def get_z(self, n = 5, t = 0.1):
        '''
        Sample the analog input and axis position to get the correct position.
        '''
        self.sample(n, t)
        v = self.sampleresult
        datavessel = [0]
        self.addlog(self.A3200handle.getPosition(address=datavessel, addresstype='pointer', axislist=[self.axis]))
        z = datavessel[0][0]
        self.last_v = v
        self.last_z = z
        self.zresult = z - self.dzdv * v

    def retract(self):
        self.addlog(self.A3200handle.Set_DO(axis=self.DOaxis, bit=self.DObit, value=0, motionmode='cmd'))
        self.extended = False

    def extend(self):
        self.addlog(self.A3200handle.Set_DO(axis=self.DOaxis, bit=self.DObit, value=1, motionmode='cmd'))
        self.extended = True


class Ueye_Camera(Sensor):
    def __init__(self, name):
        Device.__init__(self, name)
        self.descriptors.append('ueye')
        self.descriptors.append('camera')
        self.handle = ''
        self.requirements['Measure'] = {}
        self.requirements['Measure']['file'] = {'value': '', 'source': 'direct', 'address': '', 'desc': 'filename to store image at'}
        self.requirements['Configure'] = {}
        self.requirements['Configure']['gain'] = {'value': '', 'source': 'direct', 'address': '', 'desc': 'values for master and RGB gains (0-100)'}
        
    def Connect(self):
        self.fConnect()
        self.addlog(self.name + ' is availible.')
        return self.returnlog()

    def fConnect(self):
        if not self.simulation:
            from Drivers import camera
            try:
                self.handle = camera.ueye()
            except:
                temp = input('Do you want to try to connect again?([y],n)')
                if temp in ['', 'y', 'yes']:
                    self.handle = camera.ueye()
        self.addlog(self.name + ' is connected.')

    def Disconnect(self):
        self.fDisconnect()
        return self.returnlog()

    def fDisconnect(self):
        if not self.simulation:
            self.handle.close()
        self.addlog(self.name + ' is disconnected.')

    def Measure(self, file):
        if not self.simulation:
            self.handle.save_image(file)
        self.addlog(self.name + ' took image and saved at ' + str(file))
        return self.returnlog()
    
    def Configure(self, **kwargs):
        if not self.simulation:
            if 'gain' in kwargs:
                gain = kwargs['gain']
                self.handle.set_gain(master=gain[0], red=gain[1], green=gain[2], blue=gain[3])
            
        self.addlog(self.name + ' configured the following settings:\n\t' + str([k for k in kwargs.keys()]))
        return self.returnlog()

class DumpVessel(Device):
    def __init__(self, name):
        Device.__init__(self, name)
        self.descriptors.append('dump vessel')
        self.handle = ''
        self.requirements['Dump'] = {}
        self.requirements['Set']['depth'] = {'value': '', 'source': 'direct', 'address': '', 'desc': 'how far down to go into the vessel'}
        self.requirements['Set']['delay'] = {'value': '', 'source': 'direct', 'address': '', 'desc': 'how long to wait between swirls'}
        self.requirements['Set']['swirls'] = {'value': '', 'source': 'direct', 'address': '', 'desc': 'the number of swirls'}
        
        self.dependent_device = True
        
    def Connect(self, A3200name='', pumpaddress='', A3200address=''):
        self.fConnect()
        self.addlog(self.name + ' is availible.')
        return self.returnlog()


if __name__ == '__main__':
    testcamera = Ueye_Camera('Test Gantry')
    print(testcamera.Connect())
    print(testcamera.Configure(gain=[50,25,0,45]))
    print(testcamera.Measure('Data\\test.tif'))
    print(testcamera.Disconnect())
