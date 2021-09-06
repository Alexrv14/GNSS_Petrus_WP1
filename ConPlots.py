#!/usr/bin/env python

########################################################################
# PETRUS/SRC/Preprocessing.py:
# This is the Inputs (conf and input files) Module of PETRUS tool
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
from collections import OrderedDict

# Plots configuration flags
Conf = OrderedDict({})
Conf["PLOT_VIS"] = 1
Conf["PLOT_NSAT"] = 1
Conf["PLOT_POLAR"] = 1
Conf["PLOT_SATS_FLAGS"] = 1
Conf["PLOT_C1_C1SMOOTHED_T"] = 1
Conf["PLOT_C1_C1SMOOTHED_E"] = 1
Conf["PLOT_C1_RATE"] = 1
Conf["PLOT_L1_RATE"] = 1
Conf["PLOT_C1_RATE_STEP"] = 1
Conf["PLOT_L1_RATE_STEP"] = 1
Conf["PLOT_VTEC"] = 1
Conf["PLOT_AATR_INDEX"] = 1
