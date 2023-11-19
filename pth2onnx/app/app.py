from pathlib import Path
from pth2onnx.app import common
from pth2onnx.app.convert import yolox
import argparse
import sys
import time


def main(HOME_DIR:str):
    parser = argparse.ArgumentParser(prog='python -m pth2onnx', description='Convert PyTorch model to Onnx model.')
    parser.add_argument('-u', '--useopt', help=f'Use options file.')
    parser.add_argument('-s', '--saveopt', help=f'save options file. with --useopt option.', action='store_true')
    parser.add_argument('-f', '--format', help='Setting the cmd format.', action='store_true')
    parser.add_argument('-m', '--mode', help='Setting the boot mode.', choices=['yolox'])
    parser.add_argument('--data', help='Setting the data directory.', default=Path(HOME_DIR) / ".pth2onnx")
    parser.add_argument('--timeout', help='Setting the cmd timeout.', type=int, default=15)
    parser.add_argument('-c', '--cmd', help='Setting the cmd type.', choices=['install', 'zoo', 'demo', 'convert', 'inference'])
    parser.add_argument('--pycmd', help='Setting the python command.', default='python')
    parser.add_argument('--pipcmd', help='Setting the pip command.', default='pip')
    parser.add_argument('--yolox_model_name', help='Setting the model name.', default=None)
    parser.add_argument('--yolox_weight_file', help='Setting the model weight file in YOLOX dir.', default=None)
    parser.add_argument('--yolox_input_image', help='Setting the input image file in YOLOX dir.', default='assets/dog.jpg')
    parser.add_argument('--yolox_model_img_size', help='Setting the input image file in YOLOX dir.', default=416)
    parser.add_argument('--yolox_class_th', help='Setting the class threshold.', default=0.25)
    parser.add_argument('--yolox_nms_th', help='Setting the nms threshold.', default=0.45)
    parser.add_argument('--yolox_output_preview', help='Setting the output preview.', action='store_true')
    parser.add_argument('--yolox_onnx_file', help='Setting the output onnx weight file.', default=None)
    parser.add_argument('--yolox_output_dir', help='Setting the output inference directory.', default='inference/output')
    parser.add_argument('--yolox_score_th', help='Setting the inference score threshold.', default=0.3)

    args = parser.parse_args()
    args_dict = vars(args)
    opt = common.loadopt(args.useopt)
    format = common.getopt(opt, 'format', preval=args_dict, withset=True)
    mode = common.getopt(opt, 'mode', preval=args_dict, withset=True)
    data = common.getopt(opt, 'data', preval=args_dict, withset=True)
    cmd = common.getopt(opt, 'cmd', preval=args_dict, withset=True)
    pycmd = common.getopt(opt, 'pycmd', preval=args_dict, withset=True)
    pipcmd = common.getopt(opt, 'pipcmd', preval=args_dict, withset=True)
    yolox_model_name = common.getopt(opt, 'yolox_model_name', preval=args_dict, withset=True)
    yolox_weight_file = common.getopt(opt, 'yolox_weight_file', preval=args_dict, withset=True)
    yolox_input_image = common.getopt(opt, 'yolox_input_image', preval=args_dict, withset=True)
    yolox_model_img_size = common.getopt(opt, 'yolox_model_img_size', preval=args_dict, withset=True)
    yolox_class_th = common.getopt(opt, 'yolox_class_th', preval=args_dict, withset=True)
    yolox_nms_th = common.getopt(opt, 'yolox_nms_th', preval=args_dict, withset=True)
    yolox_output_preview = common.getopt(opt, 'yolox_output_preview', preval=args_dict, withset=True)
    yolox_onnx_file = common.getopt(opt, 'yolox_onnx_file', preval=args_dict, withset=True)
    yolox_output_dir = common.getopt(opt, 'yolox_output_dir', preval=args_dict, withset=True)
    yolox_score_th = common.getopt(opt, 'yolox_score_th', preval=args_dict, withset=True)

    tm = time.time()

    if args.saveopt:
        if args.useopt is None:
            common.print_format({"warn":f"Please specify the --useopt option."}, format, tm)
            exit(1)
        common.saveopt(opt, args.useopt)

    if mode == 'yolox':
        logger, _ = common.load_config(mode)
        y = yolox.Yolox(logger)
        if cmd == 'install':
            ret = y.install(pycmd=pycmd, pipcmd=pipcmd)
            common.print_format(ret, format, tm)

        elif cmd == 'zoo':
            ret = y.zoo()
            common.print_format(ret, format, tm)

        elif cmd == 'demo':
            ret = y.demo(model_name=yolox_model_name, weight_file=yolox_weight_file, input_image=yolox_input_image, model_img_size=yolox_model_img_size,
                         clsth=yolox_class_th, nms=yolox_nms_th, output_preview=yolox_output_preview, pycmd=pycmd)
            common.print_format(ret, format, tm)

        elif cmd == 'convert':
            ret = y.convert(model_name=yolox_model_name, weight_file=yolox_weight_file, output_file=yolox_onnx_file)
            common.print_format(ret, format, tm)

        elif cmd == 'inference':
            ret = y.inference(onnx_file=yolox_onnx_file, input_image=yolox_input_image, output_dir=yolox_output_dir, score_th=yolox_score_th, input_size=yolox_model_img_size, output_preview=yolox_output_preview, pycmd=pycmd)
            common.print_format(ret, format, tm)

        else:
            common.print_format({"warn":f"Unkown command."}, format, tm)
            parser.print_help()

    else:
        parser.print_help()

