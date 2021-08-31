#!/usr/bin/env python

########################################################################
# PETRUS/SRC/Preprocessing.py:
# This is the Preprocessing Module of PETRUS tool
#
#  Project:        PETRUS
#  File:           Preprocessing.py
#  Date(YY/MM/DD): 01/02/21
#
#  Author: GNSS Academy
#  Copyright 2021 GNSS Academy
#
# -----------------------------------------------------------------
# Date       | Author             | Action
# -----------------------------------------------------------------
#
########################################################################

# Import External and Internal functions and Libraries
#----------------------------------------------------------------------

# Preprocessing internal auxiliary functions
#-----------------------------------------------------------------------

def SatElevation(Const, PreproObsInfo):

    # Function returning an ordered list containing the elevation of the active satellites
    # per constellation

    SatElev = []
    for Sat, Value in PreproObsInfo.items():
        if Value["ValidL1"] == 1 and Const in Sat:
            SatElev.append([Value["Elevation"],Sat])
    SatElev.sort()

    return SatElev

def ActiveSats(PreproObsInfo):

    # Function returning the number of active satellites

    ActSatsGps = 0
    ActSatsGal = 0
    for key in PreproObsInfo.keys():
        if "G" in key:
            ActSatsGps = ActSatsGps + PreproObsInfo[key]["ValidL1"]
        elif "E" in key:
            ActSatsGal = ActSatsGal + PreproObsInfo[key]["ValidL1"]
        else:
            None

    ActSats = [ActSatsGps + ActSatsGal, ActSatsGps, ActSatsGal]

    return ActSats

def RejectSatMinElevation(NChannels, SatElev, PreproObsInfo):

    # Function removing the satellites with lower elevation from PreproObsInfo

    while len(PreproObsInfo.keys()) > NChannels:
        del PreproObsInfo[SatElev[0][1]]
        SatElev.pop(0)

def RaiseFlag(Sat, FlagNum, PreproObsInfo):

    # Function raising a flag

    # Check if there are enough satellites to compute a solution
    SatsGpsInit, SatsGalInit = ActiveSats(PreproObsInfo)[1], ActiveSats(PreproObsInfo)[2]

    # Multiconstellation case
    if SatsGpsInit != 0 and SatsGalInit != 0:
        ActSat = ActiveSats(PreproObsInfo)[0]
        if ActSat > 5: 
            PreproObsInfo[Sat]["ValidL1"] = 0
            PreproObsInfo[Sat]["RejectionCause"] = FlagNum
        else:
            None
    # Monoconstellation case 
    elif SatsGpsInit == 0 or SatsGalInit == 0:
        ActSat = ActiveSats(PreproObsInfo)[0]
        if ActSat > 4: 
            PreproObsInfo[Sat]["ValidL1"] = 0
            PreproObsInfo[Sat]["RejectionCause"] = FlagNum
        else:
            None
    else:
        None 

def ChannelsFlag(ActSats, NChannels, FlagNum, Const, PreproObsInfo):

    # Function rising a flag in PreproObsInfo for those satellites having lower elevations

    if ActSats > NChannels: 
        # Create ordered list containing the elevation of every active satellite per constellation
        SatElev = SatElevation(Const, PreproObsInfo)

        # Raise a flag for the satellite with lowest elevation
        for i in range(ActSats-NChannels):
            Sat = SatElev[0][1]
            RaiseFlag(Sat, FlagNum, PreproObsInfo)
            SatElev.pop(0)

