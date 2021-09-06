#!/usr/bin/env python

########################################################################
# PETRUS/SRC/PreprocessingPlots.py:
# This is the PreprocessingPlots Module of PETRUS tool
#
#  Project:        PETRUS
#  File:           PreprocessingPlots.py
#  Date(YY/MM/DD): 05/02/21
#
#  Author: GNSS Academy
#  Copyright 2021 GNSS Academy
#
# -----------------------------------------------------------------
# Date       | Author             | Action
# -----------------------------------------------------------------
#
########################################################################

import sys, os
from pandas import unique
from pandas import read_csv
from InputOutput import PreproIdx
from InputOutput import REJECTION_CAUSE_DESC
sys.path.append(os.getcwd() + '/' + \
    os.path.dirname(sys.argv[0]) + '/' + 'COMMON')
from COMMON import GnssConstants
from COMMON.Plots import generatePlot, saveFigure
import numpy as np
from collections import OrderedDict
from ConPlots import Conf
import matplotlib.pyplot as plt
from math import pi

def initPlot(PreproObsFile, PlotConf, Title, Label):
    
    # Compute information from PreproObsFile
    PreproObsFileName = os.path.basename(PreproObsFile)
    PreproObsFileNameSplit = PreproObsFileName.split('_')
    Rcvr = PreproObsFileNameSplit[2]
    DatepDat = PreproObsFileNameSplit[3]
    Date = DatepDat.split('.')[0]
    Year = Date[1:3]
    Doy = Date[4:]

    # Dump information into PlotConf
    PlotConf["xLabel"] = "Hour of Day %s" % Doy

    PlotConf["Title"] = "%s from %s on Year %s"\
        " DoY %s" % (Title, Rcvr, Year, Doy)

    PlotConf["Path"] = sys.argv[1] + '/OUT/PPVE/Figures/%s/' % Label + \
        '%s_%s_Y%sD%s.png' % (Label, Rcvr, Year, Doy)

