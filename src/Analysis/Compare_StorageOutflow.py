# Python 2.7
# Original author: Nicole JS Gaynor (nschiff2 [at] illinois [dot] edu)
# Created for: Illinois State Water Survey
# Date last updated: March 2016

# This program takes FLOW data from the HEC-RAS model and compares the hydrographs of different
# versions of the same river/reach. What is the output format?

import csv
import math
from Compare_Config import CompareConfig
from subprocess import call
import pickle
import os
import operator
import matplotlib.pyplot as pyplot

def getData():
    """Get data from a DSS file"""
    popd=os.getcwd()
    dssvuePath = "C:/Program Files (x86)/HEC/HEC-DSSVue/"
    os.chdir(dssvuePath)
    # Path to scritp that extracts data from DSS file
    scriptPath = "C:/Users/nschiff2/IdeaProjects/AutoHEC/src/Analysis/"
    # Use HEC-DSSVue to run script (only way to use hec package that accesses DSS files)
    call(["HEC-DSSVue.cmd", "-s", scriptPath + "getSOData.py"], shell=True)
    os.chdir(popd)

def roundSigfigs(num, sigfigs):
    """Round to specified number of sigfigs.
    from http://code.activestate.com/recipes/578114-round-number-to-specified-number-of-significant-di/
    accessed 3/24/2016"""
    if num != 0:
        return str(round(num, -int(math.floor(math.log10(abs(num))) - (sigfigs - 1))))
    else:
        return str(0.0)  # Can't take the log of 0

def writeFlowDiff(outFile, flowDiff):
    print("Writing difference data...")
    if(os.path.isfile(outFile)):
        os.remove(outFile)
    else:
        # Write overflow to a CSV file for further analysis or viewing in Excel
        with open(outFile, 'wb') as output:
            writer = csv.DictWriter(output, [key, values])
            writer.writerows(flowDiff)

def getSO(bVersions, cVersions, filePath):
    print("Reading storage-outflow data from text files...")
    soDiff = {}
    for v in range(len(bVersions)):
        bV = bVersions[v]
        cV = cVersions[v]
        dataFileB = "storageoutflow_V" + bV + ".txt"
        dataFileC = "storageoutflow_V" + cV + ".txt"
        # Loads flow data from manual and automated versions, stored as dict
        soDataB = pickle.load(open(filePath + dataFileB, 'rb'))
        soDataC = pickle.load(open(filePath + dataFileC, 'rb'))
        keyListC = soDataC.keys()
        keyListB = soDataB.keys()
        print("Number of subbasins in V" + bV + ":" + str(len(keyListC)))
        print("Number of subbasins in V" + cV + ":" + str(len(keyListB)))
        print(keyListC)
        print(keyListB)
        # Calculate difference between auto and manual versions
        #for k in keyList:
        #    flowDiff[k] = map(operator.sub, flowDataAuto[k], flowDataManual[k])
        # Get rid of interpolated stations
        for key in keyListC:
            t = key.split('/')
            u = t[2].split('_')
            if (len(u[0]) > 1):
                try:
                    float(u[1])
                    newKey = u[0]
                except Exception, e:
                    print(e, "using longer key")
                    if (len(u) > 1):
                        newKey = u[0] + "_" + u[1]
                    else:
                        newKey = u[0]
            else:
                print("Key too short, using longer key")
                newKey = u[0] + "_" + u[1]
            soDataC[newKey] = soDataC.pop(key)
        for key in keyListB:
            t = key.split('/')
            u = t[2].split('_')
            if (len(u[0]) > 1):
                try:
                    float(u[1])
                    newKey = u[0]
                except Exception, e:
                    print(e, "using longer key")
                    if (len(u) > 1):
                        newKey = u[0] + "_" + u[1]
                    else:
                        newKey = u[0]
            else:
                print("Key too short, using longer key")
                newKey = u[0] + "_" + u[1]
            soDataB[newKey] = soDataB.pop(key)
        # for key in keyListB:
        #     u = key.split('_')
        #     try:
        #         float(u[1])
        #         soDataB[u[0]] = soDataB.pop(key)
        #     except Exception, e:
        #         print(e, "using longer key")
        #         soDataB[u[0] + "_" + u[1]] = soDataB.pop(key)
            # if '_0.3' in key:
            #     startI = key.find('.0_0.3')
            #     newKey = key[0:startI] + '_0_0.15' + key[startI+5:]
            #     soDataB[newKey] = soDataB.pop(key)
            # elif '_0.3' in key:
            #     startI = key.find('.0_0.3')
            #     newKey = key[0:startI] + '_0_0.15' + key[startI+5:]
            #     soDataB[newKey] = soDataB.pop(key)
            #newKey = u[0]
            #u = key.split('/')
            try:
                print("Plotting data for " + newKey +  '...')
                plotSO(soDataB[newKey], soDataC[newKey], t[2], filePath, bV, cV)
                #print(soDataB[newKey])
                #print(soDataC[newKey])
         #       soDiff[newKey] = map(operator.sub, soDataC.pop(newKey), soDataB.pop(newKey))
            except KeyError:
                print("Key not found in V" + bV + ": " + newKey)
        # Write diff data to CSV file
        #writeFlowDiff("hydrograph_" + i + ".csv", flowDiff)
       # print(soDiff)

def plotSO(soDataManual, soDataAuto, tableName, filePath, bV, cV):
    #print("Plotting data from " + tableName + "...")
    pyplot.ioff()
    manualLine, = pyplot.plot(soDataManual[0], soDataManual[1], 'b:', lw=2, Label=bV)
    autoLine, = pyplot.plot(soDataAuto[0], soDataAuto[1], 'r-', Label=cV)
    pyplot.legend(handles=[manualLine, autoLine])
    pyplot.ylabel('Discharge (cfs)')
    pyplot.xlabel('Storage (ac-ft)')
    pyplot.title(tableName + " V" + bV + " - V" + cV)
    #pyplot.show()
    try:
        pyplot.savefig(filePath + tableName + "_V" + bV + " - V" + cV + "_SO.png")
    except Exception as e:
        print e
        print("IOError: Invalid filename?", tableName + "_V" + bV + " - V" + cV + "_SO.png")
        pyplot.show()
        print(soDataManual)
        print(soDataAuto)
    pyplot.close("all")

# Used to look at state of variables for debugging
print('done')

def main():
    getData()
    config = CompareConfig()
    getSO(config.baseVersions, config.compareVersions, config.filePath)

if __name__ == '__main__':
    main()