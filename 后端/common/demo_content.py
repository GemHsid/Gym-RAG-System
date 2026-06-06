from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.utils import timezone


GYM_CONTENT = {
    "gym_name": "美式铁馆智能健身馆",
    "subtitle": "24小时自助健身空间",
    "business_hours": "全年无休，24小时营业",
    "address": "深圳市南山区打石二路1号负一楼",
    "distance_text": "距你约 1.98km",
    "tags": [
        "营业中|7*24小时营业",
        "力量区/有氧区/自由训练区",
        "课程预约/购卡/AI咨询一体化",
    ],
    "selling_points": [
        "24小时营业，支持自助进馆",
        "力量区、有氧区、自由训练区分区清晰",
        "支持课程预约、会员购卡、AI咨询一体化体验",
    ],
    "membership_recommendation": "新用户限时特惠，低门槛开卡，随时开启训练计划",
    "banner_image": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=2070&auto=format&fit=crop",
    "banner_map": {
        "brand": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=2070&auto=format&fit=crop",
        "store": "https://images.unsplash.com/photo-1596357395217-80de13130e92?q=80&w=2071&auto=format&fit=crop",
        "rest": "https://images.unsplash.com/photo-1554284126-aa88f22d8b74?q=80&w=1988&auto=format&fit=crop",
        "locker": "https://images.unsplash.com/photo-1577221084712-45b0445d2b00",
    },
    "environment_images": [
        "gym-env-01.jpg",
        "gym-env-02.jpg",
    ],
    "equipment_images": [
        "gym-equipment-01.jpg",
        "gym-equipment-02.jpg",
    ],
    "nav_items": [
        {
            "name": "到店指引",
            "path": "/pages/profile/profile",
            "description": "查看进店视频与门店路线",
        },
        {
            "name": "门店器械",
            "path": "/pages/equipment/equipment",
            "description": "浏览热门器械与动作演示",
        },
        {
            "name": "推荐课程",
            "path": "/pages/course/course",
            "description": "查看今日可约与本周推荐课程",
        },
    ],
}


