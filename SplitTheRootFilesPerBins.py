import ROOT
import os
import argparse
import re
from array import array

# bin_edges = [750, 900, 1050, 1200, 1350, 1500, 1650, 1800, 1950, 2100, 2250, 2500, 2750, 3000, 3250, 3500, 3750, 4000, 4250, 4500, 4750, 5000, 5250, 5500]
# bin_edges = [750, 900, 1050, 5500]
bin_edges = [750, 900, 1050, 1200, 1350, 1500, 1650, 1800, 1950, 2200, 2450, 5500]


def find_year(data_string):
    # Define a regex pattern to match the years/keywords even if they are part of a larger word
    pattern = r"2024"
    match = re.search(pattern, data_string)
    # If there's a match, return it
    if match:
        return match.group(0)
    return None


def split_by_bins(input_file_name, output_dir):
    # Check if output directory exists; if not, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    outputfilename = (input_file_name.strip().split("/")[-1]).split(".")[-2]
    print(
        "This is year = ",
        find_year(outputfilename),
        "...Primary output filename.....",
        outputfilename,
    )
    # Open the input ROOT file
    input_file = ROOT.TFile.Open(input_file_name, "READ")
    if not input_file or input_file.IsZombie():
        print("Error: Could not open input file {}".format(input_file_name))
        return

    # Define the TDirectory names
    # directories = ["tt_{}".format(find_year(outputfilename)), "et_{}".format(find_year(outputfilename)), "mt_{}".format(find_year(outputfilename)),"lt_{}".format(find_year(outputfilename))]
    # directories = ["tt_{}".format(find_year(outputfilename)),"lt_{}".format(find_year(outputfilename))]
    directories = [
        "tt_{}".format(find_year(outputfilename)),
        # "et_{}".format(find_year(outputfilename)),
        # "mt_{}".format(find_year(outputfilename)),
        "lt_{}".format(find_year(outputfilename)),
    ]

    # Check if directories exist in the input file
    for dir_name in directories:
        if not input_file.GetDirectory(dir_name):
            print(
                "Warning: Directory '{}' not found in the input file.".format(dir_name)
            )

    # Get the number of bins from the first histogram (assuming all histograms have the same binning)
    first_hist = None
    for dir_name in directories:
        directory = input_file.GetDirectory(dir_name)
        if directory:
            for key in directory.GetListOfKeys():
                hist = key.ReadObj()
                if hist.InheritsFrom("TH1"):
                    first_hist = hist
                    break
        if first_hist:
            break

    if not first_hist:
        print("Error: No histograms found in the specified directories.")
        return

    n_bins = first_hist.GetNbinsX()

    # Loop over each bin
    for bin in range(1, n_bins + 1):
        # Create a new ROOT file for this bin
        print(
            "Processing bin.....",
            bin,
            "...named..",
            "{}/{}_mass_{}_{}.root".format(
                args.output_dir,
                outputfilename,
                str(bin_edges[bin - 1]),
                str(bin_edges[bin]),
            ),
        )
        # output_file_name = os.path.join(output_dir, "{}_mass_{}_{}.root".format(outputfilename,str(bin_edges[bin-1]),str(bin_edges[bin])))
        output_file = ROOT.TFile(
            "{}/{}_mass_{}_{}.root".format(
                args.output_dir,
                outputfilename,
                str(bin_edges[bin - 1]),
                str(bin_edges[bin]),
            ),
            "RECREATE",
        )

        # Loop over each TDirectory and copy histograms
        for dir_name in directories:
            directory = input_file.GetDirectory(dir_name)
            if not directory:
                continue  # Skip if directory does not exist

            # Create the corresponding directory in the output file
            if args.SR:
                if dir_name.split("_")[-2] == "tt":
                    output_dir = output_file.mkdir(
                        "tautau"
                        + "_{}_{}_{}_SR".format(
                            find_year(outputfilename),
                            str(bin_edges[bin - 1]),
                            str(bin_edges[bin]),
                        )
                    )
                elif dir_name.split("_")[-2] == "et":
                    output_dir = output_file.mkdir(
                        "eletau"
                        + "_{}_{}_{}_SR".format(
                            find_year(outputfilename),
                            str(bin_edges[bin - 1]),
                            str(bin_edges[bin]),
                        )
                    )
                elif dir_name.split("_")[-2] == "mt":
                    output_dir = output_file.mkdir(
                        "mutau"
                        + "_{}_{}_{}_SR".format(
                            find_year(outputfilename),
                            str(bin_edges[bin - 1]),
                            str(bin_edges[bin]),
                        )
                    )
                elif dir_name.split("_")[-2] == "lt":
                    output_dir = output_file.mkdir(
                        "leptau"
                        + "_{}_{}_{}_SR".format(
                            find_year(outputfilename),
                            str(bin_edges[bin - 1]),
                            str(bin_edges[bin]),
                        )
                    )
                # output_dir = output_file.mkdir('CHANNEL_'+dir_name.split('_')[-2]+"_YEAR_{}_RANGE_{}_{}_SR".format(find_year(outputfilename),str(bin_edges[bin-1]),str(bin_edges[bin])))
            elif args.SB:
                if dir_name.split("_")[-2] == "tt":
                    output_dir = output_file.mkdir(
                        "tautau"
                        + "_{}_{}_{}_SB".format(
                            find_year(outputfilename),
                            str(bin_edges[bin - 1]),
                            str(bin_edges[bin]),
                        )
                    )
                elif dir_name.split("_")[-2] == "et":
                    output_dir = output_file.mkdir(
                        "eletau"
                        + "_{}_{}_{}_SB".format(
                            find_year(outputfilename),
                            str(bin_edges[bin - 1]),
                            str(bin_edges[bin]),
                        )
                    )
                elif dir_name.split("_")[-2] == "mt":
                    output_dir = output_file.mkdir(
                        "mutau"
                        + "_{}_{}_{}_SB".format(
                            find_year(outputfilename),
                            str(bin_edges[bin - 1]),
                            str(bin_edges[bin]),
                        )
                    )

                elif dir_name.split("_")[-2] == "lt":
                    output_dir = output_file.mkdir(
                        "leptau"
                        + "_{}_{}_{}_SB".format(
                            find_year(outputfilename),
                            str(bin_edges[bin - 1]),
                            str(bin_edges[bin]),
                        )
                    )
                # output_dir = output_file.mkdir('CHANNEL_'+dir_name.split('_')[-2]+"_YEAR_{}_RANGE_{}_{}_SB".format(find_year(outputfilename),str(bin_edges[bin-1]),str(bin_edges[bin])))
            else:
                print("Please enter if it is SR or SB")
                quit()
            # Loop over histograms in the directory
            for key in directory.GetListOfKeys():
                hist = key.ReadObj()
                # print("Key.....",key,"....histname...",key.GetName())
                if not hist.InheritsFrom("TH1"):
                    continue  # Skip non-histogram objects

                # Clone the histogram and reset to zero
                hist_copy = hist.Clone()
                hist_copy.Reset()

                # Convert to one bin histogram
                hist_copy = hist_copy.Rebin(
                    1,
                    hist_copy.GetName(),
                    array("d", [bin_edges[bin - 1], bin_edges[bin]]),
                )

                # Set the content and error for the specific bin
                bin_content = hist.GetBinContent(bin)
                bin_error = hist.GetBinError(bin)
                # if ((search("top", key.GetName()) or search("others", key.GetName())) and (not search("radion", key.GetName()))):
                if key.GetName().startswith("top") or key.GetName().startswith(
                    "others"
                ):
                    if bin_content == 0:
                        print(
                            "Bin content is zero for process...",
                            key.GetName(),
                            "...for bin..",
                            bin,
                        )

                        if key.GetName().startswith("top") and args.offAutoMCTop:
                            print("Turn off automcstats for top")
                            hist_copy.SetBinContent(1, 1e-6)
                            hist_copy.SetBinError(1, 0)
                        else:
                            hist_copy.Sumw2()
                            # hist_copy.SetBinContent(bin, 1e-6)
                            hist_copy.SetBinContent(1, 1e-6)
                    elif bin_content < 0:
                        print(
                            "Bin content is Negative = ",
                            bin_content,
                            " for process...",
                            key.GetName(),
                            "...for bin..",
                            bin,
                        )
                        if key.GetName().startswith("top") and args.offAutoMCTop:
                            print("Turn off automcstats for top")
                            hist_copy.SetBinContent(1, 1e-6)
                            hist_copy.SetBinError(1, 0)
                        else:
                            hist_copy.Sumw2()
                            # hist_copy.SetBinContent(bin, 1e-6)
                            hist_copy.SetBinContent(1, 1e-6)
                    else:
                        if key.GetName().startswith("top") and args.offAutoMCTop:
                            print("Turn off automcstats for top")
                            hist_copy.SetBinContent(1, bin_content)
                            hist_copy.SetBinError(1, 0)
                        else:
                            # hist_copy.SetBinContent(bin, bin_content)
                            # hist_copy.SetBinError(bin, bin_error)
                            hist_copy.SetBinContent(1, bin_content)
                            hist_copy.SetBinError(1, bin_error)

                else:
                    # hist_copy.SetBinContent(bin, bin_content)
                    # hist_copy.SetBinError(bin, bin_error)
                    if bin_content < 0:
                        print(
                            "Bin content is Negative FOR SIGNALLL!!!! = ",
                            bin_content,
                            " for process...",
                            key.GetName(),
                            "...for bin..",
                            bin,
                        )
                        hist_copy.Sumw2()
                        # hist_copy.SetBinContent(bin, 1e-6)
                        hist_copy.SetBinContent(1, 1e-6)
                    elif bin_content == 0:
                        print(
                            "Bin content is Zero FOR SIGNALLL!!!! = ",
                            bin_content,
                            " for process...",
                            key.GetName(),
                            "...for bin..",
                            bin,
                        )
                        hist_copy.Sumw2()
                        hist_copy.SetBinContent(1, 1e-6)
                    else:
                        hist_copy.SetBinContent(1, bin_content)
                        hist_copy.SetBinError(1, bin_error)

                # Write the modified histogram into the appropriate directory in the output file
                output_dir.cd()
                output_dir.WriteObject(hist_copy, key.GetName())
                # hist_copy.Write()

        output_file.Close()
        print(
            "Created file:",
            "{}/{}_mass_{}_{}.root".format(
                args.output_dir,
                outputfilename,
                str(bin_edges[bin - 1]),
                str(bin_edges[bin]),
            ),
        )

    # Close the input file
    input_file.Close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Split histograms by bins into separate ROOT files."
    )
    parser.add_argument(
        "--input_file", "-i", help="Path to the input ROOT file", required=True
    )
    parser.add_argument(
        "--output_dir",
        "-o",
        help="Directory to save the output ROOT files",
        required=True,
    )
    parser.add_argument("--SR", help="For SR file splitting", action="store_true")
    parser.add_argument("--SB", help="For SB file splitting", action="store_true")
    parser.add_argument(
        "--offAutoMCTop",
        "-off",
        help="Turn off auto mc stats for top background",
        action="store_true",
    )

    args = parser.parse_args()
    split_by_bins(args.input_file, args.output_dir)
