#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
山东各地市电视台直播聚合（纯接口版）
/          → 纯文本频道列表
/play?id=xx → 302 跳转真实直播流
端口：9001
"""
import json
from flask import Flask, request, redirect, Response
import requests

app = Flask(__name__)

# 频道映射表
CHANNEL_MAP = {
    # 济南
    "jncqxw": [171, 2],   # 长清新闻
    "jncqsh": [171, 20],  # 长清生活
    "jnjrtv": [303, 1],   # 济铁电视台
    "jnjyzh": [85, 1],    # 济阳综合
    "jnjyys": [85, 2],    # 济阳影视
    "jnlcxw": [261, 1],   # 历城新闻综合
    "jnpyzh": [257, 1],   # 平阴综合
    "jnpyxc": [257, 3],   # 平阴乡村振兴
    "jnshzh": [97, 1],    # 商河综合
    "jnshys": [97, 2],    # 商河影视
    "jnzqzh": [195, 1],   # 章丘综合
    "jnzqgg": [195, 2],   # 章丘公共
    
    # 东营
    "dyxwzh": [537, 1],   # 东营新闻综合
    "dygg": [537, 3],     # 东营公共
    "dygg2": [29, 90],    # 东营公共
    "dykj": [537, 7],     # 东营科教
    "dydyqxw": [163, 5],  # 东营区新闻综合
    "dydyqkj": [163, 7],  # 东营区科教影视
    "dygrzh": [237, 1],   # 广饶综合
    "dygrkj": [237, 5],   # 广饶科教文艺
    "dyklxw": [269, 3],   # 垦利新闻综合
    "dyljzh": [153, 1],   # 利津综合
    "dyljwh": [153, 3],   # 利津文化生活
    
    # 青岛
    "qdcyzh": [403, 5],   # 城阳综合
    "qdhdzh": [227, 1],   # 黄岛综合
    "qdhdsh": [227, 3],   # 黄岛生活
    "qdjmzh": [221, 2],   # 即墨综合
    "qdjmsh": [221, 3],   # 即墨生活服务
    "qdjzzh": [305, 1],   # 胶州综合
    "qdjzsh": [305, 3],   # 胶州生活
    "qdlc": [173, 1],     # 李沧TV
    "qdls": [295, 1],     # 崂山TV
    "qdlxzh": [253, 1],   # 莱西综合
    "qdlxsh": [253, 3],   # 莱西生活
    "qdpdxw": [45, 4],    # 平度新闻综合
    "qdpdsh": [45, 5],    # 平度生活服务
    
    # 潍坊
    "wfxwzh": [635, 1],   # 潍坊新闻综合
    "wfsh": [635, 5],     # 潍坊生活
    "wfyswy": [635, 7],   # 潍坊影视综艺
    "wfkjwl": [635, 9],   # 潍坊科教文旅
    "wfgxq": [421, 14],   # 潍坊高新区
    "wfaqzh": [137, 3],   # 安丘综合
    "wfaqms": [137, 4],   # 安丘民生
    "wfbhxw": [199, 1],   # 滨海新闻综合
    "wfclzh": [1, 3],     # 昌乐综合
    "wfcyzh": [47, 1],    # 昌邑综合
    "wfcyjj": [47, 2],    # 昌邑经济生活
    "wffzxw": [285, 1],   # 坊子新闻综合
    "wfgmzh": [71, 24],   # 高密综合
    "wfgmdj": [71, 38],   # 高密党建农科
    "wfhtxw": [133, 1],   # 寒亭新闻
    "wfkwtv": [127, 17],  # 奎文电视台
    "wflqxw": [205, 39],  # 临朐新闻综合
    "wfqzzh": [125, 2],   # 青州综合
    "wfqzwh": [125, 3],   # 青州文化旅游
    "wfwc": [15, 3],      # 潍城TV
    "wfzcxw": [115, 23],  # 诸城新闻综合
    "wfzcsh": [115, 25],  # 诸城生活娱乐
    
    # 烟台
    "ytcd": [175, 1],     # 长岛TV
    "ytfszh": [189, 4],   # 福山综合
    "ytfssh": [189, 5],   # 福山生活(无信号)
    "ythyzh": [255, 1],   # 海阳综合
    "ytlkzh": [57, 1],    # 龙口综合
    "ytlksh": [57, 2],    # 龙口生活
    "ytlszh": [245, 4],   # 莱山综合
    "ytlsys": [245, 6],   # 莱山影视
    "ytlyzh": [241, 4],   # 莱阳综合
    "ytlyms": [241, 7],   # 莱阳民生综艺
    "ytlzzh": [239, 1],   # 莱州综合
    "ytmpzh": [281, 1],   # 牟平综合
    "ytplzh": [109, 1],   # 蓬莱综合
    "ytplzy": [109, 2],   # 蓬莱综艺
    "ytqxzh": [165, 12],  # 栖霞综合
    "ytqxpg": [165, 14],  # 栖霞苹果
    "ytzyzh": [55, 2],    # 招远综合
    "ytzyzy": [55, 4],    # 招远综艺
    
    # 淄博
    "zbbsxw": [17, 8],    # 博山新闻
    "zbbstw": [17, 9],    # 博山图文
    "zbgqzh": [61, 1],    # 高青综合
    "zbgqys": [61, 2],    # 高青影视
    "zbht1": [23, 15],    # 桓台综合
    "zbht2": [23, 16],    # 桓台影视
    "zblzxw": [151, 6],   # 临淄新闻综合
    "zblzsh": [151, 7],   # 临淄生活服务
    "zbyyzh": [203, 6],   # 沂源综合
    "zbyysh": [203, 7],   # 沂源生活
    "zbzcxw": [75, 1],    # 淄川新闻
    "zbzcsh": [75, 2],    # 淄川生活
    "zbzd1": [101, 1],    # 张店综合
    "zbzd2": [101, 6],    # 张店2
    "zbzctv1": [259, 1],  # 周村新闻
    "zbzctv2": [259, 3],  # 周村生活
    
    # 枣庄
    "zzstzh": [243, 1],   # 山亭综合
    "zzszzh": [233, 1],   # 枣庄市中综合
    "zztezxw": [185, 2],  # 台儿庄新闻综合
    "zztzzh": [103, 2],   # 滕州综合
    "zztzms": [103, 3],   # 滕州民生
    "zzxcxw": [37, 8],    # 薛城新闻综合
    "zzyczh": [209, 1],   # 峄城综合
    
    # 滨州
    "bzbctv": [249, 35],  # 滨城TV
    "bzbxzh": [207, 3],   # 博兴综合
    "bzbxsh": [207, 4],   # 博兴生活
    "bzhmzh": [211, 2],   # 惠民综合
    "bzhmys": [211, 3],   # 惠民影视
    "bzwdzh": [169, 1],   # 无棣综合
    "bzwdzy": [169, 21],  # 无棣综艺
    "bzyxxw": [217, 1],   # 阳信新闻综合
    "bzzhzh": [277, 1],   # 沾化综合
    "bzzhzy": [277, 9],   # 沾化综艺
    "bzzpzh": [11, 15],   # 邹平综合
    "bzzpms": [11, 16],   # 邹平民生
    
    # 德州
    "dzxwzh": [179, 1],   # 德州新闻综合
    "dzjjsh": [179, 2],   # 德州经济生活
    "dztw": [179, 9],     # 德州图文
    "dzlczh": [215, 6],   # 陵城综合
    "dzllxw": [267, 1],   # 乐陵新闻综合
    "dzllcs": [267, 5],   # 乐陵城市生活
    "dzly1": [49, 3],     # 临邑1
    "dzly2": [49, 4],     # 临邑2
    "dznjzh": [193, 1],   # 宁津综合
    "dzpyzh": [19, 2],    # 平原综合
    "dzqhzh": [251, 8],   # 齐河综合
    "dzqyzh": [5, 9],     # 庆云综合
    "dzqysh": [5, 7],     # 庆云生活
    "dzwczh": [33, 4],    # 武城综合
    "dzwczy": [33, 6],    # 武城综艺影视
    "dzxjzh": [223, 1],   # 夏津综合
    "dzxjgg": [223, 2],   # 夏津公共
    "dzyczh": [235, 1],   # 禹城综合
    "dzyczy": [235, 3],   # 禹城综艺
    
    # 菏泽
    "hzcwzh": [131, 1],   # 成武综合
    "hzcwzy": [131, 2],   # 成武综艺
    "hzcxzh": [87, 2],    # 曹县综合
    "hzdmxw": [111, 2],   # 东明新闻综合
    "hzdt1": [27, 7],     # 定陶新闻
    "hzdt2": [27, 8],     # 定陶综艺
    "hzjczh": [141, 186], # 鄄城综合
    "hzjyxw": [139, 1],   # 巨野新闻
    "hzmdxw": [219, 6],   # 牡丹区新闻综合
    "hzmdzy": [219, 17],  # 牡丹区综艺
    "hzsxzh": [155, 2],   # 单县综合
    "hzycxw": [135, 3],   # 郓城新闻
    "hzyczy": [135, 2],   # 郓城综艺
    
    # 济宁
    "jijiazh": [273, 1],  # 嘉祥综合
    "jijiash": [273, 3],  # 嘉祥生活
    "jijxzh": [129, 2],   # 金乡综合
    "jijxsh": [129, 4],   # 金乡生活
    "jilszh": [89, 1],    # 梁山综合
    "jiqfxw": [13, 1],    # 曲阜新闻综合
    "jircxw": [73, 8],    # 任城新闻综合
    "jircys": [73, 9],    # 任城影视娱乐
    "jissxw": [117, 5],   # 泗水新闻综合
    "jisswh": [117, 6],   # 泗水文化生活
    "jiws1": [53, 4],     # 微山综合
    "jiws2": [53, 5],     # 微山2套
    "jiwszh": [301, 1],   # 汶上综合
    "jiytxw": [63, 5],    # 鱼台新闻
    "jiytsh": [63, 15],   # 鱼台生活
    "jiyzxw": [231, 1],   # 兖州新闻
    "jiyzsh": [231, 3],   # 兖州生活
    "jizczh": [181, 1],   # 邹城综合
    "jizcwh": [181, 4],   # 邹城文化生活
    
    # 聊城
    "lccpzh": [31, 6],    # 茌平综合
    "lccpsh": [31, 8],    # 茌平生活
    "lcdczh": [265, 1],   # 东昌综合
    "lcdezh": [95, 22],   # 东阿综合
    "lcdezy": [95, 29],   # 东阿综艺
    "lcgtzh": [43, 1],    # 高唐综合
    "lcgtzy": [43, 5],    # 高唐综艺
    "lcgxzh": [79, 1],    # 冠县综合
    "lclqzh": [65, 2],    # 临清综合
    "lclqjj": [65, 5],    # 临清经济信息
    "lcsxzh": [183, 1],   # 莘县综合
    "lcsxsh": [183, 5],   # 莘县生活
    "lcygzh": [81, 1],    # 阳谷综合
    "lcygys": [81, 10],   # 阳谷影视
    
    # 临沂
    "lyfxzh": [41, 119],  # 费县综合
    "lyfxsh": [41, 117],  # 费县生活
    "lyhdys": [191, 1],   # 河东影视
    "lyhdzh": [191, 2],   # 河东综合
    "lyjnzh": [105, 4],   # 莒南综合
    "lyjnys": [105, 5],   # 莒南影视
    "lyllzh": [113, 131], # 兰陵综合
    "lyllgg": [113, 133], # 兰陵公共
    "lylszh": [201, 1],   # 兰山综合
    "lyls1": [167, 3],    # 临沭综合
    "lyls2": [167, 4],    # 临沭生活
    "lylzzh": [147, 1],   # 罗庄综合
    "lylzys": [147, 17],  # 罗庄影视
    "lymy1": [161, 13],   # 蒙阴综合
    "lymy2": [161, 15],   # 蒙阴2套
    "lypyzh": [345, 4],   # 平邑综合
    "lypysh": [345, 14],  # 平邑生活
    "lytc1": [83, 1],     # 郯城综合
    "lytc2": [83, 2],     # 郯城2套
    "lyynzh": [177, 6],   # 沂南综合
    "lyynys": [177, 7],   # 沂南红色影视
    "lyys1": [145, 1],    # 沂水综合
    "lyys2": [145, 2],    # 沂水生活
    
    # 日照
    "rzjx1": [159, 23],   # 莒县综合
    "rzjx2": [159, 27],   # 莒县2套
    "rzls": [289, 1],     # 岚山TV
    "rzwlzh": [299, 10],  # 五莲综合
    "rzwlwh": [299, 12],  # 五莲文化旅游
    
    # 泰安
    "tadpzh": [187, 9],   # 东平综合
    "tadpms": [187, 11],  # 东平民生
    "tady": [293, 1],     # 岱岳TV
    "tafczh": [51, 18],   # 肥城综合
    "tafcsh": [51, 6],    # 肥城生活
    "tany1": [123, 1],    # 宁阳综合
    "tany2": [123, 7],    # 宁阳2套
    "tats": [263, 1],     # 泰山TV
    "taxtzh": [59, 2],    # 新泰综合
    "taxtxc": [59, 3],    # 新泰乡村
    
    # 威海
    "whxwzh": [157, 1],   # 威海新闻综合
    "whdssh": [157, 3],   # 威海都市生活
    "whhy": [157, 12],    # 威海海洋
    "whhczh": [213, 5],   # 威海环翠综合
    "whrczh": [77, 10],   # 荣成综合
    "whrcsh": [77, 11],   # 荣成生活
    "whrszh": [143, 8],   # 乳山综合
    "whrssh": [143, 9],   # 乳山生活
    "whwd1": [91, 7],     # 文登TV1
    "whwd2": [91, 8],     # 文登TV2
}

# 完整的中文频道名称映射（与上面相同）
CN_NAME = {
    "jncqxw": "长清新闻", "jncqsh": "长清生活", "jnjrtv": "济铁电视台", 
    "jnjyzh": "济阳综合", "jnjyys": "济阳影视", "jnlcxw": "历城新闻综合",
    "jnpyzh": "平阴综合", "jnpyxc": "平阴乡村振兴", "jnshzh": "商河综合",
    "jnshys": "商河影视", "jnzqzh": "章丘综合", "jnzqgg": "章丘公共",
    "dyxwzh": "东营新闻综合", "dygg": "东营公共", "dygg2": "东营公共2",
    "dykj": "东营科教", "dydyqxw": "东营区新闻综合", "dydyqkj": "东营区科教影视",
    "dygrzh": "广饶综合", "dygrkj": "广饶科教文艺", "dyklxw": "垦利新闻综合",
    "dyljzh": "利津综合", "dyljwh": "利津文化生活", "qdcyzh": "城阳综合",
    "qdhdzh": "黄岛综合", "qdhdsh": "黄岛生活", "qdjmzh": "即墨综合",
    "qdjmsh": "即墨生活服务", "qdjzzh": "胶州综合", "qdjzsh": "胶州生活",
    "qdlc": "李沧TV", "qdls": "崂山TV", "qdlxzh": "莱西综合",
    "qdlxsh": "莱西生活", "qdpdxw": "平度新闻综合", "qdpdsh": "平度生活服务",
    "wfxwzh": "潍坊新闻综合", "wfsh": "潍坊生活", "wfyswy": "潍坊影视综艺",
    "wfkjwl": "潍坊科教文旅", "wfgxq": "潍坊高新区", "wfaqzh": "安丘综合",
    "wfaqms": "安丘民生", "wfbhxw": "滨海新闻综合", "wfclzh": "昌乐综合",
    "wfcyzh": "昌邑综合", "wfcyjj": "昌邑经济生活", "wffzxw": "坊子新闻综合",
    "wfgmzh": "高密综合", "wfgmdj": "高密党建农科", "wfhtxw": "寒亭新闻",
    "wfkwtv": "奎文电视台", "wflqxw": "临朐新闻综合", "wfqzzh": "青州综合",
    "wfqzwh": "青州文化旅游", "wfwc": "潍城TV", "wfzcxw": "诸城新闻综合",
    "wfzcsh": "诸城生活娱乐", "ytcd": "长岛TV", "ytfszh": "福山综合",
    "ytfssh": "福山生活", "ythyzh": "海阳综合", "ytlkzh": "龙口综合",
    "ytlksh": "龙口生活", "ytlszh": "莱山综合", "ytlsys": "莱山影视",
    "ytlyzh": "莱阳综合", "ytlyms": "莱阳民生综艺", "ytlzzh": "莱州综合",
    "ytmpzh": "牟平综合", "ytplzh": "蓬莱综合", "ytplzy": "蓬莱综艺",
    "ytqxzh": "栖霞综合", "ytqxpg": "栖霞苹果", "ytzyzh": "招远综合",
    "ytzyzy": "招远综艺", "zbbsxw": "博山新闻", "zbbstw": "博山图文",
    "zbgqzh": "高青综合", "zbgqys": "高青影视", "zbht1": "桓台综合",
    "zbht2": "桓台影视", "zblzxw": "临淄新闻综合", "zblzsh": "临淄生活服务",
    "zbyyzh": "沂源综合", "zbyysh": "沂源生活", "zbzcxw": "淄川新闻",
    "zbzcsh": "淄川生活", "zbzd1": "张店综合", "zbzd2": "张店2",
    "zbzctv1": "周村新闻", "zbzctv2": "周村生活", "zzstzh": "山亭综合",
    "zzszzh": "枣庄市中综合", "zztezxw": "台儿庄新闻综合", "zztzzh": "滕州综合",
    "zztzms": "滕州民生", "zzxcxw": "薛城新闻综合", "zzyczh": "峄城综合",
    "bzbctv": "滨城TV", "bzbxzh": "博兴综合", "bzbxsh": "博兴生活",
    "bzhmzh": "惠民综合", "bzhmys": "惠民影视", "bzwdzh": "无棣综合",
    "bzwdzy": "无棣综艺", "bzyxxw": "阳信新闻综合", "bzzhzh": "沾化综合",
    "bzzhzy": "沾化综艺", "bzzpzh": "邹平综合", "bzzpms": "邹平民生",
    "dzxwzh": "德州新闻综合", "dzjjsh": "德州经济生活", "dztw": "德州图文",
    "dzlczh": "陵城综合", "dzllxw": "乐陵新闻综合", "dzllcs": "乐陵城市生活",
    "dzly1": "临邑1", "dzly2": "临邑2", "dznjzh": "宁津综合",
    "dzpyzh": "平原综合", "dzqhzh": "齐河综合", "dzqyzh": "庆云综合",
    "dzqysh": "庆云生活", "dzwczh": "武城综合", "dzwczy": "武城综艺影视",
    "dzxjzh": "夏津综合", "dzxjgg": "夏津公共", "dzyczh": "禹城综合",
    "dzyczy": "禹城综艺", "hzcwzh": "成武综合", "hzcwzy": "成武综艺",
    "hzcxzh": "曹县综合", "hzdmxw": "东明新闻综合", "hzdt1": "定陶新闻",
    "hzdt2": "定陶综艺", "hzjczh": "鄄城综合", "hzjyxw": "巨野新闻",
    "hzmdxw": "牡丹区新闻综合", "hzmdzy": "牡丹区综艺", "hzsxzh": "单县综合",
    "hzycxw": "郓城新闻", "hzyczy": "郓城综艺", "jijiazh": "嘉祥综合",
    "jijiash": "嘉祥生活", "jijxzh": "金乡综合", "jijxsh": "金乡生活",
    "jilszh": "梁山综合", "jiqfxw": "曲阜新闻综合", "jircxw": "任城新闻综合",
    "jircys": "任城影视娱乐", "jissxw": "泗水新闻综合", "jisswh": "泗水文化生活",
    "jiws1": "微山综合", "jiws2": "微山2套", "jiwszh": "汶上综合",
    "jiytxw": "鱼台新闻", "jiytsh": "鱼台生活", "jiyzxw": "兖州新闻",
    "jiyzsh": "兖州生活", "jizczh": "邹城综合", "jizcwh": "邹城文化生活",
    "lccpzh": "茌平综合", "lccpsh": "茌平生活", "lcdczh": "东昌综合",
    "lcdezh": "东阿综合", "lcdezy": "东阿综艺", "lcgtzh": "高唐综合",
    "lcgtzy": "高唐综艺", "lcgxzh": "冠县综合", "lclqzh": "临清综合",
    "lclqjj": "临清经济信息", "lcsxzh": "莘县综合", "lcsxsh": "莘县生活",
    "lcygzh": "阳谷综合", "lcygys": "阳谷影视", "lyfxzh": "费县综合",
    "lyfxsh": "费县生活", "lyhdys": "河东影视", "lyhdzh": "河东综合",
    "lyjnzh": "莒南综合", "lyjnys": "莒南影视", "lyllzh": "兰陵综合",
    "lyllgg": "兰陵公共", "lylszh": "兰山综合", "lyls1": "临沭综合",
    "lyls2": "临沭生活", "lylzzh": "罗庄综合", "lylzys": "罗庄影视",
    "lymy1": "蒙阴综合", "lymy2": "蒙阴2套", "lypyzh": "平邑综合",
    "lypysh": "平邑生活", "lytc1": "郯城综合", "lytc2": "郯城2套",
    "lyynzh": "沂南综合", "lyynys": "沂南红色影视", "lyys1": "沂水综合",
    "lyys2": "沂水生活", "rzjx1": "莒县综合", "rzjx2": "莒县2套",
    "rzls": "岚山TV", "rzwlzh": "五莲综合", "rzwlwh": "五莲文化旅游",
    "tadpzh": "东平综合", "tadpms": "东平民生", "tady": "岱岳TV",
    "tafczh": "肥城综合", "tafcsh": "肥城生活", "tany1": "宁阳综合",
    "tany2": "宁阳2套", "tats": "泰山TV", "taxtzh": "新泰综合",
    "taxtxc": "新泰乡村", "whxwzh": "威海新闻综合", "whdssh": "威海都市生活",
    "whhy": "威海海洋", "whhczh": "威海环翠综合", "whrczh": "荣成综合",
    "whrcsh": "荣成生活", "whrszh": "乳山综合", "whrssh": "乳山生活",
    "whwd1": "文登TV1", "whwd2": "文登TV2"
}

# 城市分组映射
CITY_GROUPS = {
    "济南": ["jncqxw", "jncqsh", "jnjrtv", "jnjyzh", "jnjyys", "jnlcxw", 
            "jnpyzh", "jnpyxc", "jnshzh", "jnshys", "jnzqzh", "jnzqgg"],
    "东营": ["dyxwzh", "dygg", "dygg2", "dykj", "dydyqxw", "dydyqkj", 
            "dygrzh", "dygrkj", "dyklxw", "dyljzh", "dyljwh"],
    "青岛": ["qdcyzh", "qdhdzh", "qdhdsh", "qdjmzh", "qdjmsh", "qdjzzh", 
            "qdjzsh", "qdlc", "qdls", "qdlxzh", "qdlxsh", "qdpdxw", "qdpdsh"],
    "潍坊": ["wfxwzh", "wfsh", "wfyswy", "wfkjwl", "wfgxq", "wfaqzh", "wfaqms",
            "wfbhxw", "wfclzh", "wfcyzh", "wfcyjj", "wffzxw", "wfgmzh", "wfgmdj",
            "wfhtxw", "wfkwtv", "wflqxw", "wfqzzh", "wfqzwh", "wfwc", "wfzcxw", "wfzcsh"],
    "烟台": ["ytcd", "ytfszh", "ytfssh", "ythyzh", "ytlkzh", "ytlksh", "ytlszh",
            "ytlsys", "ytlyzh", "ytlyms", "ytlzzh", "ytmpzh", "ytplzh", "ytplzy",
            "ytqxzh", "ytqxpg", "ytzyzh", "ytzyzy"],
    "淄博": ["zbbsxw", "zbbstw", "zbgqzh", "zbgqys", "zbht1", "zbht2", "zblzxw",
            "zblzsh", "zbyyzh", "zbyysh", "zbzcxw", "zbzcsh", "zbzd1", "zbzd2",
            "zbzctv1", "zbzctv2"],
    "枣庄": ["zzstzh", "zzszzh", "zztezxw", "zztzzh", "zztzms", "zzxcxw", "zzyczh"],
    "滨州": ["bzbctv", "bzbxzh", "bzbxsh", "bzhmzh", "bzhmys", "bzwdzh", "bzwdzy",
            "bzyxxw", "bzzhzh", "bzzhzy", "bzzpzh", "bzzpms"],
    "德州": ["dzxwzh", "dzjjsh", "dztw", "dzlczh", "dzllxw", "dzllcs", "dzly1",
            "dzly2", "dznjzh", "dzpyzh", "dzqhzh", "dzqyzh", "dzqysh", "dzwczh",
            "dzwczy", "dzxjzh", "dzxjgg", "dzyczh", "dzyczy"],
    "菏泽": ["hzcwzh", "hzcwzy", "hzcxzh", "hzdmxw", "hzdt1", "hzdt2", "hzjczh",
            "hzjyxw", "hzmdxw", "hzmdzy", "hzsxzh", "hzycxw", "hzyczy"],
    "济宁": ["jijiazh", "jijiash", "jijxzh", "jijxsh", "jilszh", "jiqfxw", "jircxw",
            "jircys", "jissxw", "jisswh", "jiws1", "jiws2", "jiwszh", "jiytxw",
            "jiytsh", "jiyzxw", "jiyzsh", "jizczh", "jizcwh"],
    "聊城": ["lccpzh", "lccpsh", "lcdczh", "lcdezh", "lcdezy", "lcgtzh", "lcgtzy",
            "lcgxzh", "lclqzh", "lclqjj", "lcsxzh", "lcsxsh", "lcygzh", "lcygys"],
    "临沂": ["lyfxzh", "lyfxsh", "lyhdys", "lyhdzh", "lyjnzh", "lyjnys", "lyllzh",
            "lyllgg", "lylszh", "lyls1", "lyls2", "lylzzh", "lylzys", "lymy1",
            "lymy2", "lypyzh", "lypysh", "lytc1", "lytc2", "lyynzh", "lyynys",
            "lyys1", "lyys2"],
    "日照": ["rzjx1", "rzjx2", "rzls", "rzwlzh", "rzwlwh"],
    "泰安": ["tadpzh", "tadpms", "tady", "tafczh", "tafcsh", "tany1", "tany2",
            "tats", "taxtzh", "taxtxc"],
    "威海": ["whxwzh", "whdssh", "whhy", "whhczh", "whrczh", "whrcsh", "whrszh",
            "whrssh", "whwd1", "whwd2"]
}

# 请求头配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://app.litenews.cn/',
    'Origin': 'https://app.litenews.cn',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Connection': 'keep-alive',
}

API_BASE_URL = 'https://app.litenews.cn/v1/app/play/tv/live?_orgid_='

def get_stream_url(channel_key: str) -> str:
    """获取指定频道的直播流地址"""
    if channel_key not in CHANNEL_MAP:
        raise ValueError(f"未知的频道标识: {channel_key}")
    
    orgid, target_id = CHANNEL_MAP[channel_key]
    api_url = f"{API_BASE_URL}{orgid}"
    
    try:
        # 添加延迟避免频繁请求
        import time
        time.sleep(0.5)
        
        response = requests.get(api_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 查找对应的流
        if "data" in data:
            for item in data["data"]:
                item_id = item.get("id")
                if item_id == target_id:
                    stream = item.get("stream")
                    if stream:
                        return stream
        
        raise ValueError(f"未找到对应的直播流，orgid: {orgid}, target_id: {target_id}")
        
    except requests.RequestException as e:
        raise Exception(f"API请求失败: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("API返回数据格式错误")

@app.route('/')
def index():
    """首页：显示TiviMate格式的频道列表"""
    host = request.host
    lines = []
    
    # 按城市分组显示
    for city, channel_keys in CITY_GROUPS.items():
        # 添加分组标题
        lines.append(f"{city}频道,#genre#")
        
        # 添加该城市的所有频道
        for channel_key in channel_keys:
            if channel_key in CN_NAME:
                name = CN_NAME[channel_key]
                lines.append(f"{name},http://{host}/play?id={channel_key}")
        
        # 分组之间添加空行
        lines.append("")
    
    return Response('\n'.join(lines), mimetype='text/plain; charset=utf-8')

@app.route('/play')
def play():
    """播放接口：302重定向到真实直播流地址"""
    channel_key = request.args.get('id', 'jncqxw')  # 默认长清新闻
    
    try:
        stream_url = get_stream_url(channel_key)
        # 设置CORS头和缓存控制
        response = redirect(stream_url, code=302)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        return f'错误: {str(e)}', 500

@app.route('/test/<channel_key>')
def test_channel(channel_key):
    """测试接口：返回API原始数据"""
    if channel_key not in CHANNEL_MAP:
        return f"未知频道: {channel_key}", 404
    
    orgid, target_id = CHANNEL_MAP[channel_key]
    api_url = f"{API_BASE_URL}{orgid}"
    
    try:
        response = requests.get(api_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        result = {
            "channel": channel_key,
            "channel_name": CN_NAME.get(channel_key, channel_key),
            "orgid": orgid,
            "target_id": target_id,
            "api_url": api_url,
            "status_code": response.status_code,
            "data_structure": data
        }
        
        return result, 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/simple')
def simple_list():
    """简单列表：无分组的频道列表"""
    host = request.host
    lines = []
    
    for key in CHANNEL_MAP.keys():
        # 使用中文名，如果没有则使用key
        name = CN_NAME.get(key, key)
        lines.append(f'{name},http://{host}/play?id={key}')
    
    return Response('\n'.join(lines), mimetype='text/plain; charset=utf-8')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9002, debug=False)