EQUIPMENT_CONTENT = [
    {
        "name": "无动力跑步机",
        "part": "有氧",
        "location": "有氧区",
        "target_muscles": "心肺 / 臀腿 / 核心",
        "training_focus": "提升心肺耐力、燃脂效率和训练热身质量",
        "description": "无动力跑步机依赖下肢主动蹬伸驱动跑带，能够同步提升步频控制、髋膝踝协同与无氧耐力输出，常用于冲刺间歇和专项体能训练。",
        "action_tips": "进入动作前先完成 3 至 5 分钟低强度热身，训练中维持均匀呼吸节奏、稳定步频和躯干中立位，再按目标心率逐步提升速度或阻力。",
        "precautions": "首次使用应从低速度或低阻力区间开始，并根据心率与主观体感逐步进阶；如出现头晕、胸闷或呼吸异常应立即停止。",
        "miniapp_gif_path": "/器械库动图/有氧/无动力跑步机-剪裁.gif"
    },
    {
        "name": "椭圆机",
        "part": "有氧",
        "location": "有氧区",
        "target_muscles": "心肺 / 臀腿",
        "training_focus": "提升心肺耐力、燃脂效率和训练热身质量",
        "description": "椭圆机通过闭链低冲击轨迹完成持续有氧输出，适合在保护膝踝关节的前提下提升心肺耐力与下肢耐力。",
        "action_tips": "进入动作前先完成 3 至 5 分钟低强度热身，训练中维持均匀呼吸节奏、稳定步频和躯干中立位，再按目标心率逐步提升速度或阻力。",
        "precautions": "首次使用应从低速度或低阻力区间开始，并根据心率与主观体感逐步进阶；如出现头晕、胸闷或呼吸异常应立即停止。",
        "miniapp_gif_path": "/器械库动图/有氧/椭圆机-剪裁.gif"
    },
    {
        "name": "登山机",
        "part": "有氧",
        "location": "有氧区",
        "target_muscles": "心肺 / 臀腿 / 臀大肌",
        "training_focus": "提升心肺耐力、燃脂效率和训练热身质量",
        "description": "登山机强调髋伸与膝伸的重复发力，能明显提高心率区间并强化臀腿后链参与度，适合燃脂和体能强化。",
        "action_tips": "进入动作前先完成 3 至 5 分钟低强度热身，训练中维持均匀呼吸节奏、稳定步频和躯干中立位，再按目标心率逐步提升速度或阻力。",
        "precautions": "首次使用应从低速度或低阻力区间开始，并根据心率与主观体感逐步进阶；如出现头晕、胸闷或呼吸异常应立即停止。",
        "miniapp_gif_path": "/器械库动图/有氧/登山机-剪裁.gif"
    },
    {
        "name": "跑步机",
        "part": "有氧",
        "location": "有氧区",
        "target_muscles": "心肺 / 臀腿 / 核心",
        "training_focus": "提升心肺耐力、燃脂效率和训练热身质量",
        "description": "跑步机属于基础心肺训练器械，可用于稳态有氧、间歇跑和热身激活，有助于提升摄氧效率、下肢循环与整体代谢水平。",
        "action_tips": "进入动作前先完成 3 至 5 分钟低强度热身，训练中维持均匀呼吸节奏、稳定步频和躯干中立位，再按目标心率逐步提升速度或阻力。",
        "precautions": "首次使用应从低速度或低阻力区间开始，并根据心率与主观体感逐步进阶；如出现头晕、胸闷或呼吸异常应立即停止。",
        "miniapp_gif_path": "/器械库动图/有氧/跑步机-剪裁.gif"
    },
    {
        "name": "上斜哑铃交替弯举",
        "part": "手臂",
        "location": "自由力量区",
        "target_muscles": "肱二头 / 前臂",
        "training_focus": "强化手臂围度、孤立发力能力和上肢控制感",
        "description": "上斜哑铃交替弯举通过肩关节轻度伸展位拉长肱二头肌长头，能够放大离心阶段张力并强化顶峰收缩感。",
        "action_tips": "肩关节保持中立，上臂尽量固定，向心阶段专注肘屈发力，离心阶段控制下放速度以延长肌肉张力时间。",
        "precautions": "避免通过躯干摆动制造惯性，训练重量应控制在目标次数区间内，离心阶段必须保持可控以降低肘关节压力。",
        "miniapp_gif_path": "/器械库动图/手臂/上斜哑铃交替弯举-剪裁.gif"
    },
    {
        "name": "仰卧哑铃肱三头肌臂屈伸",
        "part": "手臂",
        "location": "自由力量区",
        "target_muscles": "肱三头",
        "training_focus": "强化手臂围度、孤立发力能力和上肢控制感",
        "description": "仰卧哑铃肱三头肌臂屈伸以肘伸为主导，可充分刺激肱三头肌长头，对推举类动作的锁定能力提升明显。",
        "action_tips": "肘部保持相对固定并朝向前下方，发力时专注完成肘伸，动作末端充分收缩肱三头肌，避免肩关节代偿。",
        "precautions": "避免通过躯干摆动制造惯性，训练重量应控制在目标次数区间内，离心阶段必须保持可控以降低肘关节压力。",
        "miniapp_gif_path": "/器械库动图/手臂/仰卧哑铃肱三头肌臂屈伸-剪裁.gif"
    },
    {
        "name": "佐特曼弯举",
        "part": "手臂",
        "location": "自由力量区",
        "target_muscles": "肱二头 / 前臂",
        "training_focus": "强化手臂围度、孤立发力能力和上肢控制感",
        "description": "佐特曼弯举结合正握向心与反握离心，兼顾肱二头肌、肱桡肌和前臂旋后控制，是上臂与前臂协同训练动作。",
        "action_tips": "肩关节保持中立，上臂尽量固定，向心阶段专注肘屈发力，离心阶段控制下放速度以延长肌肉张力时间。",
        "precautions": "避免通过躯干摆动制造惯性，训练重量应控制在目标次数区间内，离心阶段必须保持可控以降低肘关节压力。",
        "miniapp_gif_path": "/器械库动图/手臂/佐特曼弯举-剪裁.gif"
    },
    {
        "name": "双杠臂屈伸",
        "part": "手臂",
        "location": "自由力量区",
        "target_muscles": "肱三头",
        "training_focus": "强化手臂围度、孤立发力能力和上肢控制感",
        "description": "双杠臂屈伸强调肘伸与肩关节稳定协同，适合提升肱三头肌力量输出，并辅助胸肩推类动作表现。",
        "action_tips": "肘部保持相对固定并朝向前下方，发力时专注完成肘伸，动作末端充分收缩肱三头肌，避免肩关节代偿。",
        "precautions": "避免通过躯干摆动制造惯性，训练重量应控制在目标次数区间内，离心阶段必须保持可控以降低肘关节压力。",
        "miniapp_gif_path": "/器械库动图/手臂/双杠臂屈伸-剪裁.gif"
    },
    {
        "name": "反握杠铃牧师凳弯举",
        "part": "手臂",
        "location": "自由力量区",
        "target_muscles": "肱二头 / 前臂",
        "training_focus": "强化手臂围度、孤立发力能力和上肢控制感",
        "description": "牧师凳弯举通过固定上臂位置减少代偿，能显著提高肘关节屈曲阶段的孤立度，适合强化肱二头肌短头发力。",
        "action_tips": "肩关节保持中立，上臂尽量固定，向心阶段专注肘屈发力，离心阶段控制下放速度以延长肌肉张力时间。",
        "precautions": "避免通过躯干摆动制造惯性，训练重量应控制在目标次数区间内，离心阶段必须保持可控以降低肘关节压力。",
        "miniapp_gif_path": "/器械库动图/手臂/反握杠铃牧师凳弯举-剪裁.gif"
    },
    {
        "name": "器械臂屈伸",
        "part": "手臂",
        "location": "自由力量区",
        "target_muscles": "肱三头",
        "training_focus": "强化手臂围度、孤立发力能力和上肢控制感",
        "description": "器械臂屈伸强调肘伸与肩关节稳定协同，适合提升肱三头肌力量输出，并辅助胸肩推类动作表现。",
        "action_tips": "肘部保持相对固定并朝向前下方，发力时专注完成肘伸，动作末端充分收缩肱三头肌，避免肩关节代偿。",
        "precautions": "避免通过躯干摆动制造惯性，训练重量应控制在目标次数区间内，离心阶段必须保持可控以降低肘关节压力。",
        "miniapp_gif_path": "/器械库动图/手臂/器械臂屈伸-剪裁.gif"
    },
    {
        "name": "站姿曲杆弯举",
        "part": "手臂",
        "location": "自由力量区",
        "target_muscles": "肱二头 / 前臂",
        "training_focus": "强化手臂围度、孤立发力能力和上肢控制感",
        "description": "曲杆弯举能够在相对舒适的腕部角度下完成肘屈训练，适合提升肱二头肌围度和重复输出能力。",
        "action_tips": "肩关节保持中立，上臂尽量固定，向心阶段专注肘屈发力，离心阶段控制下放速度以延长肌肉张力时间。",
        "precautions": "避免通过躯干摆动制造惯性，训练重量应控制在目标次数区间内，离心阶段必须保持可控以降低肘关节压力。",
        "miniapp_gif_path": "/器械库动图/手臂/站姿曲杆弯举-剪裁.gif"
    },
    {
        "name": "绳索臂屈伸",
        "part": "手臂",
        "location": "自由力量区",
        "target_muscles": "肱三头",
        "training_focus": "强化手臂围度、孤立发力能力和上肢控制感",
        "description": "绳索臂屈伸在全程张力环境下强化肱三头肌向心收缩，适合用于容量训练和充血阶段。",
        "action_tips": "肘部保持相对固定并朝向前下方，发力时专注完成肘伸，动作末端充分收缩肱三头肌，避免肩关节代偿。",
        "precautions": "避免通过躯干摆动制造惯性，训练重量应控制在目标次数区间内，离心阶段必须保持可控以降低肘关节压力。",
        "miniapp_gif_path": "/器械库动图/手臂/绳索臂屈伸-剪裁.gif"
    },
    {
        "name": "单臂哑铃侧平举",
        "part": "肩部",
        "location": "肩部训练区",
        "target_muscles": "三角肌中束",
        "training_focus": "提升肩部稳定性、线条感和上肢推举表现",
        "description": "单臂哑铃侧平举主要针对三角肌中束，适合提升肩宽视觉效果，并优化肩关节外展阶段的张力控制。",
        "action_tips": "采用轻度屈肘姿势完成外展，抬至接近肩高即可，主动维持三角肌中束张力，避免借助惯性摆荡。",
        "precautions": "训练中保持核心稳定与节奏可控，若出现明显关节疼痛、麻木或失去动作控制，应立即停止并调整训练方案。",
        "miniapp_gif_path": "/器械库动图/肩部/单臂哑铃侧平举-剪裁.gif"
    },
    {
        "name": "单臂绳索侧平举",
        "part": "肩部",
        "location": "肩部训练区",
        "target_muscles": "三角肌中束",
        "training_focus": "提升肩部稳定性、线条感和上肢推举表现",
        "description": "单臂绳索侧平举主要针对三角肌中束，适合提升肩宽视觉效果，并优化肩关节外展阶段的张力控制。",
        "action_tips": "采用轻度屈肘姿势完成外展，抬至接近肩高即可，主动维持三角肌中束张力，避免借助惯性摆荡。",
        "precautions": "训练中保持核心稳定与节奏可控，若出现明显关节疼痛、麻木或失去动作控制，应立即停止并调整训练方案。",
        "miniapp_gif_path": "/器械库动图/肩部/单臂绳索侧平举-剪裁.gif"
    },
    {
        "name": "哑铃推举",
        "part": "肩部",
        "location": "肩部训练区",
        "target_muscles": "三角肌前束 / 中束 / 肱三头",
        "training_focus": "提升肩部稳定性、线条感和上肢推举表现",
        "description": "哑铃推举属于肩部推举类动作，强调肩关节屈曲与外展协同，对提升三角肌整体力量和上肢垂直推举能力效果明显。",
        "action_tips": "核心与臀部主动收紧，推举轨迹保持在肩关节稳定平面，顶端保留微屈肘避免完全锁死，保持持续受力。",
        "precautions": "训练前应充分激活肩袖与肩胛稳定肌群，正式组避免过度腰椎代偿；大重量训练建议使用保护架或同伴保护。",
        "miniapp_gif_path": "/器械库动图/肩部/哑铃推举-剪裁.gif"
    },
    {
        "name": "器械后飞鸟",
        "part": "肩部",
        "location": "肩部训练区",
        "target_muscles": "三角肌后束 / 上背",
        "training_focus": "提升肩部稳定性、线条感和上肢推举表现",
        "description": "器械后飞鸟重点刺激三角肌后束与肩胛后缩肌群，可改善圆肩体态并增强上背稳定。",
        "action_tips": "先固定肩胛位置，再完成肩关节水平外展或内收；顶峰短暂停顿 1 秒，离心阶段保持持续张力不过度松弛。",
        "precautions": "训练中保持核心稳定与节奏可控，若出现明显关节疼痛、麻木或失去动作控制，应立即停止并调整训练方案。",
        "miniapp_gif_path": "/器械库动图/肩部/器械后飞鸟-剪裁.gif"
    },
    {
        "name": "坐姿哑铃侧平举",
        "part": "肩部",
        "location": "肩部训练区",
        "target_muscles": "三角肌中束",
        "training_focus": "提升肩部稳定性、线条感和上肢推举表现",
        "description": "坐姿哑铃侧平举主要针对三角肌中束，适合提升肩宽视觉效果，并优化肩关节外展阶段的张力控制。",
        "action_tips": "采用轻度屈肘姿势完成外展，抬至接近肩高即可，主动维持三角肌中束张力，避免借助惯性摆荡。",
        "precautions": "训练中保持核心稳定与节奏可控，若出现明显关节疼痛、麻木或失去动作控制，应立即停止并调整训练方案。",
        "miniapp_gif_path": "/器械库动图/肩部/坐姿哑铃侧平举-剪裁.gif"
    },
    {
        "name": "坐姿哑铃飞鸟",
        "part": "肩部",
        "location": "肩部训练区",
        "target_muscles": "三角肌后束 / 上背",
        "training_focus": "提升肩部稳定性、线条感和上肢推举表现",
        "description": "坐姿哑铃飞鸟重点刺激三角肌后束与肩胛后缩肌群，可改善圆肩体态并增强上背稳定。",
        "action_tips": "先固定肩胛位置，再完成肩关节水平外展或内收；顶峰短暂停顿 1 秒，离心阶段保持持续张力不过度松弛。",
        "precautions": "训练中保持核心稳定与节奏可控，若出现明显关节疼痛、麻木或失去动作控制，应立即停止并调整训练方案。",
        "miniapp_gif_path": "/器械库动图/肩部/坐姿哑铃飞鸟-剪裁.gif"
    },
    {
        "name": "坐姿杠铃推肩",
        "part": "肩部",
        "location": "肩部训练区",
        "target_muscles": "三角肌前束 / 中束 / 肱三头",
        "training_focus": "提升肩部稳定性、线条感和上肢推举表现",
        "description": "坐姿杠铃推肩属于肩部推举类动作，强调肩关节屈曲与外展协同，对提升三角肌整体力量和上肢垂直推举能力效果明显。",
        "action_tips": "核心与臀部主动收紧，推举轨迹保持在肩关节稳定平面，顶端保留微屈肘避免完全锁死，保持持续受力。",
        "precautions": "训练前应充分激活肩袖与肩胛稳定肌群，正式组避免过度腰椎代偿；大重量训练建议使用保护架或同伴保护。",
        "miniapp_gif_path": "/器械库动图/肩部/坐姿杠铃推肩-剪裁.gif"
    },
    {
        "name": "推肩器推肩",
        "part": "肩部",
        "location": "肩部训练区",
        "target_muscles": "三角肌前束 / 中束 / 肱三头",
        "training_focus": "提升肩部稳定性、线条感和上肢推举表现",
        "description": "推肩器推肩属于肩部推举类动作，强调肩关节屈曲与外展协同，对提升三角肌整体力量和上肢垂直推举能力效果明显。",
        "action_tips": "核心与臀部主动收紧，推举轨迹保持在肩关节稳定平面，顶端保留微屈肘避免完全锁死，保持持续受力。",
        "precautions": "训练前应充分激活肩袖与肩胛稳定肌群，正式组避免过度腰椎代偿；大重量训练建议使用保护架或同伴保护。",
        "miniapp_gif_path": "/器械库动图/肩部/推肩器推肩-剪裁.gif"
    },
    {
        "name": "绳索交叉侧平举",
        "part": "肩部",
        "location": "肩部训练区",
        "target_muscles": "三角肌中束",
        "training_focus": "提升肩部稳定性、线条感和上肢推举表现",
        "description": "绳索交叉侧平举主要针对三角肌中束，适合提升肩宽视觉效果，并优化肩关节外展阶段的张力控制。",
        "action_tips": "采用轻度屈肘姿势完成外展，抬至接近肩高即可，主动维持三角肌中束张力，避免借助惯性摆荡。",
        "precautions": "训练中保持核心稳定与节奏可控，若出现明显关节疼痛、麻木或失去动作控制，应立即停止并调整训练方案。",
        "miniapp_gif_path": "/器械库动图/肩部/绳索交叉侧平举-剪裁.gif"
    },
    {
        "name": "绳索反向飞鸟",
        "part": "肩部",
        "location": "肩部训练区",
        "target_muscles": "三角肌后束 / 上背",
        "training_focus": "提升肩部稳定性、线条感和上肢推举表现",
        "description": "绳索反向飞鸟重点刺激三角肌后束与肩胛后缩肌群，可改善圆肩体态并增强上背稳定。",
        "action_tips": "先固定肩胛位置，再完成肩关节水平外展或内收；顶峰短暂停顿 1 秒，离心阶段保持持续张力不过度松弛。",
        "precautions": "训练中保持核心稳定与节奏可控，若出现明显关节疼痛、麻木或失去动作控制，应立即停止并调整训练方案。",
        "miniapp_gif_path": "/器械库动图/肩部/绳索反向飞鸟-剪裁.gif"
    },
    {
        "name": "阿诺德哑铃推举",
        "part": "肩部",
        "location": "肩部训练区",
        "target_muscles": "三角肌前束 / 中束 / 肱三头",
        "training_focus": "提升肩部稳定性、线条感和上肢推举表现",
        "description": "阿诺德哑铃推举属于肩部推举类动作，强调肩关节屈曲与外展协同，对提升三角肌整体力量和上肢垂直推举能力效果明显。",
        "action_tips": "核心与臀部主动收紧，推举轨迹保持在肩关节稳定平面，顶端保留微屈肘避免完全锁死，保持持续受力。",
        "precautions": "训练前应充分激活肩袖与肩胛稳定肌群，正式组避免过度腰椎代偿；大重量训练建议使用保护架或同伴保护。",
        "miniapp_gif_path": "/器械库动图/肩部/阿诺德哑铃推举-剪裁.gif"
    },
    {
        "name": "T杠划船",
        "part": "背部",
        "location": "背部训练区",
        "target_muscles": "背阔肌 / 菱形肌 / 后束",
        "training_focus": "建立背部发力感，提升拉力动作稳定性和体态支撑",
        "description": "T杠划船属于水平拉训练动作，强调肩胛后缩与肘部后引，能够提升背部厚度、姿态稳定和拉力表现。",
        "action_tips": "维持脊柱中立与核心张力，拉动时用肘部引导向后，顶峰阶段完成肩胛后缩并短暂停顿感受背部收紧。",
        "precautions": "不要为追求负重而牺牲肩胛控制或借助惯性后仰，若无法维持背部持续张力应及时下调重量。",
        "miniapp_gif_path": "/器械库动图/背部/T杠划船-剪裁.gif"
    },
    {
        "name": "V把高位下拉",
        "part": "背部",
        "location": "背部训练区",
        "target_muscles": "背阔肌 / 肱二头",
        "training_focus": "建立背部发力感，提升拉力动作稳定性和体态支撑",
        "description": "V把高位下拉是垂直拉训练代表动作，重点强化背阔肌下压与肩胛下沉控制，适合建立背部发力路径。",
        "action_tips": "动作起始先完成肩胛下沉，再通过肘部向下向后引导发力；胸椎微伸但不后仰借力，保持背阔肌主导。",
        "precautions": "不要为追求负重而牺牲肩胛控制或借助惯性后仰，若无法维持背部持续张力应及时下调重量。",
        "miniapp_gif_path": "/器械库动图/背部/V把高位下拉-剪裁.gif"
    },
    {
        "name": "上斜俯身哑铃划船",
        "part": "背部",
        "location": "背部训练区",
        "target_muscles": "背阔肌 / 菱形肌 / 后束",
        "training_focus": "建立背部发力感，提升拉力动作稳定性和体态支撑",
        "description": "上斜俯身哑铃划船属于水平拉训练动作，强调肩胛后缩与肘部后引，能够提升背部厚度、姿态稳定和拉力表现。",
        "action_tips": "维持脊柱中立与核心张力，拉动时用肘部引导向后，顶峰阶段完成肩胛后缩并短暂停顿感受背部收紧。",
        "precautions": "不要为追求负重而牺牲肩胛控制或借助惯性后仰，若无法维持背部持续张力应及时下调重量。",
        "miniapp_gif_path": "/器械库动图/背部/上斜俯身哑铃划船-剪裁.gif"
    },
    {
        "name": "俯身杠铃划船",
        "part": "背部",
        "location": "背部训练区",
        "target_muscles": "背阔肌 / 菱形肌 / 后束",
        "training_focus": "建立背部发力感，提升拉力动作稳定性和体态支撑",
        "description": "俯身杠铃划船属于水平拉训练动作，强调肩胛后缩与肘部后引，能够提升背部厚度、姿态稳定和拉力表现。",
        "action_tips": "维持脊柱中立与核心张力，拉动时用肘部引导向后，顶峰阶段完成肩胛后缩并短暂停顿感受背部收紧。",
        "precautions": "不要为追求负重而牺牲肩胛控制或借助惯性后仰，若无法维持背部持续张力应及时下调重量。",
        "miniapp_gif_path": "/器械库动图/背部/俯身杠铃划船-剪裁.gif"
    },
    {
        "name": "坐姿划船",
        "part": "背部",
        "location": "背部训练区",
        "target_muscles": "背阔肌 / 菱形肌 / 后束",
        "training_focus": "建立背部发力感，提升拉力动作稳定性和体态支撑",
        "description": "坐姿划船属于水平拉训练动作，强调肩胛后缩与肘部后引，能够提升背部厚度、姿态稳定和拉力表现。",
        "action_tips": "维持脊柱中立与核心张力，拉动时用肘部引导向后，顶峰阶段完成肩胛后缩并短暂停顿感受背部收紧。",
        "precautions": "不要为追求负重而牺牲肩胛控制或借助惯性后仰，若无法维持背部持续张力应及时下调重量。",
        "miniapp_gif_path": "/器械库动图/背部/坐姿划船-剪裁.gif"
    },
    {
        "name": "引体向上",
        "part": "背部",
        "location": "背部训练区",
        "target_muscles": "背阔肌 / 肱二头",
        "training_focus": "建立背部发力感，提升拉力动作稳定性和体态支撑",
        "description": "引体向上强调自身体重条件下的垂直拉力输出，对背阔肌、肱二头肌及核心稳定均有较高要求。",
        "action_tips": "动作起始先完成肩胛下沉，再通过肘部向下向后引导发力；胸椎微伸但不后仰借力，保持背阔肌主导。",
        "precautions": "不要为追求负重而牺牲肩胛控制或借助惯性后仰，若无法维持背部持续张力应及时下调重量。",
        "miniapp_gif_path": "/器械库动图/背部/引体向上-剪裁.gif"
    },
    {
        "name": "辅助引体向上",
        "part": "背部",
        "location": "背部训练区",
        "target_muscles": "背阔肌 / 肱二头",
        "training_focus": "建立背部发力感，提升拉力动作稳定性和体态支撑",
        "description": "辅助引体向上强调自身体重条件下的垂直拉力输出，对背阔肌、肱二头肌及核心稳定均有较高要求。",
        "action_tips": "动作起始先完成肩胛下沉，再通过肘部向下向后引导发力；胸椎微伸但不后仰借力，保持背阔肌主导。",
        "precautions": "不要为追求负重而牺牲肩胛控制或借助惯性后仰，若无法维持背部持续张力应及时下调重量。",
        "miniapp_gif_path": "/器械库动图/背部/辅助引体向上-剪裁.gif"
    },
    {
        "name": "高位下拉",
        "part": "背部",
        "location": "背部训练区",
        "target_muscles": "背阔肌 / 肱二头",
        "training_focus": "建立背部发力感，提升拉力动作稳定性和体态支撑",
        "description": "高位下拉是垂直拉训练代表动作，重点强化背阔肌下压与肩胛下沉控制，适合建立背部发力路径。",
        "action_tips": "动作起始先完成肩胛下沉，再通过肘部向下向后引导发力；胸椎微伸但不后仰借力，保持背阔肌主导。",
        "precautions": "不要为追求负重而牺牲肩胛控制或借助惯性后仰，若无法维持背部持续张力应及时下调重量。",
        "miniapp_gif_path": "/器械库动图/背部/高位下拉-剪裁.gif"
    },
    {
        "name": "上斜哑铃卧推",
        "part": "胸部",
        "location": "胸部训练区",
        "target_muscles": "胸大肌 / 三角肌前束 / 肱三头",
        "training_focus": "增强胸部推力、挤压感和上肢整体力量表现",
        "description": "上斜哑铃卧推属于胸部复合推举动作，能够同时调动胸大肌、三角肌前束与肱三头肌，对上肢最大力量和训练容量提升显著。",
        "action_tips": "准备阶段先完成肩胛后缩下沉并建立下肢支撑，杠铃或哑铃下放至可控深度后垂直向上推起，保持胸部主动发力。",
        "precautions": "训练前应充分激活肩袖与肩胛稳定肌群，正式组避免过度腰椎代偿；大重量训练建议使用保护架或同伴保护。",
        "miniapp_gif_path": "/器械库动图/胸部/上斜哑铃卧推-剪裁.gif"
    },
    {
        "name": "上斜杠铃卧推",
        "part": "胸部",
        "location": "胸部训练区",
        "target_muscles": "胸大肌 / 三角肌前束 / 肱三头",
        "training_focus": "增强胸部推力、挤压感和上肢整体力量表现",
        "description": "上斜杠铃卧推属于胸部复合推举动作，能够同时调动胸大肌、三角肌前束与肱三头肌，对上肢最大力量和训练容量提升显著。",
        "action_tips": "准备阶段先完成肩胛后缩下沉并建立下肢支撑，杠铃或哑铃下放至可控深度后垂直向上推起，保持胸部主动发力。",
        "precautions": "训练前应充分激活肩袖与肩胛稳定肌群，正式组避免过度腰椎代偿；大重量训练建议使用保护架或同伴保护。",
        "miniapp_gif_path": "/器械库动图/胸部/上斜杠铃卧推-剪裁.gif"
    },
    {
        "name": "史密斯杠铃上斜卧推",
        "part": "胸部",
        "location": "胸部训练区",
        "target_muscles": "胸大肌 / 三角肌前束 / 肱三头",
        "training_focus": "增强胸部推力、挤压感和上肢整体力量表现",
        "description": "史密斯杠铃上斜卧推属于胸部复合推举动作，能够同时调动胸大肌、三角肌前束与肱三头肌，对上肢最大力量和训练容量提升显著。",
        "action_tips": "准备阶段先完成肩胛后缩下沉并建立下肢支撑，杠铃或哑铃下放至可控深度后垂直向上推起，保持胸部主动发力。",
        "precautions": "训练前应充分激活肩袖与肩胛稳定肌群，正式组避免过度腰椎代偿；大重量训练建议使用保护架或同伴保护。",
        "miniapp_gif_path": "/器械库动图/胸部/史密斯杠铃上斜卧推-剪裁.gif"
    },
    {
        "name": "史密斯杠铃下斜卧推",
        "part": "胸部",
        "location": "胸部训练区",
        "target_muscles": "胸大肌 / 三角肌前束 / 肱三头",
        "training_focus": "增强胸部推力、挤压感和上肢整体力量表现",
        "description": "史密斯杠铃下斜卧推属于胸部复合推举动作，能够同时调动胸大肌、三角肌前束与肱三头肌，对上肢最大力量和训练容量提升显著。",
        "action_tips": "准备阶段先完成肩胛后缩下沉并建立下肢支撑，杠铃或哑铃下放至可控深度后垂直向上推起，保持胸部主动发力。",
        "precautions": "训练前应充分激活肩袖与肩胛稳定肌群，正式组避免过度腰椎代偿；大重量训练建议使用保护架或同伴保护。",
        "miniapp_gif_path": "/器械库动图/胸部/史密斯杠铃下斜卧推-剪裁.gif"
    },
    {
        "name": "史密斯杠铃平板卧推",
        "part": "胸部",
        "location": "胸部训练区",
        "target_muscles": "胸大肌 / 三角肌前束 / 肱三头",
        "training_focus": "增强胸部推力、挤压感和上肢整体力量表现",
        "description": "史密斯杠铃平板卧推属于胸部复合推举动作，能够同时调动胸大肌、三角肌前束与肱三头肌，对上肢最大力量和训练容量提升显著。",
        "action_tips": "准备阶段先完成肩胛后缩下沉并建立下肢支撑，杠铃或哑铃下放至可控深度后垂直向上推起，保持胸部主动发力。",
        "precautions": "训练前应充分激活肩袖与肩胛稳定肌群，正式组避免过度腰椎代偿；大重量训练建议使用保护架或同伴保护。",
        "miniapp_gif_path": "/器械库动图/胸部/史密斯杠铃平板卧推-剪裁.gif"
    },
    {
        "name": "哑铃平板卧推",
        "part": "胸部",
        "location": "胸部训练区",
        "target_muscles": "胸大肌 / 三角肌前束 / 肱三头",
        "training_focus": "增强胸部推力、挤压感和上肢整体力量表现",
        "description": "哑铃平板卧推属于胸部复合推举动作，能够同时调动胸大肌、三角肌前束与肱三头肌，对上肢最大力量和训练容量提升显著。",
        "action_tips": "准备阶段先完成肩胛后缩下沉并建立下肢支撑，杠铃或哑铃下放至可控深度后垂直向上推起，保持胸部主动发力。",
        "precautions": "训练前应充分激活肩袖与肩胛稳定肌群，正式组避免过度腰椎代偿；大重量训练建议使用保护架或同伴保护。",
        "miniapp_gif_path": "/器械库动图/胸部/哑铃平板卧推-剪裁.gif"
    },
    {
        "name": "杠铃平板卧推",
        "part": "胸部",
        "location": "胸部训练区",
        "target_muscles": "胸大肌 / 三角肌前束 / 肱三头",
        "training_focus": "增强胸部推力、挤压感和上肢整体力量表现",
        "description": "杠铃平板卧推属于胸部复合推举动作，能够同时调动胸大肌、三角肌前束与肱三头肌，对上肢最大力量和训练容量提升显著。",
        "action_tips": "准备阶段先完成肩胛后缩下沉并建立下肢支撑，杠铃或哑铃下放至可控深度后垂直向上推起，保持胸部主动发力。",
        "precautions": "训练前应充分激活肩袖与肩胛稳定肌群，正式组避免过度腰椎代偿；大重量训练建议使用保护架或同伴保护。",
        "miniapp_gif_path": "/器械库动图/胸部/杠铃平板卧推-去水印.gif"
    },
    {
        "name": "绳索夹胸",
        "part": "胸部",
        "location": "胸部训练区",
        "target_muscles": "胸大肌 / 胸肌中缝",
        "training_focus": "增强胸部推力、挤压感和上肢整体力量表现",
        "description": "绳索夹胸以肩关节水平内收为主，能强化胸大肌中后段收缩感，适合作为胸部孤立补充训练。",
        "action_tips": "保持肘部轻屈并以弧线轨迹完成水平内收，顶峰位置主动挤压胸肌，离心阶段缓慢打开保持胸部张力。",
        "precautions": "训练中保持核心稳定与节奏可控，若出现明显关节疼痛、麻木或失去动作控制，应立即停止并调整训练方案。",
        "miniapp_gif_path": "/器械库动图/胸部/绳索夹胸-剪裁.gif"
    },
    {
        "name": "臂屈伸",
        "part": "胸部",
        "location": "胸部训练区",
        "target_muscles": "下胸 / 肱三头",
        "training_focus": "增强胸部推力、挤压感和上肢整体力量表现",
        "description": "臂屈伸在身体前倾条件下可显著增加下胸与肱三头肌参与度，适合用于胸部末端强化与自重力量提升。",
        "action_tips": "肘部保持相对固定并朝向前下方，发力时专注完成肘伸，动作末端充分收缩肱三头肌，避免肩关节代偿。",
        "precautions": "避免通过躯干摆动制造惯性，训练重量应控制在目标次数区间内，离心阶段必须保持可控以降低肘关节压力。",
        "miniapp_gif_path": "/器械库动图/胸部/臂屈伸-去水印.gif"
    },
    {
        "name": "蝴蝶机夹胸",
        "part": "胸部",
        "location": "胸部训练区",
        "target_muscles": "胸大肌 / 胸肌中缝",
        "training_focus": "增强胸部推力、挤压感和上肢整体力量表现",
        "description": "蝴蝶机夹胸以肩关节水平内收为主，能强化胸大肌中后段收缩感，适合作为胸部孤立补充训练。",
        "action_tips": "保持肘部轻屈并以弧线轨迹完成水平内收，顶峰位置主动挤压胸肌，离心阶段缓慢打开保持胸部张力。",
        "precautions": "训练中保持核心稳定与节奏可控，若出现明显关节疼痛、麻木或失去动作控制，应立即停止并调整训练方案。",
        "miniapp_gif_path": "/器械库动图/胸部/蝴蝶机夹胸-去水印.gif"
    },
    {
        "name": "倒蹬",
        "part": "臀腿",
        "location": "下肢训练区",
        "target_muscles": "股四头 / 臀大肌 / 腘绳肌",
        "training_focus": "提升下肢力量、稳定性和臀腿线条表现",
        "description": "倒蹬通过固定轨迹提升下肢推蹬输出，适合在降低平衡要求的同时增强股四头肌与臀腿力量。",
        "action_tips": "下放阶段保持膝盖与脚尖方向一致，髋膝同步屈曲，核心全程稳定；起身时通过脚跟与全脚掌均匀发力完成伸展。",
        "precautions": "开始前需完成髋、膝、踝与核心激活，训练中优先保证脊柱稳定和关节对线；动作幅度应根据活动度与训练经验逐步推进。",
        "miniapp_gif_path": "/器械库动图/臀腿/倒蹬-剪裁.gif"
    },
    {
        "name": "史密斯倒蹬",
        "part": "臀腿",
        "location": "下肢训练区",
        "target_muscles": "股四头 / 臀大肌 / 腘绳肌",
        "training_focus": "提升下肢力量、稳定性和臀腿线条表现",
        "description": "史密斯倒蹬通过固定轨迹提升下肢推蹬输出，适合在降低平衡要求的同时增强股四头肌与臀腿力量。",
        "action_tips": "下放阶段保持膝盖与脚尖方向一致，髋膝同步屈曲，核心全程稳定；起身时通过脚跟与全脚掌均匀发力完成伸展。",
        "precautions": "开始前需完成髋、膝、踝与核心激活，训练中优先保证脊柱稳定和关节对线；动作幅度应根据活动度与训练经验逐步推进。",
        "miniapp_gif_path": "/器械库动图/臀腿/史密斯倒蹬-剪裁.gif"
    },
    {
        "name": "哈克深蹲",
        "part": "臀腿",
        "location": "下肢训练区",
        "target_muscles": "股四头 / 臀大肌 / 腘绳肌",
        "training_focus": "提升下肢力量、稳定性和臀腿线条表现",
        "description": "哈克深蹲属于下肢基础复合动作，强调髋膝同步屈伸，可全面提升股四头肌、臀大肌与核心抗屈稳定能力。",
        "action_tips": "下放阶段保持膝盖与脚尖方向一致，髋膝同步屈曲，核心全程稳定；起身时通过脚跟与全脚掌均匀发力完成伸展。",
        "precautions": "开始前需完成髋、膝、踝与核心激活，训练中优先保证脊柱稳定和关节对线；动作幅度应根据活动度与训练经验逐步推进。",
        "miniapp_gif_path": "/器械库动图/臀腿/哈克深蹲-剪裁.gif"
    },
    {
        "name": "哑铃直腿硬拉",
        "part": "臀腿",
        "location": "下肢训练区",
        "target_muscles": "腘绳肌 / 臀大肌 / 下背稳定",
        "training_focus": "提升下肢力量、稳定性和臀腿线条表现",
        "description": "哑铃直腿硬拉强调髋主导铰链模式，可有效训练腘绳肌、臀大肌与后侧动力链的离心控制能力。",
        "action_tips": "全程以髋铰链模式主导动作，保持脊柱中立和杠铃贴近身体，下放时重点感受腘绳肌离心拉伸。",
        "precautions": "开始前需完成髋、膝、踝与核心激活，训练中优先保证脊柱稳定和关节对线；动作幅度应根据活动度与训练经验逐步推进。",
        "miniapp_gif_path": "/器械库动图/臀腿/哑铃直腿硬拉-剪裁.gif"
    },
    {
        "name": "器械后抬腿",
        "part": "臀腿",
        "location": "下肢训练区",
        "target_muscles": "臀大肌 / 臀中肌",
        "training_focus": "提升下肢力量、稳定性和臀腿线条表现",
        "description": "器械后抬腿可集中刺激臀大肌与臀中肌，是下肢训练中常用的臀部孤立补强动作。",
        "action_tips": "躯干稳定后再进行髋伸，动作末端主动收缩臀大肌并短暂停顿，避免腰椎代偿性后伸。",
        "precautions": "训练中保持核心稳定与节奏可控，若出现明显关节疼痛、麻木或失去动作控制，应立即停止并调整训练方案。",
        "miniapp_gif_path": "/器械库动图/臀腿/器械后抬腿-剪裁.gif"
    },
    {
        "name": "器械臀内收",
        "part": "臀腿",
        "location": "下肢训练区",
        "target_muscles": "大腿内收肌群",
        "training_focus": "提升下肢力量、稳定性和臀腿线条表现",
        "description": "器械臀内收主要用于强化大腿内收肌群与骨盆稳定，对改善下肢发力路径和动作对称性有帮助。",
        "action_tips": "坐姿保持骨盆中立，向心阶段主动完成髋内收，离心阶段控制打开幅度，避免快速回弹造成关节压力。",
        "precautions": "训练中保持核心稳定与节奏可控，若出现明显关节疼痛、麻木或失去动作控制，应立即停止并调整训练方案。",
        "miniapp_gif_path": "/器械库动图/臀腿/器械臀内收-剪裁.gif"
    },
    {
        "name": "杠铃深蹲",
        "part": "臀腿",
        "location": "下肢训练区",
        "target_muscles": "股四头 / 臀大肌 / 腘绳肌",
        "training_focus": "提升下肢力量、稳定性和臀腿线条表现",
        "description": "杠铃深蹲属于下肢基础复合动作，强调髋膝同步屈伸，可全面提升股四头肌、臀大肌与核心抗屈稳定能力。",
        "action_tips": "下放阶段保持膝盖与脚尖方向一致，髋膝同步屈曲，核心全程稳定；起身时通过脚跟与全脚掌均匀发力完成伸展。",
        "precautions": "开始前需完成髋、膝、踝与核心激活，训练中优先保证脊柱稳定和关节对线；动作幅度应根据活动度与训练经验逐步推进。",
        "miniapp_gif_path": "/器械库动图/臀腿/杠铃深蹲-剪裁.gif"
    },
    {
        "name": "杠铃臀推",
        "part": "臀腿",
        "location": "下肢训练区",
        "target_muscles": "臀大肌 / 臀中肌",
        "training_focus": "提升下肢力量、稳定性和臀腿线条表现",
        "description": "杠铃臀推以髋伸顶峰发力为核心，能够高效强化臀大肌募集，适合提升臀部力量、爆发力与线条表现。",
        "action_tips": "上背稳定贴合支撑点，发力时以髋伸驱动杠铃上行，顶峰主动后倾骨盆并夹紧臀部，避免腰椎过伸。",
        "precautions": "开始前需完成髋、膝、踝与核心激活，训练中优先保证脊柱稳定和关节对线；动作幅度应根据活动度与训练经验逐步推进。",
        "miniapp_gif_path": "/器械库动图/臀腿/杠铃臀推-剪裁.gif"
    }
]


