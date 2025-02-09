# 画面遷移

## Talk room

### 機能

- チャット機能
  - 画面上部に表示
- 候補地の提案機能
  - リスト化して画面下部表示
  - グループメンバーによる投票機能を兼ねる
  - (コメント)
- Map表示機能
  - Map表示ボタンがあり，画面右半分に表示/非表示を選択可
  - Map画面は，候補地に関する情報をリスト化された提案機能から取得するのみ．
    - 名称
    - 投票数
    - (コメント)
- ルート作成AIによるルート提案機能
  - ルート作成ボタン
  - 必要情報の入力
    - 開始日
    - 終了日
    - 出発場所
    - 予算
    - (備考)
- 招待機能
- (AIとの会話による候補地提案機能)

# アーキテクチャ

## 候補地(1つ) CandidateSite

id(PK): int
user_id(FK): int
place_name: str
place_id(SK): str
description: str (optional)
like: int
comment: List(tuple(int, str)) (optional)
room_id(FK): int
enable: bool

## 最終スケジュール AcceptedRoute

id(PK): int
place_id(FK): str
destination_id(FK): int
order: int
day: int

## トークルーム Room

room_id(PK): int
user_id(FK): int
title: str
(Icon: str)

## 処理フロー

User
候補地の提案をリスト <- AIによる提案があってもよい
-> Map上に可視化
-> いいね等の投票機能
-> ルート作成を押すと，AIが当たり障りのないプランを考えてくれる．

# 内部仕様

## AIについて

### 場所提案AI

Chatから呼び出す．Userの要望に沿った場所の提案をしてくれるのみ．

### ルート作成AI

- 入力
  - 開始日
  - 終了日
  - 出発場所
  - 予算
  - (備考)
  - 候補地リスト(以下の要素を持つdict)
    - place_name(候補地名): str
    - likes(いいね数): int
    - comments(コメント): List(str)
  - 除外地リスト(以下の要素を持つdict)
    - place_name(候補地名): str
    - likes(いいね数): -1
    - comments(コメント): List(str)
- 出力例
  - スケジュール表
    - 日付
    - 場所
    - 予算
    - (備考)
