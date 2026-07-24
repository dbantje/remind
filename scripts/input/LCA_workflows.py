import argparse
import os
import time
from datetime import datetime

import pandas as pd
import xarray as xr

from internalizer import Internalizer
from internalizer.internalizer import CONFIG_NO_REMOVAL
from internalizer.utils import get_automatic_exclude_list
from internalizer.mif_processing import process_mif

EI_VERSION = "3.10.1"
YEARS_INTERNALIZATION = [2020, 2030, 2040, 2050, 2060, 2070]
IMPACT_CATEGORIES_MC = [
    "acidification",
    "climate change",
    "ecotoxicity",
    "eutrophication",
    "fossil resources",
    "human toxicity",
    "ionizing radiation",
    "land use",
    "metal/mineral resources",
    "ozone depletion",
    "particulate matter formation",
    "photochemical oxidant formation",
    "water use"
]

def get_monetization_arg(args):
    if args.quantile is not None:
        return args.quantile
    elif args.perspective is not None:
        return args.perspective
    else:
        df = pd.read_csv(args.monetization_factors, header=None)
        if len(df.columns) != 2:
            raise ValueError("File with monetization factors must have exactly two columns!")
        else:
            k = df.columns[0]
            v = df.columns[1]
            return df.set_index(k)[v].to_dict()
        
def get_impact_categories(args):
    # get selected impact categories
    if args.monetization_factors is not None:
        monetization = get_monetization_arg(args)
        all_ics = list(monetization.keys())
    else:
        all_ics = IMPACT_CATEGORIES_MC
    ics = []
    if args.single_midpoint != "none":
        ics = [args.single_midpoint]
    else:
        exclude_list = []
        if args.exclude_midpoints != "none":
            if args.exclude_midpoints == "auto":
                print("Getting automatic exclude list based on the mapping file.")
                exclude_list = get_automatic_exclude_list(all_ics)
            else:
                exclude_list = list(args.exclude_midpoints.split(","))
        print(f"Excluding the following midpoints/methods: {exclude_list}")
        ics = [ic for ic in all_ics if ic not in exclude_list]

    return ics
        

if __name__ == "__main__":
    # Parsing arguments
    parser = argparse.ArgumentParser(
        prog="run_lca_workflow",
        description='Runs the LCA internalization workflow'
        )
    parser.add_argument('mifpath', type=str, help="Path to the .mif file")
    parser.add_argument('gdxpath', type=str, help="Path to the .gdx file")
    parser.add_argument('pathway', type=str, help="Name of the REMIND scenario")
    parser.add_argument('rampStart', type=int, help="Start year of linear cost ramp up")
    parser.add_argument('rampEnd', type=int, help="End year of linear cost ramp up")
    parser.add_argument('levels', type=str, help="Levels to internalize (SE, FE or SE,FE)")
    routines = parser.add_argument_group(title="Routines", description="Flags determining which routines to run.")
    routines.add_argument('--plca', action='store_true', help="Run pLCA updates with premise")
    routines.add_argument('--calcCosts', action='store_true', help="Run the cost calculation")
    routines.add_argument('--aggTaxes', action='store_true', help="Run the cost aggregation to REMIND taxes")
    group = parser.add_argument_group(title="Monetization", description="Flags that determine the monetization")
    monetization_group = group.add_mutually_exclusive_group(required=True)
    monetization_group.add_argument('--quantile', type=float, help="quantile for MC monetization")
    monetization_group.add_argument('--perspective', type=str, help="monetization perspective")
    monetization_group.add_argument('--monetization_factors', type=str, help="File with explicit monetization factors")
    parser.add_argument('--single_midpoint', type=str, help="Run for a single midpoint", default="none")
    parser.add_argument('--exclude_midpoints', type=str, help="Run with some midpoints excluded", default="none")
    parser.add_argument('--foldername', type=str, help="Name of the folder to store the results", default="lca")
    parser.add_argument('--multiple_runs', action='store_true', help="Whether several runs are assessed in the same folder")
    parser.add_argument('--no-compartments-change', action='store_true', help="Do not change PM emission compartments.")
    parser.add_argument('--no-interventions', action='store_true', help="Do not include interventions.")
    parser.add_argument('--skip-processing', action='store_true',
                        help="Whether to skip the processing of the .mif files (if already done.)")

    args = parser.parse_args()

    # setup logging file
    logFile = open("log_lca.txt", "a")
    logFile.writelines([f"LCA workflows started with arguments:\n"])
    logFile.writelines(
        [
            f"\t {k}: {v}\n" for k, v in vars(args).items()
        ]
    )
    logFile.writelines(["\n"])

    # append to reporting
    if not args.skip_processing:
        process_mif(args.mifpath, model="remind")

    # in any case, initialize an Internalizer instance and call the setup
    bw_project = f"scenarioLCA_{EI_VERSION}"
    I = Internalizer(
        args.mifpath,
        "remind",
        args.pathway,
        EI_VERSION,
        bw_project,
        args.gdxpath,
        outputfolder = args.foldername,
        single_run = not args.multiple_runs,
    )

    if args.plca:
        t0 = time.time()
        I.run_premise(
            YEARS_INTERNALIZATION,
            include_interventions=not args.no_interventions,
            change_pm_compartments=not args.no_compartments_change
        )
        t1 = time.time()
        logFile.writelines([f"Premise runs done in {t1-t0} seconds", "\n"])

    else:
        I.years = YEARS_INTERNALIZATION

    I.set_calculation_setup(levels=args.levels) # defaults to REMIND Internalization setup

    if args.calcCosts:
        t0 = time.time()
        monetization = get_monetization_arg(args)
        I.calculate_costs(monetization, save_intermediate_results=True)
        t1 = time.time()
        logFile.writelines([f"Cost calculation done in {t1-t0} seconds", "\n"])

    if args.aggTaxes:
        t0 = time.time()
        I.load_costs()

        # SE_zeroed = {}
        # for year, xa in I.cost_results["SE"].items():
        #     SE_zeroed[year] = xa * 0

        # I.cost_results["SE"] = SE_zeroed

        ics = get_impact_categories(args)
        I.write_remind_input_files(
            args.rampStart,
            args.rampEnd,
            ics
        )
        t1 = time.time()
        logFile.writelines([f"Tax recalculation done in {t1-t0} seconds", "\n"])

    logFile.close()