COACH_CONTENT = [
    {
        "name": "教练阿杰",
        "role": "coach",
        "phone": "13800138001",
        "bio": "擅长新手入门、减脂训练和体能提升指导。",
    },
    {
        "name": "教练小林",
        "role": "coach",
        "phone": "13800138002",
        "bio": "擅长自由力量训练、动作纠正与基础力量提升。",
    },
]


COURSE_CONTENT = [
    {
        "name": "新手燃脂训练课",
        "category": "有氧燃脂",
        "coach_name": "教练阿杰",
        "start_time": "09:30",
        "duration": 60,
        "capacity": 16,
        "suitable_for": "零基础用户、减脂入门用户",
        "intensity_level": "中低强度",
        "description": "通过跑步机热身、基础循环训练和拉伸放松，帮助新手建立稳定训练节奏。",
        "class_prep": "穿运动服和运动鞋，提前10分钟到场，建议自带水杯和毛巾。",
        "image_url": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1470&auto=format&fit=crop",
        "membership_hint": "会员可直接预约，非会员建议先购卡后体验。",
    },
    {
        "name": "基础力量提升课",
        "category": "力量提升",
        "coach_name": "教练小林",
        "start_time": "19:30",
        "duration": 75,
        "capacity": 14,
        "suitable_for": "有一定训练基础、希望提升力量表现的用户",
        "intensity_level": "中高强度",
        "description": "结合深蹲、卧推、硬拉等基础动作训练，帮助学员建立标准发力模式。",
        "class_prep": "课前避免空腹，提前热身，建议佩戴护腕或训练手套。",
        "image_url": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?q=80&w=1470&auto=format&fit=crop",
        "membership_hint": "建议穿着稳定支撑型训练鞋，按教练安排分组完成训练。",
    },
    {
        "name": "增肌塑形循环课",
        "category": "增肌塑形",
        "coach_name": "教练小林",
        "start_time": "15:00",
        "duration": 60,
        "capacity": 12,
        "suitable_for": "希望提升肌肉线条和训练密度的进阶用户",
        "intensity_level": "中强度",
        "description": "结合上肢推拉与下肢循环训练，帮助提升整体代谢与肌肉参与度。",
        "class_prep": "建议自带毛巾，课程开始前完成肩髋关节热身。",
        "image_url": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?q=80&w=1471&auto=format&fit=crop",
        "membership_hint": "课程中会使用哑铃与固定器械，适合有基础用户参与。",
    },
    {
        "name": "基础体验拉伸课",
        "category": "基础体验",
        "coach_name": "教练阿杰",
        "start_time": "21:00",
        "duration": 45,
        "capacity": 18,
        "suitable_for": "初次到店体验用户、训练后恢复用户",
        "intensity_level": "低强度",
        "description": "通过基础拉伸、呼吸调整和轻量激活训练，帮助用户熟悉训练环境。",
        "class_prep": "穿着舒适运动服，避免餐后立即参加课程。",
        "image_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=1470&auto=format&fit=crop",
        "membership_hint": "适合作为首次到店课程，便于熟悉器械区和训练流程。",
    },
]


