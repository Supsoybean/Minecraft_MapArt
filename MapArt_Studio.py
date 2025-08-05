import os
import json
from PIL import Image, ImageDraw
import numpy as np
import sys
import csv

# ==============================================================================
# ---                           全局配置区域                           ---
# ==============================================================================
# 1. 白名单关键词：程序将只处理文件名【包含】以下任意一个关键词的贴图。
MAPART_KEYWORDS = [
     # 各种羊毛
    "wool", 
    # 各种混凝土
    "concrete",
    # 各种陶瓦
    "terracotta",
    # 各种染色玻璃
    "stained_glass",
    # 各种木板
    "planks",
    # 各种原木、菌柄、去皮木 (会自动匹配到 _top 和 _side)
    "oak_log", "spruce_log", "birch_log", "jungle_log", "acacia_log", "dark_oak_log",
    "mangrove_log", "cherry_log", "stripped_oak_log", "stripped_spruce_log", 
    "stripped_birch_log", "stripped_jungle_log", "stripped_acacia_log", 
    "stripped_dark_oak_log", "stripped_mangrove_log", "stripped_cherry_log",
    "crimson_stem", "warped_stem", "stripped_crimson_stem", "stripped_warped_stem",
    "bamboo"
    # 各种功能方块 (会自动匹配到 _top, _side 等)
    "hay_block", "piston", "mushroom",
    # 土、沙、石
    "dirt", "coarse_dirt", "rooted_dirt", "sand", "red_sand", "gravel", "clay",
    "stone", "cobblestone", "andesite", "diorite", "granite", "deepslate",
    "sandstone", "red_sandstone", "moss_block", "mud",
    # 常见矿物与资源块
    "coal_block", "iron_block", "gold_block", "redstone_block", "lapis_block",
    "emerald_block", "diamond_block", "dried_kelp_block", "glowstone", "snow_block",
    "copper_block", "cut_copper", "exposed_copper", "exposed_cut_copper",
    "weathered_copper", "weathered_cut_copper", "oxidized_copper", "oxidized_cut_copper",
    "raw_copper_block",
    # 地狱相关
    "netherrack", "nether_wart_block", "warped_wart_block", "soul_sand", "soul_soil", "blackstone"
]

# 2. 黑名单关键词：如果文件名【包含】以下任意一个关键词，则【优先排除】。
#    现在您可以用一个词（如'door'）排除一整类方块。
BLACKLIST_CONTAINS_KEYWORDS = [
    "ore",          # 排除所有矿石 (如 redstone_ore, diamond_ore)
    "door",         # 排除所有门 (如 oak_door_top, iron_door_bottom)
    "rail",         # 排除所有铁轨
    "sapling",      # 排除所有树苗
    "potted",       # 排除所有盆栽
    "pane",         # 排除所有玻璃板 (通常不用作地图画主色块)
    "shulker_box",  # 排除所有潜影盒
    "banner",       # 排除所有旗帜
    "bed",          # 排除所有床
    "coral_fan",    # 排除所有扇形珊瑚
    "reinforced_deepslate",
    "copper_bulb",
    "mushroom",
    "piston",
    "suspicious",
]
TEXTURES_FOLDER = "block_textures"
LANG_FILE = "zh_cn.json"


# ==============================================================================
# ---                           核心功能函数区域                         ---
# ==============================================================================

# ++++ 新增：后缀翻译词典 ++++
# 定义了文件名后缀和其中文描述的对应关系
SUFFIX_MAP = {
    '_top': ' (顶部)',
    '_side': ' (侧面)',
    '_bottom': ' (底部)',
    '_front': ' (正面)',
    '_end': ' (末端)',
    '_lock': ' (锁定)',
    '_on': ' (开启)',
    '_stage': ' (阶段)', # 用于部分植物
    '_age': ' (阶段)',  # 用于部分作物
}

