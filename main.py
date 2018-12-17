#!/usr/bin/python


from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from tools import ImageProccesisngModuls
import ProfileHandler as ph
import csv
from collections import defaultdict


def pre_encode_post(input_dir, input_seq_list, interpolation_method):

    new_size = 'wqvga'

    # ----------------------------------down-sample-----------------------------------------

    imp = ImageProccesisngModuls(input_dir, input_seq_list, 'down_sampled_' +
                                 input_seq_list.split('/')[-1].split('.')[0]+'/', 'ffmpeg/')
    #
    seq_list = imp.DownUp_sampling_ffmpeg(new_size, interpolation_method)

    # create allinfo file for encoding with down-sampled sequences
    allinfof = 'allInfo_encoder/all_info_' + input_seq_list.split('/')[-1].split('.')[0]+'.txt'
    all_info_file(allinfof, 'down_sampled_' + input_seq_list.split('/')[-1].split('.')[0]+'/', seq_list
                  ,'encoded_down_sampled_' + input_seq_list.split('/')[-1].split('.')[0]+'/')

    # -----------------------------------encode----------------------------------------------

    current_profile = ph.ProfileHandler(allinfof)
    out_folder = current_profile.encode()
    #
    # # extract rate-distortion for encoding
    evaluation = ph.EvaluationResults(allinfof, out_folder)
    evaluation.read_logs()

    # ------------------------------------up-sample--------------------------------------------
    fid_seq_list = open(input_seq_list, 'r')
    fid_seq_list_in = open(input_seq_list.split('.')[0] + '_sampled.txt', 'r')

    raw_lines_seq_in = fid_seq_list_in.readlines()
    raw_lines_seq = fid_seq_list.readlines()

    for i in range(len(raw_lines_seq)):
        current_out = 'encoded_down_sampled_' + input_seq_list.split('/')[-1].split('.')[0] + '/' + out_folder + '/' \
                      + raw_lines_seq_in[i].split('.')[0] + '/'
        imp1 = ImageProccesisngModuls(current_out, current_out + 'Decoded_list_seq_' +
                                      raw_lines_seq_in[i].split('.')[0] + '.txt', current_out + 'up_sampled/', 'ffmpeg/')

        imp1.DownUp_sampling_ffmpeg(raw_lines_seq[i].split('_')[1].split('x')[0] + 'x' +
                                    raw_lines_seq[i].split('_')[1].split('x')[1], interpolation_method)

        imp2 = ImageProccesisngModuls(input_dir, input_seq_list, current_out + 'up_sampled/', 'ffmpeg/', current_out
                                      + 'Decoded_list_seq_' + raw_lines_seq_in[i].split('.')[0] + '_sampled.txt')
        imp2.cal_psnr()

        # gather all information in one csv file
        for_rate = open(current_out + raw_lines_seq_in[i].split('.')[0] + '_all.csv')
        for_psnr = open(current_out + '/up_sampled/Sampled_list.csv')
        new_psnr_with_rate = open(current_out + raw_lines_seq_in[i].split('.')[0] + '_all_ffmpeg_psnr.csv', mode= 'w')
        writer_new_psnr_with_rate = csv.writer(new_psnr_with_rate)

        columns = defaultdict(list)
        reader_for_rate = csv.reader(for_rate, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in reader_for_rate:
            for (it1, v) in enumerate(row):
                columns[it1].append(v)

        reader_for_psnr = csv.reader(for_psnr)
        for (it2, row) in enumerate(reader_for_psnr):
            writer_new_psnr_with_rate.writerow([columns[1][it2]] + row)


def all_info_file(nameoffile, input_dir, seq_list, output_dir):
    with open(nameoffile, 'w') as fidw:
        fidw.write('input directory :' + input_dir + '\n')
        fidw.write('input_sequences :' + seq_list + '\n')
        fidw.write('output directory :' + output_dir + '\n')
        rest_config = 'codec_path :/home/vagrant/1-Codes/PycharmProjects/VVC_Diff_Configs/' + '\n' \
                        'encoder_name :EncoderApp_VTM' + '\n' \
                        'decoder_name :DecoderApp_VTM' + '\n' \
                        'config_file_dir:cfg/' + '\n' \
                        'config_file:encoder_randomaccess_vtm.cfg' + '\n' \
                        'config_ovral : -v 6' + '\n' \
                        'config_rep_1:-f:10' + '\n' \
                        'config_rep_2:-s:32' + '\n' \
                        'config_rep_3:-q:22:27:32:37' + '\n'

        fidw.write(rest_config)


def encode(input_dir, input_seq_list):

    allinfof = 'allInfo_encoder/all_info_' + input_seq_list.split('/')[-1].split('.')[0] + '.txt'
    all_info_file(allinfof, input_dir, input_seq_list
                  ,'encoded_original_' + input_seq_list.split('/')[-1].split('.')[0]+'/')
    current_profile = ph.ProfileHandler(allinfof)
    out_folder = current_profile.encode()

    # extract rate-distortion for encoding
    evaluation = ph.EvaluationResults(allinfof, out_folder)
    evaluation.read_logs()


def main():

    pre_encode_post('input/seq/', 'input/seq_list_classA.txt', 'bilinear')
    encode('input/seq/', 'input/seq_list_classA.txt')


if __name__ == "__main__":
    main()
