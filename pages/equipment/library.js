const PART_META = {
  有氧: {
    part_id: 1,
    part_name: '有氧',
    location: '有氧区',
    training_focus: '提升心肺耐力、燃脂效率和训练热身质量',
    default_target: '心肺 / 臀腿'
  },
  手臂: {
    part_id: 2,
    part_name: '手臂',
    location: '自由力量区',
    training_focus: '强化手臂围度、孤立发力能力和上肢控制感',
    default_target: '肱二头 / 肱三头 / 前臂'
  },
  肩部: {
    part_id: 3,
    part_name: '肩部',
    location: '肩部训练区',
    training_focus: '提升肩部稳定性、线条感和上肢推举表现',
    default_target: '三角肌 / 斜方肌'
  },
  背部: {
    part_id: 4,
    part_name: '背部',
    location: '背部训练区',
    training_focus: '建立背部发力感，提升拉力动作稳定性和体态支撑',
    default_target: '背阔肌 / 菱形肌'
  },
  胸部: {
    part_id: 5,
    part_name: '胸部',
    location: '胸部训练区',
    training_focus: '增强胸部推力、挤压感和上肢整体力量表现',
    default_target: '胸大肌 / 三角肌前束'
  },
  臀腿: {
    part_id: 6,
    part_name: '臀腿',
    location: '下肢训练区',
    training_focus: '提升下肢力量、稳定性和臀腿线条表现',
    default_target: '臀大肌 / 股四头 / 腘绳肌'
  }
}

const RAW_GIF_FILES = {
  有氧: [
    '无动力跑步机-剪裁.gif',
    '椭圆机-剪裁.gif',
    '登山机-剪裁.gif',
    '跑步机-剪裁.gif'
  ],
  手臂: [
    '上斜哑铃交替弯举-剪裁.gif',
    '仰卧哑铃肱三头肌臂屈伸-剪裁.gif',
    '佐特曼弯举-剪裁.gif',
    '双杠臂屈伸-剪裁.gif',
    '反握杠铃牧师凳弯举-剪裁.gif',
    '器械臂屈伸-剪裁.gif',
    '站姿曲杆弯举-剪裁.gif',
    '绳索臂屈伸-剪裁.gif'
  ],
  肩部: [
    '单臂哑铃侧平举-剪裁.gif',
    '单臂绳索侧平举-剪裁.gif',
    '哑铃推举-剪裁.gif',
    '器械后飞鸟-剪裁.gif',
    '坐姿哑铃侧平举-剪裁.gif',
    '坐姿哑铃飞鸟-剪裁.gif',
    '坐姿杠铃推肩-剪裁.gif',
    '推肩器推肩-剪裁.gif',
    '绳索交叉侧平举-剪裁.gif',
    '绳索反向飞鸟-剪裁.gif',
    '阿诺德哑铃推举-剪裁.gif'
  ],
  背部: [
    'T杠划船-剪裁.gif',
    'V把高位下拉-剪裁.gif',
    '上斜俯身哑铃划船-剪裁.gif',
    '俯身杠铃划船-剪裁.gif',
    '坐姿划船-剪裁.gif',
    '引体向上-剪裁.gif',
    '辅助引体向上-剪裁.gif',
    '高位下拉-剪裁.gif'
  ],
  胸部: [
    '上斜哑铃卧推-剪裁.gif',
    '上斜杠铃卧推-剪裁.gif',
    '史密斯杠铃上斜卧推-剪裁.gif',
    '史密斯杠铃下斜卧推-剪裁.gif',
    '史密斯杠铃平板卧推-剪裁.gif',
    '哑铃平板卧推-剪裁.gif',
    '杠铃平板卧推-去水印.gif',
    '绳索夹胸-剪裁.gif',
    '臂屈伸-去水印.gif',
    '蝴蝶机夹胸-去水印.gif'
  ],
  臀腿: [
    '倒蹬-剪裁.gif',
    '史密斯倒蹬-剪裁.gif',
    '哈克深蹲-剪裁.gif',
    '哑铃直腿硬拉-剪裁.gif',
    '器械后抬腿-剪裁.gif',
    '器械臀内收-剪裁.gif',
    '杠铃深蹲-剪裁.gif',
    '杠铃臀推-剪裁.gif'
  ]
}

function stripGifSuffix(fileName = '') {
  return String(fileName)
    .replace(/-(剪裁|去水印)\.gif$/u, '')
    .replace(/\.gif$/u, '')
}

