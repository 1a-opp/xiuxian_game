import streamlit as st
import random
import time
import json
import os
from datetime import datetime

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
     "price": 550, "description": "180秒内增加20%暴击率"}
]


class Equipment:
    def __init__(self, name, equip_type, level, attack_bonus=0, defense_bonus=0, hp_bonus=0):
        self.name = name
        self.type = equip_type
        self.level = level
        self.attack_bonus = attack_bonus
        self.defense_bonus = defense_bonus
        self.hp_bonus = hp_bonus

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "level": self.level,
            "attack_bonus": self.attack_bonus,
            "defense_bonus": self.defense_bonus,
            "hp_bonus": self.hp_bonus
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["name"],
            data["type"],
            data["level"],
            data["attack_bonus"],
            data["defense_bonus"],
            data["hp_bonus"]
        )

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
        return f"{self.name} (等级: {self.level}) - 攻击+{self.attack_bonus}, 防御+{self.defense_bonus}, 生命+{self.hp_bonus}"


class Player:
    def __init__(self, name):
        self.name = name
        self.realm_index = 0  # 当前境界索引
        self.realm_level = 1  # 境界内等级
        self.base_health = 100
        self.health = self.base_health
        self.base_attack = 10
        self.base_defense = 5
        self.critical_rate = 0.1  # 10%暴击率
        self.critical_damage = 1.5  # 150%暴击伤害

        self.experience = 0
        self.experience_to_next_level = self.calculate_exp_to_next_level()

        self.gold = 1000
        self.inventory = {item["name"]: 0 for item in SHOP_ITEMS}

        # 装备系统
        self.equipped = {eq_type: None for eq_type in EQUIPMENT_TYPES}
        self.equipment_inventory = []

        # 状态增益
        self.buffs = {
            "attack_boost": {"value": 0, "end_time": None},
            "defense_boost": {"value": 0, "end_time": None},
            "crit_boost": {"value": 0, "end_time": None}
        }

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
        return int(total)

    def get_max_health(self):
        total = self.base_health * self.get_current_realm()["hp_multiplier"]
        # 加上装备加成
        for eq in self.equipped.values():
            if eq:
                total += eq.hp_bonus
        return int(total)

    def get_critical_rate(self):
        rate = self.critical_rate
        current_time = time.time()
        if self.buffs["crit_boost"]["end_time"] and current_time < self.buffs["crit_boost"]["end_time"]:
            rate += self.buffs["crit_boost"]["value"]
        return min(rate, 1.0)  # 最大100%暴击率

    def clean_expired_buffs(self):
        """清理过期的增益效果"""
        current_time = time.time()
        for buff_type in self.buffs:
            if self.buffs[buff_type]["end_time"] and current_time >= self.buffs[buff_type]["end_time"]:
                self.buffs[buff_type] = {"value": 0, "end_time": None}

    def level_up(self):
        # 提升境界内等级
        self.realm_level += 1
        self.experience -= self.experience_to_next_level

        # 提升基础属性
        self.base_health += 20
        self.base_attack += 5
        self.base_defense += 3

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

            # 大境界提升，属性大幅提升
            self.base_health = int(self.base_health * 1.5)
            self.base_attack = int(self.base_attack * 1.8)
            self.base_defense = int(self.base_defense * 1.6)

            # 恢复全部生命值
            self.health = self.get_max_health()

            # 计算下一级所需经验
            self.experience = 0
            self.experience_to_next_level = self.calculate_exp_to_next_level()

            return f"恭喜！{self.name}突破到了{self.get_current_realm()['name']}！属性大幅提升！"
        else:
            return "已经达到最高境界！"

    def gain_experience(self, amount):
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

        for item in SHOP_ITEMS:
            if item["name"] == item_name:
                if item["effect"] == "max_hp":
                    self.base_health = int(self.base_health * (1 + item["value"]))
                    self.health = min(self.health + int(self.get_max_health() * item["value"]), self.get_max_health())
                    return True, f"使用了{item_name}，生命上限永久增加{int(item['value'] * 100)}%！"

                elif item["effect"] == "heal":
                    heal_amount = int(self.get_max_health() * item["value"])
                    self.health = min(self.health + heal_amount, self.get_max_health())
                    return True, f"使用了{item_name}，恢复了{heal_amount}点生命值！"

                elif item["effect"] == "full_heal":
                    self.health = self.get_max_health()
                    return True, f"使用了{item_name}，生命值完全恢复！"

                elif item["effect"] in ["attack_boost", "defense_boost", "crit_boost"]:
                    end_time = time.time() + item["duration"]
                    self.buffs[item["effect"]] = {
                        "value": item["value"],
                        "end_time": end_time
                    }
                    return True, f"使用了{item_name}，{int(item['value'] * 100)}%{item['description'].split('增加')[1]}，持续{int(item['duration'])}秒！"

        return False, "未知物品"

    def equip_item(self, equipment):
        # 卸下当前装备
        current = self.equipped[equipment.type]
        self.equipped[equipment.type] = equipment
        return current

    def is_alive(self):
        return self.health > 0

    def to_dict(self):
        return {
            "name": self.name,
            "realm_index": self.realm_index,
            "realm_level": self.realm_level,
            "base_health": self.base_health,
            "health": self.health,
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
            "buffs": self.buffs
        }

    @classmethod
    def from_dict(cls, data):
        player = cls(data["name"])
        player.realm_index = data["realm_index"]
        player.realm_level = data["realm_level"]
        player.base_health = data["base_health"]
        player.health = data["health"]
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
            "crit_boost": {"value": 0, "end_time": None}
        })
        player.clean_expired_buffs()

        return player

    def __str__(self):
        # 检查并清理过期增益
        self.clean_expired_buffs()

        # 构建增益信息字符串
        buffs_info = []
        current_time = time.time()

        if self.buffs["attack_boost"]["end_time"] and current_time < self.buffs["attack_boost"]["end_time"]:
            remaining = int(self.buffs["attack_boost"]["end_time"] - current_time)
            buffs_info.append(f"攻击提升+{int(self.buffs['attack_boost']['value'] * 100)}% ({remaining}秒)")

        if self.buffs["defense_boost"]["end_time"] and current_time < self.buffs["defense_boost"]["end_time"]:
            remaining = int(self.buffs["defense_boost"]["end_time"] - current_time)
            buffs_info.append(f"防御提升+{int(self.buffs['defense_boost']['value'] * 100)}% ({remaining}秒)")

        if self.buffs["crit_boost"]["end_time"] and current_time < self.buffs["crit_boost"]["end_time"]:
            remaining = int(self.buffs["crit_boost"]["end_time"] - current_time)
            buffs_info.append(f"暴击提升+{int(self.buffs['crit_boost']['value'] * 100)}% ({remaining}秒)")

        buffs_text = "\n".join(buffs_info) if buffs_info else "无"

        return f"{self.name} - {self.get_current_realm()['name']}{self.realm_level}级\n" + \
            f"生命值: {self.health}/{self.get_max_health()}\n" + \
            f"攻击力: {self.get_total_attack()}\n" + \
            f"防御力: {self.get_total_defense()}\n" + \
            f"暴击率: {int(self.get_critical_rate() * 100)}%\n" + \
            f"经验值: {self.experience}/{self.experience_to_next_level}\n" + \
            f"金币: {self.gold}\n" + \
            f"当前增益:\n{buffs_text}"


