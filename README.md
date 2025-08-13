# Travel Hub

このレポジトリは，「AI Agent Hackathon with Google Cloud」に提出するプロダクト，Travel Hubのソースコードを管理するためのものです．

## 目次

- [Travel Hub](#travel-hub)
  - [目次](#目次)
  - [使用技術](#使用技術)
  - [環境構築](#環境構築)
    - [1. リポジトリのクローン](#1-リポジトリのクローン)
    - [2. 仮想環境の構築](#2-仮想環境の構築)
    - [3. 必要なライブラリのインストール](#3-必要なライブラリのインストール)
    - [4. ローカルサーバの起動](#4-ローカルサーバの起動)

## 使用技術

- Python
- Flask
- SQLAlchemy
- Google Cloud Platform
- Google Maps API

## 環境構築

### 1. リポジトリのクローン

```bash
git clone https://github.com/tatesoto/ZennHackathon1.git
```

### 2. 仮想環境の構築

Windowsの場合．
```bash
python -m venv calc_env
calc_env\Scripts\activate
```

Linuxの場合．
```bash
python3 -m venv calc_env
source calc_env/bin/activate
```

### 3. 必要なライブラリのインストール

```bash
pip install -r requirements.txt
```

### 4. ローカルサーバの起動

```bash
python app.py
```

その後，[ここ](http://localhost:5000/)にアクセスしてください．