# Plot Satellite Visibility
def plotSatVisibility(PreproObsFile, PreproObsData):

    # Graph settings definition
    PlotConf = {}
    initPlot(PreproObsFile, PlotConf, "Satellites Visibility", "SATS_VISIBILITY_vs_TIME")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,7.6)
    PlotConf["SecondAxis"] = 1

    PrnList = sorted(unique(PreproObsData[PreproIdx["PRN"]]))
    PlotConf["yLabel"] = "GPS-PRN"
    PlotConf["yTicks"] = range(min(PrnList), max(PrnList) + 1)
    PlotConf["yLim"] = [0, max(PrnList) + 1]
    PlotConf["yTicksLabels"] = range(min(PrnList), max(PrnList) + 1)

    PlotConf["xTicks"] = range(0,25)
    PlotConf["xLim"] = [0,24]

    PlotConf["Grid"] = 1

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 3.0

    # Colorbar definition
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "Elevation [Deg]"
    PlotConf["ColorBarMin"] = 0.0
    PlotConf["ColorBarMax"] = 90.0
    PlotConf["ColorBarTicks"] = None

    # Plotting
    PlotConf["xData"], PlotConf["xData2"] = {}, {}
    PlotConf["yData"], PlotConf["yData2"] = {}, {}
    PlotConf["zData"] = {}

    FilterCond2 = PreproObsData[PreproIdx["STATUS"]] == 1
    FilterCond3 = PreproObsData[PreproIdx["STATUS"]] == 0
    for Prn in PrnList:
        Label = "G" + ("%02d" % Prn)
        FilterCond1 = PreproObsData[PreproIdx["PRN"]] == Prn
        PlotConf["xData"][Label] = PreproObsData[PreproIdx["SOD"]][FilterCond1][FilterCond2] / GnssConstants.S_IN_H
        PlotConf["yData"][Label] = PreproObsData[PreproIdx["PRN"]][FilterCond1][FilterCond2]
        PlotConf["zData"][Label] = PreproObsData[PreproIdx["ELEV"]][FilterCond1][FilterCond2]
        PlotConf["xData2"][Label] = PreproObsData[PreproIdx["SOD"]][FilterCond1][FilterCond3] / GnssConstants.S_IN_H
        PlotConf["yData2"][Label] = PreproObsData[PreproIdx["PRN"]][FilterCond1][FilterCond3]

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot Number of Satellites
def plotNumSats(PreproObsFile, PreproObsData):

    # Graph settings definition
    PlotConf = {}
    initPlot(PreproObsFile, PlotConf, "Number of Satellites", "SATS_vs_TIME")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,7.6)

    PlotConf["yLabel"] = "Number of Satellites"
    PlotConf["yLim"] = [0,15]

    PlotConf["xTicks"] = range(0,25)
    PlotConf["xLim"] = [0,24]

    PlotConf["Grid"] = 1

    PlotConf["Marker"] = '-'
    PlotConf["LineWidth"] = 0.75

    # Processing the data to be plotted
    Sod = np.arange(GnssConstants.S_IN_D + 1)
    SatsRaw = []
    SatsSmooth = []
    Data = [SatsRaw, SatsSmooth]

    for Second in Sod:
        FilterCond = PreproObsData[PreproIdx["SOD"]] == Second
        DataEpoch = PreproObsData[PreproIdx["VALID"]][FilterCond]
        DataEpoch.to_numpy()
        SatsRaw.append(len(DataEpoch))
        SatsSmooth.append(sum(DataEpoch))

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    Label = ["Raw","Smoothed"]
    for index in range(len(Label)): 
        PlotConf["xData"][index] = Sod / GnssConstants.S_IN_H
        PlotConf["yData"][index] = np.array(Data[index])

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot Satellite Polar View
def plotSatPolarView(PreproObsFile, PreproObsData):

    # Graph settings definition
    PlotConf = {}
    initPlot(PreproObsFile, PlotConf, "Polar View", "SATS_POLAR_VIEW")

    PlotConf["yTicksLabels"] = ["0°", "10°", "20°", "30°", "40°", "50°", "60°", "70°", "80°", "90°"]
    PlotConf["yLim"] = [0, 90]

    PlotConf["xTicksLabels"] = ["N", "E", "S", "W"]
    PlotConf["xTicks"] = [0, pi/2, pi, 3*pi/2]

    PlotConf["Grid"] = 1

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 0.005

    # Colorbar definition
    PrnList = sorted(unique(PreproObsData[PreproIdx["PRN"]]))
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "GPS-PRN"
    PlotConf["ColorBarMin"] = min(PrnList)
    PlotConf["ColorBarMax"] = max(PrnList)
    PlotConf["ColorBarTicks"] = range(min(PrnList), max(PrnList) + 1)

    # Plotting
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='polar')

    ax.set_title(PlotConf["Title"], y = 1.1)

    if PlotConf["Grid"] == 1:
        ax.grid(linestyle = '--', linewidth = 0.5, which = 'both')

    ax.set_theta_zero_location("N")
    ax.set_theta_direction(1)
    ax.set_xticks(PlotConf["xTicks"])
    ax.set_xticklabels(PlotConf["xTicksLabels"])

    ax.set_rlabel_position(-15)
    ax.set_ylim(PlotConf["yLim"])
    ax.set_yticklabels(PlotConf["yTicksLabels"])
    plt.gca().invert_yaxis()

    xData = PreproObsData[PreproIdx["AZIM"]]
    yData = PreproObsData[PreproIdx["ELEV"]]
    zData = PreproObsData[PreproIdx["PRN"]]

    p = ax.scatter(x = np.radians(xData), y = yData, c = zData, cmap = PlotConf["ColorBar"],\
        marker = PlotConf["Marker"], linewidth = PlotConf["LineWidth"])

    fig.colorbar(p, ticks = PlotConf["ColorBarTicks"], label = PlotConf["ColorBarLabel"], pad = 0.1)  

    # Call saveFigure from Plots library
    saveFigure(plt, PlotConf["Path"])

