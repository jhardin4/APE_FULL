import time
import sys


class Executor():
    def __init__(self):
        self.devicelist = {}
        self.log = ''
        self.logaddress = str(int(round(time.time(), 0))) + 'log.txt'
        self.logging = True
        self.debug = False

    def execute(self, eproclist):
        for line in eproclist:
            for eproc in line:
                self.Send(eproc)

    def loadDevice(self, devName, devAddress, devAddressType):
        self.devicelist[devName] = {}
        self.devicelist[devName]['Address'] = devAddress
        self.devicelist[devName]['AddressType'] = devAddressType

    def Send(self, eproc):
        if self.devicelist[eproc['devices']]['AddressType'] == 'pointer':
            if not self.debug:
                try:
                    if eproc['details'] == {}:
                        self.log += getattr(self.devicelist[eproc['devices']]['Address'],
                                            eproc['procedure'])()
                    else:
                        self.log += getattr(self.devicelist[eproc['devices']]['Address'],
                                            eproc['procedure'])(**eproc['details'])

                    self.log += '\n'

                    if self.logging:
                        loghandle = open('Logs/' + self.logaddress, mode='a')
                        loghandle.write(self.log)
                        loghandle.close()
                        self.log = ''

                except Exception:
                    print('The following line failed to send:\n' + str(eproc))
                    print("Oops!", sys.exc_info()[0], "occured.")
                    raise Exception('EXECUTOR SEND FAILURE')

            else:
                if eproc['details'] == {}:
                    self.log += getattr(self.devicelist[eproc['devices']]['Address'],
                                        eproc['procedure'])()
                else:
                    self.log += getattr(self.devicelist[eproc['devices']]['Address'],
                                        eproc['procedure'])(**eproc['details'])

                self.log += '\n'

                if self.logging:
                    loghandle = open('Logs/' + self.logaddress, mode='a')
                    loghandle.write(self.log)
                    loghandle.close()
                    self.log = ''
