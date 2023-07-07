#!/usr/bin/env python3
#***************************************************************************
#  This file is part of Project Apollo - NASSP
#
#  Copyright 2023 Matthew Hume
#
#  Scenerio Update Utility
#
#  Project Apollo is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  Project Apollo is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with Project Apollo; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#  See https://github.com/orbiternassp/NASSP/blob/Orbiter2016/COPYING.txt
#  for more details.
# **************************************************************************
import re
import glob
import os

### THIS SCRIPT HAS NO UNDO BUTTON. IT UPDATES *ALL* SCENERIOS IN THE CURRENT DIRECTORY ###
### BACK UP YOUR FILES. KNOW WHAT DIRECTORY THIS IS RUNNING IN.
### I WILL DO THE UPDATE FOR YOU, BUT I CAN'T FIX AN INCORRECTLY PERFORMED UPDATE THAT YOU DO
### PM ME ON ORBITER-FORUM.COM (@n72.75)

all_scn_files = glob.glob('./*.scn')

#all_scn_files = ["LEMSystems.cfg","SaturnSystems.cfg"]

SPECIFICC_GAS =	[0.658, 10.183, 1.4108, 0.743, 0.6553, 3.625769, 0.48102, 4.6, 3.12]
SPECIFICC_LIQ = [1.1519, 9.668, 4.184, 1.040, 0.858, 3.691041, 1.0724, 1.5525, 5.193]
SPECIFICC_OLD = [1.669, 9.668, 4.184, 1.040, 0.858, 3.691041, 2.9056392, 1.270, 5.193]

cryo_tanks = ["\s<TANK>\s{2,2}O2TANK1", "\s<TANK>\s{2,2}O2TANK2", "\s<TANK>\s{2,2}H2TANK1", "\s<TANK>\s{2,2}H2TANK2"]

substance_pattern = "\sCHM"
version_pattern = "\sNASSPVER"

lm_class_pattern = "\S*ProjectApollo\/LEM"

update_valve_list = [["\s*<TANK>\s{2,2}H2TANK1\s", None, 0.0001, None, None, None], #CSM VALVES
                    ["\s*<TANK>\s{2,2}H2TANK2\s", None, 0.0001, None, None, None],
                    ["\s*<TANK>\s{2,2}O2FUELCELL1MANIFOLD\s", None, 0.0001, None, None, 1.0],
                    ["\s*<TANK>\s{2,2}H2FUELCELL1MANIFOLD\s", 0.0001, 0.0001, None, None, 1.0],
                    ["\s*<TANK>\s{2,2}O2FUELCELL2MANIFOLD\s", None, 0.0001, None, None, 1.0],
                    ["\s*<TANK>\s{2,2}H2FUELCELL2MANIFOLD\s", 0.0001, 0.0001, None, None, 1.0],
                    ["\s*<TANK>\s{2,2}O2FUELCELL3MANIFOLD\s", None, 0.0001, None, None, 1.0],
                    ["\s*<TANK>\s{2,2}H2FUELCELL3MANIFOLD\s", 0.0001, 0.0001, None, None, 1.0],
                    ["\s*<TANK>\s{2,2}CSMTUNNEL\s", None, 0.1, None, None, None],]

def calcTemp(A,B,C,D):  
    T = - (A*C+B-C*D)/(A-D)
    return T

def updateEnergy(quantity, substance):
    O2Tcrit = 154.7
    H2Tcrit = 33.2
    O2TankSize = 133.9387
    H2TankSize = 191.1387
    O2SpecificC = 1.1519
    H2SpecificC = 9.668
    O2CompressFactor = 0.9945
    H2CompressFactor = 0.968

    newTemp = None
    density = None
    newEnergy = None

    if(substance == 0):
        density = quantity/O2TankSize
        newTemp = calcTemp(1434.338998096669,30827.66466562366,-186.3966881148979,density*O2CompressFactor)
        if(newTemp>O2Tcrit):
            newTemp = calcTemp(44.24461555143480,7784.502442355128,-136.05498694800465,density*O2CompressFactor)*1.05

        newEnergy = quantity*O2SpecificC*newTemp
    elif(substance == 1):
        density = quantity/H2TankSize
        newTemp = calcTemp(136.4894046680936,3242.617524782929,-67.46034096292647,density*H2CompressFactor)
        if(newTemp>O2Tcrit):
            newTemp = calcTemp(0.741833633973125,642.4040759445162,-17.5701803944558,density*H2CompressFactor)

        newEnergy = quantity*H2SpecificC*newTemp

    return newEnergy

def updatelines80001(scn_name):
    scn_file = open(scn_name,'r')
    scn_lines = scn_file.readlines()
    line = 0
    print("Updating " + scn_name + " to 80001")
    for scn_line in scn_lines:
        if(re.search(version_pattern,scn_line)):
            scn_line_split = scn_line.split()
            version = substance = int(scn_line_split[1])
            if(version >= 80001):
                print(scn_filename + " Already Updated to 80001")
                break
            else:
                new_version_line = scn_line.replace(scn_line_split[1],str(80001))
                scn_lines[line] = new_version_line
        if(re.search(substance_pattern,scn_line)):
            scn_line_split = scn_line.split()
            commented = 0
            if(scn_line_split[0] == "#"):
                commented = 1
            substance = int(scn_line_split[1+commented])
            mass = float(scn_line_split[2+commented])
            vapor_mass = float(scn_line_split[3+commented])
            internal_energy = float(scn_line_split[4+commented])
            old_temp = 0.0
            if(mass > 0.0):
                old_temp = internal_energy/(mass*SPECIFICC_OLD[substance])
            new_internal_energy = ((mass-vapor_mass)*SPECIFICC_LIQ[substance]+vapor_mass*SPECIFICC_GAS[substance])*old_temp
            new_substance_line = scn_line.replace(scn_line_split[4+commented],str(new_internal_energy))

            scn_lines[line] = new_substance_line
        line += 1

    with open(scn_name,'w') as new_file:
        new_file.writelines(scn_lines)