# Plot C1 - C1 Smoothed vs Time
def plotC1C1Smoothed(PreproObsFile, PreproObsData):

    # Graph settings definition
    PlotConf = {}
    initPlot(PreproObsFile, PlotConf, "C1 - C1 Smoothed", "C1_C1SMOOTHED_vs_TIME")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,7.6)

    PlotConf["yLabel"] = "C1 - C1 Smoothed [m]"
    PlotConf["yLim"] = [-3,2.5]
    PlotConf["yTicks"] = range(-2,3)

    PlotConf["xTicks"] = range(0,25)
    PlotConf["xLim"] = [0,24]

    PlotConf["Grid"] = 1

    PlotConf["Marker"] = '+'
    PlotConf["LineWidth"] = 0.25

    # Processing the data to be plotted
    PreproObsData[PreproIdx["SOD"]].to_numpy()
    PreproObsData[PreproIdx["VALID"]].to_numpy()
    PreproObsData[PreproIdx["C1"]].to_numpy()
    PreproObsData[PreproIdx["C1SMOOTHED"]].to_numpy()
    PreproObsData[PreproIdx["S1"]].to_numpy()

    Noise, Sod, Cn0 = [], [], []
    for i in range(len(PreproObsData[PreproIdx["SOD"]])):
        if PreproObsData[PreproIdx["VALID"]][i] == 1:
            Noise.append(PreproObsData[PreproIdx["C1"]][i]-PreproObsData[PreproIdx["C1SMOOTHED"]][i])
            Sod.append(PreproObsData[PreproIdx["SOD"]][i])
            Cn0.append(PreproObsData[PreproIdx["S1"]][i])

    # Colorbar definition
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "C/N0 [dB-Hz]"
    PlotConf["ColorBarMin"] = int(min(Cn0))
    PlotConf["ColorBarMax"] = int(max(Cn0))
    PlotConf["ColorBarTicks"] = range(PlotConf["ColorBarMin"],PlotConf["ColorBarMax"],2)

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    Label = 0
    PlotConf["xData"][Label] = np.array(Sod) / GnssConstants.S_IN_H
    PlotConf["yData"][Label] = np.array(Noise)
    PlotConf["zData"][Label] = np.array(Cn0)

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot C1 - C1 Smoothed vs Elevation
def plotC1C1SmoothedE(PreproObsFile, PreproObsData):

    # Graph settings definition
    PlotConf = {}
    initPlot(PreproObsFile, PlotConf, "C1 - C1 Smoothed", "C1_C1SMOOTHED_vs_ELEV")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,7.6)

    PlotConf["yLabel"] = "C1 - C1 Smoothed [m]"
    PlotConf["yLim"] = [-3,2.5]
    PlotConf["yTicks"] = range(-2,3)

    PlotConf["xLabel"] = "Elevation [Deg]"
    PlotConf["xTicks"] = range(0,91,10)
    PlotConf["xLim"] = [0,90]

    PlotConf["Grid"] = 1

    PlotConf["Marker"] = '+'
    PlotConf["LineWidth"] = 0.25

    # Processing the data to be plotted
    PreproObsData[PreproIdx["ELEV"]].to_numpy()
    PreproObsData[PreproIdx["VALID"]].to_numpy()
    PreproObsData[PreproIdx["C1"]].to_numpy()
    PreproObsData[PreproIdx["C1SMOOTHED"]].to_numpy()
    PreproObsData[PreproIdx["S1"]].to_numpy()

    Noise, Elev, Cn0 = [], [], []
    for i in range(len(PreproObsData[PreproIdx["ELEV"]])):
        if PreproObsData[PreproIdx["VALID"]][i] == 1:
            Noise.append(PreproObsData[PreproIdx["C1"]][i]-PreproObsData[PreproIdx["C1SMOOTHED"]][i])
            Elev.append(PreproObsData[PreproIdx["ELEV"]][i])
            Cn0.append(PreproObsData[PreproIdx["S1"]][i])

    # Colorbar definition
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "C/N0 [dB-Hz]"
    PlotConf["ColorBarMin"] = int(min(Cn0))
    PlotConf["ColorBarMax"] = int(max(Cn0))
    PlotConf["ColorBarTicks"] = range(PlotConf["ColorBarMin"],PlotConf["ColorBarMax"],2)

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    Label = 0
    PlotConf["xData"][Label] = np.array(Elev)
    PlotConf["yData"][Label] = np.array(Noise)
    PlotConf["zData"][Label] = np.array(Cn0)

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot Rejection Flags vs Time
def plotRejectionFlags(PreproObsFile, PreproObsData):

    # Graph settings definition
    PlotConf = {}
    initPlot(PreproObsFile, PlotConf, "Rejection Flags", "FLAGS_vs_TIME")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,7.6)

    PlotConf["yLabel"] = "Rejection Flag"
    PlotConf["yLim"] = [0,11]
    PlotConf["yTicks"] = range(1,11)
    PlotConf["yTicksLabels"] = REJECTION_CAUSE_DESC.keys()

    PlotConf["xTicks"] = range(0,25)
    PlotConf["xLim"] = [0,24]

    PlotConf["Grid"] = 1

    PlotConf["Marker"] = 'o'
    PlotConf["LineWidth"] = 1.0

    # Colorbar definition
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "GPS-PRN"
    PlotConf["ColorBarMin"] = min(unique(PreproObsData[PreproIdx["PRN"]]))
    PlotConf["ColorBarMax"] = max(unique(PreproObsData[PreproIdx["PRN"]]))
    PlotConf["ColorBarTicks"] = range(PlotConf["ColorBarMin"], PlotConf["ColorBarMax"] + 1)

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    Label = 0
    FilterCond = PreproObsData[PreproIdx["REJECT"]] != 0
    PlotConf["xData"][Label] = PreproObsData[PreproIdx["SOD"]][FilterCond] / GnssConstants.S_IN_H
    PlotConf["yData"][Label] = PreproObsData[PreproIdx["REJECT"]][FilterCond]
    PlotConf["zData"][Label] = PreproObsData[PreproIdx["PRN"]][FilterCond]

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot Code Rate vs Time
def plotCodeRate(PreproObsFile, PreproObsData):

    # Graph settings definition
    PlotConf = {}
    initPlot(PreproObsFile, PlotConf, "Code Rate", "C1_RATE_vs_TIME")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,7.6)

    PlotConf["yLabel"] = "Code Rate [m/s]"
    PlotConf["yLim"] = [-1000,1000]
    PlotConf["yTicks"] = range(-1000,1000,100)

    PlotConf["xTicks"] = range(0,25)
    PlotConf["xLim"] = [0,24]

    PlotConf["Grid"] = 1

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 0.25

    # Processing the data to be plotted
    PreproObsData[PreproIdx["SOD"]].to_numpy()
    PreproObsData[PreproIdx["ELEV"]].to_numpy()
    PreproObsData[PreproIdx["VALID"]].to_numpy()
    PreproObsData[PreproIdx["CODE RATE"]].to_numpy()

    CodeRate, Sod, Elev = [], [], []
    for i in range(len(PreproObsData[PreproIdx["SOD"]])):
        if PreproObsData[PreproIdx["VALID"]][i] == 1 and PreproObsData[PreproIdx["CODE RATE"]][i] !=0:
            CodeRate.append(PreproObsData[PreproIdx["CODE RATE"]][i])
            Sod.append(PreproObsData[PreproIdx["SOD"]][i])
            Elev.append(PreproObsData[PreproIdx["ELEV"]][i])

    # Colorbar definition
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "Elevation [Deg]"
    PlotConf["ColorBarMin"] = 0.0
    PlotConf["ColorBarMax"] = 90.0
    PlotConf["ColorBarTicks"] = None

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    Label = 0
    PlotConf["xData"][Label] = np.array(Sod) / GnssConstants.S_IN_H
    PlotConf["yData"][Label] = np.array(CodeRate)
    PlotConf["zData"][Label] = np.array(Elev)

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot Phase Rate vs Time
def plotPhaseRate(PreproObsFile, PreproObsData):

    # Graph settings definition
    PlotConf = {}
    initPlot(PreproObsFile, PlotConf, "Phase Rate", "L1_RATE_vs_TIME")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,7.6)

    PlotConf["yLabel"] = "Phase Rate [m/s]"
    PlotConf["yLim"] = [-1000,1000]
    PlotConf["yTicks"] = range(-1000,1000,100)

    PlotConf["xTicks"] = range(0,25)
    PlotConf["xLim"] = [0,24]

    PlotConf["Grid"] = 1

    PlotConf["Marker"] = '.'
    PlotConf["LineWidth"] = 0.25

    # Processing the data to be plotted
    PreproObsData[PreproIdx["SOD"]].to_numpy()
    PreproObsData[PreproIdx["ELEV"]].to_numpy()
    PreproObsData[PreproIdx["VALID"]].to_numpy()
    PreproObsData[PreproIdx["PHASE RATE"]].to_numpy()

    PhaseRate, Sod, Elev = [], [], []
    for i in range(len(PreproObsData[PreproIdx["SOD"]])):
        if PreproObsData[PreproIdx["VALID"]][i] == 1 and PreproObsData[PreproIdx["PHASE RATE"]][i] !=0:
            PhaseRate.append(PreproObsData[PreproIdx["PHASE RATE"]][i])
            Sod.append(PreproObsData[PreproIdx["SOD"]][i])
            Elev.append(PreproObsData[PreproIdx["ELEV"]][i])

    # Colorbar definition
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "Elevation [Deg]"
    PlotConf["ColorBarMin"] = 0.0
    PlotConf["ColorBarMax"] = 90.0
    PlotConf["ColorBarTicks"] = None

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    Label = 0
    PlotConf["xData"][Label] = np.array(Sod) / GnssConstants.S_IN_H
    PlotConf["yData"][Label] = np.array(PhaseRate)
    PlotConf["zData"][Label] = np.array(Elev)

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot Code Rate Step vs Time
def plotCodeRateStep(PreproObsFile, PreproObsData):

    # Graph settings definition
    PlotConf = {}
    initPlot(PreproObsFile, PlotConf, "Code Rate Step", "C1_RATE_STEP_vs_TIME")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,7.6)

    PlotConf["yLabel"] = "Code Rate Step [m/s^2]"

    PlotConf["xTicks"] = range(0,25)
    PlotConf["xLim"] = [0,24]

    PlotConf["Grid"] = 1

    PlotConf["Marker"] = '+'
    PlotConf["LineWidth"] = 0.25

    # Processing the data to be plotted
    PreproObsData[PreproIdx["SOD"]].to_numpy()
    PreproObsData[PreproIdx["ELEV"]].to_numpy()
    PreproObsData[PreproIdx["VALID"]].to_numpy()
    PreproObsData[PreproIdx["CODE ACC"]].to_numpy()

    CodeRateStep, Sod, Elev = [], [], []
    for i in range(len(PreproObsData[PreproIdx["SOD"]])):
        if PreproObsData[PreproIdx["VALID"]][i] == 1 and PreproObsData[PreproIdx["CODE ACC"]][i] !=0:
            CodeRateStep.append(PreproObsData[PreproIdx["CODE ACC"]][i])
            Sod.append(PreproObsData[PreproIdx["SOD"]][i])
            Elev.append(PreproObsData[PreproIdx["ELEV"]][i])

    # Colorbar definition
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "Elevation [Deg]"
    PlotConf["ColorBarMin"] = 0.0
    PlotConf["ColorBarMax"] = 90.0
    PlotConf["ColorBarTicks"] = None

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    Label = 0
    PlotConf["xData"][Label] = np.array(Sod) / GnssConstants.S_IN_H
    PlotConf["yData"][Label] = np.array(CodeRateStep)
    PlotConf["zData"][Label] = np.array(Elev)

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# Plot Phase Rate Step vs Time
def plotPhaseRateStep(PreproObsFile, PreproObsData):

    # Graph settings definition
    PlotConf = {}
    initPlot(PreproObsFile, PlotConf, "Phase Rate Step", "L1_RATE_STEP_vs_TIME")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,7.6)

    PlotConf["yLabel"] = "Phase Rate Step [m/s^2]"

    PlotConf["xTicks"] = range(0,25)
    PlotConf["xLim"] = [0,24]

    PlotConf["Grid"] = 1

    PlotConf["Marker"] = '+'
    PlotConf["LineWidth"] = 0.25

    # Processing the data to be plotted
    PreproObsData[PreproIdx["SOD"]].to_numpy()
    PreproObsData[PreproIdx["ELEV"]].to_numpy()
    PreproObsData[PreproIdx["VALID"]].to_numpy()
    PreproObsData[PreproIdx["PHASE ACC"]].to_numpy()

    PhaseRateStep, Sod, Elev = [], [], []
    for i in range(len(PreproObsData[PreproIdx["SOD"]])):
        if PreproObsData[PreproIdx["VALID"]][i] == 1 and PreproObsData[PreproIdx["PHASE ACC"]][i] !=0:
            PhaseRateStep.append(PreproObsData[PreproIdx["PHASE ACC"]][i])
            Sod.append(PreproObsData[PreproIdx["SOD"]][i])
            Elev.append(PreproObsData[PreproIdx["ELEV"]][i])

    # Colorbar definition
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "Elevation [Deg]"
    PlotConf["ColorBarMin"] = 0.0
    PlotConf["ColorBarMax"] = 90.0
    PlotConf["ColorBarTicks"] = None

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    Label = 0
    PlotConf["xData"][Label] = np.array(Sod) / GnssConstants.S_IN_H
    PlotConf["yData"][Label] = np.array(PhaseRateStep)
    PlotConf["zData"][Label] = np.array(Elev)

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# VTEC Gradient vs Time
def plotVtecGradient(PreproObsFile, PreproObsData):

    # Graph settings definition
    PlotConf = {}
    initPlot(PreproObsFile, PlotConf, "VTEC Gradient", "VTEC_GRADIENT_vs_TIME")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,7.6)

    PlotConf["yLabel"] = "VTEC rate [mm/s]"

    PlotConf["xTicks"] = range(0,25)
    PlotConf["xLim"] = [0,24]

    PlotConf["Grid"] = 1

    PlotConf["Marker"] = '+'
    PlotConf["LineWidth"] = 0.25

    # Processing the data to be plotted
    PreproObsData[PreproIdx["SOD"]].to_numpy()
    PreproObsData[PreproIdx["ELEV"]].to_numpy()
    PreproObsData[PreproIdx["VALID"]].to_numpy()
    PreproObsData[PreproIdx["VTEC RATE"]].to_numpy()

    Vtec, Sod, Elev = [], [], []
    for i in range(len(PreproObsData[PreproIdx["SOD"]])):
        if PreproObsData[PreproIdx["VALID"]][i] == 1 and PreproObsData[PreproIdx["VTEC RATE"]][i] !=0:
            Vtec.append(PreproObsData[PreproIdx["VTEC RATE"]][i])
            Sod.append(PreproObsData[PreproIdx["SOD"]][i])
            Elev.append(PreproObsData[PreproIdx["ELEV"]][i])

    # Colorbar definition
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "Elevation [Deg]"
    PlotConf["ColorBarMin"] = 0.0
    PlotConf["ColorBarMax"] = 90.0
    PlotConf["ColorBarTicks"] = None

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    Label = 0
    PlotConf["xData"][Label] = np.array(Sod) / GnssConstants.S_IN_H
    PlotConf["yData"][Label] = np.array(Vtec)
    PlotConf["zData"][Label] = np.array(Elev)

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