# (generate_palette_in_memory, create_missing_texture_placeholder, 等函数保持不变)
def generate_palette_in_memory():
    if not os.path.isdir(TEXTURES_FOLDER): print(f"错误：关键贴图文件夹 '{TEXTURES_FOLDER}' 不存在。"); return None
    palette, processed_files, skipped_stats = [], set(), {"blacklisted": 0, "not_whitelisted": 0, "resolution": 0, "transparency": 0, "corrupted": 0}
    all_texture_files = [f for f in os.listdir(TEXTURES_FOLDER) if f.endswith('.png')]
    print(f"正在从 '{TEXTURES_FOLDER}' 中准备调色盘...")
    for filename in all_texture_files:
        file_basename = os.path.splitext(filename)[0]
        if any(keyword in file_basename for keyword in BLACKLIST_CONTAINS_KEYWORDS): skipped_stats["blacklisted"] += 1; continue
        if not any(keyword in file_basename for keyword in MAPART_KEYWORDS): skipped_stats["not_whitelisted"] += 1; continue
        texture_path = os.path.join(TEXTURES_FOLDER, filename)
        try:
            with Image.open(texture_path) as img:
                if img.size != (16, 16): skipped_stats["resolution"] += 1; continue
                img_rgba = img.convert('RGBA')
                if np.any(np.array(img_rgba)[:, :, 3] < 255): skipped_stats["transparency"] += 1; continue
                img_rgb = img.convert('RGB')
                avg_color = [int(c) for c in np.mean(np.array(img_rgb), axis=(0, 1))]
                palette.append({"name": file_basename, "color": avg_color})
        except Exception: skipped_stats["corrupted"] += 1; continue
    if not palette: print("错误：未能生成任何有效的方块颜色。"); return None
    palette.sort(key=lambda x: x['name'])
    print(f"调色盘准备就绪，共载入 {len(palette)} 种有效方块/表面。")
    return palette
def generate_translation_map():
    if not os.path.exists(LANG_FILE): return None
    try:
        with open(LANG_FILE, 'r', encoding='utf-8') as f: official_translations = json.load(f)
        dynamic_map = {key.replace("block.minecraft.", "", 1): value for key, value in official_translations.items() if key.startswith("block.minecraft.")}
        print(f"中文翻译模块加载成功，共 {len(dynamic_map)} 条目。")
        return dynamic_map
    except Exception: return None
def create_missing_texture_placeholder():
    img = Image.new('RGB', (16, 16)); draw = ImageDraw.Draw(img)
    pink = (255, 0, 255); black = (0, 0, 0)
    for i in range(2):
        for j in range(2): draw.rectangle([i*8, j*8, (i+1)*8-1, (j+1)*8-1], fill=pink if (i + j) % 2 == 0 else black)
    return img
def find_best_match(pixel_rgb, palette):
    best_match_name = ""; min_distance = float('inf')
    for block in palette:
        dist = sum((c1 - c2) ** 2 for c1, c2 in zip(pixel_rgb, block["color"]))
        if dist < min_distance: min_distance = dist; best_match_name = block["name"]
    return best_match_name
def generate_pixel_art(image_path, width, palette):
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            h = int(width * (img.height / img.width))
            resized_img = img.resize((width, h), Image.Resampling.LANCZOS)
            print("-> 正在分析图片并匹配方块...")
            blueprint = [[find_best_match(resized_img.getpixel((x, y)), palette) for x in range(width)] for y in range(h)]
            print("-> 正在拼接高分辨率预览图...")
            hires_preview = Image.new('RGB', (width * 16, h * 16))
            texture_cache = {"missing": create_missing_texture_placeholder()}
            for y, row in enumerate(blueprint):
                for x, name in enumerate(row):
                    if name not in texture_cache:
                        path = os.path.join(TEXTURES_FOLDER, f"{name}.png")
                        try: texture_cache[name] = Image.open(path).convert('RGBA')
                        except FileNotFoundError: texture_cache[name] = texture_cache["missing"]
                    hires_preview.paste(texture_cache[name], (x * 16, y * 16))
            return blueprint, hires_preview
    except Exception as e: print(f"\n错误：在处理图片时发生问题: {e}"); return None, None

