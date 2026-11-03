"""Prepare six coherent visual-design prompts. Does not modify game files."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
PRICES = json.loads((REPO/'docs/balance/2026-11-01-vehicle-economy/pricing-candidate.json').read_text())
cars = {x['grade']: x for x in PRICES['vehicles']}
snapshot = {
    'status': 'illustrative-concept-state-not-user-save-not-a-game-replay',
    'wallet': 680, 'reputation': 96, 'energy': 78, 'heroLevel': 5,
    'heroName': '澄川骑手', 'area': '澄川县', 'npcOwnedHere': 1, 'npcLimitHere': 2,
    'nextNpcRecruitmentPrice': 110, 'heroVehicle': {'grade': 'C', 'level': 5},
    'ownedCars': {'D': 2, 'C': 1},
    'npc': {'name': '阿航', 'level': 1, 'state': '配送中', 'vehicle': 'D', 'vehicleLevel': 1},
    'today': {'deliveryIncome': 222, 'supplies': 5, 'netDeliveryIncome': 217,
              'heroOrders': 12, 'npcOrders': 3, 'totalOrders': 15,
              'heroDistanceKm': 24, 'onlineMinutes': 38},
    'lifetime': {'initialCash': 100, 'deliveryIncome': 1190, 'recruitment': 100,
                 'vehiclePurchases': 470, 'vehicleUpgrades': 15, 'supplies': 25,
                 'totalExpenses': 610, 'completedOrders': 82, 'heroDistanceKm': 186},
    'sevenDayIncome': [0, 58, 104, 176, 240, 390, 222],
    'mapNpcAdditions': [2, 4, 6, 8, 10], 'mapNpcTotals': [2, 6, 12, 20, 30],
    'vehiclePrices': {k:v['purchasePriceYuan'] for k,v in cars.items()},
    'heroCLevel5UpgradeSpent': cars['C']['levels'][4]['cumulativeUpgradeYuan'],
    'heroCLevel5NextUpgrade': cars['C']['levels'][5]['upgradeToThisLevelYuan'],
}

common = '''Use case: ui-mockup
Asset type: one complete portrait mobile game page, 9:16 matching reference 1, high-fidelity original game concept. Not a multi-screen board and no device bezel.
Project: a Chinese urban delivery management game. This is one of a SIX-PAGE COHERENT UI SERIES, not a fresh art direction.
Input image 1 is the USER-SELECTED MASTER: cream/ivory panels and B-style information architecture over C-style detailed rainy urban anime city painting. Treat image 1 as the strict shared design-system and protagonist/NPC portrait reference. Additional input roles, when present, are specified below.
Shared style: warm ivory surfaces, restrained fine warm-grey borders, charcoal Chinese typography, amber/orange primary actions, blue delivery states, grey locked states; refined painterly urban anime and adult character faces, cool wet streets and warm shop lighting. Never use chibi, plastic toy 3D, fantasy jewel borders, premium gems, unrelated cyberpunk effects or a website/dashboard aesthetic.
SHARED HEADER, preserve the same layout, scale and character identity as input 1: top-left dark-haired orange-jacket adult protagonist portrait with '澄川骑手' and 'Lv.5'; location chip '澄川县'; top-right ivory status strip with coin '680', heart '96', energy '体力 78/100'. All displayed quantities integer, no decimal points. Do not invent a second currency.
SHARED FOOTER, preserve the same cream navigation geometry and icons as input 1: exactly '骑手', '车辆', a larger central orange circular '抢单', '地图', '账单'. Highlight only the relevant section as specified; keep labels readable and consistent. Page content ends above this footer and never overlaps it. No extra sixth navigation tab.
Page titles below the global header use the same understated type treatment. Use clear generous spacing and a readable visual hierarchy. List content may continue below the visible scroll area; do not shrink all typography to force an entire catalogue onto one screen. Chinese words must be crisp, intentional and verbatim; avoid invented filler text.
This is an illustrative state, not the user's real save. Do not print technical instructions, 'concept', sample-data disclaimers or screen IDs inside the page. No logos, watermark, phone frame or external explanatory captions.
'''

pages = {
 '01-home': {
  'label': '首页',
  'body': '''Primary request: refine the idle HOME page from reference 1 while retaining its selected composition. The central view is a modern riverside Chinese county with C-style rooftops, realistic road hierarchy, crosswalks, trees, shop windows, wet road reflections and soft after-rain daylight. Preserve a top-down road-map feeling, not an isometric city builder. The map occupies most of the screen and remains legible.
Keep the working-team strip just above the footer: title '骑手 1/2'; adult NPC portrait from reference 1, name '阿航', blue state '配送中'; second slot is a silhouette and '招募 ¥110'. Do not turn it into an already-hired second NPC. Show only the player's scooter and one working NPC as owned vehicles; ambient traffic cars are fine. One small locate button and a '15 m' scale.
There is no active player order, so no numbered destination pins, no delivery route, no order sheet, no acceleration or food/water buttons. The central orange '抢单' is the one main player action. Keep the footer neutral apart from the central main action.
Use the same portrait identities and same 680/96/78 values as the other five pages. Match the cool-map/warm-UI relationship of reference 1 without making the scene pitch-black night.'''
 },
 '02-riders': {
  'label': '骑手页面',
  'body': '''Primary request: the RIDER MANAGEMENT page in the same game. Show title '骑手' with a small '本图 1/2' summary. The content is a warm ivory management panel with a subtle dark rainy-city background only at its margins; do not put another giant map behind every card.
Additional image 2 fixes the accepted protagonist's full-body identity and orange/charcoal practical courier outfit. Additional image 3 is character refinement and technical-fabric rendering reference only; do not replace the protagonist's face with its male character. Additional image 4 gives the exact C scooter shape, yellow/cream body, square lamp and yellow rear delivery box.
The upper main card is explicitly '主角 · 澄川骑手' with 'Lv.5', a refined half-body adult protagonist illustration and a restrained experience display '经验 620'. Current vehicle is 'C级 · 品牌电动车' and '车辆 Lv.5'; show small C scooter preview. A compact stat row says '速度 18 km/h' and '载重 11 kg'. Actions '配置车辆' and '升级车辆 ¥7'. Do not sell coin-based protagonist experience training.
Below is one distinct NPC card: '阿航', 'Lv.1', blue '配送中', vehicle 'D级 · 旧电动车', '今日收入 ¥30'. Keep his attractive black-haired technical courier portrait from reference 1, recognizably different from the orange-jacket protagonist. Actions '配置车辆' and '培养' (no invented training price).
The final recruitment card is a silhouette, '第2名骑手', '招募 ¥110'. It is not an owned or working rider. There is one free D instance in the illustrative inventory, but no need to expose internal IDs. No manual order-dispatch buttons: NPCs accept and deliver automatically after being assigned a vehicle. '骑手' is the active footer section.
This page owns vehicle assignment and rider training; do not put a car-purchase catalogue inside it. The art must feel like the same cream/orange game, not a science-fiction character gacha screen.'''
 },
 '03-vehicles': {
  'label': '车辆页面',
  'body': '''Primary request: the VEHICLE SHOP page. Title '车辆商城', same global header and ivory/orange footer, '车辆' active. Use a subtle county garage/display nook as the hero panel, with warm local light and a glimpse of the same rainy city, not a different heavy metal or futuristic UI skin.
Additional image 2 supplies the exact selected C scooter shape. Additional image 3 supplies existing vehicle silhouettes across tiers: old/simple delivery scooters, blue long-range scooter, darker large motorcycle, red sports motorcycle and premium later bikes. These inputs are shape references only; ignore their contact-sheet labels/backgrounds. Do not redesign all vehicles into the same scooter with recolours.
Hero preview is the selected C model, the yellow-and-cream scooter facing right in a three-quarter side view, wheels grounded. Name 'C级 · 品牌电动车', '已拥有 1辆'. Its NEW-PURCHASE base stats are '速度 17 km/h', '载重 10 kg', '收入 +32%'. Clear orange primary '购买 ¥320'. Newly bought car is Lv.1. Do not use the protagonist's current upgraded C stats 18/11 as the shop's new-model base stats.
Tabs '全部车型' and '已拥有'; selected tab '全部车型'. Below, a two-column scrolling card grid with the first six models visible: 'D ¥150 已拥有2', 'D+ ¥220 已拥有0', 'C ¥320 已拥有1', 'C+ ¥460 已拥有0', 'B ¥680 未解锁', 'B+ ¥1000 未解锁'. Selected C card outlined orange. Locked B/B+ remain readable with a small grey lock/capsule, not a large blocking overlay. A small '10款车型' catalogue label may indicate that higher models continue below.
The shop displays and buys MODELS and aggregated ownership only. No '主角使用中', no NPC-assignment labels, no equipment checkmarks and no automatic equip toggle. Every purchase creates another independent car; actual assignment is on the rider page. Preserve the same font, panel borders, chip shapes and amber buttons as the other pages.'''
 },
 '04-orders': {
  'label': '抢单页面',
  'body': '''Primary request: the ORDER LOBBY page before departure. Title '抢单大厅', status '已选 2/3', small refresh action '刷新 2/2'. It is a cream in-game page over subtle rainy-city margins, not a physical phone drawn inside a phone.
Show three complete food-order cards and the hint of a fourth below the scroll area. Each has a painterly appetizing food thumbnail, clear name, fee, deadline, pickup and destination, integer weight and a selectable state. The first two are selected with a modest amber check and border, the third is unselected.
Card 1: '牛肉饭', '¥16', '30分钟内送达', '2 kg', '取 阿婆小馆', '送 沿河小区', '4 km'.
Card 2: '鲜虾面', '¥16', '25分钟内送达', '2 kg', '取 河畔面馆', '送 春和里', '3 km'.
Card 3: '水果拼盘', '¥16', '35分钟内送达', '3 kg', a small '易损' tag, '取 鲜果铺', '送 桂花里'.
Do not invent a per-card fee inconsistent with the sample vehicle; these illustrative quotes can reflect the user's car/experience bonuses over the base fee10. Each card has its own deadline. No shared countdown pretending all three are one order.
A fixed summary above the shared footer says '预计收入 ¥32' and '载重 4/11 kg', with a clear wide orange '选择路线 2/3' action. The central footer '抢单' stays the page's active section. This page is selection/planning, not active delivery, so no acceleration button, rain penalty popups, supply buttons or running-car timer.
Preserve the same character header, coins680, reputation96 and stamina78; selecting is not already a successful delivery and must not increase the displayed wallet.'''
 },
 '05-maps': {
  'label': '地图页面',
  'body': '''Primary request: the REGION PROGRESSION page, clearly different from the live home map. Title '地图旅程', small overview '5张地图 · 30名骑手'. Keep the same ivory/orange design system with five vertically connected region cards and small urban-anime landscape thumbnails. The visual language and map materials must match the selected C-style city; don't turn it into a fantasy island map or a 3D board game.
All five region names and rider counts should be visible in a readable vertical journey:
1 '县城' — '当前地图', '新增2名 · 累计2名', 'D / D+ / C / C+'; thumbnail of the current river town. Mark as unlocked/current.
2 '城市' — '可解锁', '新增4名 · 累计6名', 'B / B+'; denser modern streets thumbnail and a modest amber '解锁新地图' action. This is an illustrative available-next-stage state; do not put in unapproved numeric unlock gates.
3 '省会' — grey '未解锁', '新增6名 · 累计12名', 'A'; civic park/urban avenues thumbnail.
4 '一线' — grey '未解锁', '新增8名 · 累计20名', 'S / SS'; taller business district thumbnail.
5 '国际都会' — grey '未解锁', '新增10名 · 累计30名', 'SSS'; coastal city lights thumbnail.
A small footer note above navigation can say '换地图保留骑手、车辆和成长'. Maximum30 recruitable NPCs, plus the protagonist, never80 or81. Current county remains 1/2 hired in other screens; showing the next region as available does not auto-recruit anyone or automatically switch the player's location.
Footer '地图' active. Use subtle connecting lines, not decorative locks larger than the city art. Different region lighting is acceptable but retain the same painterly materials, type and panel style.'''
 },
 '06-bills': {
  'label': '账单页面',
  'body': '''Primary request: the BILL/LEDGER page, same cream Chinese mobile game design, not an office analytics dashboard or bank app. Title '经营账单'; tabs '今日' and '累计', with '今日' selected. Keep the header portrait and wallet680, reputation96 and stamina78 unchanged.
Three primary summary values: '配送收入 ¥222', '补给支出 ¥5', '配送净赚 ¥217'. Under them, three quieter metrics: '完成15单', '主角里程24 km', '在线38分钟'. A small line can clarify '主角12单 · 骑手3单'. NPC revenue is already included, never add it twice.
One simple restrained amber bar chart titled '近7日配送收入'. Seven values exactly 0,58,104,176,240,390,222, summing1190. Use small day labels, not a wall of tiny axis numbers or a spreadsheet grid. Keep a warm minimal illustration of paper/receipt texture, consistent with the game.
Lower cumulative account section shows '累计配送收入 ¥1190', '累计支出 ¥610', and four expense rows '招募骑手 ¥100', '购买车辆 ¥470', '车辆升级 ¥15', '补给 ¥25'. These expenses sum610. Initial cash100 plus total earned1190 minus total expenses610 equals wallet680. A compact '初始资金 ¥100' line can complete the balance explanation. Do not invent taxes, wages, loan payments or new revenue sources.
The sample lifetime includes buying a C car320 and an extra D150, hiring the first rider100, C upgrades15 and supplies25. This is not required text inside the UI, only the reason for the numbers. The page should communicate earnings versus spending clearly with a small number of strong cards and rows.
Footer '账单' active. No delivery countdown, recruitment call-to-action, vehicle purchase button or 3D chart ornaments on this screen.'''
 },
}

ROOT.mkdir(parents=True, exist_ok=True)
(ROOT/'sample-state.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n')
for key,page in pages.items():
    (ROOT/(key+'-prompt.txt')).write_text(common+'\n'+page['body']+'\n')
(ROOT/'page-specs.json').write_text(json.dumps({k:{'label':v['label'],'prompt':k+'-prompt.txt'} for k,v in pages.items()},ensure_ascii=False,indent=2)+'\n')
print('六份完整实际提示词已生成：',', '.join(pages))
print('样例余额核对：',snapshot['lifetime']['initialCash']+snapshot['lifetime']['deliveryIncome']-snapshot['lifetime']['totalExpenses'])
print('费用明细合计：',sum(snapshot['lifetime'][x] for x in ['recruitment','vehiclePurchases','vehicleUpgrades','supplies']))
print('7日配送收入合计：',sum(snapshot['sevenDayIncome']))
print('C车5级累计升级/下一级：',snapshot['heroCLevel5UpgradeSpent'],snapshot['heroCLevel5NextUpgrade'])
print('仅准备概念提示词与样例数据；没有操作游戏、测试或存档。')
