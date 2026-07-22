*** SOF ./modules/52_internalizeLCAimpacts/coupled/presolve.gms

***---------------------------------------------------------------------------
*' TODO: adapt for LCA workflow
*' MAGICC is run and its output is read using different current R scripts in the external MAGICC folder
*' that are copied to each run's folder during the preparation phase. Different parametrizations of MAGICC can also be chosen with `cm_magicc_config`,
*' and are also handled during the preparation phase
*'
*' Below is the main code that handles the input prepration, running and output reading of MAGICC.
***---------------------------------------------------------------------------
*' @code

*** 

if( (ord(iteration) ge max(cm_startIter_EDGET+1, cm_startIter_LCA)),
  Execute_unload 'fulldata_presolve';
  if ((mod(ord(iteration), cm_freqIter_LCA) eq 0),
    Execute "Rscript run_LCA_workflows.R fulldata_presolve.gdx update_plca";
  else
    Execute "Rscript run_LCA_workflows.R fulldata_presolve.gdx recalculate_taxes";
  );
);

!! Read in results
$ifThen.internalizeSE "%cm_52_internalize_levels%" == "SE"
Execute_Loadpoint 'LCA_SE' p52_LCAcosts_SE=pm_LCAcosts_SE;
$endIf.internalizeSE

$ifThen.internalizeFE "%cm_52_internalize_levels%" == "FE"
Execute_Loadpoint 'LCA_FE' p52_LCAcosts_FE=pm_LCAcosts_FE;
$endIf.internalizeFE

$ifThen.internalizeBoth "%cm_52_internalize_levels%" == "SE,FE"
Execute_Loadpoint 'LCA_SE' p52_LCAcosts_SE=pm_LCAcosts_SE;
Execute_Loadpoint 'LCA_FE' p52_LCAcosts_FE=pm_LCAcosts_FE;
$endIf.internalizeBoth

!! convert units
pm_taxEI_SE(ttot,all_regi,all_te) = p52_LCAcosts_SE(ttot,all_regi,all_te) * sm_DpGJ_2_TDpTWa;
pm_taxEI_FE(ttot,all_regi,emi_sectors,all_enty) = p52_LCAcosts_FE(ttot,all_regi,emi_sectors,all_enty) * sm_DpGJ_2_TDpTWa;

*** EOF ./modules/52_internalizeLCAimpacts/coupled/presolve.gms
