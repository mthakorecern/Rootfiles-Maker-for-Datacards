import ROOT
import argparse  ##Importing root and package to take arguments

# from variables import *
import os
from array import array
import glob
from re import search
import re
from datetime import datetime

variableAxisTitleDictionary = {"X_m": "X_Mass (GeV)"}


class MakeHistograms(object):
    # constructor to initialize the objects
    def __init__(self, RootFilePath, RootFileName, userWeight="1.0"):
        self.RootFileName = ROOT.TFile(RootFilePath + RootFileName + ".root")
        self.HistogramName = None
        self.userWeight = userWeight

    def CreateCutString(self, standardCutString, otherCuts, weighting):
        # cutString = weighting+'*('+standardCutString+' && '
        if standardCutString != None:
            cutString = weighting + "*(" + "(" + standardCutString + ")" + " && "
            if otherCuts != None:
                for cut in otherCuts:
                    cutString += "(" + cut + ")" + " && "
        else:
            cutString = weighting + " && "
        cutString = cutString[
            : len(cutString) - 3
        ]  # removing the && at the very end of the final cutstring
        cutString += ")"
        return cutString

    # Histogram Making member function and storing it in an attribute
    def StandardDraw(
        self,
        theFile,
        variable,
        standardCutString,
        additionalSelections,
        histogramName,
        theWeight="FinalWeighting",
    ):
        bin_edges = [
            750,
            900,
            1050,
            1200,
            1350,
            1500,
            1650,
            1800,
            1950,
            2200,
            2450,
            5500,
        ]

        n_bins = len(bin_edges) - 1
        theTree = theFile.Get("Events")
        histogram = ROOT.TH1F(histogramName, "Title", n_bins, array("d", bin_edges))
        theTree.Draw(
            variable + ">>" + histogramName,
            self.CreateCutString(standardCutString, additionalSelections, theWeight),
        )
        try:
            theHisto = ROOT.gDirectory.Get(histogramName).Clone()
        except ReferenceError:
            theHisto = None
        self.HistogramName = theHisto


def clubHistograms(list, histObjects):
    clubHist = None
    for name in list:
        if histObjects[name].HistogramName != None:
            if clubHist == None:
                clubHist = histObjects[name].HistogramName.Clone()
                continue
            clubHist.Add(histObjects[name].HistogramName)
    return clubHist