AI_CONTENT = {
    "page_title": "AI 教练",
    "welcome_message": "你好，我是你的智能健身教练，可以为你解答营业时间、课程预约、办卡与基础训练问题。",
    "quick_questions": [
        "营业时间到几点？",
        "会员卡有哪些？",
        "新手适合上什么课？",
        "史密斯机怎么使用？",
    ],
    "training_examples": [
        "如何系统提升深蹲力量？",
        "新手第一次练胸应该注意什么？",
    ],
    "gym_examples": [
        "场馆内有提供阻力带等辅助工具吗？",
        "门店的营业时间和地址是什么？",
    ],
    "membership_examples": [
        "办卡后可以预约哪些课程？",
        "年度VIP卡和基础月卡有什么区别？",
    ],
    "equipment_examples": [
        "高位下拉主要练哪里？",
        "椭圆机适合减脂热身吗？",
    ],
    "demo_questions": [
        "场馆具体的营业时间范围",
        "会员卡有哪些，价格分别是多少",
        "新手推荐什么课程",
        "史密斯机怎么使用",
    ],
    "show_sources": True,
    "show_related_questions": True,
}


PROFILE_CONTENT = {
    "member_benefits": "开通会员后可使用场馆基础训练区域，支持查看课程、预约训练和管理个人记录。",
    "face_notice": "用户可在个人中心完成人脸录入，用于后续快速身份校验与到店业务演示。",
    "door_notice": "已录入人脸信息的用户可在演示流程中完成人脸识别验证，提升到店体验。",
    "visit_notice": "系统将自动记录用户的签到、签退和到店时间，用于展示个人训练轨迹。",
    "group_buy_notice": "支持在首页或相关服务入口输入团购券码，完成核销流程演示。",
    "entry_guide_text": "到店后请先完成签到或身份验证，再根据课程安排进入对应训练区域。",
    "feedback_examples": [
        "场馆环境整洁，器械分区明确，适合日常训练。",
        "课程预约流程清晰，适合新手快速上手。",
        "AI页面提问响应较快，适合查询营业时间和办卡信息。",
    ],
}


