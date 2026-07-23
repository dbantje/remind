from internalizer import Internalizer

EI_VERSION = "3.10.1"

# set paths a previous run
folder = "/p/tmp/davidba/internalization_develop/remind/output/SSP2-only-nonCC-ep-v0p8p3_2026-07-22_12.11.59"
pathway = "SSP2-only-nonCC-ep-v0p8p3"
mifpath = folder + f"/lca/remind_runs/{pathway}.mif"
gdxpath = folder + "/fulldata.gdx"

# in any case, initialize an Internalizer instance and call the setup
bw_project = f"scenarioLCA_{EI_VERSION}"
I = Internalizer(
    mifpath,
    "remind",
    pathway,
    EI_VERSION,
    bw_project,
    gdxpath,
    outputfolder = "lca"
)

I.recreate_premise_cache()