# AATR index vs Time
def plotAatr(PreproObsFile, PreproObsData):

    # Graph settings definition
    PlotConf = {}
    initPlot(PreproObsFile, PlotConf, "AATR Index", "AATR_vs_TIME")

    PlotConf["Type"] = "Lines"
    PlotConf["FigSize"] = (8.4,7.6)

    PlotConf["yLabel"] = "AATR Index [mm/s]"

    PlotConf["xTicks"] = range(0,25)
    PlotConf["xLim"] = [0,24]

    PlotConf["Grid"] = 1

    PlotConf["Marker"] = '+'
    PlotConf["LineWidth"] = 0.25

    # Processing the data to be plotted
    PreproObsData[PreproIdx["SOD"]].to_numpy()
    PreproObsData[PreproIdx["ELEV"]].to_numpy()
    PreproObsData[PreproIdx["VALID"]].to_numpy()
    PreproObsData[PreproIdx["iAATR"]].to_numpy()

    Aatr, Sod, Elev = [], [], []
    for i in range(len(PreproObsData[PreproIdx["SOD"]])):
        if PreproObsData[PreproIdx["VALID"]][i] == 1 and PreproObsData[PreproIdx["iAATR"]][i] !=0:
            Aatr.append(PreproObsData[PreproIdx["iAATR"]][i])
            Sod.append(PreproObsData[PreproIdx["SOD"]][i])
            Elev.append(PreproObsData[PreproIdx["ELEV"]][i])

    # Colorbar definition
    PlotConf["ColorBar"] = "gnuplot"
    PlotConf["ColorBarLabel"] = "Elevation [Deg]"
    PlotConf["ColorBarMin"] = 0.0
    PlotConf["ColorBarMax"] = 90.0
    PlotConf["ColorBarTicks"] = None

    # Plotting
    PlotConf["xData"] = {}
    PlotConf["yData"] = {}
    PlotConf["zData"] = {}
    Label = 0
    PlotConf["xData"][Label] = np.array(Sod) / GnssConstants.S_IN_H
    PlotConf["yData"][Label] = np.array(Aatr)
    PlotConf["zData"][Label] = np.array(Elev)

    # Call generatePlot from Plots library
    generatePlot(PlotConf)

