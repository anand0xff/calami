#! /usr/bin/env python

import argparse
import glob
import os
import yaml
import time

import numpy as np
from astropy.io import fits
from mirage.apt import read_apt_xml
from mirage.yaml.generate_observationlist import expand_for_dithers


def verify_1093(xml_file=None, datadir=None, suffix=None, save_yml=True, verbose=False):
    """
    This function checks that each of the exposures specified in an XML file
    of Program 1093 exported from APT (Astronomer's Proposal Tool) exist in the
    given directory.
    It optionally produces a dictionary where the key is a mnemonic string of the format:
    [obsnum_pupil_filter_ngroups_nints_primarypos_subpixelpos].
    e.g.:
    'obs001_NRM_F480M_5_65_pri1_sub0'
    and the value is the base of the filename assigned by the archive not including the
    product type and file extension, e.g.:
    'jw01093001001_01101_00001_nis'
    and saves the dictionary to a YAML file called 'prog1093.yml'
    Inputs:
            xml_file: (str) Name of Program 1093 XML file exported from APT
            datadir: (str) Directory where fits files are located
            save_yml: (Bool, default=True) Save the dictionary of keys and filename roots
            verbose: (Bool, default=False) Print all Mirage output
    """
    start = time.time()
    if xml_file is None:
        xml_file = "1093.xml"
    if not os.path.exists(xml_file):
        raise Exception(
            "Could not find XML file %s. Enter filename with --xml_file"
        )
    if datadir is None:
        datadir = "pipeline_calibrated_data/"
        if not os.path.exists(datadir):
            raise Exception(
                "Input data directory %s could not be found. Enter dir name with --datadir"
            )
    if suffix is None:
        suffix = "uncal"

    # read in the contents of the APT XML file using a Mirage tool
    readxml_obj = read_apt_xml.ReadAPTXML()
    xml_dict = readxml_obj.read_xml(xml_file, verbose=False)
    # create an expanded dictionary that contains lists of parameters expanded for dithers
    xml_dict = expand_for_dithers(xml_dict, verbose=False)

    num_exps = len(xml_dict["PI_Name"])  # could use any key, should all be same length

    priditherlist = []
    subditherlist = []
    pripos = 1
    subpos = 1
    obskeys0 = []
    print("\nWorking...\n")
    for expo in np.arange(num_exps):
        obsnum = xml_dict["ObservationID"][expo]
        pup = xml_dict["PupilWheel"][expo]
        filt = xml_dict["Filter"][expo]
        grps = xml_dict["Groups"][expo]
        ints = xml_dict["Integrations"][expo]
        pridith = xml_dict["PrimaryDithers"][expo]
        subdith = xml_dict["SubpixelPositions"][expo]
        priditherlist.append(pridith)
        subditherlist.append(subdith)
        try:
            # if dither position is same as previous one
            if (pridith == priditherlist[-2]) & (pripos < int(pridith)):
                pripos += 1
            else:
                pripos = 1
        except IndexError:
            pripos = 1

        if subdith == "None":
            subpos = 0
        elif subdith == "1":
            subpos = 0
        else:
            subpos += 1
            #pripos = subpos
        # for epoch 1:
        # if pup == "None":
        #     if int(obsnum) > 7:
        #         if int(grps) == 10:
        #             pup = "NRM"
        #         else:
        #             pup = "CLEARP"
        #     else:
        #         pup = "NRM"
        # for epoch 2:
        if pup == "None":
            if int(obsnum) > 20:
                if int(grps) == 10:
                    pup = "NRM"
                else:
                    pup = "CLEARP"
            else:
                pup = "NRM"

        if filt == "None":  # true for TA observations
            filt = "F480M"
            obsnum = obsnum + "ta"

        key = "obs%s_%s_%s_%s_%s_pri%s_sub%s" % (
            obsnum,
            pup,
            filt,
            grps,
            ints,
            str(pripos),
            str(subpos),
        )
        obskeys0.append(key)

    # gather all the {suffix}.fits files
    fnlist = sorted(
        glob.glob(os.path.join(datadir, "jw01093*{}.fits".format(suffix)))
    )  # only get {suffix}.fits files from this program
    nfiles = len(fnlist)

    # remove observations 1-11 from dict (to just use re-observation)
    # or, remove observations 12-23 to just use epoch 1 
    obskeys = []
    #obslist = list(np.arange(1,12)) # for epoch 2
    obslist = list(np.arange(12,24)) # for epoch 1
    strings = [str(obsnum).zfill(3) for obsnum in obslist]
    for obskey in obskeys0:
        if not any(string in obskey for string in strings):
            obskeys.append(obskey)

    nexpected = len(obskeys)

    if nfiles > nexpected:
        print(
            "Warning: more files found than expected. Looking for %i exposures; found %i files"
            % (nexpected, nfiles)
        )
    elif nfiles < nexpected:
        print(
            "Warning: fewer files found than expected. Looking for %i exposures; found %i files"
            % (nexpected, nfiles)
        )
    # Set up dictionary for keys and filenames
    filedict = {}
    for fullfn in fnlist:
        bn = os.path.basename(fullfn)
        # Read in exposure info from header
        prihdr = fits.getheader(fullfn)
        obshdr = int(prihdr["OBSERVTN"])  # strips leading zeros
        exphdr = int(prihdr["EXPOSURE"])
        puphdr = prihdr["PUPIL"]
        flthdr = prihdr["FILTER"]
        ngrphdr = int(prihdr["NGROUPS"])
        ninthdr = int(prihdr["NINTS"])
        npridth = int(prihdr["NUMDTHPT"])
        try:
            nsubdth = int(prihdr["SUBPXPTS"])
        except KeyError: # TA exposures do not have this keyword
            nsubdth = 1
        pattnumhdr = int(prihdr["PATT_NUM"])
        
    #     print("from header:")
    #     print("exposure, numdthpt, subpxpts, pattnum")
    #     print(exphdr, npridth, nsubdth, pattnumhdr)

        # Now parse the keys
        for key in obskeys:
            # print('Looking for file that matches %s' % key)
            obs, pup, flt, ngrp, nint, pripos, subpos = key.split("_")
            # figure out dither configuration
            # this is pretty fragile and dependent on current dither keywords
            if "ta" in obs:
                # this is a TA exposure
                priposhdr = exphdr  # use the exposure number as alias for primary dither position
                subposhdr = 0
            elif npridth > 1:
                priposhdr = pattnumhdr
                subposhdr = 0
            elif npridth == 1:
                # assume only subpixel dither pattern in this obs, or only one primary dither
                priposhdr = 1
            if nsubdth > 1:
                # this will not work for real observations (different exposure numbering than sims)
                # subposhdr = (
                #     exphdr - 4
                # )  # first four exposures always TA, so assume subpixel position from exp number
                # or for real exposures:
                subposhdr = pattnumhdr
                priposhdr = 1
            elif nsubdth == 1:
                subposhdr = 0

            
            # reformat for easier comparison
            obs = int(obs[3:6])  # remove the 'obs' string
            pripos = int(pripos[3:])  # remove the 'pri' string
            subpos = int(subpos[3:])  # remove the 'sub' string
            ngrp = int(ngrp)
            nint = int(nint)

            # Now compare components from header to components in key (from APT)
            if (
                (obshdr == obs)
                and (puphdr == pup)
                and (flthdr == flt)
                and (ngrphdr == ngrp)
                and (ninthdr == nint)
                and (priposhdr == pripos)
                and (subposhdr == subpos)
            ):
                if verbose:
                    print("%s matches header from %s" % (key, bn))
                # populate dictionary with fits filename
                fileroot = bn.split("_{}.fits".format(suffix))[0]
                filedict[key] = fileroot


    # make sure a file was found for each key:
    for key in obskeys:
        obs, pup, flt, ngrp, nint, pripos, subpos = key.split("_")
        if key not in filedict.keys():
            print(
                "WARNING!!! No file found that matches: \n obs #: %s \n pupil: %s \n filter: %s \n ngroups: %s \n nints: %s \n pripos: %s \n subpos: %s"
                % (obs, pup, flt, ngrp, nint, pripos, subpos)
            )

    # inform about any files that were globbed but did not match a key:
    for fullfn in fnlist:
        bn = os.path.basename(fullfn)
        fileroot = bn.split("_{}.fits".format(suffix))[0]
        if fileroot not in filedict.values():
            print("File %s did not match any expected exposures" % bn)
            if verbose:
                prihdr = fits.getheader(fullfn)
                obshdr = int(prihdr["OBSERVTN"])  # strip leading zeros
                exphdr = int(prihdr["EXPOSURE"])
                puphdr = prihdr["PUPIL"]
                flthdr = prihdr["FILTER"]
                ngrphdr = int(prihdr["NGROUPS"])
                ninthdr = int(prihdr["NINTS"])
                npridth = int(prihdr["NUMDTHPT"])
                nsubdth = int(prihdr["SUBPXPTS"])
            if "ta" in obs:
                # this is a TA exposure
                priposhdr = exphdr  # use the exposure number as alias for primary dither position
                subposhdr = 0
            elif npridth > 1:
                priposhdr = pattnumhdr
                subposhdr = 0
            elif npridth == 1:
                # assume only subpixel dither pattern in this obs, or only one primary dither
                priposhdr = 1
            if nsubdth > 1:
                # this will not work for real observations (different exposure numbering than sims)
                # subposhdr = (
                #     exphdr - 4
                # )  # first four exposures always TA, so assume subpixel position from exp number
                # or for real exposures:
                subposhdr = pattnumhdr
                priposhdr = 1
            elif nsubdth == 1:
                subposhdr = 0

            print(
                "obs #: %s \n pupil: %s \n filter: %s \n ngroups: %s \n nints: %s \n pripos: %s \n subpos: %s"
                % (obshdr, puphdr, flthdr, ngrphdr, ninthdr, priposhdr, subposhdr)
            )

    if save_yml:
        # write out the dictionary to a YAML file. Will overwrite if already exists.
        yml_file = "prog1093.yml"
        #yml_file = "prog1093_epoch1.yml"
        with open(yml_file, "w") as f:
            yaml.dump(filedict, f)
        print("Dictionary saved to %s" % yml_file)
    stop = time.time()
    print("Runtime: %i s" % (stop - start))


if __name__ == "__main__":
    # # XML file name exported from APT
    # xml_file = '1093.xml'
    #
    # # define location of fits files from program 1093
    # datadir = 'mirage_sim_data_nobadpix/'
    #
    # verbose = False

    parser = argparse.ArgumentParser()
    parser.add_argument("--xml-file", help="Name of an XML file exported from APT. Default: 1093.xml")
    parser.add_argument("--datadir", help="Directory containing {suffix}.fits files. Default: pipeline_calibrated_data/")
    parser.add_argument(
        "--suffix",
        default="uncal",
        help="Suffix the calibration level (uncal by default)",
    )
    parser.add_argument(
        "--save",
        dest="save_yml",
        help="Save dictionary of keys and filename roots in a YAML",
        action="store_true",
    )
    parser.add_argument(
        "-v", "--verbose", help="increase output verbosity", action="store_true"
    )
    args = parser.parse_args()

    verify_1093(
        xml_file=args.xml_file,
        datadir=args.datadir,
        suffix=args.suffix,
        save_yml=args.save_yml,
        verbose=args.verbose,
    )
