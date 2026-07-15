*** SOF ./modules/52_internalizeLCAimpacts/coupled/preloop.gms

*** Set taxes to zero to begin with.
pm_taxEI_SE(ttot,all_regi,all_te) = 0;
pm_taxEI_PE(ttot,all_regi,all_enty) = 0;
pm_taxEI_cap(ttot,all_regi,all_te) = 0;
pm_taxEI_FE(ttot,all_regi,emi_sectors,all_enty) = 0;
p52_LCAcosts_SE(ttot,all_regi,all_te) = 0;
p52_LCAcosts_FE(ttot,all_regi,emi_sectors,all_enty) = 0;

Execute "Rscript run_LCA_workflows.R input.gdx preloop";

!! Read in results
$ifThen.internalizeSE ("%cm_52_internalize_levels%" == "SE") or ("%cm_52_internalize_levels%" == "SE,FE")
Execute_Loadpoint 'LCA_SE' p52_LCAcosts_SE=pm_LCAcosts_SE;
$endIf.internalizeSE

$ifThen.internalizeFE ("%cm_52_internalize_levels%" == "FE") or ("%cm_52_internalize_levels%" == "SE,FE")
Execute_Loadpoint 'LCA_FE' p52_LCAcosts_FE=pm_LCAcosts_FE;
$endIf.internalizeFE

!! convert units
pm_taxEI_SE(ttot,all_regi,all_te) = p52_LCAcosts_SE(ttot,all_regi,all_te) * sm_DpGJ_2_TDpTWa;
pm_taxEI_FE(ttot,all_regi,emi_sectors,all_enty) = p52_LCAcosts_FE(ttot,all_regi,emi_sectors,all_enty) * sm_DpGJ_2_TDpTWa;

*** EOF ./modules/52_internalizeLCAimpacts/coupled/preloop.gms
