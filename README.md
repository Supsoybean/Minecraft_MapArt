# 🎨 Minecraft 地图画工作室 (Minecraft MapArt Studio)

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/status-stable-green.svg)](https://github.com/)

一个强大、灵活且用户友好的Python命令行工具，旨在将任何图片转换为《我的世界》中的巨型地图画（Map Art）。

本工具从复杂的颜色分析到最终的施工蓝图生成，实现了全自动化流程，让每一位玩家都能成为地图画艺术家。

---

## ✨ 核心功能

* **智能调色盘生成**：无需手动配置颜色！程序会自动扫描您提供的游戏贴图文件夹，通过“白名单关键词”和“黑名单关键词”双重过滤，并进行严格的质量检查（16x16尺寸、100%不透明），动态生成一个最适合当前任务的高质量调色盘。
* **完全交互式操作**：无需修改任何代码。程序启动后，会通过命令行引导您输入图片路径和期望的成品宽度。
* **自动化文件管理**：为每一次的转换任务自动创建一个以图片名命名的专属文件夹，将所有结果（蓝图、预览图）整齐存放，绝不混乱。
* **高保真预览图**：最终生成的预览图不再是简单的马赛克色块，而是由真实的16x16方块贴图一张张拼接而成的高分辨率图像，让您在动工前就能100%预见成品的外观和质感。
* **双语施工蓝图**：自动生成易于查阅的`.csv`格式施工蓝图。如果检测到官方中文语言文件，还会额外生成一份智能翻译的中文版蓝图，清晰标注“橡木 (顶部)”或“草方块 (侧面)”等详细信息。
* **高度可配置**：通过简单修改脚本顶部的关键词列表，您可以轻松定义自己的“建筑材料范围”，无论是追求生存模式的经济实惠，还是创造模式的色彩斑斓，都能轻松实现。

---

## 🖼️ 效果展示

<table>
  <tr>
    <td align="center">原图</td>
    <td align="center">地图画预览图</td>
  </tr>
  <tr>
    <td><img src="https://i.imgur.com/b5980698.png" width="250"></td>
    <td><img src="https://i.imgur.com/44427726.png" width="250"></td>
  </tr>
</table>

---

## 🚀 快速开始

### 1. 环境准备

在开始之前，请确保您的电脑已安装 Python 3.7 或更高版本。

**a. 克隆或下载本项目**
```bash
git clone [https://github.com/YourUsername/Your-Repo-Name.git](https://github.com/YourUsername/Your-Repo-Name.git)
cd Your-Repo-Name
```

**b. 安装依赖库**
项目依赖 `Pillow` 和 `Numpy` 库。运行以下命令以自动安装：
```bash
pip install -r requirements.txt
```

**c. 准备Minecraft资源**
请在项目根目录下（与`.py`脚本同级）准备以下资源：
* **`block_textures/` (必需)**: 创建一个名为 `block_textures` 的文件夹，并将从游戏核心文件 (`.jar`) 中提取的所有16x16方块贴图（`.png`文件）放入其中。
* **`zh_cn.json` (可选)**: 将从游戏中提取的官方简体中文语言文件放在根目录，以启用蓝图的自动翻译功能。

### 2. 运行程序

一切准备就绪后，在命令行中运行主程序：

```bash
python MapArt_Studio_Pro.py
```

程序启动后，只需根据屏幕上的提示操作即可：
1.  输入您想要转换的图片文件的完整路径（支持拖拽文件到窗口）。
2.  输入您期望地图画最终的宽度（以方块为单位）。

程序将自动完成所有工作，并将结果保存在一个以您的图片名命名的文件夹中。

---

## 🛠️ 高级配置

您可以直接编辑 `MapArt_Studio_Pro.py` 脚本顶部的两个列表，来精确控制您的方块调色盘。

* **`MAPART_KEYWORDS` (白名单)**:
    定义了程序会考虑的方块类型。只有文件名中包含此列表内任一关键词的贴图，才会被纳入分析范围。
    ```python
    # 示例
    MAPART_KEYWORDS = [
        "wool", "concrete", "terracotta", "planks", "log", ...
    ]
    ```

* **`BLACKLIST_CONTAINS_KEYWORDS` (黑名单)**:
    用于优先排除某些方块。如果一个贴图的文件名包含此列表内的任一关键词，它将被直接跳过，即使它也匹配了白名单。
    ```python
    # 示例
    BLACKLIST_CONTAINS_KEYWORDS = [
        "ore",          # 排除所有矿石
        "door",         # 排除所有门
        "rail",         # 排除所有铁轨
        ...
    ]
    ```

---

## 📄 许可

本项目采用 [MIT License](https://opensource.org/licenses/MIT) 授权。

## 致谢

* 感谢 **Mojang Studios** 创造了伟大的《我的世界》。
* 感谢 Pillow 和 Numpy 开源社区。
