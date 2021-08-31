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
import sys, os
# Add path to find all modules
Common = os.path.dirname(os.path.dirname(
    os.path.abspath(sys.argv[0]))) + '/COMMON'
sys.path.insert(0, Common)
from collections import OrderedDict
from COMMON import GnssConstants as Const
from InputOutput import RcvrIdx, ObsIdx, REJECTION_CAUSE, REJECTION_CAUSE_DESC
from InputOutput import FLAG, VALUE, TH, CSNEPOCHS
from PreprocessingFunc import ChannelsFlag
from PreprocessingFunc import RaiseFlag
from PreprocessingFunc import ActiveSats
from PreprocessingFunc import UpdatePrevPro
from PreprocessingFunc import DetectCycleSlip
from PreprocessingFunc import UpdateBuff
# import numpy as np
# from COMMON.Iono import computeIonoMappingFunction

# Preprocessing internal functions
#-----------------------------------------------------------------------

def runPreProcMeas(Conf, Rcvr, ObsInfo, PrevPreproObsInfo):
    
    # Purpose: preprocess GNSS raw measurements from OBS file
    #          and generate PREPRO OBS file with the cleaned,
    #          smoothed measurements
    #          More in detail, this function handles:
             
    #          * Measurements cleaning and validation and exclusion due to different 
    #          criteria as follows:
    #             - Minimum Masking angle
    #             - Maximum Number of channels
    #             - Minimum Carrier-To-Noise Ratio (CN0)
    #             - Pseudo-Range Output of Range 
    #             - Maximum Pseudo-Range Step
    #             - Maximum Pseudo-Range Rate
    #             - Maximum Carrier Phase Increase
    #             - Maximum Carrier Phase Increase Rate
    #             - Data Gaps checks and handling 
    #             - Cycle Slips detection

    #         * Filtering of Code-Phase Measurements
    #         * Smoothing of Code-Phase Measurements with a Hatch filter 

    # Parameters
    # ==========
    # Conf: dict
    #       Configuration dictionary
    # Rcvr: dict
    #       Receiver information: position, masking angle...
    # ObsInfo: list
    #          OBS info for current epoch
    #          ObsInfo[1][1] is the second field of the 
    #          second satellite
    # PrevPreproObsInfo: dict
    #                    Preprocessed observations for previous epoch per sat
    #                    PrevPreproObsInfo["G01"]["C1"]

    # Returns
    # =======
    # PreproObsInfo: dict
    #         Preprocessed observations for current epoch per sat
    #         PreproObsInfo["G01"]["C1"]
    

    # Initialize output
    PreproObsInfo = OrderedDict({})

    # Loop over satellites
    for SatObs in ObsInfo:
        # Initialize output info
        SatPreproObsInfo = {
            "Sod": 0.0,             # Second of day
            "Doy": 0,               # Day of year
            "Elevation": 0.0,       # Elevation
            "Azimuth": 0.0,         # Azimuth
            "C1": 0.0,              # GPS L1C/A pseudorange
            "P1": 0.0,              # GPS L1P pseudorange
            "L1": 0.0,              # GPS L1 carrier phase (in cycles)
            "L1Meters": 0.0,        # GPS L1 carrier phase (in m)
            "S1": 0.0,              # GPS L1C/A C/No
            "P2": 0.0,              # GPS L2P pseudorange
            "L2": 0.0,              # GPS L2 carrier phase 
            "S2": 0.0,              # GPS L2 C/No
            "SmoothC1": 0.0,        # Smoothed L1CA 
            "GeomFree": 0.0,        # Geom-free in Phases
            "GeomFreePrev": 0.0,    # t-1 Geom-free in Phases
            "ValidL1": 1,           # L1 Measurement Status
            "RejectionCause": 0,    # Cause of rejection flag
            "StatusL2": 0,          # L2 Measurement Status
            "Status": 0,            # L1 Smoothing status
            "RangeRateL1": 0.0,     # L1 Code Rate
            "RangeRateStepL1": 0.0, # L1 Code Rate Step
            "PhaseRateL1": 0.0,     # L1 Phase Rate
            "PhaseRateStepL1": 0.0, # L1 Phase Rate Step
            "VtecRate": 0.0,        # VTEC Rate
            "iAATR": 0.0,           # Instantaneous AATR
            "Mpp": 0.0,             # Iono Mapping

        } # End of SatPreproObsInfo

        # Get satellite label
        SatLabel = SatObs[ObsIdx["CONST"]] + "%02d" % int(SatObs[ObsIdx["PRN"]])

        # Prepare outputs
        # Get SoD
        SatPreproObsInfo["Sod"] = float(SatObs[ObsIdx["SOD"]])
        # Get DoY
        SatPreproObsInfo["Doy"] = int(SatObs[ObsIdx["DOY"]])
        # Get Elevation
        SatPreproObsInfo["Elevation"] = float(SatObs[ObsIdx["ELEV"]])
        # Get Azimuth
        SatPreproObsInfo["Azimuth"] = float(SatObs[ObsIdx["AZIM"]])
        # Get GPS L1C/A pseudorange
        SatPreproObsInfo["C1"] = float(SatObs[ObsIdx["C1"]])
        # Get GPS L1P pseudorange
        # SatPreproObsInfo["P1"] = 
        # Get GPS L1 carrier phase (in cycles)
        SatPreproObsInfo["L1"] = float(SatObs[ObsIdx["L1"]])
        # Get GPS L1 carrier phase (in m)
        SatPreproObsInfo["L1Meters"] = float(SatObs[ObsIdx["L1"]])*Const.GPS_L1_WAVE
        # Get GPS L1C/A C/No
        SatPreproObsInfo["S1"] = float(SatObs[ObsIdx["S1"]])
        # Get GPS L2P pseudorange
        SatPreproObsInfo["P2"] = float(SatObs[ObsIdx["P2"]])
        # Get GPS L2 carrier phase 
        SatPreproObsInfo["L2"] = float(SatObs[ObsIdx["L2"]])
        # Get GPS L2 C/No
        SatPreproObsInfo["S2"] = float(SatObs[ObsIdx["S2"]])
        # Get Smoothed L1CA 
        # SatPreproObsInfo["SmoothC1"] =
        # Get Geom-free in Phases
        # SatPreproObsInfo["GeomFree"] =
        # Get t-1 Geom-free in Phases
        # SatPreproObsInfo["GeomFreePrev"] =
        # Get L1 Measurement Status
        # SatPreproObsInfo["StatusL2"] =
        # Get L1 Smoothing status
        # SatPreproObsInfo["Status"] =
        # Get L1 Code Rate
        # SatPreproObsInfo["RangeRateL1"] =
        # Get L1 Code Rate Step
        # SatPreproObsInfo["RangeRateStepL1"] =
        # Get L1 Phase Rate
        # SatPreproObsInfo["PhaseRateL1"] =
        # Get L1 Phase Rate Step
        # SatPreproObsInfo["PhaseRateStepL1"] =
        # Get VTEC Rate
        # SatPreproObsInfo["VtecRate"] =
        # Get Instantaneous AATR
        # SatPreproObsInfo["iAATR"] =
        # Get Iono Mapping
        # SatPreproObsInfo["Mpp"] =

        # Prepare output for the satellite
        PreproObsInfo[SatLabel] = SatPreproObsInfo

    # Limit the satellites to the Number of Channels
    # ----------------------------------------------------------
    # Discard the satellites having lower elevation when the Number of Sats > Number of Channels

    # Identify the number of active satellites per constellation
    ActSats = ActiveSats(PreproObsInfo)
    
    # FLAG 1 : Maximum Number of Channels per constellation
    # Rise a flag for those satellites having lower elevations

    # GPS Satellites
    ActSatsGps = ActSats[1]
    NChannelsGps = int(Conf["NCHANNELS_GPS"])
    FlagNum = REJECTION_CAUSE["NCHANNELS_GPS"]
    ChannelsFlag(ActSatsGps, NChannelsGps, FlagNum, "G", PreproObsInfo)

    # Galileo
    ActSatsGal = ActSats[2]
    NChannelsGal = int(Conf["NCHANNELS_GAL"])
    ChannelsFlag(ActSatsGal, NChannelsGal, FlagNum, "E", PreproObsInfo)

    # VARIABLES DEFINITION
    # ----------------------------------------------------------
    
    # Gap Detector definition
    GapCounter = OrderedDict({})
    for Prn, Epoch in PreproObsInfo.items():
        if PrevPreproObsInfo[Prn]["PrevEpoch"] == 0:
            GapCounter[Prn] = int(Conf["SAMPLING_RATE"])
        else:
            GapCounter[Prn] = int(Epoch["Sod"] - PrevPreproObsInfo[Prn]["PrevEpoch"])

    GapDect = []
    for Prn, Gap in GapCounter.items():
        if Gap > int(Conf["HATCH_GAP_TH"]) and Gap < 10800:
            GapDect.append(Prn)
    
    # QUALITY CHECK FLAGS
    # ----------------------------------------------------------

    # Loop over all the active satellites
    for Sat, Value in PreproObsInfo.items():
        if Value["ValidL1"] == 1:
                
        # FLAG 2: Minimum Mask Angle 
        # Raise a flag when the satellite's elevation is lower than the mask angle

            if Value["Elevation"] < float(Conf["ELEV_NOISE_TH"]): 
                FlagNum = REJECTION_CAUSE["MASKANGLE"]
                RaiseFlag(Sat, FlagNum, PreproObsInfo)

        # FLAG 3 : Signal to Noise Ratio C/N0
        # Raise a flag when the carrier S/N0 is over the limit

            elif int(Conf["MIN_CNR"][0]) == 1 and Value["S1"] < float(Conf["MIN_CNR"][1]):
                FlagNum = REJECTION_CAUSE["MIN_CNR"]
                RaiseFlag(Sat, FlagNum, PreproObsInfo)
         
        # FLAG 4 : Maximum Pseudo-Range
        # Raise a flag when the code Pseudo-Range exceeds a threshold

            elif int(Conf["MAX_PSR_OUTRNG"][0]) == 1 and Value["C1"] > float(Conf["MAX_PSR_OUTRNG"][1]):
                FlagNum = REJECTION_CAUSE["MAX_PSR_OUTRNG"]
                RaiseFlag(Sat, FlagNum, PreproObsInfo)

        # FLAG 6 : Data Gaps
        # Raise a flag when a gap in the data is detected

            elif Sat in GapDect:
                FlagNum = REJECTION_CAUSE["DATA_GAP"]
                RaiseFlag(Sat, FlagNum, PreproObsInfo)

        # FLAG 5 : Cycle Slips
        # Raise a flag when a cycle slip is detected 
                
            elif int(Conf["MIN_NCS_TH"][0]) == 1 and PrevPreproObsInfo[Sat]["ResetHatchFilter"] == 0:
                FlagNum = REJECTION_CAUSE["CYCLE_SLIP"]
                CsFlag = DetectCycleSlip(Sat, Value, PrevPreproObsInfo, float(Conf["MIN_NCS_TH"][1]))
                if CsFlag:
                    RaiseFlag(Sat, FlagNum, PreproObsInfo)
                
                # Update the cycle slip buffer
                UpdateBuff(PrevPreproObsInfo[Sat]["CsBuff"], CsFlag)
                PrevPreproObsInfo[Sat]["CsIdx"] = sum(PrevPreproObsInfo[Sat]["CsBuff"])
                    
            else:
                None

        # Update PrevPreproObsInfo corresponding to each satellite for next epoch
        UpdatePrevPro(Sat, Value, PrevPreproObsInfo, Conf)
            
    # End of Quality Checks loop

    return PreproObsInfo

# End of function runPreProcMeas()

########################################################################
# END OF PREPROCESSING FUNCTIONS MODULE
########################################################################