function inferTargetMuscles(name, part) {
  if (part === '有氧') {
    if (/跑步机/u.test(name)) return '心肺 / 臀腿 / 核心'
    if (/椭圆机/u.test(name)) return '心肺 / 臀腿'
    if (/登山机/u.test(name)) return '心肺 / 臀腿 / 臀大肌'
    return PART_META[part].default_target
  }
  if (part === '手臂') {
    if (/弯举/u.test(name)) return '肱二头 / 前臂'
    if (/屈伸/u.test(name)) return '肱三头'
    return PART_META[part].default_target
  }
  if (part === '肩部') {
    if (/侧平举/u.test(name)) return '三角肌中束'
    if (/飞鸟|反向/u.test(name)) return '三角肌后束 / 上背'
    if (/推举|推肩/u.test(name)) return '三角肌前束 / 中束 / 肱三头'
    return PART_META[part].default_target
  }
  if (part === '背部') {
    if (/下拉|引体/u.test(name)) return '背阔肌 / 肱二头'
    if (/划船/u.test(name)) return '背阔肌 / 菱形肌 / 后束'
    return PART_META[part].default_target
  }
  if (part === '胸部') {
    if (/卧推/u.test(name)) return '胸大肌 / 三角肌前束 / 肱三头'
    if (/夹胸|飞鸟/u.test(name)) return '胸大肌 / 胸肌中缝'
    if (/臂屈伸/u.test(name)) return '下胸 / 肱三头'
    return PART_META[part].default_target
  }
  if (part === '臀腿') {
    if (/深蹲|哈克|倒蹬/u.test(name)) return '股四头 / 臀大肌 / 腘绳肌'
    if (/臀推|后抬腿/u.test(name)) return '臀大肌 / 臀中肌'
    if (/内收/u.test(name)) return '大腿内收肌群'
    if (/直腿硬拉/u.test(name)) return '腘绳肌 / 臀大肌 / 下背稳定'
    return PART_META[part].default_target
  }
  return ''
}

