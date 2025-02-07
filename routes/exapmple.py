import re

travel_plan_text = """
会話の要約

Haya Hori は、大阪観光の計画を希望しています。
旅行プラン

1日目

大阪に到着
ホテルにチェックイン
道頓堀で夕食
2日目

大阪城の見学
通天閣の訪問
心斎橋でショッピング
3日目

ユニバーサル・スタジオ・ジャパンの訪問
大阪駅周辺で夕食
4日目

大阪から出発
移動手段

大阪市内は徒歩や公共交通機関で移動できます。
ユニバーサル・スタジオ・ジャパンへは、ユニバーサルシティ駅を利用します。
予算

予算は記載されていませんが、宿泊費、交通費、食費、アクティビティ費を考慮する必要があります。
場所

travel:[大阪]
"""

import re

def extract_destinations(travel_plan_text):
    # 行ごとに分割
    lines = travel_plan_text.split('\n')
    
    # 行き先を格納するリスト
    destinations = []
    
    # 行き先を抽出する正規表現パターン
    pattern = re.compile(r'^\d+日目|^移動手段|^予算|^場所|^会話の要約|^旅行プラン')
    
    for line in lines:
        # 行が日付や移動手段、予算、場所のセクションで始まる場合はスキップ
        if pattern.match(line):
            continue
        
        # 行き先を抽出
        match = re.search(r'([^\s]+)(で|に|の|へ|から)', line)
        if match:
            destinations.append(match.group(1))
    
    
    return destinations

print(extract_destinations(travel_plan_text))