ORDER_CONTENT = {
    "refund_note": "支持发起退款申请，退款状态以订单页展示为准（答辩演示口径）。",
    "order_status_note": "订单支付后即可查看会员权益生效状态，如有异常可刷新订单状态或提交退款申请。",
    "project_summary": "本项目是一个面向智能健身场景的微信小程序系统，集成了会员管理、课程预约、AI问答、人脸识别与对象存储等能力。",
    "payment_simulation_note": "当前支付模块完成了交易流程仿真闭环，能够演示购卡、订单状态流转与退款申请，但不宣称已完成真实微信支付商用接入。",
    "demo_path": "首页查看门店信息 -> 进入会员卡页购卡 -> 查看订单状态 -> 进入AI页面提问 -> 进入我的页查看服务功能",
}


MEMBERSHIP_PRODUCT_CONTENT = [
    {
        "name": "基础月卡",
        "price": Decimal("199.00"),
        "original_price": Decimal("299.00"),
        "days_duration": 30,
        "tags": ["新手推荐", "限时优惠"],
        "is_promotion": True,
        "description": "适合新用户体验与短期健身需求。",
    },
    {
        "name": "年度VIP卡",
        "price": Decimal("1999.00"),
        "original_price": Decimal("2399.00"),
        "days_duration": 365,
        "tags": ["全年畅练", "高性价比"],
        "is_promotion": True,
        "description": "适合长期训练用户，性价比更高。",
    },
]


