from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw
from pkg_resources import resource_string
from tabulate import tabulate
from typing import List
import base64
import json
import logging
import logging.config
import numpy as np
import os
import random
import requests
import shutil
import string
import subprocess
import time
import yaml

APP_ID = 'pth2onnx'

def load_config(mode:str):
    """
    指定されたモードのロガーと設定を読み込みます。

    Args:
        mode (str): モード名

    Returns:
        logger (logging.Logger): ロガー
        config (dict): 設定
    """
    log_config = yaml.safe_load(resource_string(APP_ID, "logconf.yml"))
    logging.config.dictConfig(log_config)
    logger = logging.getLogger(mode)
    config = yaml.safe_load(resource_string(APP_ID, "config.yml"))
    return logger, config

def saveopt(opt:dict, opt_path:Path):
    """
    コマンドラインオプションをJSON形式でファイルに保存します。

    Args:
        opt (dict): コマンドラインオプション
        opt_path (Path): 保存先のファイルパス
    """
    if opt_path is None:
        return
    def _json_enc(o):
        if isinstance(o, Path):
            return str(o)
        raise TypeError(f"Type {type(o)} not serializable")
    with open(opt_path, 'w') as f:
        json.dump(opt, f, indent=4, default=_json_enc)

def loadopt(opt_path:str):
    """
    JSON形式のファイルからコマンドラインオプションを読み込みます。

    Args:
        opt_path (str): 読み込むファイルパス

    Returns:
        dict: 読み込んだコマンドラインオプション
    """
    if opt_path is None or not Path(opt_path).exists():
        return dict()
    with open(opt_path) as f:
        return json.load(f)

def getopt(opt:dict, key:str, preval=None, defval=None, withset=False):
    """
    コマンドラインオプションから指定されたキーの値を取得します。

    Args:
        opt (dict): コマンドラインオプション
        key (str): キー
        preval (Any, optional): 優先する値. Defaults to None.
        defval (Any, optional): デフォルト値. Defaults to None.
        withset (bool, optional): キーが存在しない場合にデフォルト値を設定するかどうか. Defaults to False.

    Returns:
        Any: 取得した値
    """
    if preval is not None:
        v = preval
        if isinstance(preval, dict):
            v = preval.get(key, defval)
        if (v is None or not v) and key in opt:
            v = opt[key]
        if withset:
            opt[key] = v
        return v
    if key in opt:
        return opt[key]
    else:
        if withset:
            opt[key] = defval
        return defval

def mkdirs(dir_path:Path):
    """
    ディレクトリを中間パスも含めて作成します。

    Args:
        dir_path (Path): 作成するディレクトリのパス

    Returns:
        Path: 作成したディレクトリのパス
    """
    if not dir_path.exists():
        dir_path.mkdir(parents=True)
    if not dir_path.is_dir():
        raise BaseException(f"Don't make diredtory.({str(dir_path)})")
    return dir_path

def rmdirs(dir_path:Path):
    """
    ディレクトリをサブディレクトリ含めて削除します。

    Args:
        dir_path (Path): 削除するディレクトリのパス
    """
    shutil.rmtree(dir_path)

def random_string(size:int=16):
    """
    ランダムな文字列を生成します。

    Args:
        size (int, optional): 文字列の長さ. Defaults to 16.

    Returns:
        str: 生成された文字列
    """
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=size))

def print_format(data:dict, format:bool, tm:float):
    """
    データを指定されたフォーマットで出力します。

    Args:
        data (dict): 出力するデータ
        format (bool): フォーマットするかどうか
        tm (float): 処理時間
    """
    if format:
        if 'success' in data and type(data['success']) == list:
            print(tabulate(data['success'], headers='keys'))
        elif 'success' in data and type(data['success']) == dict:
            print(tabulate([data['success']], headers='keys'))
        elif type(data) == list:
            print(tabulate(data, headers='keys'))
        else:
            print(tabulate([data], headers='keys'))
        print(f"{time.time() - tm:.03f} seconds.")
    else:
        print(data)

