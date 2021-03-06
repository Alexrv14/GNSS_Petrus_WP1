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
from PreprocessingFunc import ChannelsFlag, ResetHatch
from PreprocessingFunc import RaiseFlag
from PreprocessingFunc import ActiveSats
from PreprocessingFunc import UpdatePrevPro
from PreprocessingFunc import DetectCycleSlip
from PreprocessingFunc import UpdateBuff
from PreprocessingFunc import ResetHatch
from PreprocessingFunc import UpdateRates
from PreprocessingFunc import UpdateGeomFree
from COMMON.Iono import computeIonoMappingFunction

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

    # Other internal variables definition 
    # Dictionaries
    GapCounter = OrderedDict({})                                        # Gap Detector definition
    HacthFilterReset = OrderedDict({})                                  # Hatch Filter reset
    Ksmooth = OrderedDict({})                                           # Hatch Filter K
    DeltaStec = OrderedDict({})                                         # Delta STEC
    # Constants
    HatchConv = float(Conf["HATCH_STATE_F"])*int(Conf["HATCH_TIME"])    # Hatch Filter Convergence Condition   

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
            "GeomFree": 0.0,        # Geom-free (in m)
            "GeomFreePrev": 0.0,    # t-1 Geom-free (in m)
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
        # Get t-1 Geom-free (in m)
        SatPreproObsInfo["GeomFreePrev"] = PrevPreproObsInfo[SatLabel]["PrevGeomFree"]
        # Get Iono Mapping
        SatPreproObsInfo["Mpp"] = computeIonoMappingFunction(SatPreproObsInfo["Elevation"])

        # Prepare output for the satellite
        PreproObsInfo[SatLabel] = SatPreproObsInfo
    
    # Limit the satellites to the Number of Channels
    # ----------------------------------------------------------
    # Discard the satellites having lower elevation when the Number of Sats > Number of Channels

    # Identify the number of active satellites per constellation
    ActSats = ActiveSats(PreproObsInfo)
    
    # Maximum Number of Channels per constellation
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
    
    # QUALITY CHECKS AND SIGNAL SMOOTHING
    # ----------------------------------------------------------

    # Loop over all the active satellites by epoch
    for Sat, Value in PreproObsInfo.items():
        HacthFilterReset[Sat] = 0

        # Check if the satellite is not valid
        if Value["ValidL1"] != 1:
            continue
                
        # Minimum Mask Angle
        # ----------------------------------------------------------
        # Raise a flag when the satellite's elevation is lower than the receiver mask angle

        if Value["Elevation"] < float(Rcvr[RcvrIdx["MASK"]]): 
            RaiseFlag(Sat, REJECTION_CAUSE["MASKANGLE"], PreproObsInfo)
            continue

        # Signal to Noise Ratio C/N0
        # ----------------------------------------------------------
        # Raise a flag when the carrier S/N0 is over the threshold

        if int(Conf["MIN_CNR"][0]) == 1 and Value["S1"] < float(Conf["MIN_CNR"][1]):
            RaiseFlag(Sat, REJECTION_CAUSE["MIN_CNR"], PreproObsInfo)
            continue
         
        # Maximum Pseudo-Range
        # ----------------------------------------------------------
        # Raise a flag when the code Pseudo-Range exceeds the threshold

        if int(Conf["MAX_PSR_OUTRNG"][0]) == 1 and Value["C1"] > float(Conf["MAX_PSR_OUTRNG"][1]):
            RaiseFlag(Sat, REJECTION_CAUSE["MAX_PSR_OUTRNG"], PreproObsInfo)
            continue

        # Detect Data Gaps in the Observation Information
        # ----------------------------------------------------------
        # Raise a flag when a gap is longer than the maximum gap defined in the configuration
        # Attention: Visibility periods are not considered as Data Gaps

        # Compute the DeltaT taking into account the first appearance of a satellite
        DeltaT = int(Value["Sod"] - PrevPreproObsInfo[Sat]["PrevEpoch"])
        if PrevPreproObsInfo[Sat]["PrevEpoch"] == 0:
            DeltaT = int(Conf["SAMPLING_RATE"])

        GapCounter[Sat] = DeltaT
        if GapCounter[Sat] > int(Conf["HATCH_GAP_TH"]):
            HacthFilterReset[Sat] = 1
            # Do not tag gaps due to the visibility periods as data gaps
            if PrevPreproObsInfo[Sat]["PrevRej"] != 2:
                Value["RejectionCause"] = REJECTION_CAUSE["DATA_GAP"]

        # Cycle Slips
        # ----------------------------------------------------------
        # Detect cycle slips in the Carrier Phase L1
                
        if int(Conf["MIN_NCS_TH"][0]) == 1 and HacthFilterReset[Sat] == 0:
            CsFlag = DetectCycleSlip(Sat, Value, PrevPreproObsInfo, float(Conf["MIN_NCS_TH"][1]))
            # Update the cycle slips buffer
            UpdateBuff(PrevPreproObsInfo[Sat]["CsBuff"], CsFlag)
            # Reset the Hatch Filter and raiso a flag when three consecutive cycle slips are detected
            if CsFlag == True:
                if sum(PrevPreproObsInfo[Sat]["CsBuff"]) == 3:
                    HacthFilterReset[Sat] = 1
                    Value["RejectionCause"] = REJECTION_CAUSE["CYCLE_SLIP"]
                else:
                    Value["ValidL1"] = 0
                    continue
        
        # Hatch Filter implementation
        # ----------------------------------------------------------
        # Smooth the code C1 measurements with the Carrier Phase L1 in meters

        # Update ResetHatchFilter dictionary
        if PrevPreproObsInfo[Sat]["ResetHatchFilter"] == 1:
            HacthFilterReset[Sat] = PrevPreproObsInfo[Sat]["ResetHatchFilter"]
            PrevPreproObsInfo[Sat]["ResetHatchFilter"] = 0

        # Check if Hatch filter must be reset
        if ResetHatch(HacthFilterReset[Sat]) == True: 
            Ksmooth[Sat] = 0
            Value["SmoothC1"] = Value["C1"]
        else:
            Ksmooth[Sat] = PrevPreproObsInfo[Sat]["Ksmooth"] + DeltaT
            # Compute alpha parameter
            if Ksmooth[Sat] < int(Conf["HATCH_TIME"]):
                alpha = DeltaT/Ksmooth[Sat]
            else:
                alpha = DeltaT/int(Conf["HATCH_TIME"])
            # Obtain Smoothed C1 at a given epoch by propagating with the Carrier Phase L1
            PredSmoothC1 = PrevPreproObsInfo[Sat]["PrevSmoothC1"] + (Value["L1Meters"]-PrevPreproObsInfo[Sat]["PrevL1"])
            Value["SmoothC1"] = alpha*Value["C1"] + (1-alpha)*PredSmoothC1
    
        # Carrier Phase Rate L1
        # ----------------------------------------------------------
        # Raise a flag when the rate of the Carrier Phase exceeds the threshold

        if int(Conf["MAX_PHASE_RATE"][0]) == 1 and HacthFilterReset[Sat] == 0:
            Value["PhaseRateL1"] = (Value["L1Meters"]-PrevPreproObsInfo[Sat]["PrevL1"])/DeltaT
            if abs(Value["PhaseRateL1"]) > float(Conf["MAX_PHASE_RATE"][1]):
                RaiseFlag(Sat, REJECTION_CAUSE["MAX_PHASE_RATE"], PreproObsInfo)
                PrevPreproObsInfo[Sat]["ResetHatchFilter"] = 1
                continue

        # Carrier Phase Rate Step L1
        # ----------------------------------------------------------
        # Raise a flag when the step of the Carrier Phase rate exceeds the threshold

        if int(Conf["MAX_PHASE_RATE_STEP"][0]) == 1 and HacthFilterReset[Sat] == 0:
            if PrevPreproObsInfo[Sat]["PrevPhaseRateL1"] == 0.0:
                pass
            else:
                Value["PhaseRateStepL1"] = (Value["PhaseRateL1"]-PrevPreproObsInfo[Sat]["PrevPhaseRateL1"])/DeltaT
                if abs(Value["PhaseRateStepL1"]) > float(Conf["MAX_PHASE_RATE_STEP"][1]):
                    RaiseFlag(Sat, REJECTION_CAUSE["MAX_PHASE_RATE_STEP"], PreproObsInfo)
                    PrevPreproObsInfo[Sat]["ResetHatchFilter"] = 1
                    continue

        # Code Rate C1
        # ----------------------------------------------------------
        # Raise a flag when the rate of the Code C1 exceeds the threshold

        if int(Conf["MAX_CODE_RATE"][0]) == 1 and HacthFilterReset[Sat] == 0:
            Value["RangeRateL1"] = (Value["SmoothC1"]-PrevPreproObsInfo[Sat]["PrevSmoothC1"])/DeltaT
            if abs(Value["RangeRateL1"]) > float(Conf["MAX_CODE_RATE"][1]):
                RaiseFlag(Sat, REJECTION_CAUSE["MAX_CODE_RATE"], PreproObsInfo)
                PrevPreproObsInfo[Sat]["ResetHatchFilter"] = 1
                continue

        # Code Rate Step C1
        # ----------------------------------------------------------
        # Raise a flag when the step of the Code C1 rate exceeds the threshold

        if int(Conf["MAX_CODE_RATE_STEP"][0]) == 1 and HacthFilterReset[Sat] == 0:
            if PrevPreproObsInfo[Sat]["PrevRangeRateL1"] == 0.0:
                pass
            else:
                Value["RangeRateStepL1"] = (Value["RangeRateL1"]-PrevPreproObsInfo[Sat]["PrevRangeRateL1"])/DeltaT
                if abs(Value["RangeRateStepL1"]) > float(Conf["MAX_CODE_RATE_STEP"][1]):
                    RaiseFlag(Sat, REJECTION_CAUSE["MAX_CODE_RATE_STEP"], PreproObsInfo)
                    PrevPreproObsInfo[Sat]["ResetHatchFilter"] = 1
                    continue

        # Carrier Phase L1 smoothing status
        # ----------------------------------------------------------
        # Set Status = 1 if the Hacth Filter has converged
        # Reject the first 6 minutes of data whenever the Hacth Filter is reset

        if Ksmooth[Sat] > HatchConv and Value["ValidL1"] == 1:
            Value["Status"] = 1
        else:
            Value["Status"] = 0
        
        # Update parameters for computing rates flags in PrevPreproObsInfo
        UpdateRates(Sat, Value, PrevPreproObsInfo, HacthFilterReset, Ksmooth)
        
        ########################################################################
        # End of quality checks and signal smoothing
        ########################################################################

        # SIGNAL COMBINATION
        # ----------------------------------------------------------

        # Geometry Free Combination
        # ----------------------------------------------------------
        # Compute the pertinent Geometry Free combinations between L1/L2 signals

        if Value["ValidL1"] == 1 and Value["L2"] > 0.0:
            Value["GeomFree"] = (Value["L1Meters"] - Value["L2"]*Const.GPS_L2_WAVE)/(1-Const.GPS_GAMMA_L1L2)
        else:
            continue
            
        # VTEC Rate and AATR
        # ----------------------------------------------------------
        # Compute the iononospheric gradients

        if HacthFilterReset[Sat] == 0:
            # Compute the STEC Rate
            DeltaTGeom = Value["Sod"] - PrevPreproObsInfo[Sat]["PrevGeomFreeEpoch"]
            DeltaStec[Sat] = (Value["GeomFree"] - Value["GeomFreePrev"])/DeltaTGeom
            # Compute VTEC Rate
            Value["VtecRate"] = 1000.0*(DeltaStec[Sat]/Value["Mpp"])
            # Compute instantaneous AATR
            Value["iAATR"] = Value["VtecRate"]/Value["Mpp"]

        # Update parameters for computing Geometry Free combination in PrevPreproObsInfo
        UpdateGeomFree(Sat, Value, PrevPreproObsInfo, HacthFilterReset)

        ########################################################################
        # End of signal combination
        ########################################################################         

    # Update PrevPreproObsInfo corresponding to each satellite for next epoch
    UpdatePrevPro(PreproObsInfo, PrevPreproObsInfo, HacthFilterReset)

    return PreproObsInfo

# End of function runPreProcMeas()

########################################################################
# END OF PREPROCESSING FUNCTIONS MODULE
########################################################################