COURSE_TEMPLATE_MAP = {item["name"]: item for item in COURSE_CONTENT}
EQUIPMENT_TEMPLATE_MAP = {item["name"]: item for item in EQUIPMENT_CONTENT}
PRODUCT_TEMPLATE_MAP = {item["name"]: item for item in MEMBERSHIP_PRODUCT_CONTENT}


def ensure_demo_membership_products():
    from orders.models import MembershipProduct

    created_products = []
    for item in MEMBERSHIP_PRODUCT_CONTENT:
        product, _ = MembershipProduct.objects.get_or_create(
            name=item["name"],
            defaults={
                "price": item["price"],
                "original_price": item["original_price"],
                "days_duration": item["days_duration"],
                "tags": item["tags"],
                "is_promotion": item["is_promotion"],
            },
        )
        created_products.append(product)
    return created_products


def ensure_demo_equipment():
    from fitness.models import BodyPart, Equipment

    created_equipment = []
    for item in EQUIPMENT_CONTENT:
        part, _ = BodyPart.objects.get_or_create(name=item["part"])
        equipment, _ = Equipment.objects.update_or_create(
            name=item["name"],
            defaults={
                "part": part,
                "description": item["description"],
                "target_muscles": item["target_muscles"],
                "training_focus": item.get("training_focus", ""),
                "action_tips": item.get("action_tips", ""),
                "precautions": item["precautions"],
                "location": item["location"],
                "miniapp_gif_path": item.get("miniapp_gif_path", ""),
            },
        )
        created_equipment.append(equipment)
    return created_equipment


