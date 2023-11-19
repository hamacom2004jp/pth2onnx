# Convert PyTorch model to Onnx model

PyTorchで作成した重みファイルをONNX形式の重みファイルに変換するCLIアプリケーションです。

サポートしているAIタスクは以下のとおりです。
- Image Classification
- Object Detection

## 動作確認OS
- `Windows 10 Pro`
- `Windows 11 Pro`

## インストール方法

``` cmd or bash
pip install pth2onnx
```

## pth2onnxの実行方法
YOLOXモードの場合
``` cmd or bash
# githubからソースをダウンロードし、YOLOXフォルダ内に.venvを生成しインストールする
pth2onnx -m yolox -c install -f

# 学習済みモデルのダウンロード先URLを表示
pth2onnx -m yolox -c zoo -f
# see: https://github.com/Megvii-BaseDetection/YOLOX/#benchmark

# pytorchの重みファイルでデモを実行
pth2onnx -m yolox -c demo -f --yolox_model_name <モデル名> --yolox_weight_file <pytorchモデルファイルのパス> --yolox_output_preview
# モデル名は「yolox_nano」「yolox_tiny」「yolox_s」「yolox_m」「yolox_l」「yolox_x」など
# pytorchモデルファイルのパスはYOLOXフォルダ内のパス。「models/yolox_tiny.pth」など

# pytorchの重みファイルをONNXの重みファイルに変換
pth2onnx -m yolox -c convert -f --yolox_model_name <モデル名> --yolox_weight_file <pytorchモデルファイルのパス> --yolox_onnx_file <ONNXモデルファイルのパス>
# ONNXモデルファイルのパスはYOLOXフォルダ内のパス。「models/yolox_tiny.onnx」など

# ONNXの重みファイルで推論を実行
pth2onnx -m yolox -c inference -f --yolox_onnx_file <ONNXモデルファイルのパス> --yolox_model_img_size <モデルのINPUTサイズ> --yolox_output_preview
# モデルのINPUTサイズは「416」など

```

## その他便利なオプション
コマンドラインオプションが多いので、それを保存して再利用できるようにする
``` cmd or bash
# 通常のコマンドに「-u」と「-s」オプションを追加する
pth2onnx -u <オプションを保存するファイル> -s

# 次から使用するときは「-u」を使用する
pth2onnx -u <オプションを保存するファイル>
```

コマンドの実行結果を見やすくする。
``` cmd or bash
# 通常のコマンドに「-f」オプションを追加する
pth2onnx -f

# 「-f」オプションを外せば、結果はjson形式で取得できる
pth2onnx 
```

コマンドラインオプションのヘルプ。
``` cmd or bash
pth2onnx -h
```

## pth2onnxコマンドについて
```python -m pth2onnx```の省略形です。
実体は```scripts```ディレクトリ内にあります。

### データの保存場所
```
pathlib.Path(HOME_DIR) / '.pth2onnx'
```

## 動作確認したモデル
|AI Task|base|Model|
|------|------|------|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|YOLOX-Nano|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|YOLOX-Tiny|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|YOLOX-s|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|YOLOX-m|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|YOLOX-l|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|YOLOX-x|


## 開発環境構築
```
git clone https://github.com/hamacom2004jp/pth2onnx.git
cd pth2onnx
python -m venv .venv
.venv\Scripts\activate
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

## pyplにアップするための準備

``` cmd or bash
python setup.py sdist
python setup.py bdist_wheel
```

- pyplのユーザー登録【本番】
  https://pypi.org/account/register/

- pyplのユーザー登録【テスト】
  https://test.pypi.org/account/register/

- それぞれ2要素認証とAPIトークンを登録

- ホームディレクトリに```.pypirc```を作成
``` .pypirc
[distutils]
index-servers =
  pypi
  testpypi

[pypi]
repository: https://upload.pypi.org/legacy/
username: __token__
password: 本番環境のAPIトークン

[testpypi]
repository: https://test.pypi.org/legacy/
username: __token__
password: テスト環境のAPIトークン
```

- テスト環境にアップロード
  ```.pyplrc```を作っていない場合はコマンド実行時にusernameとpasswordを要求される
  成功するとURLが返ってくる。
``` cmd or bash
twine upload --repository testpypi dist/*
```
- pipコマンドのテスト
``` cmd or bash
pip install -i https://test.pypi.org/simple/ pth2onnx
```

- 本番環境にアップロード
``` cmd or bash
twine upload --repository pypi dist/*
```

## Lisence

This project is licensed under the MIT License, see the LICENSE.txt file for details