def main():
    parser = argparse.ArgumentParser(
        description="Create a input root files for combine DataCard."
    )
    parser.add_argument(
        "--year",
        nargs="?",
        choices=["2024"],
        help="Use the file's fake factor weightings when making plots for these files.",
        required=True,
    )
    parser.add_argument("--batchMode", help="run in batch mode", action="store_true")

    parser.add_argument(
        "--variables",
        nargs="+",
        help="Variables to draw the control plots for",
        default=["X_m"],
    )

    parser.add_argument(
        "--Channel", choices=["tt", "et", "mt", "all", "lt"], required=True
    )
    parser.add_argument(
        "--update", help="Update exsiting ROOT file", action="store_true"
    )
    parser.add_argument(
        "--recreate", help="Recreate exsiting ROOT file", action="store_true"
    )
    parser.add_argument(
        "--doSystematics",
        help="Produce systematic variation histograms. Default: nominal histograms only.",
        action="store_true",
    )
    parser.add_argument("--Path", help="path to the files", required=True)

    parser.add_argument("--Output", "-o", help="output folder", required=True)

    args = parser.parse_args()

    ROOT.gStyle.SetOptStat(0)
    ROOT.gROOT.SetBatch(ROOT.kTRUE)

    # change the standard cut definition if that's available

    bandregion = ["SR", "SB"]
    for band in bandregion:
        print(
            "\n\n\n\n\n\n\n\n\n>>>>>>>>>>Processing for ",
            band,
            " ...................\n\n\n",
        )
        if args.year == "2024":
            year_unc = "2024"
            dataPath = args.Path

        # Consider all Radion Signals
        # Remove the QCD Files
        fnames = list(
            set(glob.glob(args.Path + "/*.root"))
            - set(glob.glob(args.Path + "/QCD*.root"))
        )

        # List to hold all the dataset names
        DatasetNameList = []
        SignalNameList = []
        # TTbar and single-Top merged into one, rest are merged into others
        TopNameList = []
        OthersNameList = []

        # One to hold the Data
        # Data_HistoList = []

        for file in fnames:
            nameStrip = file.strip()
            filename = (nameStrip.split("/")[-1]).split(".")[-2]
            if not search("Radion", filename):
                DatasetNameList.append(filename)
            else:
                SignalNameList.append(filename)

            if search("^(TTto)", filename) or search(
                "^(TbarBQ|TbarB|TbarWplus|TBbarQ|TBbar|TWminus)", filename
            ):
                TopNameList.append(filename)
            if search("^(DY)", filename):
                OthersNameList.append(filename)
            if search("^(Wto)", filename):
                OthersNameList.append(filename)
            if search("^QCD", filename):
                # if (band == "SB" and args.Channel=="lt" and search("QCD_HT500to700", filename)):
                #   continue
                OthersNameList.append(filename)
            if (
                search("^(WW)", filename)
                or search("^(WZ)", filename)
                or search("^(ZZ)", filename)
            ):
                OthersNameList.append(filename)

            # if search("MET", filename) or search("Run", filename):
            #     Data_HistoList.append(filename)

        print("\n\n\nSignal Samples = [  ", SignalNameList, " ]")
        print("\n\n\nTTbar plus SingleTop Samples = [  ", TopNameList, " ]")
        print("\n\n\nRest of the MC background Samples = [  ", OthersNameList, " ]")
        # print("\n\n\nData Files = [ ", Data_HistoList, " ]")
        print("\n\n\n>>>SANITY CHECK>>>>")
        if (len(TopNameList) + len(OthersNameList)) == len(DatasetNameList):
            print(
                "\n\n\nGrouping success...Sum of groups = ",
                (len(TopNameList) + len(OthersNameList)),
                " Total = ",
                len(DatasetNameList),
            )
        else:
            print("\n\n\nERROR!#! - Please check the sample grouping")

        ########################################################################################################
        variable = "X_m"

        if year_unc == "2024":
            Weight_signal = "xsWeight*pileupcorrWeight*ewkWDeborahsWeight*qcdWWeight*WnnloWeight*ewkZDeborahsWeight*qcdZTo2LWeight*ZnnloWeight*hpstauidWeight*(138.0/109.95)"
            Weight_bkg = "xsWeight*pileupcorrWeight*ewkWDeborahsWeight*qcdWWeight*WnnloWeight*ewkZDeborahsWeight*qcdZTo2LWeight*ZnnloWeight*hpstauidWeight*(138.0/109.95)"

        if band == "SR":
            GlobalparT3cut = " && ((FatJet_globalParT3Xbb_mass[index_gFatJets[0]] >=100) && (FatJet_globalParT3Xbb_mass[index_gFatJets[0]]<=150))"
        elif band == "SB":
            GlobalparT3cut = " && ((FatJet_globalParT3Xbb_mass[index_gFatJets[0]]>=0) && ((FatJet_globalParT3Xbb_mass[index_gFatJets[0]]<100) || (FatJet_globalParT3Xbb_mass[index_gFatJets[0]]>150)))"

        if args.Channel == "tt":
            standardCutString = (
                "(channel==0) && (HTTvis_deltaR<1.5) && (abs(Hbb_met_phi)>1) && (HTTvis_m>20) && (ngood_UparTMediumJets==0) && (FatJet_globalParT3_XbbvsQCD[index_gFatJets[0]] >= 0.95) && (X_m>=750) && (X_m<=5500) && (FatJet_msoftdrop[index_gFatJets[0]]>=30) && (boostedTau_rawBoostedDeepTauRunIIv2p0VSjet[index_gboostedTaus[0]] >= 0.85) && (boostedTau_rawBoostedDeepTauRunIIv2p0VSjet[index_gboostedTaus[1]] >= 0.85)"
                + GlobalparT3cut
            )
        # elif args.Channel == "et":
        #     standardCutString = (
        #         "(channel==1) && (HTTvis_deltaR<1.5) && (abs(Hbb_met_phi)>1) && (HTTvis_m>20) && (ngood_UparTMediumJets==0) && (FatJet_globalParT3_XbbvsQCD[index_gFatJets[0]] >= 0.95) && (X_m>=750) && (X_m<=5500) && (FatJet_msoftdrop[index_gFatJets[0]]>=30)"
        #         + GlobalparT3cut
        #     )
        # elif args.Channel == "mt":
        #     standardCutString = (
        #         "(channel==2) && (HTTvis_deltaR<1.5) && (abs(Hbb_met_phi)>1) && (HTTvis_m>20) && (ngood_UparTMediumJets==0) && (FatJet_globalParT3_XbbvsQCD[index_gFatJets[0]] >= 0.95) && (X_m>=750) && (X_m<=5500) && (FatJet_msoftdrop[index_gFatJets[0]]>=30)"
        #         + GlobalparT3cut
        #     )
        elif args.Channel == "lt":
            standardCutString = (
                "((channel==1) || (channel==2)) && (HTTvis_deltaR<1.5) && (abs(Hbb_met_phi)>1) && (HTTvis_m>20) && (ngood_UparTMediumJets==0) && (FatJet_globalParT3_XbbvsQCD[index_gFatJets[0]] >= 0.95) && (X_m>=750) && (X_m<=5500) && (FatJet_msoftdrop[index_gFatJets[0]]>=30) && (boostedTau_rawBoostedDeepTauRunIIv2p0VSjet[index_gboostedTaus[0]] >= 0.85)"
                + GlobalparT3cut
            )

        if not os.path.exists(args.Output):
            os.makedirs(args.Output)
            print(f"Created directory: {args.Output}")

        if args.update:
            # outputRootFile= ROOT.TFile(args.year+'_allHists_SignalRegion_1fb_bin60gev.root', 'UPDATE')
            # outputRootFile= ROOT.TFile('StoreRootFiles/Default_AK8pt200GeV_RelIso'+'/'+args.year+'_allHists_SignalRegion_1fb_varbin.root', 'UPDATE')
            if band == "SR":
                outputRootFile = ROOT.TFile(
                    args.Output
                    + "/"
                    + args.year
                    + "_allHists_SignalRegion_1fb_varbin.root",
                    "UPDATE",
                )
            elif band == "SB":
                outputRootFile = ROOT.TFile(
                    args.Output
                    + "/"
                    + args.year
                    + "_allHists_SideBand_1fb_varbin.root",
                    "UPDATE",
                )

        elif args.recreate:
            # outputRootFile= ROOT.TFile('StoreRootFiles/Default_AK8pt200GeV_RelIso'+'/'+args.year+'_allHists_SignalRegion_1fb_varbin.root', 'RECREATE')
            if band == "SR":
                outputRootFile = ROOT.TFile(
                    args.Output
                    + "/"
                    + args.year
                    + "_allHists_SignalRegion_1fb_varbin.root",
                    "RECREATE",
                )
            elif band == "SB":
                outputRootFile = ROOT.TFile(
                    args.Output
                    + "/"
                    + args.year
                    + "_allHists_SideBand_1fb_varbin.root",
                    "RECREATE",
                )

        else:
            print("Please enter the option to either recreate or update a root file")
            exit()
        outputRootFile.cd()
        RootFiledir = outputRootFile.mkdir(args.Channel + "_" + args.year)
        RootFiledir.cd()
        # try:
        # variableSettingDictionary[variable] != None
        # except KeyError:
        # print("No defined histogram settings for variable: "+variable)
        # try:
        # variableAxisTitleDictionary[variable]
        # except KeyError:
        # print("No defined title information for variable: "+variable)

        # Before drawing the histograms, we need to get the write weight

        def CreateClubAndStoreHists(
            DatasetNameList,
            variableToPlot,
            SignalNameList,
            Weight_signal,
            Weight_bkg,
            standardCutString,
            systematics=None,
            var=None,
            verbose=False,
        ):
            # print("This is addtional selections for the channel added to the draw string = ", additionalSelections)
            DatasetObjects = {}
            for index in range(len(DatasetNameList)):
                DatasetObjects[DatasetNameList[index]] = MakeHistograms(
                    dataPath, DatasetNameList[index]
                )
            for index in range(len(DatasetNameList)):
                # if search("MET", DatasetNameList[index]) or search(
                #     "Run", DatasetNameList[index]
                # ):
                #     if systematics == None:
                #         DatasetObjects[DatasetNameList[index]].StandardDraw(
                #             DatasetObjects[DatasetNameList[index]].RootFileName,
                #             variableToPlot,
                #             # args.standardCutString,
                #             standardCutString,
                #             # args.additionalSelections,
                #             None,
                #             # additionalSelections,
                #             DatasetNameList[index],
                #             theWeight="1",
                #         )
                # else:
                DatasetObjects[DatasetNameList[index]].StandardDraw(
                    DatasetObjects[DatasetNameList[index]].RootFileName,
                    variableToPlot,
                    # args.standardCutString,
                    standardCutString,
                    # args.additionalSelections,
                    None,
                    # additionalSelections,
                    DatasetNameList[index],
                    theWeight=Weight_bkg,
                )
            SignalObjects = {}
            for index in range(len(SignalNameList)):
                SignalObjects[SignalNameList[index]] = MakeHistograms(
                    dataPath, SignalNameList[index]
                )
            for index in range(len(SignalNameList)):
                # print (SignalNameList[index])
                SignalObjects[SignalNameList[index]].StandardDraw(
                    SignalObjects[SignalNameList[index]].RootFileName,
                    variableToPlot,
                    # args.standardCutString,
                    standardCutString,
                    # args.additionalSelections,
                    None,
                    # additionalSelections,
                    SignalNameList[index],
                    theWeight="0.001*" + Weight_signal,
                )
            ########################Signal-Histogram#############################
            # Signal_Histo = [SignalObjects["RadionTohhTohtatahbb_narrow_M-1000"].HistogramName.Clone(),SignalObjects["RadionTohhTohtatahbb_narrow_M-2000"].HistogramName.Clone(),SignalObjects["RadionTohhTohtatahbb_narrow_M-3000"].HistogramName.Clone(),SignalObjects["RadionTohhTohtatahbb_narrow_M-4000"].HistogramName.Clone()]
            #####################################################################
            ####################################TT-Histograms######################################
            Top_Histo = clubHistograms(TopNameList, DatasetObjects)
            Others_Histo = clubHistograms(OthersNameList, DatasetObjects)
            radion_1000 = clubHistograms(
                [
                    "GluGlutoRadiontoHHto2B2Tau_M-1000_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                ],
                SignalObjects,
            )
            radion_1200 = clubHistograms(
                [
                    "GluGlutoRadiontoHHto2B2Tau_M-1200_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                ],
                SignalObjects,
            )
            radion_1400 = clubHistograms(
                [
                    "GluGlutoRadiontoHHto2B2Tau_M-1400_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                ],
                SignalObjects,
            )
            radion_1600 = clubHistograms(
                [
                    "GluGlutoRadiontoHHto2B2Tau_M-1600_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                ],
                SignalObjects,
            )
            radion_1800 = clubHistograms(
                [
                    "GluGlutoRadiontoHHto2B2Tau_M-1800_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                ],
                SignalObjects,
            )
            radion_2000 = clubHistograms(
                [
                    "GluGlutoRadiontoHHto2B2Tau_M-2000_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                ],
                SignalObjects,
            )
            radion_2500 = clubHistograms(
                [
                    "GluGlutoRadiontoHHto2B2Tau_M-2500_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                ],
                SignalObjects,
            )
            radion_3000 = clubHistograms(
                [
                    "GluGlutoRadiontoHHto2B2Tau_M-3000_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                ],
                SignalObjects,
            )
            radion_3500 = clubHistograms(
                [
                    "GluGlutoRadiontoHHto2B2Tau_M-3500_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                ],
                SignalObjects,
            )
            radion_4000 = clubHistograms(
                [
                    "GluGlutoRadiontoHHto2B2Tau_M-4000_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                ],
                SignalObjects,
            )
            radion_4500 = clubHistograms(
                [
                    "GluGlutoRadiontoHHto2B2Tau_M-4500_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                ],
                SignalObjects,
            )
            # radion_1000 = clubHistograms(["RadionTohhTohtatahbb_narrow_M-1000","RadionToHHTo2B2VTo2L2Nu_M-1000","RadionToHHTo2B2WToLNu2J_M-1000"],SignalObjects)
            # radion_1200 = clubHistograms(["RadionTohhTohtatahbb_narrow_M-1200","RadionToHHTo2B2VTo2L2Nu_M-1200","RadionToHHTo2B2WToLNu2J_M-1200"],SignalObjects)
            # radion_1400 = clubHistograms(["RadionTohhTohtatahbb_narrow_M-1400","RadionToHHTo2B2VTo2L2Nu_M-1400","RadionToHHTo2B2WToLNu2J_M-1400"],SignalObjects)
            # radion_1600 = clubHistograms(["RadionTohhTohtatahbb_narrow_M-1600","RadionToHHTo2B2VTo2L2Nu_M-1600","RadionToHHTo2B2WToLNu2J_M-1600"],SignalObjects)
            # radion_1800 = clubHistograms(["RadionTohhTohtatahbb_narrow_M-1800","RadionToHHTo2B2VTo2L2Nu_M-1800","RadionToHHTo2B2WToLNu2J_M-1800"],SignalObjects)
            # radion_2000 = clubHistograms(["RadionTohhTohtatahbb_narrow_M-2000","RadionToHHTo2B2VTo2L2Nu_M-2000","RadionToHHTo2B2WToLNu2J_M-2000"],SignalObjects)
            # radion_2500 = clubHistograms(["RadionTohhTohtatahbb_narrow_M-2500","RadionToHHTo2B2VTo2L2Nu_M-2500","RadionToHHTo2B2WToLNu2J_M-2500"],SignalObjects)
            # radion_3000 = clubHistograms(["RadionTohhTohtatahbb_narrow_M-3000","RadionToHHTo2B2VTo2L2Nu_M-3000","RadionToHHTo2B2WToLNu2J_M-3000"],SignalObjects)
            # radion_3500 = clubHistograms(["RadionTohhTohtatahbb_narrow_M-3500","RadionToHHTo2B2VTo2L2Nu_M-3500","RadionToHHTo2B2WToLNu2J_M-3500"],SignalObjects)
            # radion_4000 = clubHistograms(["RadionTohhTohtatahbb_narrow_M-4000","RadionToHHTo2B2VTo2L2Nu_M-4000","RadionToHHTo2B2WToLNu2J_M-4000"],SignalObjects)
            # radion_4500 = clubHistograms(["RadionTohhTohtatahbb_narrow_M-4500","RadionToHHTo2B2VTo2L2Nu_M-4500","RadionToHHTo2B2WToLNu2J_M-4500"],SignalObjects)

            ########################################################################################
            #########CLUB Data Histograms################################
            # Should a sumw2 be done for the data histogram? - or it is fine as is??
            Data_Histo = None
            if systematics == None:
                # Data_Histo = clubHistograms(Data_HistoList, DatasetObjects)
                Data_Histo = Top_Histo.Clone("data_obs")
                Data_Histo.Add(Others_Histo)
                Data_Histo.SetMarkerStyle(20)
                Data_Histo.SetMarkerSize(0.7)

            if verbose:
                print(
                    "Number of events in TTBar + ST (incl over and under) = ",
                    Top_Histo.Integral(0, Top_Histo.GetNbinsX() + 1),
                )
                print(
                    "Number of events in rest of the backgrounds (incl over and under) = ",
                    Others_Histo.Integral(0, Others_Histo.GetNbinsX() + 1),
                )
                print(
                    "Total Background (incl over and under) = ",
                    Top_Histo.Integral(0, Top_Histo.GetNbinsX() + 1)
                    + Others_Histo.Integral(0, Others_Histo.GetNbinsX() + 1),
                )
                # print ("Number of events for the 1 TeV (incl over and under) = ",Signal_Histo[0].Integral(0,Signal_Histo[0].GetNbinsX()+1))
                # print ("Number of events for the 2 TeV (incl over and under) = ",Signal_Histo[1].Integral(0,Signal_Histo[1].GetNbinsX()+1))
                # print ("Number of events for the 3 TeV (incl over and under) = ",Signal_Histo[2].Integral(0,Signal_Histo[2].GetNbinsX()+1))
                # print ("Number of events for the 4 TeV (incl over and under) = ",Signal_Histo[3].Integral(0,Signal_Histo[3].GetNbinsX()+1))
                print("\n\n\n")
                print(
                    "Number of events for the bbtt 1.0 TeV (incl over and under) = ",
                    SignalObjects[
                        "GluGlutoRadiontoHHto2B2Tau_M-1000_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                    ].HistogramName.Integral(
                        0,
                        SignalObjects[
                            "GluGlutoRadiontoHHto2B2Tau_M-1000_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                        ].HistogramName.GetNbinsX()
                        + 1,
                    ),
                )
                print(
                    "Number of events for the bbtt 1.2 TeV (incl over and under) = ",
                    SignalObjects[
                        "GluGlutoRadiontoHHto2B2Tau_M-1200_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                    ].HistogramName.Integral(
                        0,
                        SignalObjects[
                            "GluGlutoRadiontoHHto2B2Tau_M-1200_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                        ].HistogramName.GetNbinsX()
                        + 1,
                    ),
                )
                print(
                    "Number of events for the bbtt 1.4 TeV (incl over and under) = ",
                    SignalObjects[
                        "GluGlutoRadiontoHHto2B2Tau_M-1400_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                    ].HistogramName.Integral(
                        0,
                        SignalObjects[
                            "GluGlutoRadiontoHHto2B2Tau_M-1400_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                        ].HistogramName.GetNbinsX()
                        + 1,
                    ),
                )
                print(
                    "Number of events for the bbtt 1.6 TeV (incl over and under) = ",
                    SignalObjects[
                        "GluGlutoRadiontoHHto2B2Tau_M-1600_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                    ].HistogramName.Integral(
                        0,
                        SignalObjects[
                            "GluGlutoRadiontoHHto2B2Tau_M-1600_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                        ].HistogramName.GetNbinsX()
                        + 1,
                    ),
                )
                print(
                    "Number of events for the bbtt 1.8 TeV (incl over and under) = ",
                    SignalObjects[
                        "GluGlutoRadiontoHHto2B2Tau_M-1800_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                    ].HistogramName.Integral(
                        0,
                        SignalObjects[
                            "GluGlutoRadiontoHHto2B2Tau_M-1800_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                        ].HistogramName.GetNbinsX()
                        + 1,
                    ),
                )
                print(
                    "Number of events for the bbtt 2.0 TeV (incl over and under) = ",
                    SignalObjects[
                        "GluGlutoRadiontoHHto2B2Tau_M-2000_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                    ].HistogramName.Integral(
                        0,
                        SignalObjects[
                            "GluGlutoRadiontoHHto2B2Tau_M-2000_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                        ].HistogramName.GetNbinsX()
                        + 1,
                    ),
                )
                print(
                    "Number of events for the bbtt 2.5 TeV (incl over and under) = ",
                    SignalObjects[
                        "GluGlutoRadiontoHHto2B2Tau_M-2500_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                    ].HistogramName.Integral(
                        0,
                        SignalObjects[
                            "GluGlutoRadiontoHHto2B2Tau_M-2500_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                        ].HistogramName.GetNbinsX()
                        + 1,
                    ),
                )
                print(
                    "Number of events for the bbtt 3.0 TeV (incl over and under) = ",
                    SignalObjects[
                        "GluGlutoRadiontoHHto2B2Tau_M-3000_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                    ].HistogramName.Integral(
                        0,
                        SignalObjects[
                            "GluGlutoRadiontoHHto2B2Tau_M-3000_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                        ].HistogramName.GetNbinsX()
                        + 1,
                    ),
                )
                print(
                    "Number of events for the bbtt 3.5 TeV (incl over and under) = ",
                    SignalObjects[
                        "GluGlutoRadiontoHHto2B2Tau_M-3500_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                    ].HistogramName.Integral(
                        0,
                        SignalObjects[
                            "GluGlutoRadiontoHHto2B2Tau_M-3500_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                        ].HistogramName.GetNbinsX()
                        + 1,
                    ),
                )
                print(
                    "Number of events for the bbtt 4.0 TeV (incl over and under) = ",
                    SignalObjects[
                        "GluGlutoRadiontoHHto2B2Tau_M-4000_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                    ].HistogramName.Integral(
                        0,
                        SignalObjects[
                            "GluGlutoRadiontoHHto2B2Tau_M-4000_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                        ].HistogramName.GetNbinsX()
                        + 1,
                    ),
                )
                print(
                    "Number of events for the bbtt 4.5 TeV (incl over and under) = ",
                    SignalObjects[
                        "GluGlutoRadiontoHHto2B2Tau_M-4500_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                    ].HistogramName.Integral(
                        0,
                        SignalObjects[
                            "GluGlutoRadiontoHHto2B2Tau_M-4500_narrow_TuneCP5_13p6TeV_madgraph-pythia8"
                        ].HistogramName.GetNbinsX()
                        + 1,
                    ),
                )
                print("\n\n\n")
                print(
                    "Number of events for the 1.0 TeV (incl over and under) = ",
                    radion_1000.Integral(0, radion_1000.GetNbinsX() + 1),
                )
                print(
                    "Number of events for the 1.2 TeV (incl over and under) = ",
                    radion_1200.Integral(0, radion_1200.GetNbinsX() + 1),
                )
                print(
                    "Number of events for the 1.4 TeV (incl over and under) = ",
                    radion_1400.Integral(0, radion_1400.GetNbinsX() + 1),
                )
                print(
                    "Number of events for the 1.6 TeV (incl over and under) = ",
                    radion_1600.Integral(0, radion_1600.GetNbinsX() + 1),
                )
                print(
                    "Number of events for the 1.8 TeV (incl over and under) = ",
                    radion_1800.Integral(0, radion_1800.GetNbinsX() + 1),
                )
                print(
                    "Number of events for the 2.0 TeV (incl over and under) = ",
                    radion_2000.Integral(0, radion_2000.GetNbinsX() + 1),
                )
                print(
                    "Number of events for the 2.5 TeV (incl over and under) = ",
                    radion_2500.Integral(0, radion_2500.GetNbinsX() + 1),
                )
                print(
                    "Number of events for the 3.0 TeV (incl over and under) = ",
                    radion_3000.Integral(0, radion_3000.GetNbinsX() + 1),
                )
                print(
                    "Number of events for the 3.5 TeV (incl over and under) = ",
                    radion_3500.Integral(0, radion_3500.GetNbinsX() + 1),
                )
                print(
                    "Number of events for the 4.0 TeV (incl over and under) = ",
                    radion_4000.Integral(0, radion_4000.GetNbinsX() + 1),
                )
                print(
                    "Number of events for the 4.5 TeV (incl over and under) = ",
                    radion_4500.Integral(0, radion_4500.GetNbinsX() + 1),
                )
                print("\n\n\n")
                # print ("Number of events for the 2 TeV (incl over and under) = ",Signal_Histo[1].Integral(0,Signal_Histo[1].GetNbinsX()+1))
                # print ("Number of events for the 3 TeV (incl over and under) = ",Signal_Histo[2].Integral(0,Signal_Histo[2].GetNbinsX()+1))
                # print ("Number of events for the 4 TeV (incl over and under) = ",Signal_Histo[3].Integral(0,Signal_Histo[3].GetNbinsX()+1))
                # print(
                #     "Number of events of Data (incl over and under) = ",
                #     Data_Histo.Integral(0, Data_Histo.GetNbinsX() + 1),
                # )
                if systematics is None:
                    print(
                        "Asimov data_obs yield = ",
                        Data_Histo.Integral(0, Data_Histo.GetNbinsX() + 1),
                    )
            if systematics != None:
                # RootFiledir.WriteObject(SignalObjects["RadionTohhTohtatahbb_narrow_M-1000"].HistogramName,"radion1000_"+systematic+var)
                # RootFiledir.WriteObject(SignalObjects["RadionTohhTohtatahbb_narrow_M-1200"].HistogramName,"radion1200_"+systematic+var)
                # RootFiledir.WriteObject(SignalObjects["RadionTohhTohtatahbb_narrow_M-1400"].HistogramName,"radion1400_"+systematic+var)
                # RootFiledir.WriteObject(SignalObjects["RadionTohhTohtatahbb_narrow_M-1600"].HistogramName,"radion1600_"+systematic+var)
                # RootFiledir.WriteObject(SignalObjects["RadionTohhTohtatahbb_narrow_M-1800"].HistogramName,"radion1800_"+systematic+var)
                # RootFiledir.WriteObject(SignalObjects["RadionTohhTohtatahbb_narrow_M-2000"].HistogramName,"radion2000_"+systematic+var)
                # RootFiledir.WriteObject(SignalObjects["RadionTohhTohtatahbb_narrow_M-2500"].HistogramName,"radion2500_"+systematic+var)
                # RootFiledir.WriteObject(SignalObjects["RadionTohhTohtatahbb_narrow_M-3000"].HistogramName,"radion3000_"+systematic+var)
                # RootFiledir.WriteObject(SignalObjects["RadionTohhTohtatahbb_narrow_M-3500"].HistogramName,"radion3500_"+systematic+var)
                # RootFiledir.WriteObject(SignalObjects["RadionTohhTohtatahbb_narrow_M-4000"].HistogramName,"radion4000_"+systematic+var)
                # RootFiledir.WriteObject(SignalObjects["RadionTohhTohtatahbb_narrow_M-4500"].HistogramName,"radion4500_"+systematic+var)
                RootFiledir.WriteObject(radion_1000, "radion1000_" + systematics + var)
                RootFiledir.WriteObject(radion_1200, "radion1200_" + systematics + var)
                RootFiledir.WriteObject(radion_1400, "radion1400_" + systematics + var)
                RootFiledir.WriteObject(radion_1600, "radion1600_" + systematics + var)
                RootFiledir.WriteObject(radion_1800, "radion1800_" + systematics + var)
                RootFiledir.WriteObject(radion_2000, "radion2000_" + systematics + var)
                RootFiledir.WriteObject(radion_2500, "radion2500_" + systematics + var)
                RootFiledir.WriteObject(radion_3000, "radion3000_" + systematics + var)
                RootFiledir.WriteObject(radion_3500, "radion3500_" + systematics + var)
                RootFiledir.WriteObject(radion_4000, "radion4000_" + systematics + var)
                RootFiledir.WriteObject(radion_4500, "radion4500_" + systematics + var)
                RootFiledir.WriteObject(Top_Histo, "top_" + systematics + var)
                RootFiledir.WriteObject(Others_Histo, "others_" + systematics + var)
            else:
                # RootFiledir.WriteObject(SignalObjects["RadionTohhTohtatahbb_narrow_M-1000"].HistogramName,"radion1000")
                # RootFiledir.WriteObject(SignalObjects["RadionTohhTohtatahbb_narrow_M-1200"].HistogramName,"radion1200")
                # RootFiledir.WriteObject(SignalObjects["RadionTohhTohtatahbb_narrow_M-1400"].HistogramName,"radion1400")
                # RootFiledir.WriteObject(SignalObjects["RadionTohhTohtatahbb_narrow_M-1600"].HistogramName,"radion1600")
                # RootFiledir.WriteObject(SignalObjects["RadionTohhTohtatahbb_narrow_M-1800"].HistogramName,"radion1800")
                # RootFiledir.WriteObject(SignalObjects["RadionTohhTohtatahbb_narrow_M-2000"].HistogramName,"radion2000")
                # RootFiledir.WriteObject(SignalObjects["RadionTohhTohtatahbb_narrow_M-2500"].HistogramName,"radion2500")
                # RootFiledir.WriteObject(SignalObjects["RadionTohhTohtatahbb_narrow_M-3000"].HistogramName,"radion3000")
                # RootFiledir.WriteObject(SignalObjects["RadionTohhTohtatahbb_narrow_M-3500"].HistogramName,"radion3500")
                # RootFiledir.WriteObject(SignalObjects["RadionTohhTohtatahbb_narrow_M-4000"].HistogramName,"radion4000")
                # RootFiledir.WriteObject(SignalObjects["RadionTohhTohtatahbb_narrow_M-4500"].HistogramName,"radion4500")

                RootFiledir.WriteObject(radion_1000, "radion1000")
                RootFiledir.WriteObject(radion_1200, "radion1200")
                RootFiledir.WriteObject(radion_1400, "radion1400")
                RootFiledir.WriteObject(radion_1600, "radion1600")
                RootFiledir.WriteObject(radion_1800, "radion1800")
                RootFiledir.WriteObject(radion_2000, "radion2000")
                RootFiledir.WriteObject(radion_2500, "radion2500")
                RootFiledir.WriteObject(radion_3000, "radion3000")
                RootFiledir.WriteObject(radion_3500, "radion3500")
                RootFiledir.WriteObject(radion_4000, "radion4000")
                RootFiledir.WriteObject(radion_4500, "radion4500")

                RootFiledir.WriteObject(Top_Histo, "top")
                RootFiledir.WriteObject(Others_Histo, "others")
                RootFiledir.WriteObject(Data_Histo, "data_obs")

            del DatasetObjects
            del SignalObjects

        # print("This is additional selections = ", additionalSelections)
        print("\n\n\n>>>>>>>>>>>>>>>>>STRINGS for nominal>>>>>>>>>>>>>>>>>>>>>>")
        print("This is Selection String = ", standardCutString)
        print("This is Weight String for Background = ", Weight_bkg)
        print("This is Weight String for Signal = ", Weight_signal)
        CreateClubAndStoreHists(
            DatasetNameList,
            "X_m",
            SignalNameList,
            Weight_signal,
            Weight_bkg,
            standardCutString,
            verbose=True,
        )

        if args.doSystematics:
            print(
                "\n\n\n\n\n>>>Next store histograms for the split systematics for W and Z nlo qcd weights >>>>>"
            )
            event_weight_split_systematicslist = ["qcdWWeight", "qcdZTo2LWeight"]
            variation_event_weight_split = ["RenUp", "RenDown", "FacUp", "FacDown"]

            for systematic in event_weight_split_systematicslist:
                for var in variation_event_weight_split:
                    WeightVar_signal = Weight_signal.replace(
                        systematic, systematic + var
                    )
                    WeightVar_bkg = Weight_bkg.replace(systematic, systematic + var)
                    # print ("Weight string for ",systematic," ",var," is = ",WeightVar_signal, WeightVar_bkg)
                    print(
                        "\n\nWeight string for ",
                        systematic + var,
                        "\n\n...bkg = ",
                        WeightVar_bkg,
                        "\n\n...sig = ",
                        WeightVar_signal,
                    )
                    print(
                        "\n\nCutstring for ",
                        systematic + var,
                        "..= ",
                        standardCutString,
                    )
                    CreateClubAndStoreHists(
                        DatasetNameList,
                        "X_m",
                        SignalNameList,
                        WeightVar_signal,
                        WeightVar_bkg,
                        standardCutString,
                        systematics=systematic,
                        var=var,
                    )

            print(
                "\n\n\n\n\n>>>Next store histograms for the split systematics for W and Z EWK weights and top pt reweighting >>>>>"
            )

            event_weight_split_systematicslist = [
                "ewkWDeborahsWeight",
                "ewkZDeborahsWeight",
                "topptWeight",
            ]
            variation_event_weight_split = ["Up", "Down"]

            for systematic in event_weight_split_systematicslist:
                for var in variation_event_weight_split:
                    if var == "Up":
                        WeightVar_signal = Weight_signal.replace(systematic, "1.0")
                        WeightVar_bkg = Weight_bkg.replace(systematic, "1.0")
                        # print ("Weight string for ",systematic," ",var," is = ",WeightVar_signal, WeightVar_bkg)
                        print(
                            "\n\nWeight string for ",
                            systematic + var,
                            "\n\n...bkg = ",
                            WeightVar_bkg,
                            "\n\n...sig = ",
                            WeightVar_signal,
                        )
                        print(
                            "\n\nCutstring for ",
                            systematic + var,
                            "..= ",
                            standardCutString,
                        )
                        CreateClubAndStoreHists(
                            DatasetNameList,
                            "X_m",
                            SignalNameList,
                            WeightVar_signal,
                            WeightVar_bkg,
                            standardCutString,
                            systematics=systematic,
                            var=var,
                        )
                    elif var == "Down":
                        WeightVar_signal = Weight_signal
                        WeightVar_bkg = Weight_bkg
                        # print ("Weight string for ",systematic," ",var," is = ",WeightVar_signal, WeightVar_bkg)
                        print(
                            "\n\nWeight string for ",
                            systematic + var,
                            "\n\n...bkg = ",
                            WeightVar_bkg,
                            "\n\n...sig = ",
                            WeightVar_signal,
                        )
                        print(
                            "\n\nCutstring for ",
                            systematic + var,
                            "..= ",
                            standardCutString,
                        )
                        CreateClubAndStoreHists(
                            DatasetNameList,
                            "X_m",
                            SignalNameList,
                            WeightVar_signal,
                            WeightVar_bkg,
                            standardCutString,
                            systematics=systematic,
                            var=var,
                        )

            print(
                "\n\n\n\n\n>>>Next store histograms for the split systematics for Theory Weights (LHEPDF, QCDscale, LHEScale) >>>>>"
            )
            event_weight_split_systematicslist = [
                "isr",
                "fsr",
                "pdf",
                "qcdscalerenorm",
                "qcdscalefacto",
            ]
            variation_event_weight_split = ["Up", "Down"]

            for systematic in event_weight_split_systematicslist:
                for var in variation_event_weight_split:
                    WeightVar_signal = Weight_signal + "*" + systematic + var
                    WeightVar_bkg = Weight_bkg + "*" + systematic + var
                    # print ("Weight string for ",systematic," ",var," is = ",WeightVar_signal, WeightVar_bkg)
                    print(
                        "\n\nWeight string for ",
                        systematic + var,
                        "\n\n...bkg = ",
                        WeightVar_bkg,
                        "\n\n...sig = ",
                        WeightVar_signal,
                    )
                    print(
                        "\n\nCutstring for ",
                        systematic + var,
                        "..= ",
                        standardCutString,
                    )
                    CreateClubAndStoreHists(
                        DatasetNameList,
                        "X_m",
                        SignalNameList,
                        WeightVar_signal,
                        WeightVar_bkg,
                        standardCutString,
                        systematics=systematic,
                        var=var,
                    )

            print(
                "\n\n\n\n\n>>>Next store histograms for the split systematics for pnet regressed mass >>>>>"
            )
            event_weight_split_systematicslist = ["jmr", "jms"]
            variation_event_weight_split = ["Up", "Down"]

            for systematic in event_weight_split_systematicslist:
                for var in variation_event_weight_split:
                    WeightVar_signal = Weight_signal
                    WeightVar_bkg = Weight_bkg
                    standardCutString_Var = standardCutString.replace(
                        "pnetmassnom", "pnetmass" + systematic + var
                    )
                    # print ("Weight string for ",systematic," ",var," is = ",WeightVar_signal, WeightVar_bkg)
                    print(
                        "\n\nWeight string for ",
                        systematic + var,
                        "\n\n...bkg = ",
                        WeightVar_bkg,
                        "\n\n...sig = ",
                        WeightVar_signal,
                    )
                    print(
                        "\n\nCutstring for ",
                        systematic + var,
                        "..= ",
                        standardCutString_Var,
                    )
                    CreateClubAndStoreHists(
                        DatasetNameList,
                        "X_m",
                        SignalNameList,
                        WeightVar_signal,
                        WeightVar_bkg,
                        standardCutString_Var,
                        systematics=systematic,
                        var=var,
                    )

            print(
                "\n\n\n\n\n>>>Next store histograms for the split systematics for event weights (Btag Systmatics)>>>>>"
            )

            event_weight_split_systematicslist = ["btagmediumWeight"]
            variation_event_weight_split = [
                "bcUp",
                "bcDown",
                "bc%sUp" % (args.year),
                "bc%sDown" % (args.year),
                "lightUp",
                "lightDown",
                "light%sUp" % (args.year),
                "light%sDown" % (args.year),
            ]

            for systematic in event_weight_split_systematicslist:
                for var in variation_event_weight_split:
                    WeightVar_signal = Weight_signal.replace(
                        systematic, systematic + var
                    )
                    WeightVar_bkg = Weight_bkg.replace(systematic, systematic + var)
                    # print ("Weight string for ",systematic," ",var," is = ",WeightVar_signal, WeightVar_bkg)
                    print(
                        "\n\nWeight string for ",
                        systematic + var,
                        "\n\n...bkg = ",
                        WeightVar_bkg,
                        "\n\n...sig = ",
                        WeightVar_signal,
                    )
                    print(
                        "\n\nCutstring for ",
                        systematic + var,
                        "..= ",
                        standardCutString,
                    )
                    CreateClubAndStoreHists(
                        DatasetNameList,
                        "X_m",
                        SignalNameList,
                        WeightVar_signal,
                        WeightVar_bkg,
                        standardCutString,
                        systematics=systematic,
                        var=var,
                    )

            # print ("\n\n>>>Next store histograms for the Special systematics - L1 prefire>>>>>")

            # Now brace ourselves for the systematics
            print("\n\n>>>Next store histograms for the systematics>>>>>")
            variation = ["Up", "Down"]
            # systematicslist = ["pileupWeight","triggerWeight","electronIDWeight","electronRecoWeight","muonIDWeight","muonIsoWeight","HPStauIDWeight"]
            # The OG list
            # systematicslist = ["pileup","trigger","electronID","electronReco","muonID","muonIso","HPStauID"]
            # List for the RelIso test - since the ElectronID and MuonIso could not be applied.
            # systematicslist = ["pileup","trigger","electronReco","muonID","HPStauID"]
            systematicslist = [
                "boosteddeeptauWeight",
                "L1PreFiringWeight_Nom",
                "pileupcorrWeight",
                "metsfWeight",
                "eleidWeight",
                "elerecoWeight",
                "muonidWeight",
                "muonisoWeight",
                "hpstauidWeight",
                "hbblooseWeight",
            ]

            for systematic in systematicslist:
                for var in variation:
                    # First modify the event weight string
                    if var == "Up":
                        if systematic == "hbblooseWeight":
                            WeightVar_signal = Weight_signal.replace(
                                systematic, systematic + var
                            )
                            WeightVar_bkg = Weight_bkg
                        elif systematic == "L1PreFiringWeight_Nom":
                            WeightVar_signal = Weight_signal.replace(
                                systematic, systematic.split("_")[-2] + "_Up"
                            )
                            WeightVar_bkg = Weight_bkg.replace(
                                systematic, systematic.split("_")[-2] + "_Up"
                            )
                        else:
                            WeightVar_signal = Weight_signal.replace(
                                systematic, systematic + var
                            )
                            WeightVar_bkg = Weight_bkg.replace(
                                systematic, systematic + var
                            )
                    elif var == "Down":
                        if systematic == "hbblooseWeight":
                            WeightVar_signal = Weight_signal.replace(
                                systematic, systematic + var
                            )
                            WeightVar_bkg = Weight_bkg
                        elif systematic == "L1PreFiringWeight_Nom":
                            WeightVar_signal = Weight_signal.replace(
                                systematic, systematic.split("_")[-2] + "_Dn"
                            )
                            WeightVar_bkg = Weight_bkg.replace(
                                systematic, systematic.split("_")[-2] + "_Dn"
                            )
                        else:
                            WeightVar_signal = Weight_signal.replace(
                                systematic, systematic + var
                            )
                            WeightVar_bkg = Weight_bkg.replace(
                                systematic, systematic + var
                            )

                    # print ("Weight string for ",systematic," ",var," is = ",WeightVar_signal, WeightVar_bkg)
                    print(
                        "\n\nWeight string for ",
                        systematic + var,
                        "\n\n...bkg = ",
                        WeightVar_bkg,
                        "\n\n...sig = ",
                        WeightVar_signal,
                    )
                    print(
                        "\n\nCutstring for ",
                        systematic + var,
                        "..= ",
                        standardCutString,
                    )
                    if systematic == "L1PreFiringWeight_Nom":
                        print(
                            "Storing the nuisance name in datacards : ",
                            systematic.split("_")[-2],
                        )
                        CreateClubAndStoreHists(
                            DatasetNameList,
                            "X_m",
                            SignalNameList,
                            WeightVar_signal,
                            WeightVar_bkg,
                            standardCutString,
                            systematics=systematic.split("_")[-2],
                            var=var,
                        )
                    else:
                        CreateClubAndStoreHists(
                            DatasetNameList,
                            "X_m",
                            SignalNameList,
                            WeightVar_signal,
                            WeightVar_bkg,
                            standardCutString,
                            systematics=systematic,
                            var=var,
                        )

            # Now brace ourselves for the unorthodox systematics
            # systematicsUnortholist = ["HbbLoose"]
            print(
                "\n\n\n\n\n>>>Next store histograms for the JETS, MET, TES (Systematics affecting the objects)>>>>>"
            )
            systematicsUnortholist = [
                "tesUp",
                "tesDown",
                "jesTotalUp",
                "jesTotalDown",
                "jerUp",
                "jerDown",
                "jesAbsoluteUp",
                "jesAbsoluteDown",
                "jesAbsolute_%sUp" % (year_unc),
                "jesAbsolute_%sDown" % (year_unc),
                "jesBBEC1Up",
                "jesBBEC1Down",
                "jesBBEC1_%sUp" % (year_unc),
                "jesBBEC1_%sDown" % (year_unc),
                "jesEC2Up",
                "jesEC2Down",
                "jesEC2_%sUp" % (year_unc),
                "jesEC2_%sDown" % (year_unc),
                "jesFlavorQCDUp",
                "jesFlavorQCDDown",
                "jesHFUp",
                "jesHFDown",
                "jesHF_%sUp" % (year_unc),
                "jesHF_%sDown" % (year_unc),
                "jesRelativeBalUp",
                "jesRelativeBalDown",
                "jesRelativeSample_%sUp" % (year_unc),
                "jesRelativeSample_%sDown" % (year_unc),
                "UnclustUp",
                "UnclustDown",
            ]

            # Function to modify the cut string for a given systematic
            def modify_cut_string(cut_string, systematic):
                pattern = r"(\w+)([><=!]+)"
                modified_string = re.sub(
                    pattern, r"\1" + systematic + r"\2", cut_string
                )
                return modified_string

            # Function to modify the weight string for a given systematic
            def modify_weight_string(weight_string, systematic, exclusions):
                pattern = (
                    r"\b(" + "|".join(re.escape(var) for var in exclusions) + r")\b"
                )
                modified_weights = [
                    f"{var}{systematic}" if not re.fullmatch(pattern, var) else var
                    for var in weight_string.split("*")
                ]
                return "*".join(modified_weights)

            excluded_weights = [
                "L1PreFiringWeight_Nom",
                "xsWeight",
                "pileupcorrWeight",
                "topptWeight",
                "qcdWWeight",
                "ewkWDeborahsWeight",
                "qcdZTo2LWeight",
                "ewkZDeborahsWeight",
                "WnnloWeight",
                "ZnnloWeight",
            ]

            for systematic in systematicsUnortholist:
                modified_cut_string = modify_cut_string(standardCutString, systematic)
                modified_weightbkg_string = modify_weight_string(
                    Weight_bkg, systematic, excluded_weights
                )
                modified_weightsig_string = modify_weight_string(
                    Weight_signal, systematic, excluded_weights
                )
                print(
                    "\n\nWeight string for ",
                    systematic,
                    "\n\n...bkg = ",
                    modified_weightbkg_string,
                    "\n\n...sig = ",
                    modified_weightsig_string,
                )
                print("\n\nCutstring for ", systematic, "..= ", modified_cut_string)
                print("\n\nVariable to plot..= ", "X_m%s" % (systematic))
                CreateClubAndStoreHists(
                    DatasetNameList,
                    "X_m%s" % (systematic),
                    SignalNameList,
                    modified_weightsig_string,
                    modified_weightbkg_string,
                    modified_cut_string,
                    systematics=systematic,
                    var="",
                )

        else:
            print(
                "\nSystematic production disabled. Only nominal histograms were written."
            )

        outputRootFile.Close()


if __name__ == "__main__":
    start_time = datetime.now()
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    main()

    end_time = datetime.now()
    print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

    duration = end_time - start_time
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    print(f"Total duration: {hours}h {minutes}m {seconds}s")
