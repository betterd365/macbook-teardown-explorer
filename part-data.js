export const productInfo = {
  model: 'MacBook Pro 14-inch (Nov 2023) · M3 Pro',
  configuration: 'Apple M3 Pro · 12 核 CPU / 18 核 GPU · 18 GB 统一内存 · 512 GB SSD',
  modelDimensions: '31.26 × 22.12 × 1.55 cm（官方整机尺寸）',
  display: '14.2 英寸 Liquid Retina XDR · 3024 × 1964 · 254 ppi · ProMotion 最高 120 Hz',
  battery: '72.4 Wh 锂聚合物电池',
  source: 'https://support.apple.com/en-us/117736'
};

const apple = 'https://support.apple.com/en-us/117736';
const teardown = 'https://www.ifixit.com/Teardown/MacBook+Pro+14-Inch+Late+2023+M3+Pro+Chip+ID/167049';
const repair = 'https://www.ifixit.com/Device/MacBook_Pro_14%22_Late_2023_%28M3_Pro_and_M3_Max%29';
const fanGuide = 'https://www.ifixit.com/Guide/Macbook+Pro+14-Inch+Late+2023+(M3+Pro+and+M3+Max)+Fans+Replacement/167653';
const unverified = '未公开 / 未核实';

export const partData = {
  bottom_case: {
    label: '底壳 / 下机身',
    role: '承载电池、主板、散热模组与扬声器的铝合金下壳。',
    parameters: [{ label: '整机外形', value: '31.26 × 22.12 × 1.55 cm', type: '官方规格' }],
    designCompany: 'Apple（整机设计）', manufacturer: unverified,
    sources: [{ label: 'Apple 技术规格', url: apple }, { label: 'iFixit 拆机 / 维修资料', url: repair }]
  },
  logic_board: {
    label: '逻辑主板', role: '承载 Apple silicon、存储、供电、接口控制器及无线模块的定制主板。',
    parameters: [{ label: '尺寸', value: '按展示网格测量；非 Apple 发布的裸板规格', type: '按模型测量' }],
    designCompany: 'Apple（主板与系统设计）', manufacturer: unverified,
    sources: [{ label: 'iFixit M3 Pro 芯片识别', url: teardown }, { label: 'iFixit 维修资料', url: repair }]
  },
  soc_m3: {
    label: 'Apple M3 Pro 系统级芯片', role: '集成 CPU、GPU、媒体引擎与统一内存控制等功能的主处理器。',
    parameters: [{ label: '配置', value: '12 核 CPU / 18 核 GPU（本展示配置）', type: '官方规格' }, { label: '识别信息', value: 'APL1203 / 339S01320', type: '拆机识别' }],
    designCompany: 'Apple', manufacturer: '芯片设计：Apple；晶圆代工：未公开 / 未核实',
    sources: [{ label: 'Apple 技术规格', url: apple }, { label: 'iFixit 芯片识别', url: teardown }]
  },
  unified_memory_left: {
    label: '统一内存区域（左）', role: '展示 M3 Pro 封装周边的统一内存区域；模型拆分用于解释布局，不代表该区域可单独升级。',
    parameters: [{ label: '系统统一内存', value: '18 GB（整机配置；非单颗容量）', type: '官方规格' }],
    designCompany: 'Apple（统一内存架构）', manufacturer: unverified,
    sources: [{ label: 'Apple 技术规格', url: apple }, { label: 'iFixit 芯片识别', url: teardown }]
  },
  unified_memory_right: {
    label: '统一内存区域（右）', role: '与 M3 Pro 封装相关的统一内存视觉分区；左右网格不是独立内存容量标注。',
    parameters: [{ label: '系统统一内存', value: '18 GB（整机配置；非单颗容量）', type: '官方规格' }],
    designCompany: 'Apple（统一内存架构）', manufacturer: unverified,
    sources: [{ label: 'Apple 技术规格', url: apple }, { label: 'iFixit 芯片识别', url: teardown }]
  },
  ssd_controller: {
    label: 'SSD 存储控制逻辑（示意）', role: '展示 SSD 控制功能所在区域；拆机芯片识别未将其确认为可单独更换的独立主控封装。',
    parameters: [{ label: '独立器件身份', value: '未在本机型来源中确认；此网格为功能示意', type: '示意估算' }],
    designCompany: 'Apple（存储系统设计）', manufacturer: unverified,
    sources: [{ label: 'iFixit 芯片识别', url: teardown }]
  },
  ssd_nand: {
    label: 'NAND 闪存', role: '非易失存储介质；iFixit 在 M3 Pro 主板识别到 Kioxia NAND 封装。',
    parameters: [{ label: '整机 SSD', value: '512 GB（本展示配置）', type: '官方规格' }, { label: '拆机识别封装', value: 'Kioxia K5A3U08299 / K5A3UN0975，标识为 128 GB NAND', type: '拆机识别' }],
    designCompany: 'Apple（存储系统设计）', manufacturer: 'Kioxia（iFixit 对该拆机样本的芯片识别）',
    sources: [{ label: 'Apple 技术规格', url: apple }, { label: 'iFixit 芯片识别', url: teardown }]
  },
  wifi_bt_module: {
    label: 'Wi‑Fi / Bluetooth 模块', role: '提供无线局域网与蓝牙连接。',
    parameters: [{ label: '无线规格', value: 'Wi‑Fi 6E / Bluetooth 5.3', type: '官方规格' }, { label: '拆机标识', value: '339S01093；iFixit 标注 likely USI', type: '拆机识别 / 推测' }],
    designCompany: 'Apple（无线系统集成）', manufacturer: 'USI（iFixit 推测，未作确定识别）',
    sources: [{ label: 'Apple 技术规格', url: apple }, { label: 'iFixit 芯片识别', url: teardown }]
  },
  power_management_ic: {
    label: '电源管理芯片', role: '主板上的电源转换与管理器件；产品包含多个电源管理封装。',
    parameters: [{ label: '拆机识别', value: 'Apple APL109H / 343S00652 等 PMIC 标识', type: '拆机识别' }],
    designCompany: 'Apple（电源系统设计）', manufacturer: '芯片标识为 Apple；晶圆代工：未公开 / 未核实',
    sources: [{ label: 'iFixit 芯片识别', url: teardown }]
  },
  display_assembly: {
    label: '14.2 英寸显示屏总成', role: 'Liquid Retina XDR 显示屏、玻璃盖板、边框、摄像头开口与显示背板。',
    parameters: [{ label: '显示尺寸', value: '14.2 英寸（对角线）', type: '官方规格' }, { label: '分辨率 / 像素密度', value: '3024 × 1964 / 254 ppi', type: '官方规格' }, { label: '刷新率', value: 'ProMotion 最高 120 Hz', type: '官方规格' }],
    designCompany: 'Apple（显示系统与整机设计）', manufacturer: unverified,
    sources: [{ label: 'Apple 技术规格', url: apple }, { label: 'iFixit 屏幕维修资料', url: repair }]
  },
  display_connector: {
    label: '显示屏连接排线 / 连接区域', role: '连接显示总成与主板，传递显示与摄像头相关信号。',
    parameters: [{ label: '尺寸', value: '按展示网格测量；排线实际走线为示意', type: '按模型测量 / 示意估算' }],
    designCompany: 'Apple（显示系统集成）', manufacturer: unverified,
    sources: [{ label: 'iFixit 拆机 / 维修资料', url: repair }]
  },
  battery: {
    label: '锂聚合物电池组', role: '为整机提供电能的多电芯电池包。',
    parameters: [{ label: '电池能量', value: '72.4 Wh', type: '官方规格' }, { label: '电芯外形', value: '按拆机布局重建；尺寸为展示模型测量', type: '按模型测量' }],
    designCompany: 'Apple（电池系统设计）', manufacturer: unverified,
    sources: [{ label: 'Apple 技术规格', url: apple }, { label: 'iFixit 电池 / 维修资料', url: repair }]
  },
  battery_management_board: {
    label: '电池管理与连接板', role: '电池包与主板之间的连接及电池监测接口展示区域。',
    parameters: [{ label: '器件独立性', value: '连接板位置依据拆机流程；板级尺寸为展示估算', type: '示意估算' }],
    designCompany: 'Apple（电池系统集成）', manufacturer: unverified,
    sources: [{ label: 'iFixit 电池维修资料', url: repair }]
  },
  trackpad: {
    label: 'Force Touch 触控板', role: '支持压力感应与多点触控手势的触控输入组件。',
    parameters: [{ label: '技术', value: 'Force Touch', type: '官方规格' }, { label: '外形尺寸', value: '按展示网格测量；Apple 未在技术规格页列出', type: '按模型测量' }],
    designCompany: 'Apple', manufacturer: unverified,
    sources: [{ label: 'Apple 技术规格', url: apple }, { label: 'iFixit 触控板维修资料', url: repair }]
  },
  keyboard_top_case: {
    label: '键盘 / 上机身', role: '包含铝合金键盘面、Magic Keyboard、Touch ID 视觉区域与掌托。',
    parameters: [{ label: '键盘', value: 'Magic Keyboard；US 键位示意，78 键（布局因地区而异）', type: '官方规格 / 展示选择' }],
    designCompany: 'Apple', manufacturer: unverified,
    sources: [{ label: 'Apple 技术规格', url: apple }, { label: 'iFixit 键盘维修资料', url: repair }]
  },
  speaker_left: {
    label: '左扬声器 / 低音单元', role: '六扬声器系统中的左侧扬声器与力消除低音单元示意。',
    parameters: [{ label: '整机音响', value: '高保真六扬声器系统，含力消除低音单元', type: '官方规格' }, { label: '外壳尺寸', value: '按展示网格测量', type: '按模型测量' }],
    designCompany: 'Apple（声学系统设计）', manufacturer: unverified,
    sources: [{ label: 'Apple 技术规格', url: apple }, { label: 'iFixit 扬声器维修资料', url: repair }]
  },
  speaker_right: {
    label: '右扬声器 / 低音单元', role: '六扬声器系统中的右侧扬声器与力消除低音单元示意。',
    parameters: [{ label: '整机音响', value: '高保真六扬声器系统，含力消除低音单元', type: '官方规格' }, { label: '外壳尺寸', value: '按展示网格测量', type: '按模型测量' }],
    designCompany: 'Apple（声学系统设计）', manufacturer: unverified,
    sources: [{ label: 'Apple 技术规格', url: apple }, { label: 'iFixit 扬声器维修资料', url: repair }]
  },
  fan_left: {
    label: '左侧散热风扇', role: '主动散热模组的一部分；M3 Pro 机型维修步骤涉及两只风扇。',
    parameters: [{ label: '数量', value: '2 只风扇（本机型配置）', type: '拆机资料' }, { label: '外壳尺寸', value: '按展示网格测量', type: '按模型测量' }],
    designCompany: 'Apple（散热系统集成）', manufacturer: unverified,
    sources: [{ label: 'iFixit 风扇维修指南', url: fanGuide }]
  },
  fan_right: {
    label: '右侧散热风扇', role: '与左侧风扇共同驱动散热气流的主动散热模组。',
    parameters: [{ label: '数量', value: '2 只风扇（本机型配置）', type: '拆机资料' }, { label: '外壳尺寸', value: '按展示网格测量', type: '按模型测量' }],
    designCompany: 'Apple（散热系统集成）', manufacturer: unverified,
    sources: [{ label: 'iFixit 风扇维修指南', url: fanGuide }]
  },
  usb_c_board: {
    label: 'USB‑C / Thunderbolt 端口区域', role: '展示三个 Thunderbolt 4 / USB‑C 端口及其板级连接区域（两侧位置依实机布局）。',
    parameters: [{ label: '端口数量与规格', value: '3 × Thunderbolt 4 / USB‑C，最高 40 Gb/s', type: '官方规格' }, { label: '控制器识别', value: 'TI SN25A12 USB‑C controller（iFixit 芯片识别）', type: '拆机识别' }],
    designCompany: 'Apple（端口系统设计）', manufacturer: '端口板供应商未公开 / 未核实；Texas Instruments 为被识别出的控制器芯片厂商',
    sources: [{ label: 'Apple 技术规格', url: apple }, { label: 'iFixit 芯片识别', url: teardown }]
  },
  magsafe_board: {
    label: 'MagSafe 3 充电接口区域', role: '显示 MagSafe 3 磁吸充电接口及其与内部电路的连接。',
    parameters: [{ label: '接口', value: 'MagSafe 3', type: '官方规格' }, { label: '板件尺寸', value: '按展示网格测量', type: '按模型测量' }],
    designCompany: 'Apple（接口与充电系统设计）', manufacturer: unverified,
    sources: [{ label: 'Apple 技术规格', url: apple }, { label: 'iFixit MagSafe 维修资料', url: repair }]
  },
  audio_board: {
    label: '音频接口区域', role: '显示右侧 3.5 mm 耳机接口与其内部连接区域；音频放大/编解码器位于主板。',
    parameters: [{ label: '耳机接口', value: '3.5 mm', type: '官方规格' }, { label: '音频器件', value: '主板可识别 Cirrus Logic CS42L84A 编解码器、TI 音频放大器', type: '拆机识别' }],
    designCompany: 'Apple（音频系统设计）', manufacturer: 'Cirrus Logic / Texas Instruments（对应主板器件，不代表接口板供应商）',
    sources: [{ label: 'Apple 技术规格', url: apple }, { label: 'iFixit 芯片识别', url: teardown }]
  }
};
// Reconstructed Mesh bounds from the Blender asset (cm). These are presentation
// geometry measurements, not Apple engineering dimensions.
const modelDimensions = {
  bottom_case: '31.26 × 22.12 × 1.42 cm',
  logic_board: '23.20 × 7.32 × 0.27 cm',
  soc_m3: '2.80 × 2.70 × 0.34 cm',
  unified_memory_left: '1.40 × 1.21 × 0.28 cm',
  unified_memory_right: '1.40 × 1.21 × 0.28 cm',
  ssd_controller: '1.20 × 1.00 × 0.24 cm',
  ssd_nand: '2.40 × 0.90 × 0.22 cm（两颗封装合并展示）',
  wifi_bt_module: '2.00 × 1.80 × 0.22 cm',
  power_management_ic: '1.20 × 1.00 × 0.24 cm',
  display_assembly: '31.26 × 21.50 × 0.58 cm（面板宽 × 高 × 厚）',
  display_connector: '10.00 × 1.15 × 0.15 cm（排线展开示意）',
  battery: '28.60 × 12.13 × 0.72 cm（六片电芯展示体）',
  battery_management_board: '4.50 × 3.00 × 0.19 cm',
  trackpad: '13.50 × 8.30 × 0.21 cm',
  keyboard_top_case: '30.94 × 21.72 × 0.37 cm',
  speaker_left: '3.90 × 14.40 × 0.95 cm',
  speaker_right: '3.90 × 14.40 × 0.95 cm',
  fan_left: '6.90 × 6.60 × 0.74 cm',
  fan_right: '6.90 × 6.60 × 0.74 cm',
  usb_c_board: '31.20 × 13.55 × 0.51 cm（左右端口区域合并布局）',
  magsafe_board: '3.30 × 2.35 × 0.50 cm',
  audio_board: '4.09 × 3.44 × 0.65 cm'
};
for (const [name, value] of Object.entries(modelDimensions)) {
  partData[name].parameters.unshift({ label: '模型外形', value, type: '按模型测量' });
}