# ++++ 新增：智能翻译函数 ++++
def translate_block_name(block_name, translation_map):
    """
    智能翻译方块名，能自动处理_top, _side等后缀。
    """
    if not translation_map:
        return block_name

    # 检查是否有完全匹配的（例如 "terracotta"）
    if block_name in translation_map:
        return translation_map[block_name]

    # 检查后缀
    for suffix, descriptor in SUFFIX_MAP.items():
        if block_name.endswith(suffix):
            # 找到后缀，尝试翻译基础部分
            base_name = block_name[:-len(suffix)]
            translated_base = translation_map.get(base_name, base_name)
            return translated_base + descriptor
    
    # 如果没有找到任何后缀，则返回原名
    return block_name

def save_results(blueprint, preview_img, folder, t_map):
    """保存所有结果到指定文件夹，使用新的智能翻译逻辑"""
    # 保存英文蓝图
    csv_path_en = os.path.join(folder, "blueprint_en.csv")
    with open(csv_path_en, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Y/X'] + [f'X{i+1}' for i in range(len(blueprint[0]))])
        for i, row in enumerate(blueprint):
            writer.writerow([f'Y{i+1}'] + row)
    print(f"-> 英文蓝图已保存至: '{csv_path_en}'")

    # 保存中文蓝图
    if t_map:
        csv_path_cn = os.path.join(folder, "blueprint_cn.csv")
        with open(csv_path_cn, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['Y/X'] + [f'X{i+1}' for i in range(len(blueprint[0]))])
            for i, row in enumerate(blueprint):
                # ++++ 调用新的智能翻译函数 ++++
                translated_row = [translate_block_name(cell, t_map) for cell in row]
                writer.writerow([f'Y{i+1}'] + translated_row)
        print(f"-> 智能翻译中文蓝图已保存至: '{csv_path_cn}'")

    # 保存预览图
    if preview_img:
        preview_path = os.path.join(folder, "preview.png")
        preview_img.save(preview_path)
        print(f"-> 高清预览图已保存至: '{preview_path}'")


# ==============================================================================
# ---                        主程序交互与控制流程                        ---
# ==============================================================================

def main_studio():
    print("--- 欢迎使用 Minecraft 地图画工作室 (终极版) ---")
    palette = generate_palette_in_memory()
    if not palette: return
    translation_map = generate_translation_map()
    while True:
        while True:
            image_path = input("\n请输入您想转换的图片路径 (或拖入文件后按回车): ").strip().replace('"', '')
            if os.path.exists(image_path): break
            else: print("错误：文件不存在，请检查路径。")
        while True:
            try:
                width = int(input("请输入您期望的最终宽度 (单位：方块，例如 120): "))
                if width > 0: break
                else: print("错误：宽度必须是正整数。")
            except ValueError: print("错误：请输入一个有效的数字。")
        
        folder_name = f"{os.path.splitext(os.path.basename(image_path))[0]}_mapart_output"
        os.makedirs(folder_name, exist_ok=True)
        print(f"\n结果将保存在新文件夹: '{folder_name}'")
        
        blueprint, hires_preview = generate_pixel_art(image_path, width, palette)
        
        if blueprint:
            save_results(blueprint, hires_preview, folder_name, translation_map)
        
        print("\n--- 本次任务完成 ---")
        if input("是否要转换另一张图片? (y/n): ").lower() != 'y':
            print("感谢使用，再见！"); break

if __name__ == "__main__":
    try:
        import numpy
        from PIL import Image
    except ImportError: print("错误: 缺少 Pillow 和 Numpy 库。请运行: pip install Pillow numpy")
    else: main_studio()