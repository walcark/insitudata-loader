"""
slurm_commands.py

Author  : Kévin Walcarius
Date    : 2025-09-01
Version : 1.0
License : MIT
Summary : Defines text wrappers for slurm commands to launch.
"""

from insitudata_loader.utils import dedent


slurm_l1c = dedent("""
    #!/bin/bash
    #SBATCH --job-name={job_name}
    #SBATCH --output={TMP_DIR}/{job_name}.out
    #SBATCH --error={TMP_DIR}/{job_name}.err
    #SBATCH -N 1
    #SBATCH -n 1
    #SBATCH --mem-per-cpu=8G
    #SBATCH --time=72:00:00
    #SBATCH --account=cesbio
    #SBATCH --export=none

    cd ${{SLURM_SUBMIT_DIR}}

    module load conda
    conda activate /softs/rh8/conda-envs/amalthee_prod_clientlib

    [ ! -d "{path_linkto}" ] && mkdir -p "{path_linkto}"

    /work/softs/rh8/conda-envs/amalthee_prod_clientlib/bin/python \\
        {TREX_EXT_ROOT}/get_amalthee.py \\
        {tile_id} \\
        {sub_from} \\
        {sub_to} \\
        "{path_linkto}" \\
        --mail "{mail}"
        
    cd {path_linkto} || exit 1
    
    # List all symbolic links with a given regex pattern
    links=($(find . -maxdepth 1 -type l -name "S2*.SAFE" -printf "%f\\n"))

    # Extract unique acquisition dates
    dates=$(printf "%s\\n" "${{links[@]}}" \\
        | grep -oP '^S2[ABC]_MSIL1C_\K\d{{8}}(?=T\d{{6}})' \\
        | sort -u)

    for date in $dates; do
        # List links for the date of interest
        files=($(printf "%s\\n" "${{links[@]}}" \\
            | grep -E "^S2[ABC]_MSIL1C_${{date}}T"))

        # Find the maximum version
        max_version=$(printf "%s\\n" "${{files[@]}}" \\
            | grep -oP 'N\d{{4}}' \\
            | sort -r \\
            | head -n 1)

        echo "Date ${{date}} → version max : ${{max_version}}"

        for f in "${{files[@]}}"; do
            if [[ $f != *"${{max_version}}"* ]]; then
                echo "  → Suppression du lien $f"
                rm "$f"
            fi
        done
    done
    
""")


maja_input_folders = dedent("""
    [Maja_Inputs]
    repWork= REPLACEME
    repGipp= /work/CESBIO/projects/Maja/maja-gipp{maja_id}
    repMNT = /work/CESBIO/projects/Maja/DTM_120
    repL1  = {L1C_ROOT}
    repL2  = {L2A_ROOT}

    exeMaja=/softs/projets/MAJA/{maja_version}/bin/maja

    repCAMS={CAMS_ROOT}

    [DTM_Creation]
    repRAW = {DTM_ROOT}/raw
    repGSW = {DTM_ROOT}/gsw
""")


slurm_maja = dedent("""
    #!/bin/bash
    #SBATCH --job-name={job_name}
    #SBATCH --output={TMP_DIR}/{job_name}.out
    #SBATCH --error={TMP_DIR}/{job_name}.err
    #SBATCH -N 1
    #SBATCH -n 8
    #SBATCH --mem-per-cpu=8G
    #SBATCH --time=72:00:00 
    #SBATCH --account=cesbio
    #SBATCH --export=none

    cd ${{SLURM_SUBMIT_DIR}}

    cat {path_folders_file} | sed "s|REPLACEME|$TMPDIR|g" > {TMP_DIR}/folders.txt

    /softs/projets/MAJA/{maja_version}/bin/startmaja -f \\
        {TMP_DIR}/folders.txt \\
        -t {tile_id} \\
        -s {site} \\
        -d {fromdate} \\
        -e {todate} \\
        --userconf {CONF_ROOT}/userconf-{maja_id}/ \\
        -y \\
        --overwrite --skip_errors {cams_arg}

    chmod -R g+rx {path_linkto}
""")
