import streamlit as st
import random
import time
import json
import os
from datetime import datetime
import urllib.parse

# 页面配置 - 针对手机优化
st.set_page_config(
    page_title="修仙打怪游戏",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 注入CSS优化手机体验（适配OPPO Reno8 Pro 5G和vivo Y73s的2400×1080竖屏）
st.markdown("""
<style>
    /* 基础样式重置 */
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }

    /* 强制竖屏布局适配 */
    .main .block-container {
        max-width: 95% !important;
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        margin: 0 auto !important;
    }

    /* 按钮样式优化 - 适合触摸操作 */
    .stButton>button {
        font-size: 18px !important;
        padding: 12px 0 !important;
        margin: 6px 0 !important;
        border-radius: 8px !important;
        border: none !important;
        background-color: #4CAF50 !important;
        color: white !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        background-color: #45a049 !important;
        transform: scale(1.02) !important;
    }
    .stButton>button:active {
        transform: scale(0.98) !important;
    }
    .stButton>button:disabled {
        background-color: #cccccc !important;
        color: #666666 !important;
        transform: none !important;
    }

    /* 文本样式优化 */
    .stText, .stMarkdown, .stHeading {
        font-size: 16px !important;
        line-height: 1.6 !important;
    }
    h1 {
        font-size: 26px !important;
        text-align: center !important;
        margin-bottom: 1rem !important;
    }
    h2 {
        font-size: 22px !important;
        margin: 1rem 0 !important;
    }

    /* 战斗日志区域样式 */
    .stTextArea textarea {
        height: 220px !important;
        font-size: 16px !important;
        border-radius: 8px !important;
    }

    /* 状态卡片样式 */
    .status-card {
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 12px;
        margin: 10px 0;
    }

    /* 适配不同屏幕尺寸 */
    @media (max-width: 412px) {
        .stButton>button {
            font-size: 16px !important;
            padding: 10px 0 !important;
        }
        h1 {
            font-size: 22px !important;
        }
        h2 {
            font-size: 18px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# 游戏核心常量定义
REALMS = [
    # 人垣三境
    {"name": "淬体境", "level": 1, "hp_multiplier": 1.0, "attack_multiplier": 1.0,
     "defense_multiplier": 1.0, "exp_multiplier": 1.0},
    {"name": "炼气境", "level": 2, "hp_multiplier": 1.8, "attack_multiplier": 1.6,
     "defense_multiplier": 1.5, "exp_multiplier": 1.5},
    {"name": "筑基境", "level": 3, "hp_multiplier": 3.0, "attack_multiplier": 2.5,
     "defense_multiplier": 2.2, "exp_multiplier": 2.5},
    # 地垣三境
    {"name": "金丹境", "level": 4, "hp_multiplier": 5.0, "attack_multiplier": 4.0,
     "defense_multiplier": 3.5, "exp_multiplier": 4.0},
    {"name": "元婴境", "level": 5, "hp_multiplier": 7.5, "attack_multiplier": 6.0,
     "defense_multiplier": 5.0, "exp_multiplier": 6.0},
    {"name": "化神境", "level": 6, "hp_multiplier": 10.0, "attack_multiplier": 8.0,
     "defense_multiplier": 7.0, "exp_multiplier": 8.0},
    # 天垣三境
    {"name": "渡劫境", "level": 7, "hp_multiplier": 15.0, "attack_multiplier": 12.0,
     "defense_multiplier": 10.0, "exp_multiplier": 12.0},
    {"name": "大乘境", "level": 8, "hp_multiplier": 20.0, "attack_multiplier": 16.0,
     "defense_multiplier": 14.0, "exp_multiplier": 16.0},
    {"name": "合道境", "level": 9, "hp_multiplier": 30.0, "attack_multiplier": 25.0,
     "defense_multiplier": 20.0, "exp_multiplier": 25.0}
]

REALM_LEVELS = 10  # 每个大境界包含的小等级数

EQUIPMENT_TYPES = ["武器", "头盔", "铠甲", "护腿", "手套", "鞋子"]

# 武器技能定义
WEAPON_SKILLS = {
    "剑": {"name": "破空斩", "effect": "对敌人造成150%伤害，有30%概率触发暴击"},
    "刀": {"name": "旋风斩", "effect": "对敌人造成130%伤害，自身恢复5%最大生命值"},
    "斧": {"name": "巨力一击", "effect": "对敌人造成180%伤害，但自身受到10%伤害反噬"},
    "杖": {"name": "元素冲击", "effect": "对敌人造成140%伤害，附加元素效果"},
    "弓": {"name": "精准射击", "effect": "对敌人造成120%伤害，必定命中且忽略20%防御"}
}

MONSTERS = {
    "基础种": {
        "仙术使": ["铁铠熊霸", "赤鳞妖蛇", "腐毒史莱姆"],
        "机械种": ["脉冲机械卫", "辐射巨蟑", "纳米虫潮"],
        "元素使": ["炎之精灵", "冰泡沫", "雷微粒"],
        "阵营种": ["暗影夜狼", "圣光侍僧", "沼泽哥布林"],
        "混合种": ["剧毒蜈蚣机甲", "熔岩傀儡", "虚空触须"]
    },
    "精英种": {
        "仙术使": ["霜牙冰狼", "血瞳妖狐", "岩甲龙龟"],
        "机械种": ["相位机甲", "核能巨蝎", "量子幽灵"],
        "元素使": ["水之使者", "风暴巨鹰", "熔岩蠕虫"],
        "阵营种": ["堕落牧师", "混沌巫师学徒", "圣光十字军"],
        "混合种": ["冰火双头龙", "机械吞噬者", "虚空撕裂者"]
    },
    "首领种": {
        "仙术使": ["赤焰妖王", "碧波龙王", "噬魂老祖"],
        "机械种": ["机械帝王", "AI仲裁者", "核能暴君"],
        "元素使": ["三元素融合体", "雷霆蜥蜴", "剧毒藤王"],
        "阵营种": ["暗影行者头目", "秩序神使", "混沌副官"],
        "混合种": ["虚空触手怪", "金属化暴龙", "元素暴走体"]
    },
    "变异种": {
        "仙术使": ["双生妖狐", "腐骨傀儡", "雷劫残魂"],
        "机械种": ["纳米虫后", "量子幽灵王", "机械吞噬者·改"],
        "元素使": ["混沌元素体", "风暴巨鹰·狂", "熔岩蠕虫·暴君"],
        "阵营种": ["圣光异化体", "混沌孢子兽", "暗影寄生体"],
        "混合种": ["熵增机甲", "虚空撕裂者·终", "元素暴走体·超"]
    },
    "BOSS级种": {
        "仙术使": ["上古剑灵", "天道意志", "五行祖巫"],
        "机械种": ["AI主脑", "机械皇帝", "量子之神"],
        "元素使": ["元素之神", "混沌元素", "虚空领主"],
        "阵营种": ["秩序之神", "混沌之神", "熵增之主"],
        "混合种": ["混沌终焉体", "天道机械师", "元素共生体"]
    }
}

# 怪物类型对应的伤害效果
MONSTER_DAMAGE_EFFECTS = {
    "仙术使": ["中毒", "眩晕"],
    "机械种": [],
    "元素使": ["火焰", "冰霜", "雷电"],
    "阵营种": ["眩晕"],
    "混合种": ["火焰", "冰霜", "雷电", "中毒", "眩晕"]
}

SHOP_ITEMS = [
    {"name": "生命上限药水", "effect": "max_hp", "value": 0.1, "price": 800,
     "description": "永久增加10%血量上限"},
    {"name": "快速回血药水", "effect": "heal", "value": 0.3, "price": 200,
     "description": "立即恢复30%当前血量"},
    {"name": "全愈药水", "effect": "full_heal", "value": 1.0, "price": 500,
     "description": "完全恢复自身所有血量"},
    {"name": "初级防御药水", "effect": "defense_boost", "value": 0.3, "duration": 180,
     "price": 350, "description": "180秒内增加30%防御"},
    {"name": "高级防御药水", "effect": "defense_boost", "value": 0.5, "duration": 180,
     "price": 650, "description": "180秒内增加50%防御"},
    {"name": "初级攻击药水", "effect": "attack_boost", "value": 0.25, "duration": 180,
     "price": 400, "description": "180秒内增加25%攻击力"},
    {"name": "高级攻击药水", "effect": "attack_boost", "value": 0.5, "duration": 180,
     "price": 750, "description": "180秒内增加50%攻击力"},
    {"name": "暴击增益药水", "effect": "crit_boost", "value": 0.2, "duration": 180,
     "price": 550, "description": "180秒内增加20%暴击率"},
    # 新增药水
    {"name": "敏捷药剂", "effect": "agility_boost", "value": 0.3, "sub_value": 0.25, "duration": 180,
     "price": 600, "description": "180秒内移动速度+30%、攻击速度+25%"},
    {"name": "法力护盾药剂", "effect": "mana_shield", "value": 0.3, "duration": 60,
     "price": 450, "description": "立即生成吸收30%最大生命值的护盾（持续60秒）"},
    {"name": "元素抗性药剂", "effect": "element_resist", "value": 0.3, "duration": 180,
     "price": 500, "description": "180秒内全元素抗性+30%"},
    {"name": "技能急速药剂", "effect": "skill_haste", "value": 0.2, "duration": 180,
     "price": 700, "description": "180秒内技能冷却时间减少20%"},
    {"name": "闪避药剂", "effect": "dodge_boost", "value": 0.25, "duration": 180,
     "price": 550, "description": "180秒内闪避率+25%"},
    {"name": "生命偷取药剂", "effect": "life_steal", "value": 0.15, "duration": 180,
     "price": 650, "description": "180秒内造成伤害的15%转化为生命"},
    {"name": "元素穿透药剂", "effect": "element_penetration", "value": 0.2, "duration": 180,
     "price": 600, "description": "180秒内忽视目标20%元素抗性"},
    {"name": "护盾增效药剂", "effect": "shield_boost", "value": 0.5, "stack": 3, "duration": 300,
     "price": 400, "description": "接下来的3次治疗效果提升50%"},
    {"name": "火焰伤害药剂", "effect": "fire_damage", "value": 0.3, "duration": 180,
     "price": 550, "description": "180秒内火焰伤害+30%"},
    {"name": "冰霜伤害药剂", "effect": "frost_damage", "value": 0.3, "duration": 180,
     "price": 550, "description": "180秒内冰霜伤害+30%"},
    {"name": "雷电伤害药剂", "effect": "thunder_damage", "value": 0.3, "duration": 180,
     "price": 550, "description": "180秒内雷电伤害+30%"},
    {"name": "减伤药剂", "effect": "damage_reduction", "value": 0.2, "duration": 180,
     "price": 750, "description": "180秒内受到的伤害减少20%"},
    {"name": "反弹药剂", "effect": "damage_reflect", "value": 0.15, "duration": 180,
     "price": 600, "description": "180秒内反弹15%受到的伤害"},
    {"name": "中毒抵抗药剂", "effect": "poison_resist", "value": 1.0, "duration": 180,
     "price": 300, "description": "180秒内免疫中毒效果"},
    {"name": "眩晕抵抗药剂", "effect": "stun_resist", "value": 1.0, "duration": 180,
     "price": 300, "description": "180秒内免疫眩晕效果"},
    {"name": "隐身药剂", "effect": "invisibility", "value": 0.8, "sub_value": 0.2, "duration": 120,
     "price": 600, "description": "隐身120秒（移动速度降低20%，有概率躲避敌人攻击）"},
    {"name": "暴击伤害药剂", "effect": "crit_damage_boost", "value": 0.5, "duration": 180,
     "price": 650, "description": "180秒内暴击伤害+50%"},
    {"name": "全属性药剂", "effect": "all_stats", "value": 0.1, "duration": 180,
     "price": 750, "description": "180秒内力量/血量/攻击/经验获取+10%"},
    {"name": "经验药剂", "effect": "exp_boost", "value": 0.2, "duration": 1800,  # 30分钟=1800秒
     "price": 1000, "description": "30分钟内经验获取+20%"},
    {"name": "护盾持续药剂", "effect": "shield_duration", "value": 0.5, "stack": 3, "duration": 300,
     "price": 450, "description": "接下来的3次护盾效果持续时间延长50%"}
]


class Equipment:
    def __init__(self, name, equip_type, level, attack_bonus=0, defense_bonus=0, hp_bonus=0):
        self.name = name
        self.type = equip_type
        self.level = level
        self.attack_bonus = attack_bonus
        self.defense_bonus = defense_bonus
        self.hp_bonus = hp_bonus

        # 提取武器类型（如果是武器）
        self.weapon_subtype = None
        if equip_type == "武器":
            for subtype in WEAPON_SKILLS.keys():
                if subtype in name:
                    self.weapon_subtype = subtype
                    break
            if not self.weapon_subtype:
                self.weapon_subtype = random.choice(list(WEAPON_SKILLS.keys()))

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "level": self.level,
            "attack_bonus": self.attack_bonus,
            "defense_bonus": self.defense_bonus,
            "hp_bonus": self.hp_bonus,
            "weapon_subtype": self.weapon_subtype
        }

    @classmethod
    def from_dict(cls, data):
        eq = cls(
            data["name"],
            data["type"],
            data["level"],
            data["attack_bonus"],
            data["defense_bonus"],
            data["hp_bonus"]
        )
        eq.weapon_subtype = data.get("weapon_subtype")
        return eq

    def get_sell_price(self):
        """计算装备出售价格"""
        return max(10, int((self.attack_bonus * 5 + self.defense_bonus * 3 + self.hp_bonus * 1) * self.level))

    def get_overall_score(self):
        """计算装备综合评分，用于比较"""
        return (self.attack_bonus * 2 + self.defense_bonus * 2 + self.hp_bonus) * self.level

    def is_inferior_to(self, other_equipment, threshold=0.6):
        """判断当前装备是否远劣于另一装备"""
        if not other_equipment:
            return False
        return self.get_overall_score() < other_equipment.get_overall_score() * threshold

    def __str__(self):
        base_str = f"{self.name} (等级: {self.level}) - 攻击+{self.attack_bonus}, 防御+{self.defense_bonus}, 生命+{self.hp_bonus}"
        if self.type == "武器" and self.weapon_subtype:
            skill = WEAPON_SKILLS[self.weapon_subtype]
            base_str += f"\n技能: {skill['name']} - {skill['effect']}"
        return base_str


class Player:
    def __init__(self, name):
        self.name = name
        self.realm_index = 0  # 当前境界索引
        self.realm_level = 1  # 境界内等级
        self.base_health = 300
        self.health = self.base_health
        self.base_attack = 20
        self.base_defense = 15
        self.critical_rate = 0.2  # 20%暴击率
        self.critical_damage = 1.5  # 150%暴击伤害

        self.experience = 0
        self.experience_to_next_level = self.calculate_exp_to_next_level()

        self.gold = 10000
        self.inventory = {item["name"]: 0 for item in SHOP_ITEMS}

        # 装备系统
        self.equipped = {eq_type: None for eq_type in EQUIPMENT_TYPES}
        self.equipment_inventory = []

        # 状态增益与减益
        self.buffs = {
            "attack_boost": {"value": 0, "end_time": None},
            "defense_boost": {"value": 0, "end_time": None},
            "crit_boost": {"value": 0, "end_time": None},
            "agility_boost": {"value": 0, "sub_value": 0, "end_time": None},  # 移动速度+攻击速度
            "mana_shield": {"value": 0, "end_time": None},  # 护盾值
            "element_resist": {"value": 0, "end_time": None},
            "skill_haste": {"value": 0, "end_time": None},  # 技能冷却减少
            "dodge_boost": {"value": 0, "end_time": None},
            "life_steal": {"value": 0, "end_time": None},
            "element_penetration": {"value": 0, "end_time": None},
            "shield_boost": {"value": 0, "stack": 0, "end_time": None},
            "fire_damage": {"value": 0, "end_time": None},
            "frost_damage": {"value": 0, "end_time": None},
            "thunder_damage": {"value": 0, "end_time": None},
            "damage_reduction": {"value": 0, "end_time": None},
            "damage_reflect": {"value": 0, "end_time": None},
            "poison_resist": {"value": 0, "end_time": None},
            "stun_resist": {"value": 0, "end_time": None},
            "invisibility": {"value": 0, "sub_value": 0, "end_time": None},  # 闪避概率+移动速度降低
            "crit_damage_boost": {"value": 0, "end_time": None},
            "all_stats": {"value": 0, "end_time": None},
            "exp_boost": {"value": 0, "end_time": None},
            "shield_duration": {"value": 0, "stack": 0, "end_time": None}
        }

        # 减益效果
        self.debuffs = {
            "poisoned": {"duration": 0, "damage": 0},  # 中毒
            "stunned": {"duration": 0},  # 眩晕
            "burning": {"duration": 0, "damage": 0},  # 火焰
            "frozen": {"duration": 0, "slow": 0},  # 冰霜减速
            "shocked": {"duration": 0, "chance": 0}  # 雷电暴击加成
        }

        # 技能冷却
        self.skill_cooldown = 0  # 剩余冷却回合数
        self.battle_turn = 0  # 当前战斗回合数

    def get_current_realm(self):
        return REALMS[self.realm_index]

    def calculate_exp_to_next_level(self):
        realm = self.get_current_realm()
        return int(100 * realm["exp_multiplier"] * (self.realm_level ** 1.5))

    def get_total_attack(self):
        total = self.base_attack * self.get_current_realm()["attack_multiplier"]
        # 加上装备加成
        for eq in self.equipped.values():
            if eq:
                total += eq.attack_bonus
        # 加上增益效果
        current_time = time.time()
        if self.buffs["attack_boost"]["end_time"] and current_time < self.buffs["attack_boost"]["end_time"]:
            total *= (1 + self.buffs["attack_boost"]["value"])
        # 全属性加成
        if self.buffs["all_stats"]["end_time"] and current_time < self.buffs["all_stats"]["end_time"]:
            total *= (1 + self.buffs["all_stats"]["value"])
        return int(total)

    def get_total_defense(self):
        total = self.base_defense * self.get_current_realm()["defense_multiplier"]
        # 加上装备加成
        for eq in self.equipped.values():
            if eq:
                total += eq.defense_bonus
        # 加上增益效果
        current_time = time.time()
        if self.buffs["defense_boost"]["end_time"] and current_time < self.buffs["defense_boost"]["end_time"]:
            total *= (1 + self.buffs["defense_boost"]["value"])
        # 全属性加成
        if self.buffs["all_stats"]["end_time"] and current_time < self.buffs["all_stats"]["end_time"]:
            total *= (1 + self.buffs["all_stats"]["value"])
        return int(total)

    def get_max_health(self):
        total = self.base_health * self.get_current_realm()["hp_multiplier"]
        # 加上装备加成
        for eq in self.equipped.values():
            if eq:
                total += eq.hp_bonus
        # 全属性加成
        current_time = time.time()
        if self.buffs["all_stats"]["end_time"] and current_time < self.buffs["all_stats"]["end_time"]:
            total *= (1 + self.buffs["all_stats"]["value"])
        return int(total)

    def get_critical_rate(self):
        rate = self.critical_rate
        current_time = time.time()
        if self.buffs["crit_boost"]["end_time"] and current_time < self.buffs["crit_boost"]["end_time"]:
            rate += self.buffs["crit_boost"]["value"]
        # 雷电减益加成
        if self.debuffs["shocked"]["duration"] > 0:
            rate += self.debuffs["shocked"]["chance"]
        return min(rate, 1.0)  # 最大100%暴击率

    def get_critical_damage(self):
        damage = self.critical_damage
        current_time = time.time()
        if self.buffs["crit_damage_boost"]["end_time"] and current_time < self.buffs["crit_damage_boost"]["end_time"]:
            damage *= (1 + self.buffs["crit_damage_boost"]["value"])
        return damage

    def get_dodge_chance(self):
        current_time = time.time()
        dodge = 0
        if self.buffs["dodge_boost"]["end_time"] and current_time < self.buffs["dodge_boost"]["end_time"]:
            dodge += self.buffs["dodge_boost"]["value"]
        if self.buffs["invisibility"]["end_time"] and current_time < self.buffs["invisibility"]["end_time"]:
            dodge += self.buffs["invisibility"]["value"]
        return min(dodge, 1.0)

    def clean_expired_buffs(self):
        """清理过期的增益效果"""
        current_time = time.time()
        for buff_type in self.buffs:
            buff = self.buffs[buff_type]
            if "end_time" in buff and buff["end_time"] and current_time >= buff["end_time"]:
                if buff_type in ["shield_boost", "shield_duration"]:
                    self.buffs[buff_type] = {"value": 0, "stack": 0, "end_time": None}
                elif buff_type in ["agility_boost", "invisibility"]:
                    self.buffs[buff_type] = {"value": 0, "sub_value": 0, "end_time": None}
                else:
                    self.buffs[buff_type] = {"value": 0, "end_time": None}

    def update_debuffs(self, battle_log):
        """更新减益效果，每回合生效"""
        current_time = time.time()
        messages = []

        # 处理中毒
        if self.debuffs["poisoned"]["duration"] > 0:
            if not (self.buffs["poison_resist"]["end_time"] and current_time < self.buffs["poison_resist"]["end_time"]):
                self.health -= self.debuffs["poisoned"]["damage"]
                messages.append(f"你受到了{self.debuffs['poisoned']['damage']}点中毒伤害！")
            self.debuffs["poisoned"]["duration"] -= 1

        # 处理燃烧
        if self.debuffs["burning"]["duration"] > 0:
            self.health -= self.debuffs["burning"]["damage"]
            messages.append(f"你受到了{self.debuffs['burning']['damage']}点火焰伤害！")
            self.debuffs["burning"]["duration"] -= 1

        # 处理眩晕减少1回合
        if self.debuffs["stunned"]["duration"] > 0:
            self.debuffs["stunned"]["duration"] -= 1
            if self.debuffs["stunned"]["duration"] == 0:
                messages.append("你从眩晕中恢复了！")

        # 处理冰冻减速减少1回合
        if self.debuffs["frozen"]["duration"] > 0:
            self.debuffs["frozen"]["duration"] -= 1
            if self.debuffs["frozen"]["duration"] == 0:
                messages.append("你从冰冻中恢复了！")

        # 处理雷电效果减少1回合
        if self.debuffs["shocked"]["duration"] > 0:
            self.debuffs["shocked"]["duration"] -= 1

        # 确保血量可以为负（允许玩家死亡血量为负）
        self.health = self.health  # 不再限制为0以上

        battle_log.extend(messages)
        return messages

    def level_up(self):
        # 提升境界内等级，降低后期属性增长幅度以平衡游戏
        self.realm_level += 1
        self.experience -= self.experience_to_next_level

        # 提升基础属性（前期增长较快，后期放缓）
        level_factor = min(1.0, self.realm_level / 20)  # 后期增长放缓
        self.base_health += int(20 * level_factor * (1 + self.realm_index * 0.2))
        self.base_attack += int(5 * level_factor * (1 + self.realm_index * 0.25))
        self.base_defense += int(3 * level_factor * (1 + self.realm_index * 0.2))

        # 恢复全部生命值
        self.health = self.get_max_health()

        # 计算下一级所需经验
        self.experience_to_next_level = self.calculate_exp_to_next_level()

        return f"恭喜！{self.name}在{self.get_current_realm()['name']}提升到了{self.realm_level}级！"

    def realm_up(self):
        # 提升大境界
        if self.realm_index < len(REALMS) - 1:
            self.realm_index += 1
            self.realm_level = 1

            # 大境界提升，属性提升（降低幅度以平衡）
            self.base_health = int(self.base_health * 1.3)  # 原1.5
            self.base_attack = int(self.base_attack * 1.5)  # 原1.8
            self.base_defense = int(self.base_defense * 1.4)  # 原1.6

            # 恢复全部生命值
            self.health = self.get_max_health()

            # 计算下一级所需经验
            self.experience = 0
            self.experience_to_next_level = self.calculate_exp_to_next_level()

            return f"恭喜！{self.name}突破到了{self.get_current_realm()['name']}！属性大幅提升！"
        else:
            return "已经达到最高境界！"

    def gain_experience(self, amount):
        # 应用经验加成
        current_time = time.time()
        if self.buffs["exp_boost"]["end_time"] and current_time < self.buffs["exp_boost"]["end_time"]:
            amount = int(amount * (1 + self.buffs["exp_boost"]["value"]))
        if self.buffs["all_stats"]["end_time"] and current_time < self.buffs["all_stats"]["end_time"]:
            amount = int(amount * (1 + self.buffs["all_stats"]["value"]))

        self.experience += amount
        messages = []

        # 检查是否可以升级
        while True:
            if self.realm_level >= REALM_LEVELS:
                # 达到当前境界上限，尝试突破大境界
                if self.realm_index < len(REALMS) - 1:
                    messages.append(self.realm_up())
                else:
                    # 最高境界，经验不再增加
                    self.experience = self.experience_to_next_level - 1
                    break
            elif self.experience >= self.experience_to_next_level:
                messages.append(self.level_up())
            else:
                break

        return messages

    def use_item(self, item_name):
        if self.inventory.get(item_name, 0) <= 0:
            return False, "物品数量不足"

        self.inventory[item_name] -= 1
        current_time = time.time()

        for item in SHOP_ITEMS:
            if item["name"] == item_name:
                if item["effect"] == "max_hp":
                    self.base_health = int(self.base_health * (1 + item["value"]))
                    self.health = min(self.health + int(self.get_max_health() * item["value"]), self.get_max_health())
                    return True, f"使用了{item_name}，生命上限永久增加{int(item['value'] * 100)}%！"

                elif item["effect"] == "heal":
                    heal_amount = int(self.get_max_health() * item["value"])
                    # 应用护盾增效
                    if self.buffs["shield_boost"]["stack"] > 0 and self.buffs["shield_boost"][
                        "end_time"] and current_time < self.buffs["shield_boost"]["end_time"]:
                        heal_amount = int(heal_amount * (1 + self.buffs["shield_boost"]["value"]))
                        self.buffs["shield_boost"]["stack"] -= 1
                    self.health = min(self.health + heal_amount, self.get_max_health())
                    return True, f"使用了{item_name}，恢复了{heal_amount}点生命值！"

                elif item["effect"] == "full_heal":
                    full_heal = self.get_max_health()
                    # 应用护盾增效
                    if self.buffs["shield_boost"]["stack"] > 0 and self.buffs["shield_boost"][
                        "end_time"] and current_time < self.buffs["shield_boost"]["end_time"]:
                        full_heal = int(full_heal * (1 + self.buffs["shield_boost"]["value"]))
                        self.buffs["shield_boost"]["stack"] -= 1
                    self.health = min(full_heal, self.get_max_health())
                    return True, f"使用了{item_name}，生命值完全恢复！"

                elif item["effect"] in ["attack_boost", "defense_boost", "crit_boost",
                                        "element_resist", "skill_haste", "dodge_boost",
                                        "life_steal", "element_penetration", "fire_damage",
                                        "frost_damage", "thunder_damage", "damage_reduction",
                                        "damage_reflect", "poison_resist", "stun_resist",
                                        "crit_damage_boost", "all_stats", "exp_boost"]:
                    # 处理可叠加持续时间的buff
                    end_time = current_time + item["duration"]
                    current_buff = self.buffs[item["effect"]]

                    # 如果已有该buff且未过期，则延长时间
                    if current_buff["end_time"] and current_time < current_buff["end_time"]:
                        end_time = current_buff["end_time"] + item["duration"]

                    self.buffs[item["effect"]] = {
                        "value": item["value"],
                        "end_time": end_time
                    }
                    return True, f"使用了{item_name}，{item['description']}！"

                elif item["effect"] in ["agility_boost", "invisibility"]:
                    end_time = current_time + item["duration"]
                    current_buff = self.buffs[item["effect"]]

                    if current_buff["end_time"] and current_time < current_buff["end_time"]:
                        end_time = current_buff["end_time"] + item["duration"]

                    self.buffs[item["effect"]] = {
                        "value": item["value"],
                        "sub_value": item["sub_value"],
                        "end_time": end_time
                    }
                    return True, f"使用了{item_name}，{item['description']}！"

                elif item["effect"] == "mana_shield":
                    shield_value = int(self.get_max_health() * item["value"])
                    end_time = current_time + item["duration"]

                    # 应用护盾持续时间加成
                    if self.buffs["shield_duration"]["stack"] > 0 and self.buffs["shield_duration"][
                        "end_time"] and current_time < self.buffs["shield_duration"]["end_time"]:
                        end_time = current_time + item["duration"] * (1 + self.buffs["shield_duration"]["value"])
                        self.buffs["shield_duration"]["stack"] -= 1

                    self.buffs["mana_shield"] = {
                        "value": shield_value,
                        "end_time": end_time
                    }
                    return True, f"使用了{item_name}，生成了{shield_value}点护盾！"

                elif item["effect"] in ["shield_boost", "shield_duration"]:
                    end_time = current_time + item["duration"]
                    current_buff = self.buffs[item["effect"]]

                    if current_buff["end_time"] and current_time < current_buff["end_time"]:
                        end_time = current_buff["end_time"] + item["duration"]
                        stack = current_buff["stack"] + item["stack"]
                    else:
                        stack = item["stack"]

                    self.buffs[item["effect"]] = {
                        "value": item["value"],
                        "stack": stack,
                        "end_time": end_time
                    }
                    return True, f"使用了{item_name}，{item['description']}！"

        return False, "未知物品"

    def equip_item(self, equipment):
        # 卸下当前装备
        current = self.equipped[equipment.type]
        self.equipped[equipment.type] = equipment
        return current

    def is_alive(self):
        return self.health > 0

    def use_skill_attack(self, monster):
        """使用技能攻击"""
        if self.skill_cooldown > 0:
            return False, "技能正在冷却中"

        # 获取当前装备的武器
        weapon = self.equipped.get("武器")
        weapon_type = weapon.weapon_subtype if weapon and weapon.weapon_subtype else "剑"
        skill = WEAPON_SKILLS[weapon_type]

        # 计算技能冷却时间（考虑技能急速）
        current_time = time.time()
        base_cooldown = 3
        if self.buffs["skill_haste"]["end_time"] and current_time < self.buffs["skill_haste"]["end_time"]:
            base_cooldown = int(base_cooldown * (1 - self.buffs["skill_haste"]["value"]))
        self.skill_cooldown = max(1, base_cooldown)

        # 基础伤害
        damage = self.get_total_attack() - monster.defense // 2
        damage = max(1, damage)

        # 应用元素伤害加成
        if weapon_type == "杖":  # 杖默认是元素伤害
            element_type = random.choice(["fire", "frost", "thunder"])
            if element_type == "fire" and self.buffs["fire_damage"]["end_time"] and current_time < \
                    self.buffs["fire_damage"]["end_time"]:
                damage = int(damage * (1 + self.buffs["fire_damage"]["value"]))
            elif element_type == "frost" and self.buffs["frost_damage"]["end_time"] and current_time < \
                    self.buffs["frost_damage"]["end_time"]:
                damage = int(damage * (1 + self.buffs["frost_damage"]["value"]))
            elif element_type == "thunder" and self.buffs["thunder_damage"]["end_time"] and current_time < \
                    self.buffs["thunder_damage"]["end_time"]:
                damage = int(damage * (1 + self.buffs["thunder_damage"]["value"]))

        # 技能特殊效果
        messages = [f"你使用了{skill['name']}！{skill['effect']}"]
        critical = False

        if weapon_type == "剑":
            # 破空斩：150%伤害，30%暴击
            damage = int(damage * 1.5)
            if random.random() < 0.3:
                critical = True

        elif weapon_type == "刀":
            # 旋风斩：130%伤害，恢复5%生命
            damage = int(damage * 1.3)
            heal = int(self.get_max_health() * 0.05)
            self.health = min(self.health + heal, self.get_max_health())
            messages.append(f"你恢复了{heal}点生命值！")

        elif weapon_type == "斧":
            # 巨力一击：180%伤害，10%反噬
            damage = int(damage * 1.8)
            reflect_damage = int(damage * 0.1)
            self.health = self.health - reflect_damage  # 允许生命值变为负数
            messages.append(f"你受到了{reflect_damage}点反噬伤害！")

        elif weapon_type == "杖":
            # 元素冲击：140%伤害，附加元素效果
            damage = int(damage * 1.4)
            if element_type == "fire":
                monster.health -= int(damage * 0.2)  # 持续伤害
                messages.append(f"{monster.name}被点燃，将持续受到伤害！")
            elif element_type == "frost":
                messages.append(f"{monster.name}被冰冻，行动迟缓！")
            elif element_type == "thunder":
                damage = int(damage * 1.2)  # 额外伤害
                messages.append(f"{monster.name}受到了额外的雷电伤害！")

        elif weapon_type == "弓":
            # 精准射击：120%伤害，忽略20%防御
            damage = int(damage * 1.2)

        # 处理暴击
        if not critical and random.random() < self.get_critical_rate():
            critical = True
            damage = int(damage * self.get_critical_damage())
            messages.append("暴击！造成了额外伤害！")

        # 应用生命偷取
        current_time = time.time()
        if self.buffs["life_steal"]["end_time"] and current_time < self.buffs["life_steal"]["end_time"]:
            steal = int(damage * self.buffs["life_steal"]["value"])
            self.health = min(self.health + steal, self.get_max_health())
            messages.append(f"你偷取了{steal}点生命值！")

        # 对怪物造成伤害
        monster.health = max(0, monster.health - damage)
        messages.append(f"你对{monster.name}造成了{damage}点伤害！")

        return True, messages

    def to_dict(self):
        return {
            "name": self.name,
            "realm_index": self.realm_index,
            "realm_level": self.realm_level,
            "base_health": self.base_health,
            "health": self.health,  # 允许保存负值
            "base_attack": self.base_attack,
            "base_defense": self.base_defense,
            "critical_rate": self.critical_rate,
            "critical_damage": self.critical_damage,
            "experience": self.experience,
            "experience_to_next_level": self.experience_to_next_level,
            "gold": self.gold,
            "inventory": self.inventory,
            "equipped": {k: v.to_dict() if v else None for k, v in self.equipped.items()},
            "equipment_inventory": [eq.to_dict() for eq in self.equipment_inventory],
            "buffs": self.buffs,
            "debuffs": self.debuffs,
            "skill_cooldown": self.skill_cooldown,
            "battle_turn": self.battle_turn
        }

    @classmethod
    def from_dict(cls, data):
        player = cls(data["name"])
        player.realm_index = data["realm_index"]
        player.realm_level = data["realm_level"]
        player.base_health = data["base_health"]
        player.health = data["health"]  # 允许负值
        player.base_attack = data["base_attack"]
        player.base_defense = data["base_defense"]
        player.critical_rate = data["critical_rate"]
        player.critical_damage = data["critical_damage"]
        player.experience = data["experience"]
        player.experience_to_next_level = data["experience_to_next_level"]
        player.gold = data["gold"]
        player.inventory = data["inventory"]

        # 恢复装备
        player.equipped = {}
        for eq_type in EQUIPMENT_TYPES:
            eq_data = data["equipped"].get(eq_type)
            if eq_data:
                player.equipped[eq_type] = Equipment.from_dict(eq_data)
            else:
                player.equipped[eq_type] = None

        # 恢复背包中的装备
        player.equipment_inventory = []
        for eq_data in data.get("equipment_inventory", []):
            if eq_data:
                player.equipment_inventory.append(Equipment.from_dict(eq_data))

        # 恢复增益效果并清理过期的
        player.buffs = data.get("buffs", {
            "attack_boost": {"value": 0, "end_time": None},
            "defense_boost": {"value": 0, "end_time": None},
            "crit_boost": {"value": 0, "end_time": None},
            "agility_boost": {"value": 0, "sub_value": 0, "end_time": None},
            "mana_shield": {"value": 0, "end_time": None},
            "element_resist": {"value": 0, "end_time": None},
            "skill_haste": {"value": 0, "end_time": None},
            "dodge_boost": {"value": 0, "end_time": None},
            "life_steal": {"value": 0, "end_time": None},
            "element_penetration": {"value": 0, "end_time": None},
            "shield_boost": {"value": 0, "stack": 0, "end_time": None},
            "fire_damage": {"value": 0, "end_time": None},
            "frost_damage": {"value": 0, "end_time": None},
            "thunder_damage": {"value": 0, "end_time": None},
            "damage_reduction": {"value": 0, "end_time": None},
            "damage_reflect": {"value": 0, "end_time": None},
            "poison_resist": {"value": 0, "end_time": None},
            "stun_resist": {"value": 0, "end_time": None},
            "invisibility": {"value": 0, "sub_value": 0, "end_time": None},
            "crit_damage_boost": {"value": 0, "end_time": None},
            "all_stats": {"value": 0, "end_time": None},
            "exp_boost": {"value": 0, "end_time": None},
            "shield_duration": {"value": 0, "stack": 0, "end_time": None}
        })

        # 恢复减益效果
        player.debuffs = data.get("debuffs", {
            "poisoned": {"duration": 0, "damage": 0},
            "stunned": {"duration": 0},
            "burning": {"duration": 0, "damage": 0},
            "frozen": {"duration": 0, "slow": 0},
            "shocked": {"duration": 0, "chance": 0}
        })

        # 恢复技能冷却
        player.skill_cooldown = data.get("skill_cooldown", 0)
        player.battle_turn = data.get("battle_turn", 0)

        player.clean_expired_buffs()

        return player

    def __str__(self):
        # 检查并清理过期增益
        self.clean_expired_buffs()

        # 构建增益信息字符串
        buffs_info = []
        current_time = time.time()

        for buff_type, buff in self.buffs.items():
            if buff["end_time"] and current_time < buff["end_time"]:
                remaining = int(buff["end_time"] - current_time)
                if buff_type == "attack_boost":
                    buffs_info.append(f"攻击提升+{int(buff['value'] * 100)}% ({remaining}秒)")
                elif buff_type == "defense_boost":
                    buffs_info.append(f"防御提升+{int(buff['value'] * 100)}% ({remaining}秒)")
                elif buff_type == "crit_boost":
                    buffs_info.append(f"暴击率提升+{int(buff['value'] * 100)}% ({remaining}秒)")
                elif buff_type == "agility_boost":
                    buffs_info.append(
                        f"移动速度+{int(buff['value'] * 100)}%，攻击速度+{int(buff['sub_value'] * 100)}% ({remaining}秒)")
                elif buff_type == "mana_shield":
                    buffs_info.append(f"法力护盾: {buff['value']}点 ({remaining}秒)")
                elif buff_type == "element_resist":
                    buffs_info.append(f"元素抗性+{int(buff['value'] * 100)}% ({remaining}秒)")
                elif buff_type == "skill_haste":
                    buffs_info.append(f"技能冷却减少{int(buff['value'] * 100)}% ({remaining}秒)")
                elif buff_type == "dodge_boost":
                    buffs_info.append(f"闪避率+{int(buff['value'] * 100)}% ({remaining}秒)")
                elif buff_type == "life_steal":
                    buffs_info.append(f"生命偷取+{int(buff['value'] * 100)}% ({remaining}秒)")

        # 构建减益信息字符串
        debuffs_info = []
        for debuff_type, debuff in self.debuffs.items():
            if debuff_type == "poisoned" and debuff["duration"] > 0:
                debuffs_info.append(f"中毒: 每回合{debuff['damage']}点伤害，剩余{debuff['duration']}回合")
            elif debuff_type == "stunned" and debuff["duration"] > 0:
                debuffs_info.append(f"眩晕: 无法行动，剩余{debuff['duration']}回合")
            elif debuff_type == "burning" and debuff["duration"] > 0:
                debuffs_info.append(f"燃烧: 每回合{debuff['damage']}点伤害，剩余{debuff['duration']}回合")
            elif debuff_type == "frozen" and debuff["duration"] > 0:
                debuffs_info.append(f"冰冻: 行动迟缓，剩余{debuff['duration']}回合")
            elif debuff_type == "shocked" and debuff["duration"] > 0:
                debuffs_info.append(f"触电: 暴击率提升，剩余{debuff['duration']}回合")

        buffs_text = "\n".join(buffs_info) if buffs_info else "无"
        debuffs_text = "\n减益效果:\n" + "\n".join(debuffs_info) if debuffs_info else ""

        return f"{self.name} - {self.get_current_realm()['name']}{self.realm_level}级\n" + \
            f"生命值: {self.health}/{self.get_max_health()}\n" + \
            f"攻击力: {self.get_total_attack()}\n" + \
            f"防御力: {self.get_total_defense()}\n" + \
            f"暴击率: {int(self.get_critical_rate() * 100)}%\n" + \
            f"经验值: {self.experience}/{self.experience_to_next_level}\n" + \
            f"金币: {self.gold}\n" + \
            f"当前增益:\n{buffs_text}" + debuffs_text


class Monster:
    def __init__(self, name, category, species, level):
        self.name = name
        self.category = category  # 基础种、精英种等
        self.species = species  # 仙术使、机械种等
        self.level = level

        # 伤害类型
        self.damage_types = MONSTER_DAMAGE_EFFECTS.get(species, [])

        # 根据类别和等级设置属性（调整成长曲线以平衡游戏）
        category_multipliers = {
            "基础种": 0.8,
            "精英种": 1.8,
            "首领种": 3.0,
            "变异种": 4.5,
            "BOSS级种": 7.0
        }

        multiplier = category_multipliers[category]
        # 调整怪物属性成长，使后期不会过于简单
        level_factor = 1.0 + (level - 1) * 0.12  # 略微提高后期怪物强度

        self.base_health = int(80 * multiplier * (level ** 0.85))  # 提高生命值成长
        self.health = self.base_health
        self.attack = int(8 * multiplier * (level ** 0.9))  # 提高攻击力成长
        self.defense = int(3 * multiplier * (level ** 0.8))  # 提高防御力成长

        # 设置经验和金币奖励（前期略高，帮助玩家度过困难期）
        self.experience_reward = int(60 * multiplier * (level ** 0.9))  # 提高前期经验
        self.gold_reward = int(25 * multiplier * (level ** 0.8))  # 提高前期金币

        # 特殊能力概率
        self.special_ability_chance = 0.1 + (multiplier - 1.0) * 0.05

        # 标记是否为区域守护者
        self.is_guardian = "（区域守护者）" in name

    def is_alive(self):
        return self.health > 0

    def use_special_ability(self):
        if random.random() < self.special_ability_chance:
            abilities = [
                {"name": "狂暴", "effect": "attack", "value": 1.5,
                 "message": f"{self.name}进入了狂暴状态，攻击力大幅提升！"},
                {"name": "坚硬外壳", "effect": "defense", "value": 1.5,
                 "message": f"{self.name}激活了坚硬外壳，防御力大幅提升！"},
                {"name": "生命吸取", "effect": "leech", "value": 0.2,
                 "message": f"{self.name}使用了生命吸取，恢复了部分生命值！"},
                {"name": "要害打击", "effect": "crit", "value": 2.0,
                 "message": f"{self.name}准备进行要害打击，下一击必定暴击！"}
            ]
            return random.choice(abilities)
        return None

    def apply_damage_effect(self, player):
        """对玩家应用伤害效果"""
        if not self.damage_types:
            return []

        messages = []
        effect = random.choice(self.damage_types)
        current_time = time.time()

        # 检查玩家是否有对应抗性
        if effect == "中毒" and (
                player.buffs["poison_resist"]["end_time"] and current_time < player.buffs["poison_resist"]["end_time"]):
            messages.append(f"你的中毒抵抗生效了，免疫了中毒效果！")
            return messages

        if effect == "眩晕" and (
                player.buffs["stun_resist"]["end_time"] and current_time < player.buffs["stun_resist"]["end_time"]):
            messages.append(f"你的眩晕抵抗生效了，免疫了眩晕效果！")
            return messages

        # 应用效果
        if effect == "火焰":
            damage = max(1, int(self.attack * 0.2))
            duration = 3
            player.debuffs["burning"] = {"duration": duration, "damage": damage}
            messages.append(f"{self.name}对你施加了火焰效果，你将在{duration}回合内每回合受到{damage}点伤害！")

        elif effect == "冰霜":
            slow = 0.2
            duration = 2
            player.debuffs["frozen"] = {"duration": duration, "slow": slow}
            messages.append(f"{self.name}对你施加了冰冻效果，你将在{duration}回合内行动迟缓！")

        elif effect == "雷电":
            chance = 0.2
            duration = 2
            player.debuffs["shocked"] = {"duration": duration, "chance": chance}
            messages.append(f"{self.name}对你施加了雷电效果，你将在{duration}回合内暴击率提升{int(chance * 100)}%！")

        elif effect == "中毒":
            damage = max(1, int(self.attack * 0.15))
            duration = 4
            player.debuffs["poisoned"] = {"duration": duration, "damage": damage}
            messages.append(f"{self.name}对你施加了中毒效果，你将在{duration}回合内每回合受到{damage}点伤害！")

        elif effect == "眩晕":
            duration = 1
            player.debuffs["stunned"] = {"duration": duration}
            messages.append(f"{self.name}对你施加了眩晕效果，你将在{duration}回合内无法行动！")

        return messages

    def __str__(self):
        damage_effects_text = f"伤害效果: {', '.join(self.damage_types)}" if self.damage_types else "无特殊伤害效果"
        return f"{self.name} ({self.category} - {self.species}) - 等级: {self.level}\n" + \
            f"生命值: {self.health}/{self.base_health}\n" + \
            f"攻击力: {self.attack}\n" + \
            f"防御力: {self.defense}\n" + \
            damage_effects_text

    def to_dict(self):
        return {
            "name": self.name,
            "category": self.category,
            "species": self.species,
            "level": self.level,
            "base_health": self.base_health,
            "health": self.health,
            "attack": self.attack,
            "defense": self.defense,
            "experience_reward": self.experience_reward,
            "gold_reward": self.gold_reward,
            "is_guardian": self.is_guardian
        }

    @classmethod
    def from_dict(cls, data):
        monster = cls(data["name"], data["category"], data["species"], data["level"])
        monster.base_health = data["base_health"]
        monster.health = data["health"]
        monster.attack = data["attack"]
        monster.defense = data["defense"]
        monster.experience_reward = data["experience_reward"]
        monster.gold_reward = data["gold_reward"]
        monster.is_guardian = data["is_guardian"]
        return monster


# 存档和读档功能
def save_game():
    """保存游戏数据到浏览器localStorage，确保死亡状态也能保存"""
    if not st.session_state.player:
        return False

    # 准备要保存的数据
    save_data = {
        "player": st.session_state.player.to_dict(),
        "current_area": st.session_state.current_area,
        "current_monster": st.session_state.current_monster.to_dict() if st.session_state.current_monster else None,
        "timestamp": datetime.now().isoformat()
    }

    # 将数据转换为JSON字符串
    save_json = json.dumps(save_data)

    # 通过JavaScript将数据存入localStorage
    st.markdown(
        f"""
        <script>
            localStorage.setItem('xiuxian_save', JSON.stringify({json.dumps(save_json)}));
        </script>
        """,
        unsafe_allow_html=True
    )

    st.session_state.save_data = save_data
    return True


def load_game_from_localstorage():
    """从浏览器localStorage加载存档"""
    # 注入JavaScript读取localStorage并通过query params传递
    st.markdown("""
    <script>
        const saveData = localStorage.getItem('xiuxian_save');
        if (saveData) {
            // 将存档数据通过URL参数传递给Streamlit
            const url = new URL(window.location);
            url.searchParams.set('save_data', encodeURIComponent(saveData));
            window.history.replaceState(null, null, url);
        }
    </script>
    """, unsafe_allow_html=True)

    # 从URL参数获取存档数据
    query_params = st.query_params
    if 'save_data' in query_params:
        try:
            save_json = urllib.parse.unquote(query_params['save_data'][0])
            save_data = json.loads(save_json)
            return save_data
        except:
            return None
    return None


# 游戏界面和逻辑控制
def init_game():
    """初始化游戏数据（首次加载或刷新时调用）"""
    if 'player' not in st.session_state:
        st.session_state.player = None
    if 'current_area' not in st.session_state:
        st.session_state.current_area = 1
    if 'current_monster' not in st.session_state:
        st.session_state.current_monster = None
    if 'battle_log' not in st.session_state:
        st.session_state.battle_log = []
    if 'current_view' not in st.session_state:
        st.session_state.current_view = "create"  # create/main/battle/shop/backpack
    if 'save_data' not in st.session_state:
        # 尝试从localStorage加载存档
        st.session_state.save_data = load_game_from_localstorage()


def generate_monster():
    """生成适合当前区域的怪物"""
    area_level = st.session_state.current_area

    # 区域等级越高，生成高级怪物的概率越大
    category_weights = {
        "基础种": max(0.7 - area_level * 0.05, 0.1),
        "精英种": max(0.25 - area_level * 0.02, 0.1),
        "首领种": min(0.05 + area_level * 0.03, 0.2),
        "变异种": min(0 + area_level * 0.02, 0.2),
        "BOSS级种": min(0 + area_level * 0.005, 0.1)
    }

    # 确保权重总和为1
    total = sum(category_weights.values())
    category_probs = {k: v / total for k, v in category_weights.items()}

    # 随机选择怪物类别
    categories = list(category_probs.keys())
    probabilities = list(category_probs.values())
    category = random.choices(categories, probabilities)[0]

    # 随机选择物种
    species_type = random.choice(list(MONSTERS[category].keys()))
    monster_name = random.choice(MONSTERS[category][species_type])

    # 区域守护者概率（每5个区域可能出现）
    if random.random() < 0.1 and area_level % 5 == 0:
        monster_name += "（区域守护者）"

    # 怪物等级基于区域等级，有一定浮动
    monster_level = max(1, int(area_level * (0.8 + random.random() * 0.4)))

    return Monster(monster_name, category, species_type, monster_level)


def generate_equipment():
    """生成装备"""
    player = st.session_state.player
    if not player:
        return None

    equip_type = random.choice(EQUIPMENT_TYPES)

    # 装备等级与玩家等级相关
    player_level = player.realm_level + player.get_current_realm()["level"] * 10
    level_variation = random.randint(-2, 3)
    level = max(1, player_level + level_variation)

    # 装备品质
    quality = random.random()
    if quality < 0.5:  # 普通
        attack = random.randint(1, 3) * level
        defense = random.randint(1, 2) * level
        hp = random.randint(5, 10) * level
    elif quality < 0.8:  # 优秀
        attack = random.randint(3, 6) * level
        defense = random.randint(2, 4) * level
        hp = random.randint(10, 20) * level
    elif quality < 0.95:  # 稀有
        attack = random.randint(6, 10) * level
        defense = random.randint(4, 7) * level
        hp = random.randint(20, 35) * level
    else:  # 史诗
        attack = random.randint(10, 15) * level
        defense = random.randint(7, 12) * level
        hp = random.randint(35, 60) * level

    # 装备名称
    prefixes = ["破旧的", "普通的", "精致的", "卓越的", "传奇的", "神圣的"]
    prefix = prefixes[min(int(quality * len(prefixes)), len(prefixes) - 1)]

    type_names = {
        "武器": ["剑", "刀", "斧", "杖", "弓"],
        "头盔": ["皮帽", "铁盔", "钢盔", "战盔", "神冠"],
        "铠甲": ["皮甲", "铁甲", "钢甲", "战甲", "神甲"],
        "护腿": ["皮裤", "铁裤", "钢裤", "战裤", "神裤"],
        "手套": ["皮手套", "铁手套", "钢手套", "战手套", "神手套"],
        "鞋子": ["皮靴", "铁靴", "钢靴", "战靴", "神靴"]
    }

    name = f"{prefix}{random.choice(type_names[equip_type])}"

    return Equipment(name, equip_type, level, attack, defense, hp)


def generate_loot():
    """生成战利品：装备和药水"""
    player = st.session_state.player
    if not player:
        return [], []

    equipment = None
    potions = []

    # 生成装备的概率
    if random.random() < 0.3:  # 30%概率获得装备
        equipment = generate_equipment()

    # 生成药水的概率
    if random.random() < 0.4:  # 40%概率获得药水
        potion_types = [item for item in SHOP_ITEMS if item["effect"] != "max_hp"]  # 不含生命上限药水
        potion = random.choice(potion_types)
        quantity = random.randint(1, 2)
        potions.append((potion["name"], quantity))
        player.inventory[potion["name"]] += quantity

    return equipment, potions


def process_attack():
    """处理玩家普通攻击"""
    player = st.session_state.player
    monster = st.session_state.current_monster

    # 检查玩家是否眩晕
    if player.debuffs["stunned"]["duration"] > 0:
        st.session_state.battle_log.append("你处于眩晕状态，无法攻击！")
        # 怪物回合
        monster_turn()
        return

    # 技能冷却减少
    if player.skill_cooldown > 0:
        player.skill_cooldown -= 1

    # 检查闪避
    dodge_chance = player.get_dodge_chance()
    if random.random() < dodge_chance:
        st.session_state.battle_log.append("你成功闪避了敌人的攻击！")
        # 怪物回合
        monster_turn()
        return

    # 计算伤害
    damage = player.get_total_attack() - monster.defense // 2
    damage = max(1, damage)

    # 检查暴击
    critical = random.random() < player.get_critical_rate()
    if critical:
        damage = int(damage * player.get_critical_damage())
        st.session_state.battle_log.append("暴击！造成了额外伤害！")

    # 应用生命偷取
    current_time = time.time()
    if player.buffs["life_steal"]["end_time"] and current_time < player.buffs["life_steal"]["end_time"]:
        steal = int(damage * player.buffs["life_steal"]["value"])
        player.health = min(player.health + steal, player.get_max_health())
        st.session_state.battle_log.append(f"你偷取了{steal}点生命值！")

    # 对怪物造成伤害
    monster.health = max(0, monster.health - damage)
    st.session_state.battle_log.append(f"你对{monster.name}造成了{damage}点伤害！")

    # 检查怪物是否死亡
    if not monster.is_alive():
        battle_victory()
        return

    # 怪物使用特殊能力
    special = monster.use_special_ability()
    if special:
        st.session_state.battle_log.append(special["message"])
        if special["effect"] == "attack":
            monster.attack = int(monster.attack * special["value"])
        elif special["effect"] == "defense":
            monster.defense = int(monster.defense * special["value"])
        elif special["effect"] == "leech":
            heal = int(monster.base_health * special["value"])
            monster.health = min(monster.health + heal, monster.base_health)
            st.session_state.battle_log.append(f"{monster.name}恢复了{heal}点生命值！")

    # 怪物回合
    monster_turn()


def process_skill_attack():
    """处理玩家技能攻击"""
    player = st.session_state.player
    monster = st.session_state.current_monster

    # 检查玩家是否眩晕
    if player.debuffs["stunned"]["duration"] > 0:
        st.session_state.battle_log.append("你处于眩晕状态，无法使用技能！")
        # 怪物回合
        monster_turn()
        return

    # 使用技能
    success, messages = player.use_skill_attack(monster)
    if not success:
        st.session_state.battle_log.append(messages)
        return

    st.session_state.battle_log.extend(messages)

    # 检查怪物是否死亡
    if not monster.is_alive():
        battle_victory()
        return

    # 怪物使用特殊能力
    special = monster.use_special_ability()
    if special:
        st.session_state.battle_log.append(special["message"])
        if special["effect"] == "attack":
            monster.attack = int(monster.attack * special["value"])
        elif special["effect"] == "defense":
            monster.defense = int(monster.defense * special["value"])
        elif special["effect"] == "leech":
            heal = int(monster.base_health * special["value"])
            monster.health = min(monster.health + heal, monster.base_health)
            st.session_state.battle_log.append(f"{monster.name}恢复了{heal}点生命值！")

    # 怪物回合
    monster_turn()


def monster_turn():
    """怪物攻击回合"""
    player = st.session_state.player
    monster = st.session_state.current_monster

    # 更新减益效果
    player.update_debuffs(st.session_state.battle_log)

    # 检查玩家是否已死亡
    if not player.is_alive():
        st.session_state.battle_log.append("你被击败了！")
        st.session_state.current_monster = None
        return

    # 检查怪物是否还活着
    if not monster.is_alive():
        return

    # 计算伤害
    damage = monster.attack - player.get_total_defense() // 3
    damage = max(1, damage)

    # 应用伤害减免
    current_time = time.time()
    if player.buffs["damage_reduction"]["end_time"] and current_time < player.buffs["damage_reduction"]["end_time"]:
        damage = int(damage * (1 - player.buffs["damage_reduction"]["value"]))
        damage = max(1, damage)

    # 应用护盾
    if player.buffs["mana_shield"]["end_time"] and current_time < player.buffs["mana_shield"]["end_time"]:
        if player.buffs["mana_shield"]["value"] >= damage:
            player.buffs["mana_shield"]["value"] -= damage
            st.session_state.battle_log.append(
                f"你的护盾吸收了{damage}点伤害！剩余护盾: {player.buffs['mana_shield']['value']}")
            damage = 0
        else:
            damage -= player.buffs["mana_shield"]["value"]
            st.session_state.battle_log.append(f"你的护盾被打破了，吸收了{player.buffs['mana_shield']['value']}点伤害！")
            player.buffs["mana_shield"] = {"value": 0, "end_time": None}

    # 对玩家造成伤害（允许生命值变为负数）
    player.health = player.health - damage
    if damage > 0:
        st.session_state.battle_log.append(f"{monster.name}对你造成了{damage}点伤害！")

    # 应用伤害反弹
    if player.buffs["damage_reflect"]["end_time"] and current_time < player.buffs["damage_reflect"]["end_time"]:
        reflect = int(damage * player.buffs["damage_reflect"]["value"])
        if reflect > 0:
            monster.health = max(0, monster.health - reflect)
            st.session_state.battle_log.append(f"你反弹了{reflect}点伤害给{monster.name}！")
            if not monster.is_alive():
                battle_victory()
                return

    # 应用怪物伤害效果
    effect_messages = monster.apply_damage_effect(player)
    st.session_state.battle_log.extend(effect_messages)

    # 检查玩家是否已死亡
    if not player.is_alive():
        st.session_state.battle_log.append("你被击败了！")
        st.session_state.current_monster = None

    # 增加战斗回合数
    player.battle_turn += 1


def battle_victory():
    """战斗胜利处理"""
    player = st.session_state.player
    monster = st.session_state.current_monster

    st.session_state.battle_log.append(f"你成功击败了{monster.name}！")

    # 获得经验
    exp_messages = player.gain_experience(monster.experience_reward)
    st.session_state.battle_log.extend(exp_messages)
    st.session_state.battle_log.append(f"获得了{monster.experience_reward}点经验值！")

    # 获得金币
    player.gold += monster.gold_reward
    st.session_state.battle_log.append(f"获得了{monster.gold_reward}枚金币！")

    # 生成战利品
    equipment, potions = generate_loot()
    if equipment:
        player.equipment_inventory.append(equipment)
        st.session_state.battle_log.append(f"获得了装备: {equipment.name}！")
    for potion_name, quantity in potions:
        st.session_state.battle_log.append(f"获得了{quantity}瓶{potion_name}！")

    # 重置技能冷却和战斗回合
    player.skill_cooldown = 0
    player.battle_turn = 0

    # 清除战斗状态
    st.session_state.current_monster = None
    st.session_state.current_view = "main"


def show_create_view():
    """角色创建界面"""
    st.title("修仙打怪升级游戏")
    st.header("创建角色")

    col1, col2 = st.columns([1, 1])
    with col1:
        name = st.text_input("请输入角色名", placeholder="输入你的修仙者名号", value="修仙者")

        if st.button("开始新游戏", use_container_width=True):
            if name and len(name.strip()) > 0:
                st.session_state.player = Player(name.strip())
                st.session_state.current_view = "main"
                st.success(f"角色 {name.strip()} 创建成功！")
                time.sleep(1)
                st.rerun()
            else:
                st.error("请输入有效的角色名")

        # 加载存档按钮
        if st.button("加载存档", use_container_width=True):
            # 先尝试从localStorage加载最新存档
            st.session_state.save_data = load_game_from_localstorage()

            if st.session_state.save_data:
                try:
                    st.session_state.player = Player.from_dict(st.session_state.save_data["player"])
                    st.session_state.current_area = st.session_state.save_data["current_area"]
                    monster_data = st.session_state.save_data.get("current_monster")
                    if monster_data:
                        st.session_state.current_monster = Monster.from_dict(monster_data)
                    st.session_state.current_view = "main"
                    st.success("存档加载成功！")
                    time.sleep(1)
                    st.rerun()
                except:
                    st.error("存档损坏，无法加载")
            else:
                st.warning("没有找到存档数据")

    with col2:
        st.image("https://picsum.photos/id/237/400/300", use_container_width=True,
                 caption="踏上修仙之路，斩妖除魔，突破境界")


def show_main_view():
    """主界面：显示角色信息和核心操作"""
    st.title("修仙打怪升级游戏")

    if not st.session_state.player:
        st.session_state.current_view = "create"
        st.rerun()

    player = st.session_state.player
    player.clean_expired_buffs()

    # 角色信息卡片
    st.subheader("角色信息")
    st.markdown('<div class="status-card">', unsafe_allow_html=True)
    st.text(str(player))
    st.markdown('</div>', unsafe_allow_html=True)

    # 区域信息
    st.subheader(f"当前区域：{st.session_state.current_area}")
    st.write("在这个区域中，你可能会遇到各种怪物，击败它们可以获得经验、金币、装备和药水！")

    # 操作按钮（探索和区域移动）
    col1, col2 = st.columns(2)
    with col1:
        if st.button("探索区域", use_container_width=True):
            # 50%概率遇到敌人
            if random.random() < 0.5:
                st.session_state.current_monster = generate_monster()
                st.session_state.battle_log.append(
                    f"你在第{st.session_state.current_area}区域遇到了{st.session_state.current_monster.name}！")
                st.session_state.current_view = "battle"
                st.rerun()
            else:
                # 没遇到敌人，可能获得装备或药水
                found_items = []

                # 生成装备的概率
                if random.random() < 0.2:  # 20%概率获得装备
                    equipment = generate_equipment()
                    player.equipment_inventory.append(equipment)
                    found_items.append(f"发现了装备：{equipment.name}")

                # 生成药水的概率
                if random.random() < 0.1:  # 10%概率获得药水
                    potion_types = [item for item in SHOP_ITEMS if item["effect"] != "max_hp"]
                    potion = random.choice(potion_types)
                    quantity = random.randint(1, 2)
                    player.inventory[potion["name"]] += quantity
                    found_items.append(f"发现了{quantity}瓶{potion['name']}")

                if found_items:
                    for item in found_items:
                        st.session_state.battle_log.append(item)
                    st.success("探索发现了一些物品！")
                else:
                    st.session_state.battle_log.append("探索了一番，没有发现任何东西")
                    st.info("探索了一番，没有发现任何东西")
                time.sleep(1)
                st.rerun()

    with col2:
        if st.button("前往下一个区域", use_container_width=True):
            # 检查是否是区域守护者且未被击败
            if (st.session_state.current_monster and
                    st.session_state.current_monster.is_guardian and
                    st.session_state.current_monster.is_alive()):
                st.error("此区域的守护者未被击败，无法前往下一个区域！")
            else:
                st.session_state.current_area += 1
                st.session_state.battle_log.append(f"成功进入第{st.session_state.current_area}区域！这里的怪物更强大了！")
                st.success(f"已前往区域 {st.session_state.current_area}！")
                time.sleep(1)
                st.rerun()

    # 快速使用药水
    st.subheader("快速使用")
    quick_items = [item for item in SHOP_ITEMS if item["effect"] in ["heal", "full_heal"]]
    cols = st.columns(2)
    for i, item in enumerate(quick_items):
        if player.inventory.get(item["name"], 0) > 0:
            with cols[i % 2]:
                if st.button(f"使用 {item['name']}", use_container_width=True):
                    success, msg = player.use_item(item["name"])
                    st.session_state.battle_log.append(msg)
                    st.success(msg)
                    time.sleep(1)
                    st.rerun()

    # 功能按钮
    st.subheader("功能菜单")
    col3, col4, col5 = st.columns(3)
    with col3:
        if st.button("商店", use_container_width=True):
            st.session_state.current_view = "shop"
            st.rerun()
    with col4:
        if st.button("背包", use_container_width=True):
            st.session_state.current_view = "backpack"
            st.rerun()
    with col5:
        if st.button("保存游戏", use_container_width=True):
            save_game()
            st.success("游戏已保存！")

    # 战斗日志
    st.subheader("事件日志")
    # 先安全获取 battle_log，确保是列表
    logs = st.session_state.get("battle_log", [])
    # 取最后10条并反转
    last_10_logs = logs[-10:]
    reversed_logs = reversed(last_10_logs)
    # 渲染文本区域
    st.text_area("", value="\n".join(reversed_logs),
                 disabled=True)


def show_battle_view():
    """战斗界面：显示怪物信息和战斗操作"""
    st.title("战斗中")

    if not st.session_state.player:
        st.session_state.current_view = "create"
        st.rerun()

    player = st.session_state.player
    monster = st.session_state.current_monster

    if not monster or not monster.is_alive():
        st.write("战斗已结束，返回主界面继续探索吧！")
        if st.button("返回主界面", use_container_width=True):
            st.session_state.current_view = "main"
            st.rerun()
        return

    # 显示双方状态
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("你的状态")
        st.markdown('<div class="status-card">', unsafe_allow_html=True)
        st.text(f"生命值: {player.health}/{player.get_max_health()}")
        st.text(f"攻击力: {player.get_total_attack()}")
        st.text(f"防御力: {player.get_total_defense()}")
        st.text(f"暴击率: {int(player.get_critical_rate() * 100)}%")
        if player.skill_cooldown > 0:
            st.text(f"技能冷却: {player.skill_cooldown}回合")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.subheader(f"敌人: {monster.name}")
        st.markdown('<div class="status-card">', unsafe_allow_html=True)
        st.text(f"生命值: {monster.health}/{monster.base_health}")
        st.text(f"攻击力: {monster.attack}")
        st.text(f"防御力: {monster.defense}")
        st.text(f"伤害类型: {', '.join(monster.damage_types) if monster.damage_types else '无'}")
        st.markdown('</div>', unsafe_allow_html=True)

    # 战斗日志
    st.subheader("战斗日志")
    st.text_area("", value="\n".join(st.session_state.battle_log),
                 disabled=True)

    # 战斗操作按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("普通攻击", use_container_width=True):
            process_attack()
            st.rerun()
    with col2:
        # 技能攻击按钮（根据冷却状态禁用）
        skill_disabled = player.skill_cooldown > 0
        if st.button("技能攻击", use_container_width=True, disabled=skill_disabled):
            if not skill_disabled:
                process_skill_attack()
                st.rerun()

    # 使用药水和逃跑按钮
    col3, col4 = st.columns(2)
    with col3:
        if st.button("使用药水", use_container_width=True):
            show_battle_items()
            return
    with col4:
        if st.button("尝试逃跑", use_container_width=True):
            # 考虑敏捷加成影响逃跑成功率
            escape_chance = 0.5
            current_time = time.time()
            if player.buffs["agility_boost"]["end_time"] and current_time < player.buffs["agility_boost"]["end_time"]:
                escape_chance += 0.2  # 敏捷加成提高逃跑成功率

            if random.random() < escape_chance:  # 基础50%逃跑成功率
                st.session_state.battle_log.append("你成功逃脱了！")
                st.session_state.current_monster = None
                st.session_state.current_view = "main"
            else:
                st.session_state.battle_log.append("逃跑失败，被怪物反击！")
                # 怪物攻击
                damage = max(1, monster.attack - player.get_total_defense() // 3)
                player.health = player.health - damage  # 允许生命值变为负数
                st.session_state.battle_log.append(f"{monster.name}对你造成了{damage}点伤害！")

                if not player.is_alive():
                    st.session_state.battle_log.append("你被击败了！")
                    st.session_state.current_monster = None
                    st.session_state.current_view = "main"

            st.rerun()


def show_battle_items():
    """战斗中显示可用物品"""
    st.subheader("选择要使用的物品")
    player = st.session_state.player

    # 按类别分组显示药水
    buff_items = [item for item in SHOP_ITEMS if item["effect"] not in ["max_hp", "heal", "full_heal"]]
    heal_items = [item for item in SHOP_ITEMS if item["effect"] in ["heal", "full_heal"]]

    st.write("恢复类:")
    cols = st.columns(2)
    for i, item in enumerate(heal_items):
        if player.inventory.get(item["name"], 0) > 0:
            with cols[i % 2]:
                if st.button(f"{item['name']} (x{player.inventory[item['name']]}) - {item['description']}",
                             use_container_width=True):
                    success, msg = player.use_item(item["name"])
                    st.session_state.battle_log.append(msg)
                    st.success(msg)
                    time.sleep(1)
                    st.rerun()

    st.write("增益类:")
    cols = st.columns(2)
    for i, item in enumerate(buff_items):
        if player.inventory.get(item["name"], 0) > 0:
            with cols[i % 2]:
                if st.button(f"{item['name']} (x{player.inventory[item['name']]}) - {item['description']}",
                             use_container_width=True):
                    success, msg = player.use_item(item["name"])
                    st.session_state.battle_log.append(msg)
                    st.success(msg)
                    time.sleep(1)
                    st.rerun()

    if st.button("返回战斗", use_container_width=True):
        st.rerun()


def show_shop_view():
    """商店界面：显示可购买的物品"""
    st.title("修仙商店")

    if not st.session_state.player:
        st.session_state.current_view = "create"
        st.rerun()

    player = st.session_state.player

    st.subheader(f"当前金币: {player.gold}")

    # 返回主界面按钮
    if st.button("返回主界面", use_container_width=True):
        st.session_state.current_view = "main"
        st.rerun()

    # 按类别分组显示商品
    st.subheader("恢复类")
    recovery_items = [item for item in SHOP_ITEMS if item["effect"] in ["max_hp", "heal", "full_heal"]]
    cols = st.columns(2)
    for i, item in enumerate(recovery_items):
        with cols[i % 2]:
            st.markdown(f"**{item['name']}** - {item['price']}金币")
            st.write(item['description'])
            if st.button(f"购买 {item['name']}", use_container_width=True):
                if player.gold >= item['price']:
                    player.gold -= item['price']
                    player.inventory[item['name']] += 1
                    st.success(f"成功购买 {item['name']}！")
                    st.session_state.battle_log.append(f"购买了{item['name']}，花费了{item['price']}金币")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("金币不足，无法购买！")
            st.write("---")

    st.subheader("战斗增益类")
    battle_items = [item for item in SHOP_ITEMS if item["effect"] in ["attack_boost", "defense_boost", "crit_boost",
                                                                      "agility_boost", "skill_haste", "dodge_boost",
                                                                      "life_steal", "damage_reduction",
                                                                      "damage_reflect",
                                                                      "crit_damage_boost", "all_stats"]]
    cols = st.columns(2)
    for i, item in enumerate(battle_items):
        with cols[i % 2]:
            st.markdown(f"**{item['name']}** - {item['price']}金币")
            st.write(item['description'])
            if st.button(f"购买 {item['name']}", use_container_width=True):
                if player.gold >= item['price']:
                    player.gold -= item['price']
                    player.inventory[item['name']] += 1
                    st.success(f"成功购买 {item['name']}！")
                    st.session_state.battle_log.append(f"购买了{item['name']}，花费了{item['price']}金币")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("金币不足，无法购买！")
            st.write("---")

    st.subheader("元素与特殊效果类")
    element_items = [item for item in SHOP_ITEMS if item["effect"] in ["mana_shield", "element_resist",
                                                                       "element_penetration", "shield_boost",
                                                                       "fire_damage", "frost_damage", "thunder_damage",
                                                                       "poison_resist", "stun_resist", "invisibility",
                                                                       "exp_boost", "shield_duration"]]
    cols = st.columns(2)
    for i, item in enumerate(element_items):
        with cols[i % 2]:
            st.markdown(f"**{item['name']}** - {item['price']}金币")
            st.write(item['description'])
            if st.button(f"购买 {item['name']}", use_container_width=True):
                if player.gold >= item['price']:
                    player.gold -= item['price']
                    player.inventory[item['name']] += 1
                    st.success(f"成功购买 {item['name']}！")
                    st.session_state.battle_log.append(f"购买了{item['name']}，花费了{item['price']}金币")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("金币不足，无法购买！")
            st.write("---")


def show_backpack_view():
    """背包界面：显示物品和装备"""
    st.title("背包")

    if not st.session_state.player:
        st.session_state.current_view = "create"
        st.rerun()

    player = st.session_state.player

    # 返回主界面按钮
    if st.button("返回主界面", use_container_width=True, key="back_to_main_from_backpack"):
        st.session_state.current_view = "main"
        st.rerun()

    # 物品标签页和装备标签页
    tab1, tab2 = st.tabs(["消耗品", "装备"])

    with tab1:
        st.subheader("消耗品")
        # 按类别分组显示物品
        items_by_type = {}
        for item in SHOP_ITEMS:
            if player.inventory.get(item["name"], 0) > 0:
                if item["effect"] in ["max_hp", "heal", "full_heal"]:
                    category = "恢复类"
                elif item["effect"] in ["attack_boost", "defense_boost", "crit_boost",
                                        "agility_boost", "skill_haste", "dodge_boost",
                                        "life_steal", "damage_reduction", "damage_reflect",
                                        "crit_damage_boost", "all_stats"]:
                    category = "战斗增益类"
                else:
                    category = "元素与特殊效果类"

                if category not in items_by_type:
                    items_by_type[category] = []
                items_by_type[category].append(item)

        for category, items in items_by_type.items():
            st.markdown(f"### {category}")
            cols = st.columns(2)
            for i, item in enumerate(items):
                if player.inventory.get(item["name"], 0) > 0:
                    with cols[i % 2]:
                        st.markdown(f"**{item['name']}** (x{player.inventory[item['name']]})")
                        st.write(item['description'])
                        if st.button(f"使用 {item['name']}", use_container_width=True, key=f"use_{item['name']}_{i}"):
                            success, msg = player.use_item(item["name"])
                            st.success(msg)
                            st.session_state.battle_log.append(msg)
                            time.sleep(1)
                            st.rerun()
                    st.write("---")

        # 如果没有物品
        if not items_by_type:
            st.info("你的背包中没有消耗品")

    with tab2:
        st.subheader("已装备")
        # 显示当前装备
        for eq_type in EQUIPMENT_TYPES:
            eq = player.equipped.get(eq_type)
            st.markdown(f"**{eq_type}**")
            if eq:
                st.markdown('<div class="status-card">', unsafe_allow_html=True)
                st.text(str(eq))
                if st.button(f"卸下 {eq.name}", use_container_width=True, key=f"unequip_{eq_type}"):
                    # 卸下装备，放入背包
                    unequipped = player.equip_item(None)
                    player.equipment_inventory.append(unequipped)
                    st.success(f"已卸下 {eq.name}")
                    st.session_state.battle_log.append(f"卸下了{eq.name}")
                    time.sleep(1)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.write("未装备")
            st.write("---")

        st.subheader("装备背包")
        # 显示背包中的装备
        if player.equipment_inventory:
            cols = st.columns(1)
            for i, eq in enumerate(player.equipment_inventory):
                with cols[i % 1]:
                    st.markdown(f"**{eq.name}** (等级: {eq.level})")
                    st.markdown('<div class="status-card">', unsafe_allow_html=True)
                    st.text(str(eq))
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(f"装备 {eq.name}", use_container_width=True, key=f"equip_{i}"):
                            # 装备物品，替换当前装备
                            current_eq = player.equip_item(eq)
                            # 从背包中移除
                            player.equipment_inventory.pop(i)
                            # 如果有被替换的装备，放入背包
                            if current_eq:
                                player.equipment_inventory.append(current_eq)
                            st.success(f"已装备 {eq.name}")
                            st.session_state.battle_log.append(f"装备了{eq.name}")
                            time.sleep(1)
                            st.rerun()
                    with col_b:
                        sell_price = eq.get_sell_price()
                        if st.button(f"出售 (${sell_price})", use_container_width=True, key=f"sell_{i}"):
                            # 出售装备
                            player.gold += sell_price
                            player.equipment_inventory.pop(i)
                            st.success(f"已出售 {eq.name}，获得 {sell_price} 金币")
                            st.session_state.battle_log.append(f"出售了{eq.name}，获得{sell_price}金币")
                            time.sleep(1)
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                st.write("---")
        else:
            st.info("你的背包中没有备用装备")


def main():
    # 初始化游戏并显示对应界面
    init_game()

    if st.session_state.current_view == "create":
        show_create_view()
    elif st.session_state.current_view == "main":
        show_main_view()
    elif st.session_state.current_view == "battle":
        show_battle_view()
    elif st.session_state.current_view == "shop":
        show_shop_view()
    elif st.session_state.current_view == "backpack":
        show_backpack_view()


if __name__ == "__main__":
    main()
