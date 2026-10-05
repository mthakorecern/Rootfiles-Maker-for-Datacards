#!/bin/bash
mkdir -p logs
echo "Processing 2024"
(
    python3 MakeInputRootFilesForDataCardsWithSystematicsFinalzingResults.py --year 2024 --Channel tt --recreate --Path /hdfs/store/user/mithakor/2024_Processed_Weighted/MC/JERC_updatedLumi_LooseMiniPFRelISO_27Sep26_2006/ -o 2024/
    python3 MakeInputRootFilesForDataCardsWithSystematicsFinalzingResults.py --year 2024 --Channel lt --update --Path /hdfs/store/user/mithakor/2024_Processed_Weighted/MC/JERC_updatedLumi_LooseMiniPFRelISO_27Sep26_2006/ -o  2024/
) > logs/2024_085.log 2>&1 &


# Wait for all background processes to complete
wait
echo "All processes completed."
