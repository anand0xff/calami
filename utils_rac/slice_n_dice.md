

## Self-calibration

Self-calibration, e.g. even integrations by odd integrations of an exposure, can be done starting with multi-integration OIFITS files, for example, for the 3 exposures of Gam Mus (program 1508):

```python
from nrm_analysis.misctools.implane2oifits import clip_oifits, calibrate_oifits

indir = os.getcwd()
odir = os.path.join(indir,'selfcal/')

moifitslist = sorted(glob.glob(os.path.join(indir,'multi_*.oifits')))
for moifits in moifitslist:
    # get nints from data shape
    oivisext = fits.getdata(moifits,4)
    nints = oivisext['VISAMP'].shape[1]

    intlist = np.arange(nints)
    evenidx = [idx for idx in intlist if idx%2 == 0]
    oddidx = [idx for idx in intlist if idx%2 != 0]

    clip_oifits(moifits, evenidx, suffix='even') # saves updated oifits, multi_oifits using only selected indices
    clip_oifits(moifits, oddidx, suffix='odd')

# calibrate even by odd integrations
even_oifits = sorted(glob.glob('gam_mus_*_odd.oifits'))
odd_oifits = sorted(glob.glob('gam_mus_*_even.oifits'))

    
for even,odd in zip(even_oifits,odd_oifits):
    filt = even.split('_')[2] # particular to these filenames    
    calib_oifn = 'gam_mus_%s_even_odd_selfcal.oifits' % filt
    calibrate_oifits(even, odd, oifn=calib_oifn, oifdir=odir)

```

Alternatively, odd and even exposures could be processed independently starting from the uncal level, but this has not been tested. The following function could be used:

```python
def even_odd_ints(filename, odir=None):
    if odir is None:
        odir = os.path.dirname(filename)
    if not os.path.exists(odir):
        os.makedirs(odir)
        print('created output dir', odir)
    # read in data
    fits.info(filename)
    with fits.open(filename) as hduin:
        data_in = hduin['SCI'].data
        hduodd = deepcopy(hduin)
        hdueven = deepcopy(hduin)
    shapein = data_in.shape
    if len(shapein) < 3:
        print('ERROR: expecting at least 3 image dimensions in input file')
    nints = shapein[0]
    half1 = nints // 2
    half2 = half1 + (nints % 2)
    print("Output data files will have %i and %i ints, respectively" % (half1, half2))
    # list of even & odd indices
    intlist = np.arange(nints)
    evenidx = [idx for idx in intlist if idx%2 == 0]
    oddidx = [idx for idx in intlist if idx%2 != 0]
    # extensions to update in the output files
    extlist = ['SCI','ERR','DQ','VAR_POISSON','VAR_RNOISE','VAR_FLAT']
    # ok to not update int times??
    for extname in extlist:
        try:
            hduodd[extname].data = hduodd[extname].data[oddidx,...]
            hdueven[extname].data = hdueven[extname].data[evenidx,...]
        except KeyError as e:
            print(e)
            continue
    bn = os.path.basename(filename)
    oddname = os.path.join(odir,filename.replace('.fits','_oddints.fits'))
    evenname = os.path.join(odir,filename.replace('.fits','_evenints.fits'))
    hduodd.writeto(oddname)
    hdueven.writeto(evenname)
    print('Files saved to: \n %s \n %s' % (oddname,evenname))

```

## Slicing and Dicing

* Slicing: splitting up an exposure by **integrations**
* Dicing: splitting up an exposure by **groups**

The functions to slice and dice JWST exposures are currently in the niriss-commissioning repo. If they continue to be useful for analysis they may be transferred elsewhere.

Example of dicing an uncalibrated file into two chunks of groups and running it through the pipeline, e.g. to look for charge migration:

```python
from nis_comm.nis_019.utils.dicegroups_sliceints_AMI import dice_groups
import nis_comm.nis_019.utils.ami_functions

outdir = 'diced/'
ndice = 2 # number of "chunks" of groups to divide each integration into
uncal_fn = 'jw...._uncal.fits' # should be a real filename
diced_fnlist = dice_groups(uncal_fn, ndice, outdir=outdir) # output path NOT prepended to returned filenames
callist = []
for diced_fn in diced_fnlist:
	diced_fn = os.path.join(outdir, fn)
    df_rate = diced_fn.replace("uncal", "rate")
    df_cal = diced_fn.replace("uncal", "cal")
    if os.path.exists(df_cal) and not overwrite:
        print("Cal file already exists; not overwriting")
    else:
        utils.ami_functions.run_detector1_uncal(diced_fn, refdir, outdir)
        utils.ami_functions.run_detector2_rate(df_rate, refdir, outdir)
    callist.append(df_cal)
```