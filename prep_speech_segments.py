# coding: utf-8

import os
import sys
import argparse
import json
import pickle
import re
from tqdm import tqdm
import numpy as np

program_descrp = """
merge kaldi speech segments to map with transcriptions and translations
"""

'''
example:
export SPEECH_FEATS=/afs/inf.ed.ac.uk/group/project/lowres/work/corpora/fisher_kaldi/fbank
python prep_speech_segments.py -m $SPEECH_FEATS -o $PWD/out/

'''
def map_speech_segments(cat_dict, cat_speech_path, cat_out_path):
    print("mapping speech data, output in: {0:s}".format(cat_out_path))
    if not os.path.isdir(cat_out_path):
        # creating directory
        print("creating directory")
        os.makedirs(cat_out_path)
    else:
        print("directory exists")

    cnt = 0
    sp_id = ""
    for utt_id in tqdm(cat_dict):
        if sp_id != utt_id.rsplit("-",1)[0]:
            # load new speech file
            sp_id = utt_id.rsplit("-",1)[0]
            sp_data = np.load(os.path.join(cat_speech_path, "{0:s}.np".format(sp_id)))
        # end if

        # check if any data in transcription
        # e.g.: map_dict['fisher_dev']['20051017_220530_275_fsp-B-21']
        # does not have any data in the spanish speech
        if len(cat_dict[utt_id]['es_w']) > 0:
            seg_names = [seg['seg_name'] for seg in cat_dict[utt_id]['seg']]

            utt_data = [sp_data[s] for s in seg_names if s in sp_data]
            missing_files = [s for s in seg_names if s not in sp_data]
            if len(missing_files) > 0:
                print("{0:s} files missing".format(" ".join(missing_files)))
            if len(utt_data) == 0:
                print(utt_id)
            utt_data = np.concatenate(utt_data, axis=0)
            np.save(os.path.join(cat_out_path, "{0:s}".format(utt_id)), utt_data)

    print("done...")



def main():
    parser = argparse.ArgumentParser(description=program_descrp)
    parser.add_argument('-m','--speech_dir', help='directory containing speech features',
                        required=True)
    parser.add_argument('-o','--out_path', help='output path',
                        required=True)

    args = vars(parser.parse_args())
    speech_dir = args['speech_dir']
    out_path = args['out_path']

    if not os.path.exists(speech_dir):
        print("speech features path given={0:s} does not exist".format(
                                                        speech_dir))
        return 0

    # create output file directory:
    if not os.path.exists(out_path):
        print("{0:s} does not exist. Exiting".format(out_path))
        return 0

    # load map dictionary
    map_dict_path = os.path.join(out_path,'map.dict')

    if not os.path.exists(map_dict_path):
        print("{0:s} does not exist. Exiting".format(map_dict_path))
        return 0

    print("-"*50)
    print("loading map_dict from={0:s}".format(map_dict_path))
    map_dict = pickle.load(open(map_dict_path, "rb"))
    print("-"*50)

    for cat in map_dict:
        if not os.path.isdir(os.path.join(speech_dir, cat)):
            print("{0:s} does not exist. Exiting!".format(cat))
            return 0
        cat_speech_path = os.path.join(speech_dir, cat)
        cat_out_path = os.path.join(out_path, cat)
        map_speech_segments(map_dict[cat], cat_speech_path, cat_out_path)

    print("-"*50)
    print("saving map dict in: {0:s}".format(map_dict_path))
    pickle.dump(map_dict, open(map_dict_path, "wb"))
    print("all done ...")

if __name__ == "__main__":
    main()