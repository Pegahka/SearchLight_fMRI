# SearchLight_fMRI

# Introduction

This code is an extension of the PYMVPA Searchlight and is meant to add important functionalities to the original searchlight script:
Figures are saved as .figs as well as niftis, coordinates and accuracies of the searchlight classification are saved as well, and the code 
allows you to balance the size of classes for classification. Additionally, the ttest_searchlight allows you to perform a group-level t-test 
with FDR correction on the searchlight results, and store these group-level results then in the nifti file format.