BASE_MODELS = dict(
    Classification_EfficientNet_Lite4=dict(
        site='https://github.com/onnx/models/tree/main/vision/classification/efficientnet-lite4',
        image_width=224,
        image_height=224
    ),
    #Classification_Resnet=dict(
    #    site='https://github.com/onnx/models/tree/main/vision/classification/resnet',
    #    image_width=224,
    #    image_height=224
    #),
    ObjectDetection_YoloV3=dict(
        site='https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/yolov3',
        image_width=416,
        image_height=416
    ),
    ObjectDetection_TinyYoloV3=dict(
        site='https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/tiny-yolov3',
        image_width=416,
        image_height=416
    )
)

def download_file(url:str, save_path:Path):
    """
    ファイルをダウンロードします。

    Args:
        url (str): ダウンロードするファイルのURL
        save_path (Path): 保存先のファイルパス

    Returns:
        Path: 保存したファイルのパス
    """
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as f:
        f.write(r.content)
    return save_path

def cmd(cmd:str, logger:logging.Logger, cwd:Path=Path('.'), outlog:bool=True):
    """
    コマンドを実行します。

    Args:
        cmd (str): 実行するコマンド
        logger (logging.Logger): ロガー
        cwd (Path, optional): 実行するディレクトリ. Defaults to '.'.
        outlog (bool, optional): 出力をログに出力するかどうか. Defaults to True.

    Returns:
        Tuple[int, str]: コマンドの戻り値と出力
    """
    if outlog: logger.debug(f"cmd:{cmd}")
    proc = subprocess.Popen(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = None
    while proc.returncode is None:
        out = proc.stdout.readline()
        if out == b'' and proc.poll() is not None:
            break
        for enc in ['utf-8', 'cp932', 'utf-16', 'utf-16-le', 'utf-16-be']:
            try:
                output = out.decode(enc).rstrip()
                if outlog: logger.debug(f"output:{output}")
                break
            except UnicodeDecodeError:
                pass

    return proc.returncode, output

def find_max_update_file(dir_path:Path, glob:str) -> Path:
    """
    指定されたディレクトリ内のファイルの中で最も更新日時が新しいファイルを返します。

    Args:
        dir_path (Path): ディレクトリのパス
        glob (str): ファイルのパターン

    Returns:
        Path: 最も更新日時が新しいファイルのパス
    """
    files = list(dir_path.glob(glob))
    file_updates = {fpath: os.stat(fpath).st_mtime for fpath in files}
    ret = max(file_updates, key=file_updates.get)
    return ret

def npyfile2npy(fp) -> np.ndarray:
    """
    npyファイルからndarrayを読み込みます。

    Args:
        fp ([type]): npyファイルのパス

    Returns:
        np.ndarray: 読み込んだndarray
    """
    return np.load(fp)

def npybytes2npy(npy:bytes) -> np.ndarray:
    """
    バイト列からndarrayを読み込みます。

    Args:
        npy (bytes): ndarrayのバイト列

    Returns:
        np.ndarray: 読み込んだndarray
    """
    return np.load(BytesIO(npy))

def npy2b64str(npy:np.ndarray) -> str:
    """
    ndarrayをBase64エンコードした文字列を返します。

    Args:
        npy (np.ndarray): ndarray

    Returns:
        str: Base64エンコードされた文字列
    """
    return base64.b64encode(npy.tobytes()).decode('utf-8')

def npy2img(npy:np.ndarray) -> Image:
    """
    ndarrayをPILのImageオブジェクトに変換します。

    Args:
        npy (np.ndarray): ndarray

    Returns:
        Image: PILのImageオブジェクト
    """
    return Image.fromarray(npy)

def b64str2npy(b64str:str, shape:tuple, dtype:str='uint8') -> np.ndarray:
    """
    Base64エンコードされた文字列からndarrayを復元します。

    Args:
        b64str (str): Base64エンコードされた文字列
        shape (tuple): ndarrayの形状
        dtype (str, optional): ndarrayのデータ型. Defaults to 'uint8'.

    Returns:
        np.ndarray: 復元したndarray
    """
    return np.frombuffer(base64.b64decode(b64str), dtype=dtype).reshape(shape)

def npy2imgfile(npy, output_image_file:Path=None, image_type:str='jpg') -> None:
    """
    ndarrayを画像bytesに変換しoutput_image_fileに保存します。
    output_image_fileが省略された場合は保存されません

    Args:
        npy ([type]): ndarray
        output_image_file (Path): 保存先の画像ファイルパス
    """
    image = Image.fromarray(npy)
    img_byte = img2byte(image, format=image_type)
    if output_image_file is not None:
        with open(output_image_file, 'wb') as f:
            f.write(img_byte)
    return img_byte

def imgbytes2npy(img:bytes, dtype:str='uint8') -> np.ndarray:
    """
    画像のバイト列をndarrayに変換します。

    Args:
        img (bytes): 画像のバイト列
        dtype (str, optional): ndarrayのデータ型. Defaults to 'uint8'.

    Returns:
        np.ndarray: ndarray
    """
    img = Image.open(BytesIO(img))
    return np.array(img, dtype=dtype)

def imgfile2npy(fp, dtype:str='uint8') -> np.ndarray:
    """
    画像ファイルをndarrayに変換します。

    Args:
        fp ([type]): 画像ファイルのパス
        dtype (str, optional): ndarrayのデータ型. Defaults to 'uint8'.

    Returns:
        np.ndarray: ndarray
    """
    img = Image.open(fp)
    return np.array(img, dtype=dtype)

def img2npy(image:Image, dtype:str='uint8') -> np.ndarray:
    """
    PILのImageオブジェクトをndarrayに変換します。

    Args:
        image (Image): PILのImageオブジェクト
        dtype (str, optional): ndarrayのデータ型. Defaults to 'uint8'.

    Returns:
        np.ndarray: ndarray
    """
    return np.array(image, dtype=dtype)

def img2byte(image:Image, format:str='JPEG') -> bytes:
    """
    画像をバイト列に変換します。

    Args:
        image (Image): PILのImageオブジェクト

    Returns:
        bytes: 画像のバイト列
    """
    with BytesIO() as buffer:
        image.save(buffer, format="JPEG")
        return buffer.getvalue()

def draw_boxes(image:Image, boxes:List[List[float]], scores:List[float], classes:List[int], labels:List[str] = None, colors = None):
    """
    画像にバウンディングボックスを描画します。

    Args:
        image (Image): PILのImageオブジェクト
        boxes (List[List[float]]): バウンディングボックスの座標リスト
        scores (List[float]): バウンディングボックスのスコアリスト
        classes (List[int]): バウンディングボックスのクラスリスト
        labels (List[str], optional): クラスのラベルリスト. Defaults to None.
        colors (List, optional): バウンディングボックスの色リスト. Defaults to None.

    Returns:
        Image: 描画された画像
    """
    draw = ImageDraw.Draw(image)
    for box, score, cl in zip(boxes, scores, classes):
        y1, x1, y2, x2 = box
        x1 = max(0, np.floor(x1 + 0.5).astype(int))
        y1 = max(0, np.floor(y1 + 0.5).astype(int))
        x2 = min(image.width, np.floor(x2 + 0.5).astype(int))
        y2 = min(image.height, np.floor(y2 + 0.5).astype(int))
        color = colors[cl] if colors is not None else (255, 0, 0)
        draw.rectangle(((x1, y1), (x2, y2)), outline=color)

        label = labels[cl] if labels is not None else str(cl)
        draw.text((x1, y1), label, bbox={'facecolor': 'white', 'alpha': 0.7, 'pad': 10})
    
    return image