def ensure_demo_courses(days=7):
    from fitness.models import Course, TeamMember

    today = timezone.localdate()
    created_courses = []
    coach_map = {}
    for coach_item in COACH_CONTENT:
        coach, _ = TeamMember.objects.get_or_create(
            name=coach_item["name"],
            defaults={
                "role": coach_item["role"],
                "phone": coach_item["phone"],
                "bio": coach_item["bio"],
                "is_active": True,
            },
        )
        coach_map[coach_item["name"]] = coach

    for day_offset in range(days):
        course_date = today + timedelta(days=day_offset)
        for item in COURSE_CONTENT:
            hour, minute = [int(part) for part in item["start_time"].split(":")]
            start_dt = timezone.make_aware(datetime.combine(course_date, time(hour, minute)))
            course, _ = Course.objects.update_or_create(
                name=item["name"],
                start_time=start_dt,
                defaults={
                    "coach": coach_map.get(item["coach_name"]),
                    "coach_name": item["coach_name"],
                    "duration": item["duration"],
                    "capacity": item["capacity"],
                    "booked_count": 0,
                },
            )
            created_courses.append(course)
    return created_courses


def get_course_template(name):
    return COURSE_TEMPLATE_MAP.get(name, {})


def get_equipment_template(name):
    return EQUIPMENT_TEMPLATE_MAP.get(name, {})


