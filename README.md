# SearchLight_fMRI, Pegah Kassraian Fard

# **Introduction**

This code is an **extension** of the PYMVPA Searchlight: http://www.pymvpa.org/

It is meant to add important functionalities to the original searchlight functionalities:

- Figures are saved as .figs as well as in the nifti file-format
- Coordinates and accuracies of the searchlight classification are saved as numpy arrays 
- The code allows you to balance the size of classes for classification (i.e. using an equal number of data samples). 

Additionally, the **ttest_searchlight.py** script allows you to:

- Perform a group-level t-test with FDR correction on the searchlight results. These group-level results are then saved in the nifti file format.

For a better understanding of relevant searchlight parameters, here two reading recommendations:

- Information-based functional brain mapping. Kriegeskorte N, Goebel R, Bandettini P. PNAS. 2006
- Searchlight analysis: promise, pitfalls, and potential.
Joset A. Etzel, Jeffrey M. Zacks, and Todd S. Braver, NeuroImage 2013.

# **How to cite**

- Please cite the sources mentioned on http://www.pymvpa.org/ 

- As well as "Prior expectation tunes neural activity within primary somatosensory cortex to sharpen tactile detection (in preparation)".
Pegah Kassraian Fard, Daniel G. Woolley, Marloes H. Maathuis, Nadja Enz, Nicole Wenderoth.

# **How to: Searchlight classification with PYMVPA_extension.py**

This code allows you to perform a searchlight analysis, the details of the searchlight algorithm can be found on 
http://www.pymvpa.org/. 

You can run the code as follows:

- Put the niftis you want to perform a searchlight classification on into subfolders in the **Input** folder. Exemplary folders are subj1_wb and subj2_wb. You can re-name the folders as you wish, however you should then change the paths accordingly in the code.

- Classification labels: Classification requires labels - here we want to indicate to which experimental condition each nifti file belongs to. Make sure to either create a numpy vector with labels or, alternatively, include a mat file with the labels into the Input folder. Currently, the code is using a label vector stored in a mat file: 
> labels = loadmat('Input/classifLabels.mat')['label'].reshape(-1)

- Defining classes: The code has been written for an experiment with 6 experimental conditions:
> for i, label_set in enumerate([[1, 2], [3, 4], [5, 6]]):

Classification is performed for classes 1 versus 2, 3 versus 4 and 5 versus 6 for each subject.

If you want to only classify class 1 versus class 2, you can change the code to:

> for i, label_set in enumerate([[1, 2]]):

If you have nifti files you wish to ignore for classification, you can label them with a number not within this range 
(you might for instance have niftis corresponding to the GLM intercept, in the example files, these are labeled with a "7").

- Balancing: The code is automatically balancing the classes you have defined for classification.

- Currently, the code is only classifying within a mask. If you wish to perform a whole-brain searchlight, you have to
change the mask attribute to 'None':

  db = mvpa2.datasets.mri.fmri_dataset(
        nii_fns, mask=None, targets=labels, chunks=grps, sprefix=sprefix_, tprefix=tprefix_,
        add_fa=None
    )

# **How to: Searchlight group-level significance testing with ttest_searchlight.py**

This code uses the resulting niftis from the searchlight analysis to perform a group-level t-test against chance level.
Currently, chance level is set to 50% classification accuracy, this can be changed however if you wish:

 > t, p = ttest_1samp(data, popmean=0.5, alternative='greater')
 
 An FDR-correction is then performed on the resulting p-values, and the group-level results are stored again as nifti files.




