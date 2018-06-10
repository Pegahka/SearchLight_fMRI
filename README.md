# SearchLight_fMRI

# **Introduction**

This code is an **extension** of the PYMVPA Searchlight: http://www.pymvpa.org/

It is meant to add important functionalities to the original searchlight functionalities:

- Figures are saved as .figs as well as in the nifti file-format
- Coordinates and accuracies of the searchlight classification are saved as numpy arrays 
- The code allows you to balance the size of classes for classification (i.e. using an equal number of data samples). 

Additionally, the **ttest_searchlight.py** script allows you to:

- Perform a group-level t-test with FDR correction on the searchlight results. These group-level results are then saved in the nifti file format.

# **How to cite**

Please cite the sources mentioned on http://www.pymvpa.org/ as well as "Prior expectation tunes neural activity within primary somatosensory cortex to sharpen tactile detection (in preparation)".
Pegah Kassraian Fard, Daniel G. Woolley, Marloes H. Maathuis, Nadja Enz, Nicole Wenderoth.