function buildDescription(name, part) {
  if (part === '有氧') {
    if (/无动力跑步机/u.test(name)) return '无动力跑步机依赖下肢主动蹬伸驱动跑带，能够同步提升步频控制、髋膝踝协同与无氧耐力输出，常用于冲刺间歇和专项体能训练。'
    if (/跑步机/u.test(name)) return '跑步机属于基础心肺训练器械，可用于稳态有氧、间歇跑和热身激活，有助于提升摄氧效率、下肢循环与整体代谢水平。'
    if (/椭圆机/u.test(name)) return '椭圆机通过闭链低冲击轨迹完成持续有氧输出，适合在保护膝踝关节的前提下提升心肺耐力与下肢耐力。'
    if (/登山机/u.test(name)) return '登山机强调髋伸与膝伸的重复发力，能明显提高心率区间并强化臀腿后链参与度，适合燃脂和体能强化。'
    return `${name}属于有氧区常用训练项目，可用于提升心肺功能、能量消耗与基础运动表现。`
  }
  if (part === '手臂') {
    if (/上斜.*弯举/u.test(name)) return '上斜哑铃交替弯举通过肩关节轻度伸展位拉长肱二头肌长头，能够放大离心阶段张力并强化顶峰收缩感。'
    if (/佐特曼弯举/u.test(name)) return '佐特曼弯举结合正握向心与反握离心，兼顾肱二头肌、肱桡肌和前臂旋后控制，是上臂与前臂协同训练动作。'
    if (/牧师凳弯举/u.test(name)) return '牧师凳弯举通过固定上臂位置减少代偿，能显著提高肘关节屈曲阶段的孤立度，适合强化肱二头肌短头发力。'
    if (/曲杆弯举/u.test(name)) return '曲杆弯举能够在相对舒适的腕部角度下完成肘屈训练，适合提升肱二头肌围度和重复输出能力。'
    if (/仰卧哑铃肱三头肌臂屈伸/u.test(name)) return '仰卧哑铃肱三头肌臂屈伸以肘伸为主导，可充分刺激肱三头肌长头，对推举类动作的锁定能力提升明显。'
    if (/绳索臂屈伸/u.test(name)) return '绳索臂屈伸在全程张力环境下强化肱三头肌向心收缩，适合用于容量训练和充血阶段。'
    if (/双杠臂屈伸|器械臂屈伸/u.test(name)) return `${name}强调肘伸与肩关节稳定协同，适合提升肱三头肌力量输出，并辅助胸肩推类动作表现。`
    return `${name}主要用于手臂孤立训练，能够提升肘屈或肘伸阶段的募集效率、肌肉围度与动作控制能力。`
  }
  if (part === '肩部') {
    if (/侧平举/u.test(name)) return `${name}主要针对三角肌中束，适合提升肩宽视觉效果，并优化肩关节外展阶段的张力控制。`
    if (/飞鸟|反向飞鸟/u.test(name)) return `${name}重点刺激三角肌后束与肩胛后缩肌群，可改善圆肩体态并增强上背稳定。`
    if (/推举|推肩|阿诺德/u.test(name)) return `${name}属于肩部推举类动作，强调肩关节屈曲与外展协同，对提升三角肌整体力量和上肢垂直推举能力效果明显。`
    return `${name}适合进行肩部专项强化，能够帮助提升肩关节稳定性、肩带控制与上半身线条表现。`
  }
  if (part === '背部') {
    if (/下拉/u.test(name)) return `${name}是垂直拉训练代表动作，重点强化背阔肌下压与肩胛下沉控制，适合建立背部发力路径。`
    if (/引体/u.test(name)) return `${name}强调自身体重条件下的垂直拉力输出，对背阔肌、肱二头肌及核心稳定均有较高要求。`
    if (/划船/u.test(name)) return `${name}属于水平拉训练动作，强调肩胛后缩与肘部后引，能够提升背部厚度、姿态稳定和拉力表现。`
    return `${name}是背部训练中的高频动作，适合建立背部发力感并提升拉力动作质量。`
  }
  if (part === '胸部') {
    if (/卧推/u.test(name)) return `${name}属于胸部复合推举动作，能够同时调动胸大肌、三角肌前束与肱三头肌，对上肢最大力量和训练容量提升显著。`
    if (/夹胸/u.test(name)) return `${name}以肩关节水平内收为主，能强化胸大肌中后段收缩感，适合作为胸部孤立补充训练。`
    if (/臂屈伸/u.test(name)) return `${name}在身体前倾条件下可显著增加下胸与肱三头肌参与度，适合用于胸部末端强化与自重力量提升。`
    return `${name}适合胸部推举或挤压训练，能够帮助提升胸部力量表现和肌肉参与度。`
  }
  if (part === '臀腿') {
    if (/深蹲|哈克/u.test(name)) return `${name}属于下肢基础复合动作，强调髋膝同步屈伸，可全面提升股四头肌、臀大肌与核心抗屈稳定能力。`
    if (/倒蹬/u.test(name)) return `${name}通过固定轨迹提升下肢推蹬输出，适合在降低平衡要求的同时增强股四头肌与臀腿力量。`
    if (/臀推/u.test(name)) return '杠铃臀推以髋伸顶峰发力为核心，能够高效强化臀大肌募集，适合提升臀部力量、爆发力与线条表现。'
    if (/后抬腿/u.test(name)) return `${name}可集中刺激臀大肌与臀中肌，是下肢训练中常用的臀部孤立补强动作。`
    if (/内收/u.test(name)) return `${name}主要用于强化大腿内收肌群与骨盆稳定，对改善下肢发力路径和动作对称性有帮助。`
    if (/直腿硬拉/u.test(name)) return `${name}强调髋主导铰链模式，可有效训练腘绳肌、臀大肌与后侧动力链的离心控制能力。`
    return `${name}适合下肢力量与臀腿塑形训练，能够帮助提升稳定性、爆发力和整体发力效率。`
  }
  return `${name}适合进行专项力量训练。`
}

