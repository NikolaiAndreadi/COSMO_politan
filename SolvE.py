import os
import re
import shutil
from collections import namedtuple
from subprocess import DEVNULL, STDOUT, check_call

import numpy as np

# A script to find a solvation energy of the .xyz or Orca .out file

# constant values
XYZpath = os.getcwd() + "\\xyz"
OUTpath = os.getcwd() + "\\out"
PM7path = os.getcwd() + "\\PM7"
COSMOpath = os.getcwd() + "\\COSMO"
errpath = os.getcwd() + "\\errorfiles"
MOPACexe = "C:\\Program files\\MOPAC\\MOPAC2016.exe"
COSMOheader = "PM7 1SCF EPS=34.8 CHARGE=0 RSOLV=1.3 Singlet \n\n\n"
PM7header = "PM7 1SCF  CHARGE=0 Singlet \n\n\n"


def read_xyz(fin):
    natoms = int(fin.readline())
    _ = fin.readline()[:-1]  # title
    coords = np.zeros([natoms, 3], dtype="float64")
    atomtypes = []
    for x in coords:
        line = fin.readline().split()
        atomtypes.append(line[0])
        x[:] = list(map(float, line[1:4]))

    return namedtuple("XYZFile", ["coo", "atom"]) \
        (coords, atomtypes)


def readXyzFromOut(fin):
    content = fin.read()

    target = content.rfind("CARTESIAN COORDINATES (ANGSTROEM)")
    target += 68
    endtar = content[target:].find("----------------------------")
    endtar += target - 2
    contStr = content[target:endtar].split("\n")
    XYZ = []
    for line in contStr:
        XYZ.append(line.strip().split())
    return XYZ


def GetOrcaOutXyz(fn):
    """
    Get xyz from Orca out file.

    :param fn: filename
    :return: xyz data set
    """
    f = open(fn, 'r')
    content = f.read()
    f.close()

    target = content.rfind("CARTESIAN COORDINATES (ANGSTROEM)")
    target += 68
    endtar = content[target:].find("----------------------------")
    endtar += target - 2
    return content[target:endtar]


def OUT2MOP(fname):
    fname = OUTpath + "\\" + fname
    f = open(fname)
    data = readXyzFromOut(f)
    f.close()

    # COSMO
    filename = COSMOpath + "\\" + os.path.basename(fname).split(".")[0] + ".mop"
    f = open(filename, "w")

    f.write(COSMOheader)
    for i in range(len(data)):
        tmp = data[i][0] + "  " + str(data[i][1]) + " 1 " + str(data[i][2]) + " 1 " + str(data[i][3]) + " 1\n"
        f.write(tmp)
    f.close()

    # PM7
    filename = PM7path + "\\" + os.path.basename(fname).split(".")[0] + ".mop"
    f = open(filename, "w")

    f.write(PM7header)
    for i in range(len(data)):
        tmp = data[i][0] + "  " + str(data[i][1]) + " 1 " + str(data[i][2]) + " 1 " + str(data[i][3]) + " 1\n"
        f.write(tmp)
    f.close()


