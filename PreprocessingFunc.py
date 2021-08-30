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

########################################################################
# END OF PREPROCESSING AUXILIARY FUNCTIONS MODULE
########################################################################