# Modifications by Pegah Kassraian Fard (Stanford University, Columbia University NY)


# Please cite:

# Prior expectation tunes neural activity within primary somatosensory
# cortex to sharpen tactile detection (in preparation).
# Pegah Kassraian Fard, Daniel G. Woolley, Marloes H. Maathuis, Nadja Enz, Nicole Wenderoth.

# The code makes use of some functions provided by PYMVPA, please also cite relevant PYMVPA sources

import numpy as np
import nibabel as nbl
from mvpa2.suite import *
from statsmodels.sandbox.stats.multicomp import multipletests

# Set the background parameters for results of group-level results
mri_args = {
    'background': 'Input/MNI_brain.nii',
    'do_stretch_colors': False,
    'cmap_bg': 'gray',
    'cmap_overlay': 'autumn',
    'interactive': False
}

sprefix_ = 'voxel'
sprefix_indices_key = '_'.join([sprefix_, 'indices'])
tprefix_ = 'tpref'

# Here you can set which classification results should undergo group-level significance testing
# Example: Here the group-level tests are applied to classifications of class 1 versus class 2
# (experimental condition 1 versus experimental condition 2), indicated by '12',
# but also of class 3 versus 4 and of class 5 versus 6.

total = [[], [], []]
nb_results = 0
ex = None
# Set path for files statistical tests should be applied to
for _, dirs, _ in os.walk('ResultsFolder'):
    for dir in dirs:
        if dir.endswith('_wb'):
            nb_results += 1
            work_dir = os.path.join('ResultsFolder', dir)
            for _, _, files in os.walk(work_dir):
                for i in range(3):
                    nifti = os.path.join(work_dir, 'volume_%s.nii' % (['12','34','56'][i]))
                    db = mvpa2.datasets.mri.fmri_dataset(nifti, sprefix=sprefix_, tprefix=tprefix_, add_fa=None )

                    if ex is None:
                        ex = db

                    total[i].append(db.samples)


for i in range(3):
    data = np.concatenate(total[i])

# Evaluate p-values by testing against chance level, followed by thresholding
# based on multiple-testing correction, here for instance FDR

    t, p = ttest_1samp(data, popmean=0.5, alternative='greater')
    str_label_set = '_' + ['12','34','56'][i]
    p = np.nan_to_num(p)
    reject, cp, _, _ = multipletests(p, method='fdr_tsbky')

# Set significance level

    mask = cp > 0.001
    data = np.mean(data, axis=0)
    data[mask] = 0

    ex.samples = data
    niftiresults = map2nifti(ex, imghdr=ex.a.imghdr)
    nbl.nifti1.save(niftiresults, 'ResultsFolder/volume_total' + str_label_set)

    fig = pl.figure(figsize=(12, 12), facecolor='white')
    try:
        plot_lightbox(overlay=niftiresults, vlim=(0.5, None), slices=range(59, 69), fig=fig, **mri_args)
        fig.savefig(filename='ResultsFolder/fig_total' + str_label_set)
    except:
        pass
