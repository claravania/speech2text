import os
import sys
import argparse
import json
import pickle

program_descrp = """
Read mapping between Kaldi segments name and order in which they appear in the
trancriptions + translations generated by fisher-callhome-corpus
"""

'''
example:
export JOSHUA=/afs/inf.ed.ac.uk/group/project/lowres/work/installs/fisher-callhome-corpus
python prep_map_kaldi_segments.py -m $JOSHUA -o $PWD/out/kaldi_segment_map.dict

'''

def main():
    parser = argparse.ArgumentParser(description=program_descrp)
    parser.add_argument('-m','--map_loc', help='fisher-callhome-corpus path',
                        required=True)
    parser.add_argument('-o','--out_name', help='output file path+name',
                        required=True)
    args = vars(parser.parse_args())
    map_loc = args['map_loc']
    out_name = args['out_name']

    if not os.path.exists(map_loc):
        print("fisher-callhome-corpus path given={0:s} does not exist".format(
                                                        map_loc))
        return 0

    # create output file directory:
    if not os.path.exists(os.path.dirname(out_name)):
        print("creating folder={0:s}".format(os.path.dirname(out_name)))
        os.makedirs(os.path.dirname(out_name))

    kaldi_out_dir = os.path.join(map_loc,"kaldi")

    json_files = [(os.path.splitext(f)[0], f)
                  for f in os.listdir(kaldi_out_dir)
                  if f.endswith(".json")]

    print(json_files)

    kaldi_segment_map = {}

    print("Reading json files from: {0:s}".format(kaldi_out_dir))

    for cat, json_file in json_files:
        print(json_file)
        with open(os.path.join(kaldi_out_dir, json_file)) as json_file:
            kaldi_segment_map[cat] = json.load(json_file)

    print("saving kaldi mapping in: {0:s}".format(out_name))
    pickle.dump(kaldi_segment_map, open(out_name, "wb"))
    print("all done ...")


if __name__ == "__main__":
    main()