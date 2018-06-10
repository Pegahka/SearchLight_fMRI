# Original code by www.pymvpa.org

# Modifications by Pegah Kassraian Fard (Columbia University NY) &
# Sergey Soloviev (Moscow Institute of Physics and Technology)


# Please cite besides relevant PYMVPA sources also:

# Prior expectation tunes neural activity within primary somatosensory
# cortex to sharpen tactile detection (in preparation).
# Pegah Kassraian Fard, Daniel G. Woolley, Marloes H. Maathuis, Nadja Enz, Nicole Wenderoth.



from glob import glob
import os
import numpy as np
import nibabel as nbl
from mvpa2.suite import *
from scipy.io import loadmat

# Define a function which subsamples to create classes of equal size
# Example: You have 2 or more experimental conditions and classification of these
# should use an equal amount of trials (data samples)

def balanced_subsample(y, subsample_size=1.0):
    class_ys = []
    min_elems = None

    for yi in np.unique(y):
        targets = (y == yi)
        class_ys.append(targets)
        if min_elems is None or sum(targets) < min_elems:
            min_elems = sum(targets)

    use_elems = min_elems
    if subsample_size < 1:
        use_elems = int(min_elems * subsample_size)

    mask = np.zeros_like(y, dtype=np.bool)

    for ci in class_ys:
        m_ = ci
        while sum(m_) > use_elems:
            r = np.random.randint(0, sum(m_))
            for i in range(len(m_)):
                if m_[i]:
                    r -= 1
                    if r == 0:
                        m_[i] = False

        mask |= m_

    return mask


# Enable debug output for searchlight call
if __debug__:
    debug.active += ["SLC"]

# Here you define the background display options
mri_args = {
    'background': 'Input/MNI_brain.nii',
    'do_stretch_colors': False,
    'cmap_bg': 'gray',
    'cmap_overlay': 'autumn',  # YlOrRd_r # pl.cm.autumn
    'interactive': cfg.getboolean('examples', 'interactive', False)
}

# Define here the labels to use, type: numpy array
# Example: Here a mat array (MATLAB) is taken and transformed to a numpy array
labels = loadmat('Input/classifLabels.mat')['label'].reshape(-1)
grps = np.repeat([0, 6], 192, axis=0)  # used for `chuncks`

sprefix_ = 'voxel'
sprefix_indices_key = '_'.join([sprefix_, 'indices'])
tprefix_ = 'tpref'

# The folder where your data (nifti files) are in to be classified
data_dir = 'Input/'

# Takes data in the specified folder. We can replace this with a hard coded list if we want to run the code
# for only some subjects
subject_list = [dI for dI in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, dI))]

# Example if classification should be done only for 'subj1_sl'
#subject_list = ['subj1_sl']

total = [[], [], []]
for subject in subject_list:
    # Output folder
    dir = os.path.join('ResultsFolder', subject)
    if not os.path.exists(dir):
        os.makedirs(dir)

    # Use glob to get the filenames of .nii data into a list
    nii_fns = sorted(glob(os.path.join(data_dir, subject) + '/beta*.nii'))

    #  Read data - here you can select the mask to apply to. For instance, here we only classify within the
    # 'hand-region' of the right hemisphere
    #  Set mask=None if you wish you perform a whole brain search-light
    db = mvpa2.datasets.mri.fmri_dataset(
        nii_fns, mask='Input/Hand_R_resz.nii', targets=labels, chunks=grps, sprefix=sprefix_, tprefix=tprefix_,
        add_fa=None
    )

    db = mvpa2.datasets.miscfx.remove_nonfinite_features(db)

    # Here you define the classifications. For instance, here classes 1 versus 2,
    # versus 4 and 5 versus 6 are classified, other labels ignored.
    for i, label_set in enumerate([[1, 2], [3, 4], [5, 6]]):
        
        db12 = db.select(sadict={'targets': label_set})

        # in-place z-score normalization - it is recommended to standardize your data before classification
        zscore(db12)

        # Choose classifier
        clf = LinearNuSVMC()

        # Setup measure to be computed by Searchlight
        # Cross-validation options
        cv = CrossValidation(clf, NFoldPartitioner())

        # Define searchlight methods
        radius_ = 2
        sl = sphere_searchlight(
            cv, radius=radius_, space=sprefix_indices_key,
            postproc=mean_sample()
        )
        
        # Here we balance classes
        mask = balanced_subsample(db12.targets)

        # Stripping all attributes from the dataset that are not required for the searchlight analysis
        db12s = db12[mask].copy(
            deep=False,
            sa=['targets', 'chunks'],
            fa=[sprefix_indices_key],
            a=['mapper']
        )

        print('running searchlight')
        
        # Run searchlight
        sl_map = sl(db12s)

        # Toggle between error rate (searchlight output) and accuracy (for plotting)
        sl_map.samples *= -1
        sl_map.samples += 1

        # The result dataset is fully aware of the original dataspace.

        str_label_set = '_' + ''.join(map(str, label_set))
        niftiresults = map2nifti(sl_map, imghdr=db12.a.imghdr)
        nbl.nifti1.save(niftiresults, dir + '/volume' + str_label_set)
        print('accuracy: %0.5f' % np.mean(sl_map.samples[0]))

        # Find and save the 3-d coordinates of extrema of error rate or accuracy
        min_i = np.argmax(sl_map.samples[0])  # max
        max_i = np.argmin(sl_map.samples[0])  # min
        coord = db12s.fa[sprefix_indices_key][max_i]
        
        np.save(dir + '/coords' + str_label_set, db12s.fa[sprefix_indices_key])
        np.save(dir + '/accuracies' + str_label_set, sl_map.samples[0])


        print('plotting')
        print(dir)
        fig = pl.figure(figsize=(12, 12), facecolor='white')
        plot_lightbox(overlay=niftiresults, vlim=(0.5, None), slices=range(59, 69), fig=fig, **mri_args)
        fig.savefig(fname=dir + '/fig' + str_label_set)


        