function buildActionTips(name) {
  if (/跑步机|椭圆机|登山机/u.test(name)) {
    return '进入动作前先完成 3 至 5 分钟低强度热身，训练中维持均匀呼吸节奏、稳定步频和躯干中立位，再按目标心率逐步提升速度或阻力。'
  }
  if (/弯举/u.test(name)) {
    return '肩关节保持中立，上臂尽量固定，向心阶段专注肘屈发力，离心阶段控制下放速度以延长肌肉张力时间。'
  }
  if (/屈伸/u.test(name)) {
    return '肘部保持相对固定并朝向前下方，发力时专注完成肘伸，动作末端充分收缩肱三头肌，避免肩关节代偿。'
  }
  if (/侧平举/u.test(name)) {
    return '采用轻度屈肘姿势完成外展，抬至接近肩高即可，主动维持三角肌中束张力，避免借助惯性摆荡。'
  }
  if (/飞鸟|反向飞鸟/u.test(name)) {
    return '先固定肩胛位置，再完成肩关节水平外展或内收；顶峰短暂停顿 1 秒，离心阶段保持持续张力不过度松弛。'
  }
  if (/推举|推肩|阿诺德/u.test(name)) {
    return '核心与臀部主动收紧，推举轨迹保持在肩关节稳定平面，顶端保留微屈肘避免完全锁死，保持持续受力。'
  }
  if (/下拉|引体/u.test(name)) {
    return '动作起始先完成肩胛下沉，再通过肘部向下向后引导发力；胸椎微伸但不后仰借力，保持背阔肌主导。'
  }
  if (/划船/u.test(name)) {
    return '维持脊柱中立与核心张力，拉动时用肘部引导向后，顶峰阶段完成肩胛后缩并短暂停顿感受背部收紧。'
  }
  if (/卧推/u.test(name)) {
    return '准备阶段先完成肩胛后缩下沉并建立下肢支撑，杠铃或哑铃下放至可控深度后垂直向上推起，保持胸部主动发力。'
  }
  if (/夹胸/u.test(name)) {
    return '保持肘部轻屈并以弧线轨迹完成水平内收，顶峰位置主动挤压胸肌，离心阶段缓慢打开保持胸部张力。'
  }
  if (/深蹲|哈克|倒蹬/u.test(name)) {
    return '下放阶段保持膝盖与脚尖方向一致，髋膝同步屈曲，核心全程稳定；起身时通过脚跟与全脚掌均匀发力完成伸展。'
  }
  if (/臀推/u.test(name)) {
    return '上背稳定贴合支撑点，发力时以髋伸驱动杠铃上行，顶峰主动后倾骨盆并夹紧臀部，避免腰椎过伸。'
  }
  if (/直腿硬拉/u.test(name)) {
    return '全程以髋铰链模式主导动作，保持脊柱中立和杠铃贴近身体，下放时重点感受腘绳肌离心拉伸。'
  }
  if (/内收/u.test(name)) {
    return '坐姿保持骨盆中立，向心阶段主动完成髋内收，离心阶段控制打开幅度，避免快速回弹造成关节压力。'
  }
  if (/后抬腿/u.test(name)) {
    return '躯干稳定后再进行髋伸，动作末端主动收缩臀大肌并短暂停顿，避免腰椎代偿性后伸。'
  }
  return '训练时先用轻重量熟悉动作轨迹，再逐步提升强度，保持全程控制。'
}

function buildPrecautions(name, part) {
  if (part === '有氧') {
    return '首次使用应从低速度或低阻力区间开始，并根据心率与主观体感逐步进阶；如出现头晕、胸闷或呼吸异常应立即停止。'
  }
  if (/弯举|屈伸/u.test(name)) {
    return '避免通过躯干摆动制造惯性，训练重量应控制在目标次数区间内，离心阶段必须保持可控以降低肘关节压力。'
  }
  if (/推举|推肩|卧推/u.test(name)) {
    return '训练前应充分激活肩袖与肩胛稳定肌群，正式组避免过度腰椎代偿；大重量训练建议使用保护架或同伴保护。'
  }
  if (/下拉|划船|引体/u.test(name)) {
    return '不要为追求负重而牺牲肩胛控制或借助惯性后仰，若无法维持背部持续张力应及时下调重量。'
  }
  if (/深蹲|倒蹬|哈克|硬拉|臀推/u.test(name)) {
    return '开始前需完成髋、膝、踝与核心激活，训练中优先保证脊柱稳定和关节对线；动作幅度应根据活动度与训练经验逐步推进。'
  }
  return '训练中保持核心稳定与节奏可控，若出现明显关节疼痛、麻木或失去动作控制，应立即停止并调整训练方案。'
}

const EQUIPMENT_LIBRARY = Object.keys(RAW_GIF_FILES).flatMap((part) => {
  const meta = PART_META[part]
  return RAW_GIF_FILES[part].map((fileName, index) => {
    const name = stripGifSuffix(fileName)
    return {
      id: meta.part_id * 1000 + index + 1,
      name,
      part_id: meta.part_id,
      part_name: meta.part_name,
      location: meta.location,
      target_muscles: inferTargetMuscles(name, part),
      training_focus: meta.training_focus,
      description: buildDescription(name, part),
      action_tips: buildActionTips(name),
      precautions: buildPrecautions(name, part),
      miniapp_gif_path: `/器械库动图/${part}/${fileName}`,
      status: 'idle'
    }
  })
})

module.exports = {
  EQUIPMENT_LIBRARY
}