def updatelines80002b(scn_name):
    scn_file = open(scn_name,'r')
    scn_lines = scn_file.readlines()
    line = 0
    in_lem_section = False #check if we've reached the LM part of the scenerio
    print("Updating " + scn_name + " to 80002--Part 2")
    for scn_line in scn_lines:

        if(re.search(lm_class_pattern,scn_line)):
            in_lem_section = True
               
        for tank_update_index, tank_to_update in enumerate(update_valve_list):
            if((not(in_lem_section) and tank_update_index>31) or (in_lem_section and tank_update_index<=31)):
                continue
            if(re.search(tank_to_update[0],scn_line)):
                scn_line_split = scn_line.split()
                tank_ident = scn_line_split[0]
                tank_name_str = scn_line_split[1]
                tank_size = float(scn_line_split[2])
                valve1Open = int(scn_line_split[3])
                valve2Open = int(scn_line_split[4])
                valve3Open = int(scn_line_split[5])
                valve4Open = int(scn_line_split[6])

                #I know this should be a loop. sorry. copy and paste is too easy.
                if(tank_to_update[1] != None):
                    valve1Size = float(tank_to_update[1])
                else:
                    valve1Size = float(scn_line_split[7])

                if(tank_to_update[2] != None):
                    valve2Size = float(tank_to_update[2])
                else:
                    valve2Size = float(scn_line_split[8])
                
                if(tank_to_update[3] != None):
                    valve3Size = float(tank_to_update[3])
                else:
                    valve3Size = float(scn_line_split[9])

                if(tank_to_update[4] != None):
                    valve4Size = float(tank_to_update[4])
                else:
                    valve4Size = float(scn_line_split[10])

                if(tank_to_update[5] != None):
                    tank_size = float(tank_to_update[5])
                else:
                    tank_size = float(scn_line_split[2])

                new_substance_line = "     "+tank_ident+"  "+tank_name_str+" "+f'{tank_size:.6f}'+" "+str(valve1Open)+" "+str(valve2Open)+" "+str(valve3Open)+" "+str(valve4Open)+" "+f'{valve1Size:.8f}'+" "+f'{valve2Size:.8f}'+" "+f'{valve3Size:.8f}'+" "+f'{valve4Size:.8f}'+"\n"
                scn_lines[line] = new_substance_line
                break

        # if(len(update_valve_list) != 0):
        #     update_valve_list.pop(0) #should prevent double-updating tanks with the same name in LM and CSM
        line += 1
        

    with open(scn_name,'w') as new_file:
        new_file.writelines(scn_lines)
        
def updatelines80002a(scn_name):
    scn_file = open(scn_name,'r')
    scn_lines = scn_file.readlines()
    line = 0
    previous_line = None
    TanksUpdated = 0
    print("Updating " + scn_name + " to 80002--Part 1")
    for scn_line in scn_lines:
        if(re.search(version_pattern,scn_line)):
            scn_line_split = scn_line.split()
            version = substance = int(scn_line_split[1])
            if(version >= 80002):
                print(scn_filename + " Already Updated to 80002")
                break
            else:
                new_version_line = scn_line.replace(scn_line_split[1],str(80002))
                scn_lines[line] = new_version_line
               
        if(re.search(substance_pattern,scn_line)):
            is_in_cryo_tank_list = False 
            for tankname in cryo_tanks:
                if(re.search(tankname,previous_line)):
                    is_in_cryo_tank_list = True
            
            if(not is_in_cryo_tank_list):
                continue

            scn_line_split = scn_line.split()
            commented = 0
            if(scn_line_split[0] == "#"):
                commented = 1
            substance = int(scn_line_split[1+commented])
            mass = float(scn_line_split[2+commented])
            vapor_mass = float(scn_line_split[3+commented])
            internal_energy = float(scn_line_split[4+commented])

            if((mass > 0.0) & is_in_cryo_tank_list):
                new_internal_energy = updateEnergy(mass,substance)
                new_substance_line = scn_line.replace(scn_line_split[4+commented],str(new_internal_energy*1.024))

            scn_lines[line] = new_substance_line
        previous_line = scn_line
        line += 1

    with open(scn_name,'w') as new_file:
        new_file.writelines(scn_lines)


# updatelines("SaturnSystems.cfg")
for scn_filename in all_scn_files:
    updatelines80001(scn_filename) #update specific heat
    updatelines80002a(scn_filename) #update cryo tanks for the "liquid density update"
    updatelines80002b(scn_filename) #update pipe sizes for the "fuel cell voltage-pressure update

os.system("pause")
