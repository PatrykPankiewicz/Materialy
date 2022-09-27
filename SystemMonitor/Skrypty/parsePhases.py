#Author Patryk Pankiewicz
#Script for parsing System Monitor logs concerning system cycle times
import re


LOG_START = "SMON|PHAS Transition  DRIVER_INIT_LIST_ONE"
LOG_ENTRY = "SMON|PHAS Transition"

logsFile = open('VuC15Log_COM11_serialData_20220706_174237.txt', 'r')
Lines = logsFile.readlines()

regex = r"SMON\|PHAS Transition  (.*)  ->  (.*) , duration:  ([0-9]{1,10})\[us\] , (.*) count:  (.*) "
#G1 - phase
#G2 - next phase
#G3 - duration
#G4 - garbage
#G5 - error count -> 0 - ok

phasesEnum = [ 
    "INIT",
    "DRIVER_INIT_ZERO",
    "DRIVER_INIT_LIST_ONE",
    "ECUM_STATE_STARTUP_TWO",
    "DRIVER_INIT_TWO",
    "NVM_READALL",
    "NVM_READALL_FINISHED",
    "DRIVER_INIT_THREE",
    "OPERATION",
    "PREP_SHUTDOWN",
    "ON_GO_OFF_ONE_A_CALLOUT",
    "NVM_WRITEALL",
    "NVM_WRITEALL_FINISHED",
    "SHUTDOWN_2",
    "PHASE_LAST",
    "NUMBER_OF_PHASE"
]

class ClassLifeCycle:
    def __init__(self, index):
        self._index = index
        self._Phases = []

class ClassPhaseEntry:
    def __init__(self, currentPhase, nextPhase, duration, error):
        self._currentPhase = currentPhase
        self._nextPhase = nextPhase
        self._duration = duration
        self._error = error

count = 0
time = ""
saveTime = ""

lifecyclesList = []

for line in Lines:
    if (LOG_START in line):
        matches = re.finditer(regex, line, re.MULTILINE)
        lifecyclesList.append(ClassLifeCycle(count))
        count += 1
        for match in matches:
            lifecyclesList[-1]._Phases.append(ClassPhaseEntry(match[1], match[2], int(match[3]), int(match[5])))
    elif(LOG_ENTRY in line):
        matches = re.finditer(regex, line, re.MULTILINE)
        for match in matches:
            lifecyclesList[-1]._Phases.append(ClassPhaseEntry(match[1], match[2], int(match[3]), int(match[5])))

def printAllEvents():
    for lifecycle in lifecyclesList:
        print("======================================================")
        print(lifecycle._index)
        for phase in lifecycle._Phases:
            print(phase._currentPhase)
            print(phase._duration)

resultString = ""

def printAllEventsForExcel():
    global resultString
    found = 0
    for lifecycle in lifecyclesList:
        for phase in phasesEnum:
            for entry in lifecycle._Phases:
               if(entry._currentPhase == phase):
                   resultString += str(entry._duration) + ";"
                   found = 1
            if(found == 0):
                resultString += "0;"
            found = 0
        print(resultString)
        resultString = ""

def printHeader():
    headerString = ""
    for phase in phasesEnum:
        headerString += phase + ";"
    print(headerString)

printHeader()
printAllEventsForExcel()