class Monster:
    def __init__(self, name, category, species, level):
        self.name = name
        self.category = category  # 基础种、精英种等
        self.species = species  # 仙术使、机械种等
        self.level = level

        # 根据类别和等级设置属性
        category_multipliers = {
            "基础种": 1.0,
            "精英种": 1.8,
            "首领种": 3.0,
            "变异种": 4.5,
            "BOSS级种": 7.0
        }

        multiplier = category_multipliers[category]

        self.base_health = int(80 * multiplier * (level ** 0.8))
        self.health = self.base_health
        self.attack = int(8 * multiplier * (level ** 0.85))
        self.defense = int(3 * multiplier * (level ** 0.75))

        # 设置经验和金币奖励
        self.experience_reward = int(50 * multiplier * (level ** 0.9))
        self.gold_reward = int(20 * multiplier * (level ** 0.8))

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

    def __str__(self):
        return f"{self.name} ({self.category} - {self.species}) - 等级: {self.level}\n" + \
            f"生命值: {self.health}/{self.base_health}\n" + \
            f"攻击力: {self.attack}\n" + \
            f"防御力: {self.defense}"


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
        st.session_state.save_data = None


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
            if st.session_state.save_data:
                try:
                    st.session_state.player = Player.from_dict(st.session_state.save_data["player"])
                    st.session_state.current_area = st.session_state.save_data["current_area"]
                    st.session_state.current_view = "main"
                    st.success("存档加载成功！")
                    time.sleep(1)
                    st.rerun()
                except:
                    st.error("存档损坏，无法加载")
            else:
                st.warning("没有找到存档数据")

    with col2:
        st.image("https://picsum.photos/id/237/400/300", use_column_width=True,
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
    st.write("在这个区域中，你可能会遇到各种怪物，击败它们可以获得经验、金币和装备！")

    # 操作按钮（探索和区域移动）
    col1, col2 = st.columns(2)
    with col1:
        if st.button("探索区域", use_container_width=True):
            if player.health <= 0:
                st.error("你的生命值已耗尽，请先恢复！")
            else:
                monster = generate_monster()
                st.session_state.current_monster = monster
                st.session_state.battle_log = [f"你在区域 {st.session_state.current_area} 遇到了 {monster.name}！"]
                st.session_state.current_view = "battle"
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
    st.text_area("", value="\n".join(reversed(st.session_state.battle_log[-10:])),
                 disabled=True, use_container_width=True)


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
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.subheader(f"敌人: {monster.name}")
        st.markdown('<div class="status-card">', unsafe_allow_html=True)
        st.text(f"生命值: {monster.health}/{monster.base_health}")
        st.text(f"攻击力: {monster.attack}")
        st.text(f"防御力: {monster.defense}")
        st.markdown('</div>', unsafe_allow_html=True)

    # 战斗日志
    st.subheader("战斗日志")
    st.text_area("", value="\n".join(st.session_state.battle_log),
                 disabled=True, use_container_width=True)

    # 战斗操作按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("普通攻击", use_container_width=True):
            process_attack()
            st.rerun()
    with col2:
        if st.button("使用药水", use_container_width=True):
            show_battle_items()
            return

    # 逃跑按钮
    if st.button("尝试逃跑", use_container_width=True):
        if random.random() < 0.5:  # 50%逃跑成功率
            st.session_state.battle_log.append("你成功逃脱了！")
            st.session_state.current_monster = None
            st.session_state.current_view = "main"
        else:
            st.session_state.battle_log.append("逃跑失败，被怪物反击！")
            # 怪物攻击
            damage = max(1, monster.attack - player.get_total_defense() // 3)
            player.health -= damage
            st.session_state.battle_log.append(f"{monster.name}对你造成了{damage}点伤害！")

            if not player.is_alive():
                st.session_state.battle_log.append("你被击败了！")
                st.session_state.current_monster = None
                st.session_state.current_view = "main"

        st.rerun()


def show_battle_items():
    """战斗中使用物品界面"""
    st.title("战斗中使用物品")

    player = st.session_state.player

    if st.button("返回战斗", use_container_width=True):
        st.rerun()

    st.subheader("可用物品")
    has_items = False
    for item in SHOP_ITEMS:
        count = player.inventory.get(item["name"], 0)
        if count > 0:
            has_items = True
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{item['name']}**：{item['description']}")
            with col2:
                st.write(f"数量: {count}")
            with col3:
                if st.button(f"使用", key=f"battle_use_{item['name']}", use_container_width=True):
                    success, msg = player.use_item(item["name"])
                    st.session_state.battle_log.append(msg)
                    st.rerun()

    if not has_items:
        st.info("背包中没有可用物品")


def process_attack():
    """处理攻击逻辑"""
    player = st.session_state.player
    monster = st.session_state.current_monster

    # 检查状态
    if not player.is_alive():
        st.session_state.battle_log.append("你已经失去战斗能力！")
        return

    if not monster.is_alive():
        return

    # 怪物使用特殊能力
    special_ability = monster.use_special_ability()
    special_attack = False
    if special_ability:
        st.session_state.battle_log.append(special_ability["message"])
        if special_ability["effect"] == "attack":
            monster.attack = int(monster.attack * special_ability["value"])
        elif special_ability["effect"] == "defense":
            monster.defense = int(monster.defense * special_ability["value"])
        elif special_ability["effect"] == "leech":
            heal_amount = int(monster.base_health * special_ability["value"])
            monster.health = min(monster.health + heal_amount, monster.base_health)
            st.session_state.battle_log.append(f"{monster.name}恢复了{heal_amount}点生命值！")
        elif special_ability["effect"] == "crit":
            special_attack = True

    # 玩家攻击
    damage = max(1, player.get_total_attack() - monster.defense // 2)
    if random.random() < player.get_critical_rate():
        damage = int(damage * player.critical_damage)
        st.session_state.battle_log.append(f"你对 {monster.name} 造成了 {damage} 点暴击伤害！")
    else:
        st.session_state.battle_log.append(f"你对 {monster.name} 造成了 {damage} 点伤害！")
    monster.health -= damage

    # 怪物死亡判定
    if not monster.is_alive():
        st.session_state.battle_log.append(f"你击败了 {monster.name}！")
        player.gold += monster.gold_reward
        st.session_state.battle_log.append(f"获得了{monster.gold_reward}金币！")

        exp_messages = player.gain_experience(monster.experience_reward)
        st.session_state.battle_log.extend(exp_messages)

        # 有概率获得装备
        if random.random() < 0.3 + (monster.level * 0.02):
            equipment = generate_equipment()
            if equipment:
                player.equipment_inventory.append(equipment)
                st.session_state.battle_log.append(f"获得了装备: {equipment.name}！")

        st.session_state.current_monster = None
        return

    # 怪物反击
    if special_attack:
        damage = int(monster.attack * 2)  # 要害打击必定暴击
        st.session_state.battle_log.append(f"{monster.name}对你造成了{damage}点暴击伤害！")
    else:
        damage = max(1, monster.attack - player.get_total_defense() // 3)
        st.session_state.battle_log.append(f"{monster.name}对你造成了{damage}点伤害！")

    player.health -= damage

    # 玩家死亡判定
    if not player.is_alive():
        st.session_state.battle_log.append("你被击败了！损失部分金币！")
        # 死亡惩罚：损失10%金币
        lose_gold = max(10, int(player.gold * 0.1))
        player.gold = max(0, player.gold - lose_gold)
        st.session_state.battle_log.append(f"损失了{lose_gold}金币！")
        # 复活：恢复30%生命值
        player.health = int(player.get_max_health() * 0.3)
        st.session_state.current_monster = None


def show_shop_view():
    """商店界面"""
    st.title("修仙商店")

    if not st.session_state.player:
        st.session_state.current_view = "create"
        st.rerun()

    player = st.session_state.player

    # 返回按钮
    if st.button("返回主界面", use_container_width=True):
        st.session_state.current_view = "main"
        st.rerun()

    st.subheader(f"当前金币：{player.gold}")

    for item in SHOP_ITEMS:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{item['name']}**：{item['description']}")
            with col2:
                st.write(f"价格: {item['price']}")
            with col3:
                if st.button(f"购买", key=f"buy_{item['name']}", use_container_width=True):
                    if player.gold >= item["price"]:
                        player.gold -= item["price"]
                        player.inventory[item["name"]] += 1
                        st.success(f"成功购买 {item['name']}！")
                        st.session_state.battle_log.append(f"购买了{item['name']}")
                    else:
                        st.error("金币不足，无法购买！")
                    time.sleep(1)
                    st.rerun()


def show_backpack_view():
    """背包界面"""
    st.title("背包")

    if not st.session_state.player:
        st.session_state.current_view = "create"
        st.rerun()

    player = st.session_state.player

    # 返回按钮
    if st.button("返回主界面", use_container_width=True):
        st.session_state.current_view = "main"
        st.rerun()

    st.subheader(f"当前金币：{player.gold}")

    # 标签页切换
    tab1, tab2 = st.tabs(["装备", "药水"])

    with tab1:
        # 一键售卖按钮
        if st.button("一键售卖劣质装备", use_container_width=True):
            inferior_indices = []
            for idx, equipment in enumerate(player.equipment_inventory):
                current_equipped = player.equipped.get(equipment.type)
                if equipment.is_inferior_to(current_equipped):
                    inferior_indices.append(idx)

            if not inferior_indices:
                st.info("没有劣质装备可出售")
            else:
                # 按索引从大到小排序，避免删除时索引变化
                inferior_indices.sort(reverse=True)
                total_gold = 0
                sold_items = []

                for idx in inferior_indices:
                    equipment = player.equipment_inventory[idx]
                    price = equipment.get_sell_price()
                    total_gold += price
                    sold_items.append(equipment.name)
                    del player.equipment_inventory[idx]

                player.gold += total_gold
                st.success(f"成功出售{len(sold_items)}件装备，获得{total_gold}金币！")
                st.session_state.battle_log.append(f"出售了{len(sold_items)}件装备，获得{total_gold}金币")
                time.sleep(1)
                st.rerun()

        st.subheader("已装备")
        for eq_type, equipment in player.equipped.items():
            if equipment:
                st.text(
                    f"{eq_type}: {equipment.name} (攻+{equipment.attack_bonus}, 防+{equipment.defense_bonus}, 血+{equipment.hp_bonus})")
            else:
                st.text(f"{eq_type}: 未装备")

        st.subheader("装备背包")
        if not player.equipment_inventory:
            st.info("背包中没有装备")
        else:
            for i, equipment in enumerate(player.equipment_inventory):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(
                        f"{equipment.name} (等级: {equipment.level}) - 攻+{equipment.attack_bonus}, 防+{equipment.defense_bonus}, 血+{equipment.hp_bonus}")
                with col2:
                    if st.button("装备", key=f"equip_{i}", use_container_width=True):
                        current_equipped = player.equip_item(equipment)
                        del player.equipment_inventory[i]
                        if current_equipped:
                            player.equipment_inventory.append(current_equipped)
                        st.success(f"已装备{equipment.name}！")
                        st.session_state.battle_log.append(f"装备了{equipment.name}")
                        time.sleep(1)
                        st.rerun()
                with col3:
                    price = equipment.get_sell_price()
                    if st.button(f"出售 (¥{price})", key=f"sell_{i}", use_container_width=True):
                        player.gold += price
                        del player.equipment_inventory[i]
                        st.success(f"成功出售{equipment.name}，获得{price}金币！")
                        st.session_state.battle_log.append(f"出售了{equipment.name}，获得{price}金币")
                        time.sleep(1)
                        st.rerun()

    with tab2:
        st.subheader("药水列表")
        has_items = False
        for item in SHOP_ITEMS:
            count = player.inventory.get(item["name"], 0)
            if count > 0:
                has_items = True
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{item['name']}**：{item['description']}")
                with col2:
                    st.write(f"数量: {count}")
                with col3:
                    if st.button(f"使用", key=f"use_{item['name']}", use_container_width=True):
                        success, msg = player.use_item(item["name"])
                        if success:
                            st.success(msg)
                            st.session_state.battle_log.append(msg)
                        else:
                            st.error(msg)
                        time.sleep(1)
                        st.rerun()

        if not has_items:
            st.info("背包中没有药水")


def save_game():
    """保存游戏数据"""
    if 'player' in st.session_state and st.session_state.player:
        data = {
            "player": st.session_state.player.to_dict(),
            "current_area": st.session_state.current_area,
            "save_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.save_data = data
        return True
    return False


# 主程序入口
if __name__ == "__main__":
    init_game()

    # 根据当前视图显示对应界面
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