def generatePreproPlots(PreproObsFile):
    
    # Purpose: generate output plots regarding Preprocessing results

    # Parameters
    # ==========
    # PreproObsFile: str
    #                Path to PREPRO OBS output file

    # Returns
    # =======
    # Nothing
    
    # Satellite Visibility
    # ----------------------------------------------------------
    if(Conf["PLOT_VIS"] == 1):
        # Read the cols we need from POS file
        PreproObsData = read_csv(PreproObsFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[PreproIdx["SOD"],PreproIdx["PRN"],PreproIdx["ELEV"],PreproIdx["STATUS"]])

        print( 'Plot Satellites Visibility vs Time ...')
      
        # Configure plot and call plot generation function
        plotSatVisibility(PreproObsFile, PreproObsData)

    # Plot Number of Satellites
    # ----------------------------------------------------------
    if(Conf["PLOT_NSAT"] == 1):
        # Read the cols we need from POS file
        PreproObsData = read_csv(PreproObsFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[PreproIdx["SOD"],PreproIdx["VALID"]])

        print( 'Plot Number of Satellites vs Time ...')
      
        # Configure plot and call plot generation function
        plotNumSats(PreproObsFile, PreproObsData)

    # Plot Polar View
    # ----------------------------------------------------------
    if(Conf["PLOT_POLAR"] == 1):
        # Read the cols we need from POS file
        PreproObsData = read_csv(PreproObsFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[PreproIdx["PRN"],PreproIdx["ELEV"],PreproIdx["AZIM"]])

        print( 'Plot Satellites Polar View ...')
      
        # Configure plot and call plot generation function
        plotSatPolarView(PreproObsFile, PreproObsData)

    # Plot Rejection Flags of satellite
    # ----------------------------------------------------------
    if(Conf["PLOT_SATS_FLAGS"] == 1):
        # Read the cols we need from POS file
        PreproObsData = read_csv(PreproObsFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[PreproIdx["SOD"],PreproIdx["PRN"],PreproIdx["REJECT"]])

        print( 'Plot Rejection Flags of Satellites vs Time ...')
      
        # Configure plot and call plot generation function
        plotRejectionFlags(PreproObsFile, PreproObsData)

    # Plot C1 - C1 Smoothed vs Time
    # ----------------------------------------------------------
    if(Conf["PLOT_C1_C1SMOOTHED_T"] == 1):
        # Read the cols we need from POS file
        PreproObsData = read_csv(PreproObsFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[PreproIdx["SOD"],PreproIdx["VALID"],PreproIdx["C1"],PreproIdx["C1SMOOTHED"],PreproIdx["S1"]])

        print( 'Plot C1 - C1 Smoothed vs Time ...')
      
        # Configure plot and call plot generation function
        plotC1C1Smoothed(PreproObsFile, PreproObsData)

    # Plot C1 - C1 Smoothed vs Elevation
    # ----------------------------------------------------------
    if(Conf["PLOT_C1_C1SMOOTHED_E"] == 1):
        # Read the cols we need from POS file
        PreproObsData = read_csv(PreproObsFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[PreproIdx["ELEV"],PreproIdx["VALID"],PreproIdx["C1"],PreproIdx["C1SMOOTHED"],PreproIdx["S1"]])

        print( 'Plot C1 - C1 Smoothed vs Elevation ...')
      
        # Configure plot and call plot generation function
        plotC1C1SmoothedE(PreproObsFile, PreproObsData)

    # Code Rate vs Time
    # ----------------------------------------------------------
    if(Conf["PLOT_C1_RATE"] == 1):
        # Read the cols we need from POS file
        PreproObsData = read_csv(PreproObsFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[PreproIdx["SOD"],PreproIdx["ELEV"],PreproIdx["VALID"],PreproIdx["CODE RATE"]])

        print( 'Plot Code Rate vs Time ...')
      
        # Configure plot and call plot generation function
        plotCodeRate(PreproObsFile, PreproObsData)

    # Code Rate vs Time
    # ----------------------------------------------------------
    if(Conf["PLOT_L1_RATE"] == 1):
        # Read the cols we need from POS file
        PreproObsData = read_csv(PreproObsFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[PreproIdx["SOD"],PreproIdx["ELEV"],PreproIdx["VALID"],PreproIdx["PHASE RATE"]])

        print( 'Plot Phase Rate vs Time ...')
      
        # Configure plot and call plot generation function
        plotPhaseRate(PreproObsFile, PreproObsData)

    # Code Rate Step vs Time
    # ----------------------------------------------------------
    if(Conf["PLOT_C1_RATE_STEP"] == 1):
        # Read the cols we need from POS file
        PreproObsData = read_csv(PreproObsFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[PreproIdx["SOD"],PreproIdx["ELEV"],PreproIdx["VALID"],PreproIdx["CODE ACC"]])

        print( 'Plot Code Rate Step vs Time ...')
      
        # Configure plot and call plot generation function
        plotCodeRateStep(PreproObsFile, PreproObsData)

    # Phase Rate Step vs Time
    # ----------------------------------------------------------
    if(Conf["PLOT_L1_RATE_STEP"] == 1):
        # Read the cols we need from POS file
        PreproObsData = read_csv(PreproObsFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[PreproIdx["SOD"],PreproIdx["ELEV"],PreproIdx["VALID"],PreproIdx["PHASE ACC"]])

        print( 'Plot Phase Rate Step vs Time ...')
      
        # Configure plot and call plot generation function
        plotPhaseRateStep(PreproObsFile, PreproObsData)
    
    # Phase Rate Step vs Time
    # ----------------------------------------------------------
    if(Conf["PLOT_VTEC"] == 1):
        # Read the cols we need from POS file
        PreproObsData = read_csv(PreproObsFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[PreproIdx["SOD"],PreproIdx["ELEV"],PreproIdx["VALID"],PreproIdx["VTEC RATE"]])

        print( 'Plot VTEC Gradient vs Time ...')
      
        # Configure plot and call plot generation function
        plotVtecGradient(PreproObsFile, PreproObsData)

    # AATR Index vs Time
    # ----------------------------------------------------------
    if(Conf["PLOT_AATR_INDEX"] == 1):
        # Read the cols we need from POS file
        PreproObsData = read_csv(PreproObsFile, delim_whitespace=True, skiprows=1, header=None,\
        usecols=[PreproIdx["SOD"],PreproIdx["ELEV"],PreproIdx["VALID"],PreproIdx["iAATR"]])

        print( 'Plot AATR Index vs Time ...')
      
        # Configure plot and call plot generation function
        plotAatr(PreproObsFile, PreproObsData)

    