#!/usr/bin/env python3
import argparse
from pathlib import Path

import numpy as np
import skimage.color as color
import matplotlib.pyplot as plt
import scipy.ndimage.interpolation as sni
import caffe

base_dir = Path(__file__).resolve().parents[1]
upstream = base_dir / 'upstream'


def parse_args():
    parser = argparse.ArgumentParser(description='Run colorful on a set of images')
    parser.add_argument('images', nargs='+', help='input images')
    parser.add_argument('destination', help='destination directory')
    parser.add_argument('--gpu', help='gpu id', type=int, default=0)
    parser.add_argument('--prototxt', help='prototxt filepath', default=str(upstream / 'models/colorization_deploy_v2.prototxt'))
    parser.add_argument('--caffemodel', help='caffemodel filepath', default=str(upstream / 'models/colorization_release_v2.caffemodel'))
    args = parser.parse_args()
    return args


def main(args):
    caffe.set_mode_gpu()
    caffe.set_device(args.gpu)

    net = caffe.Net(args.prototxt, args.caffemodel, caffe.TEST)

    (H_in, W_in) = net.blobs['data_l'].data.shape[2:]  # input shape
    (H_out, W_out) = net.blobs['class8_ab'].data.shape[2:]  # output shape
    print('Network input/output shape: {}x{} and {}x{}'.format(W_in, H_in, W_out, H_out))

    pts_in_hull = np.load(str(upstream / 'resources/pts_in_hull.npy'))  # load cluster centers
    net.params['class8_ab'][0].data[:, :, 0, 0] = pts_in_hull.transpose((1, 0))  # populate cluster centers as 1x1 convolution kernel

    destination = Path(args.destination)
    for path in args.images:
        output = destination / Path(path).name
        if output.exists():
            print('{} exists, skipping input image {}'.format(output, path))
            continue
        img_rgb = caffe.io.load_image(path)

        img_lab = color.rgb2lab(img_rgb)
        img_l = img_lab[:, :, 0]
        (H_orig, W_orig) = img_rgb.shape[:2]  # original shape

        # Resize image to network input size
        img_rs = caffe.io.resize_image(img_rgb, (H_in, W_in))  # resize image to network input size
        img_lab_rs = color.rgb2lab(img_rs)
        img_l_rs = img_lab_rs[:, :, 0]

        net.blobs['data_l'].data[0, 0, :, :] = img_l_rs - 50  # subtract 50 for mean-centering
        net.forward()  # run network

        ab_dec = net.blobs['class8_ab'].data[0, :, :, :].transpose((1, 2, 0))  # result
        ab_dec_us = sni.zoom(ab_dec, (1. * H_orig / H_out,1. * W_orig / W_out, 1))  # upsample to match original shape
        img_lab_out = np.concatenate((img_l[:, :, np.newaxis], ab_dec_us), axis=2)  # concatenate with original L
        img_rgb_out = (255 * np.clip(color.lab2rgb(img_lab_out), 0, 1)).astype('uint8') # convert to RGB

        plt.imsave(str(output), img_rgb_out)


if __name__ == '__main__':
    main(parse_args())
