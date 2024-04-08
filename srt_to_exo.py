from string import Template
from tqdm import tqdm
import tomllib
import srt

# read config
with open("config.toml", "rb") as f:
    config = tomllib.load(f)

u = config["user_config"]
o = config["object_config"]
t = config["text_config"]

InputFile = u["file_path"]

frame_rate = u["frame_rate"]

header_format = """
[exedit]
width={}
height={}
rate={}
scale=1
length={}
audio_rate={}
audio_ch={}
"""

text_obj_format = """
[$i]
start=$start
end=$end
layer={}
overlay=1
camera=0
[$i.0]
_name=テキスト
サイズ={}
表示速度=0.0
文字毎に個別オブジェクト=0
移動座標上に表示する=0
自動スクロール=0
B={}
I={}
type={}
autoadjust={}
soft={}
monospace={}
align={}
spacing_x={}
spacing_y={}
precision={}
color={}
color2={}
font={}
text=$text
[$i.1]
_name=標準描画
X={}
Y={}
Z={}
拡大率={}
透明度={}
回転={}
blend={}""".format(
    u["set_layer"],
    o["size"],
    t["Bold"],
    t["Italic"],
    t["type"],
    t["autoadjust"],
    t["soft"],
    t["monospace"],
    t["align"],
    t["spacing_x"],
    t["spacing_y"],
    t["precision"],
    t["color"],
    t["color2"],
    t["font"],
    o["X"], o["Y"], o["Z"],
    o["zoom"],
    o["alpha_blend"],
    o["rotate"],
    o["blend"])

text_obj_template = Template(text_obj_format)

def frames_from_timestamp(timestamp):
    seconds = timestamp.total_seconds()
    return int(seconds * frame_rate)

def convert_srt_to_exo(srt_file, exo_file):

    srt_obj = list(srt.parse(open(srt_file, "r", encoding="utf_8")))

    with open(exo_file, 'w', encoding='shift_jis', newline='\r\n') as file:
        file.write(header_format.format(
                                    u["movie_size"][0],
                                    u["movie_size"][1],
                                    frame_rate,
                                    frames_from_timestamp(srt_obj[-1].end),
                                    u["audio_rate"],
                                    u["audio_ch"]))

        for i, caption in tqdm(enumerate(srt_obj)):
            start_frame = frames_from_timestamp(caption.start)
            end_frame = frames_from_timestamp(caption.end)

            if i > 0:
                start_frame += 1

            if i < len(srt_obj) - 1:
                end_frame -= 1

            text = caption.content.encode('utf-16le').hex().ljust(4096, '0')
            file.write(text_obj_template.safe_substitute(i=i, start=start_frame, end=end_frame, text=text))

convert_srt_to_exo(InputFile, InputFile[:-4] + ".exo")
