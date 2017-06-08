# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import argparse
import os
import utilities.misc_csv as misc_csv

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from .filename_matching import KeywordsMatching


def _input_path_search(config):
    # match flexible input modality sections
    image_keywords = []
    label_keywords = []
    w_map_keywords = []
    for section in config.sections():
        section = section.lower()
        if 'image' in section:
            image_keywords.append(config.items(section))
        elif 'label' in section:
            label_keywords.append(config.items(section))
        elif 'weight' in section:
            w_map_keywords.append(config.items(section))
    image_matcher = [KeywordsMatching.from_tuple(mod_info)
                     for mod_info in image_keywords]
    label_matcher = [KeywordsMatching.from_tuple(mod_info)
                     for mod_info in label_keywords]
    w_map_matcher = [KeywordsMatching.from_tuple(mod_info)
                     for mod_info in w_map_keywords]
    return image_matcher, label_matcher, w_map_matcher


def run():
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "-c", "--conf",
        help="Specify configurations from a file", metavar="File")
    config_file = os.path.join(
        os.path.dirname(__file__), '../config/default_config.txt')
    default_file = {"conf": config_file}
    file_parser.set_defaults(**default_file)
    file_arg, remaining_argv = file_parser.parse_known_args()

    config = configparser.ConfigParser()
    config.read([file_arg.conf])
    # initialise search of image modality filenames
    image_matcher, label_matcher, w_map_matcher = _input_path_search(config)
    defaults = dict(config.items("settings"))

    parser = argparse.ArgumentParser(
        parents=[file_parser],
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.set_defaults(**defaults)

    parser.add_argument(
        "action", help="train or inference", choices=['train', 'inference'])

    parser.add_argument(
        "--cuda_devices",
        metavar='',
        help="Set CUDA_VISIBLE_DEVICES variable, e.g. '0,1,2,3'; " \
             "leave blank to use the system default value")
    parser.add_argument(
        "--model_dir",
        metavar='',
        help="Directory to save/load intermediate training models and logs")
    parser.add_argument(
        "--net_name",
        help="Choose a net from ./network/ ",
        metavar='')

    parser.add_argument(
        "--queue_length",
        help="Set size of preprocessing buffer queue",
        metavar='',
        type=int)
    parser.add_argument(
        "--num_threads",
        help="Set number of preprocessing threads",
        metavar='',
        type=int)

    parser.add_argument(
        "--spatial_rank", metavar='', help="Set input spatial rank",
        choices=[2,2.5,3], type=float)
    parser.add_argument(
        "--batch_size", metavar='', help="Set batch size of the net", type=int)
    parser.add_argument(
        "--image_size", metavar='', help="Set input image size", type=int)
    parser.add_argument(
        "--label_size", metavar='', help="Set label size of the net", type=int)
    parser.add_argument(
        "--w_map_size", metavar='', help="Set weight map size of the net", type=int)
    parser.add_argument(
        "--num_classes", metavar='', help="Set number of classes", type=int)

    parser.add_argument(
        "--volume_padding_size",
        metavar='',
        help="Set padding size of each volume (in all dimensions)",
        type=int)
    parser.add_argument(
        "--histogram_ref_file",
        help="A reference file of histogram for intensity normalisation")
    parser.add_argument(
        "--normalisation",
        help="Indicates if the normalisation must be performed"
    )
    parser.add_argument(
        "--whitening",
        help="Indicates if the whitening of the data should be applied"
    )
    parser.add_argument(
        "--image_interp_order",
        help="image interpolation order when do resampling/rotation",
        type=int
    )
    parser.add_argument(
        "--label_interp_order",
        help="label interpolation order when do resampling/rotation",
        type=int
    )
    parser.add_argument(
        "--w_map_interp_order",
        help="weight map interpolation order when do resampling/rotation",
        type=int
    )
    parser.add_argument(
        "--spatial_scaling",
        help="Indicates if the spatial scaling must be performed"
    )
    parser.add_argument(
        "--max_percentage",
        help="the spatial scaling factor in [-max_percentage, max_percentage]",
        type=float
    )
    parser.add_argument(
        "--reorientation",
        help="Indicates if the loaded images are put by default in the RAS "
             "orientation"
    )
    parser.add_argument(
        "--resampling",
        help="Indicates if the volumes must be interpolated to be in "
             "representing images of 1 1 1 resolution"
    )
    parser.add_argument(
        "--norm_type",
        default='percentile',
        help="Type of normalisation to perform"
    )
    parser.add_argument(
        "--cutoff_min",
        help="Cutoff values for the normalisation process",
        type=float
    )
    parser.add_argument(
        "--cutoff_max",
        help="Cutoff values for the normalisation process",
        type=float
    )
    parser.add_argument(
        "--multimod_mask_type",
        choices=['and', 'or', 'multi'],
        help="Way of associating the masks obtained for the different "
             "modalities"
    )
    parser.add_argument(
        "--mask_type",
        choices=['threshold_plus', 'threshold_minus',
                 'otsu_plus', 'otsu_minus', 'mean'],
        help="type of masking strategy used"
    )
    parser.add_argument(
        "--rotation",
        help="Indicates if a rotation should be applied"
    )
    parser.add_argument(
        "--min_angle",
        help="minimum rotation angle when rotation augmentation is enabled",
        type=float
    )
    parser.add_argument(
        "--max_angle",
        help="maximum rotation angle when rotation augmentation is enabled",
        type=float
    )

    parser.add_argument(
        "--num_gpus",
        help="[Training only] Set number of GPUs",
        metavar='',
        type=int)
    parser.add_argument(
        "--sample_per_volume",
        help="[Training only] Set number of samples per image in each batch",
        metavar='',
        type=int)

    parser.add_argument(
        "--lr",
        help="[Training only] Set learning rate", type=float)
    parser.add_argument(
        "--decay",
        help="[Training only] Set weight decay", type=float)
    parser.add_argument(
        "--loss_type",
        metavar='TYPE_STR', help="[Training only] Specify loss type")
    parser.add_argument(
        "--reg_type",
        metavar='TYPE_STR', help="[Training only] Specify regulariser type")
    parser.add_argument(
        "--starting_iter",
        metavar='', help="[Training only] Resume from iteration n", type=int)
    parser.add_argument(
        "--save_every_n",
        metavar='', help="[Training only] Model saving frequency", type=int)
    parser.add_argument(
        "--max_iter",
        metavar='', help="[Training only] Total number of iterations", type=int)

    parser.add_argument(
        "--border",
        metavar='',
        help="[Inference only] Width of cropping borders for segmented patch",
        type=int)
    parser.add_argument(
        "--pred_iter",
        metavar='',
        help="[Inference only] Using model at iteration n",
        type=int)
    parser.add_argument(
        "--save_seg_dir",
        metavar='',
        help="[Inference only] Prediction directory name")  # without '/'
    parser.add_argument(
        "--output_interp_order",
        metavar='',
        help="[Inference only] interpolation order of the network output",
        type=int)
    parser.add_argument(
        "--output_prob",
        metavar='',
        help="[Inference only] whether to output multi-class probabilities")
    #parser.add_argument(
    #    "--min_sampling_ratio",
    #    help="Minumum ratio to satisfy in the sampling of different labels"
    #)
    #parser.add_argument(
    #    "--min_numb_labels",
    #    help="Minimum number of different labels present in a patch"
    #)
    args = parser.parse_args(remaining_argv)

    # creating output
    image_csv_path = os.path.join(args.model_dir, 'image_files.csv')
    misc_csv.write_matched_filenames_to_csv(image_matcher, image_csv_path)

    if label_matcher:
        label_csv_path = os.path.join(args.model_dir, 'label_files.csv')
        misc_csv.write_matched_filenames_to_csv(label_matcher, label_csv_path)
    else:
        label_csv_path = None

    if w_map_matcher:
        w_map_csv_path = os.path.join(args.model_dir, 'w_map_files.csv')
        misc_csv.write_matched_filenames_to_csv(w_map_matcher, w_map_csv_path)
    else:
        w_map_csv_path = None

    csv_dict = {'input_image_file': image_csv_path,
                'target_image_file': label_csv_path,
                'weight_map_file': w_map_csv_path,
                'target_note': None}

    args.reorientation = True if args.reorientation == "True" else False
    args.resampling = True if args.resampling == "True" else False
    args.normalisation = True if args.normalisation == "True" else False
    args.whitening = True if args.whitening == "True" else False
    args.rotation = True if args.rotation == "True" else False
    args.spatial_scaling = True if args.spatial_scaling == "True" else False
    args.output_prob = True if args.output_prob == "True" else False
    return args, csv_dict


def run_eval():
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument("-c", "--conf",
                             help="Specify configurations from a file",
                             metavar="File")
    config_file = os.path.join(os.path.dirname(__file__),
                               '../config/default_eval_config.txt')
    defaults = {"conf": config_file}
    file_parser.set_defaults(**defaults)
    file_arg, remaining_argv = file_parser.parse_known_args()

    if file_arg.conf:
        config = configparser.ConfigParser()
        config.read([file_arg.conf])
        defaults = dict(config.items("settings"))

    parser = argparse.ArgumentParser(
        parents=[file_parser],
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.set_defaults(**defaults)
    parser.add_argument("action",
                        help="compute ROI statistics or compare segmentation maps",
                        choices=['roi', 'compare'])
    parser.add_argument("--threshold",
                        help="threshold to obtain binary segmentation",
                        type=float)
    parser.add_argument("--step",
                        help="step of increment when considering probabilistic segmentation",
                        type=float)
    parser.add_argument("--ref_dir",
                        help="path to the image to use as reference")
    parser.add_argument("--seg_dir",
                        help="path where to find the images to evaluate")
    parser.add_argument("--img_dir",
                        help="path where to find the images to evaluate")
    parser.add_argument("--save_csv_dir",
                        help="path where to save the output csv file")
    parser.add_argument("--ext",
                        help="extension of the image files to be read")
    parser.add_argument("--seg_type",
                        help="type of input: discrete maps or probabilistic maps")
    args = parser.parse_args(remaining_argv)
    return args