def get_product_template(name):
    return PRODUCT_TEMPLATE_MAP.get(name, {})


def build_profile_content():
    return {
        "member_benefits": PROFILE_CONTENT["member_benefits"],
        "face_notice": PROFILE_CONTENT["face_notice"],
        "door_notice": PROFILE_CONTENT["door_notice"],
        "visit_notice": PROFILE_CONTENT["visit_notice"],
        "group_buy_notice": PROFILE_CONTENT["group_buy_notice"],
        "entry_guide_text": PROFILE_CONTENT["entry_guide_text"],
        "feedback_examples": PROFILE_CONTENT["feedback_examples"],
    }


def build_ai_content():
    return {
        "page_title": AI_CONTENT["page_title"],
        "welcome_message": AI_CONTENT["welcome_message"],
        "quick_questions": AI_CONTENT["quick_questions"],
        "training_examples": AI_CONTENT["training_examples"],
        "gym_examples": AI_CONTENT["gym_examples"],
        "membership_examples": AI_CONTENT["membership_examples"],
        "equipment_examples": AI_CONTENT["equipment_examples"],
        "demo_questions": AI_CONTENT["demo_questions"],
        "show_sources": AI_CONTENT["show_sources"],
        "show_related_questions": AI_CONTENT["show_related_questions"],
    }


def build_order_content():
    return {
        "refund_note": ORDER_CONTENT["refund_note"],
        "order_status_note": ORDER_CONTENT["order_status_note"],
        "project_summary": ORDER_CONTENT["project_summary"],
        "payment_simulation_note": ORDER_CONTENT["payment_simulation_note"],
        "demo_path": ORDER_CONTENT["demo_path"],
    }


def build_home_content():
    return {
        **GYM_CONTENT,
        "featured_equipment_names": [item["name"] for item in EQUIPMENT_CONTENT[:4]],
        "course_categories": [item["category"] for item in COURSE_CONTENT],
    }
