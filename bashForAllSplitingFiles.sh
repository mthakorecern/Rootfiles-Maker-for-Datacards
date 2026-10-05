#!/bin/bash
years=("2024")
#years=("2016" "2016APV")
regions=("SideBand" "SignalRegion")

# Base directories
script_name="SplitTheRootFilesPerBins.py"
root_file_base="/afs/hep.wisc.edu/home/mithakor/HH_bb_tautau_Analysis/StatisticalAnalysis/CMSSW_16_0_0/src/CombineHarvester/CombineTools/python/Rootfiles_Maker_for_Datacards"

# Iterate over years and regions
for year in "${years[@]}"; do
    for region in "${regions[@]}"; do
        # Construct input and output paths
        input_file="${root_file_base}/${year}/${year}_allHists_${region}_1fb_varbin.root"
        
        # Determine the output directory and region-specific flag
        if [ "$region" == "SideBand" ]; then
            output_dir="${root_file_base}/${year}/SB_bin_by_bin_rootfiles"
            region_flag="--SB"
        elif [ "$region" == "SignalRegion" ]; then
            output_dir="${root_file_base}/${year}/SR_bin_by_bin_rootfiles"
            region_flag="--SR"
        else
            echo "Unknown region: $region. Skipping..."
            continue
        fi

        # Print information
        echo "Processing year: $year, region: $region"
        echo "Input file: $input_file"
        echo "Output directory: $output_dir"
        
        # Run the Python command
        python3 $script_name -i "$input_file" -o "$output_dir" $region_flag
        
        # Check the status of the command
        if [ $? -eq 0 ]; then
            echo "Successfully processed year: $year, region: $region"
        else
            echo "Error processing year: $year, region: $region"
        fi
        echo "----------------------------------------"
    done
done