def UpdatePrevPro(Sat, Value, PrevPreproObsInfo):

    # Function updating the values of PrevPreproObsInfo dictionary

    # Parameters for computing cycle slips
    if Value["ValidL1"] == 1:
        PrevPreproObsInfo[Sat]["L1_n_3"] = PrevPreproObsInfo[Sat]["L1_n_2"]
        PrevPreproObsInfo[Sat]["L1_n_2"] = PrevPreproObsInfo[Sat]["L1_n_1"]
        PrevPreproObsInfo[Sat]["L1_n_1"] = Value["L1"]
        PrevPreproObsInfo[Sat]["t_n_3"] = PrevPreproObsInfo[Sat]["t_n_2"]
        PrevPreproObsInfo[Sat]["t_n_2"] = PrevPreproObsInfo[Sat]["t_n_1"]
        PrevPreproObsInfo[Sat]["t_n_1"] = Value["Sod"]
   
    # Update cycle slips buffer
    if Value["RejectionCause"] == 5:
        PrevPreproObsInfo[Sat]["CsBuff"].append(1)
        PrevPreproObsInfo[Sat]["CsBuff"].pop(0)
    else:
        PrevPreproObsInfo[Sat]["CsBuff"].append(0)
        PrevPreproObsInfo[Sat]["CsBuff"].pop(0)
    PrevPreproObsInfo[Sat]["CsIdx"] = sum(PrevPreproObsInfo[Sat]["CsBuff"])

    # Parameters for computing data gaps
    PrevPreproObsInfo[Sat]["PrevL1"] = Value["L1"]
    
    # Activate Hatch Filter Flag
    if Value["RejectionCause"] == 6 or PrevPreproObsInfo[Sat]["CsIdx"] == 3:
        PrevPreproObsInfo[Sat]["ResetHatchFilter"] = 1
    else:
        PrevPreproObsInfo[Sat]["ResetHatchFilter"] = 0
    # PrevPreproObsInfo[Sat]["Ksmooth"] =

    # Other parameters
    PrevPreproObsInfo[Sat]["PrevEpoch"] = Value["Sod"]
    # PrevPreproObsInfo[Sat]["PrevSmoothC1"] = SatInfo["SmoothC1"]
    # PrevPreproObsInfo[Sat]["PrevRangeRateL1"] = SatInfo["RangeRateL1"]
    # PrevPreproObsInfo[Sat]["PrevPhaseRateL1"] = SatInfo["PhaseRateL1"]
    # PrevPreproObsInfo[Sat]["PrevGeomFree"] = SatInfo["GeomFree"]
    # PrevPreproObsInfo[Sat]["PrevGeomFreeEpoch"] =
    PrevPreproObsInfo[Sat]["PrevRej"] = Value["RejectionCause"]

def DetectCycleSlip(Sat, Value, PrevPreproObsInfo, CsThreshold):

    # Function detecting a cycle slip by comparing the Carrier Phase L1 at epoch t obtained from the 
    # observation file with the Carrier Phase computed from a 3rd order Lagrange Interpolation (TOD)

    CycleSlip = False

    # Compute the 3rd order difference (TOD)
    # Current and previous valid carrier phase measurements
    CP_n = Value["L1"]
    CP_n_1 = PrevPreproObsInfo[Sat]["L1_n_1"]
    CP_n_2 = PrevPreproObsInfo[Sat]["L1_n_2"]
    CP_n_3 = PrevPreproObsInfo[Sat]["L1_n_3"]
    
    # Previous measurements instants
    t1 = Value["Sod"] - PrevPreproObsInfo[Sat]["t_n_1"]
    t2 = PrevPreproObsInfo[Sat]["t_n_1"] - PrevPreproObsInfo[Sat]["t_n_2"]
    t3 = PrevPreproObsInfo[Sat]["t_n_2"] - PrevPreproObsInfo[Sat]["t_n_3"]
    
    # Return False if there are not enough epochs to compute the TOD
    if t2 == 0 or t3 == 0:
        return CycleSlip
    
    # Residuals equation factors
    R1 = float((t1+t2)*(t1+t2+t3))/(t2*(t2+t3))
    R2 = float(-t1*(t1+t2+t3))/(t2*t3)
    R3 = float(t1*(t1+t2))/((t2+t3)*t3)
    
    # Compute the TOD residuals
    CsResiduals = abs(CP_n-R1*CP_n_1-R2*CP_n_2-R3*CP_n_3)
    
    # Cycle Slip detection
    CycleSlip = CsResiduals > CsThreshold
    return CycleSlip
    

########################################################################
# END OF PREPROCESSING AUXILIARY FUNCTIONS MODULE
########################################################################