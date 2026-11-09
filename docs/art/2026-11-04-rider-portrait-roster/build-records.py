import json,pathlib
p=pathlib.Path(__file__).parent
rows=[
("阿航","male 26, long angular face, narrow amber eyes, thick angled brows, tousled black undercut, black jacket mustard collar","果断"),
("小夏","female 25, heart face, sharp violet eyes, straight eyebrows, short asymmetrical purple bob, white high collar black jacket","敏捷"),
("阿杰","male 28, broad cheekbones square chin, relaxed brown eyes, sandy blond wavy side part, gray jacket blue collar","开朗"),
("小雨","female 24, round cheeks, large warm brown eyes, curved brows, black high ponytail wispy bangs, coral collar charcoal jacket","亲切"),
("阿宁","male 27, slender oval face, cool gray eyes, fine straight brows, silver layered short hair, navy stand collar","沉静"),
("晓晴","female 30, oval face freckles, hazel eyes, chestnut messy bun, round glasses, cream collar teal jacket","细致"),
("阿诚","male 32, rectangular face broad jaw, deep brown eyes, black swept quiff, orange black jacket","可靠"),
("小岚","female 26, diamond face, blue eyes, cobalt chin length hair, white black sports cap, navy jacket","洒脱"),
("阿川","male 25, triangular face pointed chin, dark red eyes, vivid red curly crop, charcoal gold collar","热情"),
("阿森","male 29, long face high cheekbones, light brown eyes, ash lavender parted hair, forest green collar","温和"),
("小禾","female 25, soft square face, green eyes, pink loose braid over shoulder, black jacket rose collar","乐观"),
("知遥","female 34, long oval face, hooded dark eyes, sleek black low bun center part, burgundy collar silver stud","专注"),
("阿岳","male 38, wide square face, tan skin, heavy brows, close black buzz cut, stubble, olive high collar","稳重"),
("星澄","female 28, angular cheekbones, warm dark skin, amber eyes, short tight brown curls, sky blue collar","自信"),
("阿朔","male 31, narrow face aquiline nose, dark eyes, black long top tied small bun shaved sides, cream collar","利落"),
("小棠","female 27, rounded jaw, copper skin, brown eyes, auburn shoulder length waves side part, sage collar","活泼"),
("阿远","male 36, broad nose rounded face, medium brown skin, black loose curls, rectangular glasses, rust collar","耐心"),
("青禾","female 32, heart face high brows, hazel eyes, dark olive skin, black crown braids, yellow collar","明朗"),
("阿拓","male 28, diamond face, pale skin, teal eyes, navy blue swept fringe, steel gray jacket","机敏"),
("若云","female 35, long face defined nose, brown eyes, dark chestnut straight bob no bangs, white scarf blue jacket","从容"),
("阿柏","male 40, heavy jaw, deep tan skin, dark eyes, salt pepper short crew cut, trimmed beard, ochre collar","踏实"),
("小鹿","female 24, oval face freckles, brown eyes, strawberry blond short pixie, navy collar small green ear stud","爽朗"),
("阿洛","male 30, wide cheekbones narrow chin, dark skin, dark eyes, short black twists, cyan collar","灵活"),
("映雪","female 29, square face pale skin, narrow black eyes, long straight black hair blunt bangs, plum collar","冷静"),
("阿晋","male 33, oval face prominent nose, olive skin, brown eyes, dark brown slick side part, black glasses orange collar","认真"),
("海葵","female 31, broad round face, deep brown skin, black eyes, voluminous curly black bob, ivory collar","爽快"),
("阿屿","male 26, long narrow face, fair skin, gray green eyes, pale ash brown shag cut, lavender collar","随和"),
("小满","female 37, pear face full cheeks, warm tan skin, brown eyes, short chestnut feathered hair, red scarf navy jacket","热心"),
("阿骁","male 34, square face scar through left brow, tan skin, amber eyes, dark burgundy cropped mohawk, slate collar","坚毅"),
("书宁","female 28, angular oval face, fair skin, dark eyes, blue black side braid, thin oval glasses mint collar","谨慎")]
assets=[dict(id="hero",displayName="我",appearance="adult male 24, brown tousled short hair, amber brown eyes, soft angular face; orange reflective jacket white shirt; identity locked to rider-master-original.png",visualKeywords=["友善","坚定"])]
for i,(name,desc,key) in enumerate(rows,1): assets.append(dict(id=f"npc-{i}",displayName=name,appearance="adult "+desc,visualKeywords=[key],resource=None,rect=None))
(p/'roster.json').write_text(json.dumps(dict(status="candidate-display-names-not-business-renaming",characters=assets),ensure_ascii=False,indent=2))