def XYZ2MOP(fname):
    fname = XYZpath + "\\" + fname
    f = open(fname)
    data = read_xyz(f)
    f.close()

    # COSMO
    filename = COSMOpath + "\\" + os.path.basename(fname).split(".")[0] + ".mop"
    f = open(filename, "w")

    f.write(COSMOheader)
    for i in range(len(data.atom)):
        tmp = data.atom[i] + "  " + str(data.coo[i][0]) + " 1 " + str(data.coo[i][1]) + " 1 " + str(
            data.coo[i][2]) + " 1\n"
        f.write(tmp)
    f.close()

    # PM7
    filename = PM7path + "\\" + os.path.basename(fname).split(".")[0] + ".mop"
    f = open(filename, "w")

    f.write(PM7header)
    for i in range(len(data.atom)):
        tmp = data.atom[i] + "  " + str(data.coo[i][0]) + " 1 " + str(data.coo[i][1]) + " 1 " + str(
            data.coo[i][2]) + " 1\n"
        f.write(tmp)
    f.close()


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█'):
    """
    Call in a loop to create terminal progress bar
	
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()


def GenerateMopacFiles():
    print(".xyz folder\n")
    N = []
    for i in os.listdir(XYZpath):
        if i.endswith(".xyz"):
            N.append(i)
    N = len(N)
    print("Creating mopac input files... Total ", N, " files\n")

    i = 0
    for file in os.listdir(XYZpath):
        if file.endswith(".xyz"):
            XYZ2MOP(file)
            i += 1
            printProgressBar(i, N, prefix="Progress:")
    print("Done!\n")

    print(".out folder\n")
    N = []
    for i in os.listdir(OUTpath):
        if i.endswith(".out"):
            N.append(i)
    N = len(N)
    print("Creating mopac input files... Total ", N, " files\n")

    i = 0
    for file in os.listdir(OUTpath):
        if file.endswith(".out"):
            OUT2MOP(file)
            i += 1
            printProgressBar(i, N, prefix="Progress:")
    print("Done!\n")


def RunMopacScripts():
    N = []
    for i in os.listdir(COSMOpath):
        if i.endswith(".mop"):
            N.append(i)
    N = len(N)
    print("Running MOPAC... Total ", N * 2, " files\n")

    i = 0
    for file in os.listdir(COSMOpath):
        if file.endswith(".mop"):
            check_call([MOPACexe, os.path.join(COSMOpath, file)], stdout=DEVNULL, stderr=STDOUT)
            i += 1
            printProgressBar(i, N, prefix="Running COSMO scripts:")
    print("Done!\n")

    i = 0
    for file in os.listdir(PM7path):
        if file.endswith(".mop"):
            check_call([MOPACexe, os.path.join(PM7path, file)], stdout=DEVNULL, stderr=STDOUT)
            i += 1
            printProgressBar(i, N, prefix="Running PM7 scripts:")
    print("Done!\n")


def matchstring(string, fp):
    return [line for line in fp if string in line]


def GetEnergyFromOut(path, filename):
    if filename.endswith(".out"):
        file = open(os.path.join(path, filename), "r")
        target = matchstring("TOTAL ENERGY", file)
        file.close()
        if not target:
            return "ERR1"
        energy = re.findall("\d+\.\d+", target[0])
        if not energy:
            return "ERR2"
        return energy[0]
    else:
        return "Notout"


def GenerateSummary():
    print("Generating summary...\n")
    errcount = 0

    file = open("SolvatE.dat", "w")
    tempstring = "Filename\tEcosmo\tEpm7\tdelta(eV)\n"
    file.write(tempstring)

    for f in os.listdir(COSMOpath):
        StrE1 = GetEnergyFromOut(COSMOpath, f)
        if StrE1 == "ERR1":
            print("Error! COSMO file ", f, "is corrupted. (error 1)")
            shutil.copy(os.path.join(COSMOpath, f), errpath)
            tempstring = f + "\tERROR1\n"
            file.write(tempstring)
            errcount += 1
            continue
        if StrE1 == "ERR2":
            print("Error! COSMO file ", f, "is corrupted. (error 2)")
            shutil.copy(os.path.join(COSMOpath, f), errpath)
            tempstring = f + "\tERROR2\n"
            file.write(tempstring)
            errcount += 1
            continue
        if StrE1 == "Notout":
            continue

        StrE2 = GetEnergyFromOut(PM7path, f)

        delta = str(float(StrE1) - float(StrE2))
        tempstring = f + "\t" + StrE1 + "\t" + StrE2 + "\t" + delta + "\n"
        file.write(tempstring)
    file.close()
    print("Done! ", errcount, " errors detected\n")


GenerateMopacFiles()
RunMopacScripts()
GenerateSummary()
input("Bye! Press Enter to exit...\n")
