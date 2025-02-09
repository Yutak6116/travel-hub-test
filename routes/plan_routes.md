# Plan Routesのルーティング仕様

この文書は [routes/plan_routes.py](routes/plan_routes.py) に定義されたルーティング仕様をまとめたものです。

---
## 目次

- [Plan Routesのルーティング仕様](#plan-routesのルーティング仕様)
  - [目次](#目次)
  - [エンドポイント一覧](#エンドポイント一覧)
  - [1. 候補地を追加する](#1-候補地を追加する)
  - [2. 候補地を削除する](#2-候補地を削除する)
  - [3. すべての候補地を削除する](#3-すべての候補地を削除する)
  - [4. 削除された候補地を元に戻す](#4-削除された候補地を元に戻す)
  - [5. 候補地に「いいね」を追加する](#5-候補地にいいねを追加する)
  - [6. 候補地に対する「いいね」を取り消す](#6-候補地に対するいいねを取り消す)
  - [7. 候補地にコメントを追加する](#7-候補地にコメントを追加する)
  - [8. 候補地のコメントを削除する](#8-候補地のコメントを削除する)

## エンドポイント一覧

| ルート | メソッド | パラメータ | 処理の概要 |
| --- | --- | --- | --- |
| `/candidate_site/<int:room_id>` | POST | `room_id` (整数) | [候補地を追加する](#1-候補地を追加する) |
| `/candidate_site/<int:room_id>/<int:site_id>` | DELETE | `room_id` (整数), `site_id` (整数) | [候補地を削除する](#2-候補地を削除する) |
| `/candidate_site/<int:room_id>` | DELETE | `room_id` (整数) | [すべての候補地を削除する](#3-すべての候補地を削除する) |
| `/candidate_site/<int:room_id>/<int:site_id>/restore` | POST | `room_id` (整数), `site_id` (整数) | [削除された候補地を元に戻す](#4-削除された候補地を元に戻す) |
| `/candidate_site/<int:room_id>/<int:site_id>/like` | POST | `room_id` (整数), `site_id` (整数) | [候補地に「いいね」を追加する](#5-候補地にいいねを追加する) |
| `/candidate_site/<int:room_id>/<int:site_id>/dislike` | POST | `room_id` (整数), `site_id` (整数) | [候補地に対する「いいね」を取り消す](#6-候補地に対するいいねを取り消す) |
| `/candidate_site/<int:room_id>/<int:site_id>/comment` | POST | `room_id` (整数), `site_id` (整数) | [候補地にコメントを追加する](#7-候補地にコメントを追加する) |
| `/candidate_site/<int:room_id>/<int:site_id>/comment/<int:comment_id>` | DELETE | `room_id` (整数), `site_id` (整数), `comment_id` (整数) | [候補地のコメントを削除する](#8-候補地のコメントを削除する) |


## 1. 候補地を追加する

- **ルーティング:** `/candidate_site/<int:room_id>`
- **メソッド:** POST
- **パラメータ:**
  - URL パラメータ: `room_id` (整数)
  - フォームデータ:
    - `place_name`: 追加する場所の名称
    - `description`: 候補地の説明
- **処理:**
  1. リクエストから `place_name` と `description` を取得
  2. `get_place_coordinates` を呼び出して `place_id` を取得
  3. 取得した情報をもとに `CandidateSite` の新規インスタンスを作成
  4. データベースに新しい候補地として追加し、コミット
  5. `/chat/<room_id>` にリダイレクト
- **注意事項:** ユーザーが手動で候補地を追加する際に使用されるエンドポイントです。

---

## 2. 候補地を削除する

- **ルーティング:** `/candidate_site/<int:room_id>/<int:site_id>`
- **メソッド:** DELETE
- **パラメータ:**
  - URL パラメータ:
    - `room_id` (整数)
    - `site_id` (整数)
- **処理:**
  1. 指定された `site_id` の候補地を取得
  2. 候補地が存在する場合、`delete_by_user()` を呼び出して削除（ソフトデリート）
  3. 変更をデータベースにコミット
  4. `/chat/<room_id>` にリダイレクト
- **注意事項:** 候補地が見つからない場合は、何の操作も行わずにリダイレクトされる。

---

## 3. すべての候補地を削除する

- **ルーティング:** `/candidate_site/<int:room_id>`
- **メソッド:** DELETE
- **パラメータ:**
  - URL パラメータ: `room_id` (整数)
- **処理:**
  1. 指定した `room_id` に属する全候補地を取得
  2. 各候補地に対して `delete_by_user()` を呼び出し削除処理を実施
  3. 変更をコミットし、 `/chat/<room_id>` にリダイレクト
- **注意事項:** 対象となる候補地が存在しない場合は、単にリダイレクトが実行される。

---

## 4. 削除された候補地を元に戻す

- **ルーティング:** `/candidate_site/<int:room_id>/<int:site_id>/restore`
- **メソッド:** POST
- **パラメータ:**
  - URL パラメータ:
    - `room_id` (整数)
    - `site_id` (整数)
- **処理:**
  1. 指定された `site_id` の候補地を取得
  2. 存在する場合、`restore_by_user()` を呼び出して削除状態を解除
  3. データベースにコミットし、 `/chat/<room_id>` にリダイレクト
- **注意事項:** 対象の候補地が存在する場合のみ復元が可能

---

## 5. 候補地に「いいね」を追加する

- **ルーティング:** `/candidate_site/<int:room_id>/<int:site_id>/like`
- **メソッド:** POST
- **パラメータ:**
  - URL パラメータ:
    - `room_id` (整数)
    - `site_id` (整数)
- **処理:**
  1. 指定された `site_id` の候補地を取得
  2. 存在する場合、`add_like()` メソッドを呼び出して「いいね」カウントを増加
  3. 変更をコミットし、 `/chat/<room_id>` にリダイレクト
- **注意事項:** 候補地が存在しない場合は、リダイレクトのみ実施される。

---

## 6. 候補地に対する「いいね」を取り消す

- **ルーティング:** `/candidate_site/<int:room_id>/<int:site_id>/dislike`
- **メソッド:** POST
- **パラメータ:**
  - URL パラメータ:
    - `room_id` (整数)
    - `site_id` (整数)
- **処理:**
  1. 指定された `site_id` の候補地を取得
  2. 存在する場合、`delete_like()` メソッドを呼び出して「いいね」カウントを減少
  3. 変更をコミットし、 `/chat/<room_id>` にリダイレクト
- **注意事項:** 指定候補地が存在しない場合は、リダイレクトのみ実行される。

---

## 7. 候補地にコメントを追加する

- **ルーティング:** `/candidate_site/<int:room_id>/<int:site_id>/comment`
- **メソッド:** POST
- **パラメータ:**
  - URL パラメータ:
    - `room_id` (整数)
    - `site_id` (整数)
  - フォームデータ:
    - `user_id`: コメントを投稿するユーザーのID
    - `comment`: コメント内容
- **処理:**
  1. 指定された `site_id` の候補地を取得
  2. フォームデータから `user_id` と `comment` を取得
  3. 新規の `Comment` インスタンスを生成
  4. 候補地の `add_comment(new_comment)` を呼び出しコメントを追加
  5. コメントをデータベースに追加し、コミット
  6. `/chat/<room_id>` にリダイレクト
- **注意事項:** 候補地が存在しない場合は、リダイレクトが実行される。

---

## 8. 候補地のコメントを削除する

- **ルーティング:** `/candidate_site/<int:room_id>/<int:site_id>/comment/<int:comment_id>`
- **メソッド:** DELETE
- **パラメータ:**
  - URL パラメータ:
    - `room_id` (整数)
    - `site_id` (整数)
    - `comment_id` (整数)
- **処理:**
  1. 指定された `site_id` の候補地を取得
  2. 指定された `comment_id` のコメントを取得
  3. 候補地の `delete_comment(comment)` を呼び出しコメントを削除
  4. データベースからコメントを削除し、コミット
  5. `/chat/<room_id>` にリダイレクト
- **注意事項:** 対象の候補地およびコメントが存在する場合のみ削除が実行される。

---

*本ドキュメントは、現在の [routes/plan_routes.py](routes/plan_routes.py) の実装に基づいており、関連するモデルは [models.py](models.py) に定義されています。*
