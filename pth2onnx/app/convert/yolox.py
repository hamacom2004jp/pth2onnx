from pathlib import Path
from pth2onnx.app import common
import cv2
import logging
import platform

class Yolox(object):
    def __init__(self, logger:logging.Logger):
        """
        YOLOXクラスのコンストラクタ

        Args:
            logger (logging.Logger): ロガーオブジェクト
        """
        self.logger = logger


    def install(self, pycmd:str = 'python', pipcmd:str = 'pip'):
        """
        YOLOXをインストールする

        Args:
            pycmd (str): Pythonコマンドのパス, by default 'python'
            pipcmd (str): pipコマンドのパス, by default 'pip'

        Returns:
            dict: インストール結果を示す辞書
        """
        cwd = Path('./YOLOX')
        if not cwd.exists():
            returncode, _ = common.cmd("git clone https://github.com/Megvii-BaseDetection/YOLOX", self.logger)
            if returncode != 0:
                self.logger.error(f"Install failed. returncode={returncode}")
                return {'error':f"Install failed. returncode={returncode}"}

        if not (cwd / '.venv').exists():
            returncode, _ = common.cmd(f"{pycmd} -m venv .venv", self.logger, cwd=cwd)
            if returncode != 0:
                self.logger.error(f"Install failed. returncode={returncode}")
                return {'error':f"Install failed. returncode={returncode}"}

        actcmd = '.venv\\Scripts\\activate.bat' if platform.system() == 'Windows' else '. .venv/bin/activate'
        self.logger.debug(f"Current directory:{cwd}")
        returncode, _ = common.cmd(f"{actcmd} && python -m pip install --upgrade pip", self.logger, cwd=cwd)
        if returncode != 0:
            self.logger.error(f"Install failed. returncode={returncode}")
            return {'error':f"Install failed. returncode={returncode}"}

        returncode, _ = common.cmd(f"{actcmd} && {pipcmd} install -r requirements.txt", self.logger, cwd=cwd)
        if returncode != 0:
            self.logger.error(f"Install failed. returncode={returncode}")
            return {'error':f"Install failed. returncode={returncode}"}

        returncode, _ = common.cmd(f"{actcmd} && {pipcmd} install onnxruntime", self.logger, cwd=cwd)
        if returncode != 0:
            self.logger.error(f"Install failed. returncode={returncode}")
            return {'error':f"Install failed. returncode={returncode}"}

        returncode, _ = common.cmd(f"{actcmd} && {pipcmd} install -v -e .", self.logger, cwd=cwd)
        if returncode != 0:
            self.logger.error(f"Install failed. returncode={returncode}")
            return {'error':f"Install failed. returncode={returncode}"}

        return {'success':f"Install successed."}


    def zoo(self):
        """
        YOLOXのモデル一覧を取得するURLを示す

        Returns:
            dict: モデル一覧を示すURL
        """
        return {'site':f"https://github.com/Megvii-BaseDetection/YOLOX/#benchmark"}


    def demo(self, model_name:str, weight_file:Path, input_image:Path = Path('assets/dog.jpg'), model_img_size:int = 640, clsth:float=0.25, nms:float=0.45, output_preview:bool=False, pycmd:str = 'python'):
        """
        YOLOXのデモを実行する

        Args:
            model_name (str): モデル名
            weight_file (Path): 重みファイルのパス
            input_image (Path): 入力画像のパス, by default 'assets/dog.jpg'
            model_img_size (int): モデルの画像サイズ, by default 640
            clsth (float): クラス閾値, by default 0.25
            nms (float): NMS閾値, by default 0.45
            output_preview (bool): プレビュー画像を表示するかどうか, by default False
            pycmd (str): Pythonコマンドのパス, by default 'python'

        Returns:
            dict: デモ結果を示す辞書
        """
        cwd = Path('./YOLOX')
        if not cwd.exists() or not (cwd / '.venv').exists():
            self.logger.error(f"YOLOX is not installed. Run the command 'pth2onnx -m yolox -c install -f'.")
            return {'error':f"YOLOX is not installed. Run the command 'pth2onnx -m yolox -c install -f'."}
        weight_file = Path(weight_file) if isinstance(weight_file, str) else weight_file
        input_image = Path(input_image) if isinstance(input_image, str) else input_image

        actcmd = '.venv\\Scripts\\activate.bat' if platform.system() == 'Windows' else '.venv/Scripts/activate'
        self.logger.debug(f"Current directory:{cwd}")
        returncode, _ = common.cmd(f"{actcmd} && {pycmd} tools/demo.py image -n {model_name} -c {weight_file} --path {input_image}"
                                   f" --conf {clsth} --nms {nms} --tsize {model_img_size} --save_result --device [cpu/gpu]", self.logger, cwd=cwd)
        if returncode != 0:
            self.logger.error(f"Demo failed. returncode={returncode}")
            return {'error':f"Demo failed. returncode={returncode}"}
        outfile = common.find_max_update_file(cwd / 'YOLOX_outputs', '**/*.jpg')
        if output_preview:
            with open(outfile, 'rb') as f:
                img_npy = common.imgfile2npy(f)
                cv2.imshow(str(outfile), img_npy)
                cv2.waitKey(0)
        return {'success':f"outfile={outfile}"}


    def convert(self, model_name:str, weight_file:Path, output_file:Path = None, pycmd:str = 'python'):
        """
        YOLOXのモデルをONNXに変換する

        Args:
            model_name (str): モデル名
            weight_file (Path): 重みファイルのパス
            output_file (Path): 出力ファイルのパス
            pycmd (str): Pythonコマンドのパス, by default 'python'

        Returns:
            dict: 変換結果を示す辞書
        """
        cwd = Path('./YOLOX')
        if not cwd.exists() or not (cwd / '.venv').exists():
            self.logger.error(f"YOLOX is not installed. Run the command 'pth2onnx -m yolox -c install -f'.")
            return {'error':f"YOLOX is not installed. Run the command 'pth2onnx -m yolox -c install -f'."}
        weight_file = Path(weight_file) if isinstance(weight_file, str) else weight_file
        output_file = Path(output_file) if isinstance(output_file, str) else output_file

        actcmd = '.venv\\Scripts\\activate.bat' if platform.system() == 'Windows' else '.venv/Scripts/activate'
        self.logger.debug(f"Current directory:{cwd}")

        if output_file is None:
            output_file = weight_file.parent / Path(model_name + '.onnx')
        returncode, _ = common.cmd(f"{actcmd} && {pycmd} tools/export_onnx.py -n {model_name} -c {weight_file} --output-name {output_file} --no-onnxsim", self.logger, cwd=cwd)
        if returncode != 0:
            self.logger.error(f"Convert failed. returncode={returncode}")
            return {'error':f"Convert failed. returncode={returncode}"}
        return {'success':f"outfile={output_file}"}


    def inference(self, onnx_file:Path, input_image:Path = Path('assets/dog.jpg'), output_dir:Path = Path('inference/output'), score_th:float=0.3, input_size:int=416, output_preview:bool=False, pycmd:str = 'python'):
        """
        ONNXファイルを使用して推論を実行します。

        Parameters:
            onnx_file (Path): ONNXファイルのパス
            input_image (Path, optional): 入力画像のパス (デフォルトはPath('assets/dog.jpg'))
            output_dir (Path, optional): 出力ディレクトリのパス (デフォルトはPath('./outputs/'))
            score_th (float, optional): スコアの閾値 (デフォルトは0.3)
            input_size (int, optional): 入力画像のサイズ (デフォルトは416)
            output_preview (bool, optional): プレビュー画像を表示するかどうか (デフォルトはFalse)
            pycmd (str, optional): Pythonコマンドのパス (デフォルトは'python')

        Returns:
            dict: 処理結果を示す辞書。成功時は{'success': 'outfile=<出力ファイルパス>'}、失敗時は{'error': '<エラーメッセージ>'}
        """
        cwd = Path('./YOLOX')
        if not cwd.exists() or not (cwd / '.venv').exists():
            self.logger.error(f"YOLOX is not installed. Run the command 'pth2onnx -m yolox -c install -f'.")
            return {'error':f"YOLOX is not installed. Run the command 'pth2onnx -m yolox -c install -f'."}
        onnx_file = Path(onnx_file) if isinstance(onnx_file, str) else onnx_file
        input_image = Path(input_image) if isinstance(input_image, str) else input_image
        output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir

        actcmd = '.venv\\Scripts\\activate.bat' if platform.system() == 'Windows' else '.venv/Scripts/activate'
        self.logger.debug(f"Current directory:{cwd}")
        returncode, _ = common.cmd(f"{actcmd} && {pycmd} demo/ONNXRuntime/onnx_inference.py -m {onnx_file} --image_path {input_image} --output_dir {output_dir} "
                                    f"--score_thr {score_th} --input_shape {input_size},{input_size}", self.logger, cwd=cwd)
        if returncode != 0:
            self.logger.error(f"Onnx inference failed. returncode={returncode}")
            return {'error':f"Onnx inference failed. returncode={returncode}"}
        outfile = common.find_max_update_file(cwd / output_dir, '**/*.jpg')
        if output_preview:
            with open(outfile, 'rb') as f:
                img_npy = common.imgfile2npy(f)
                cv2.imshow(str(outfile), img_npy)
                cv2.waitKey(0)
            return {'success':f"outfile={outfile}"}

