# osuWRS - a osu! Wallpaper Replace Script

[![GitHub](https://img.shields.io/github/license/windla/osuwrs)](https://github.com/Windla/osuWRS/blob/master/LICENSE)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/windla/osuwrs)
![GitHub file size in bytes](https://img.shields.io/github/size/Windla/osuWRS/dist/osuWRS.exe)
[![996.icu](https://img.shields.io/badge/link-996.icu-red.svg)](https://996.icu)
[![State-of-the-art Shitcode](https://img.shields.io/static/v1?label=State-of-the-art&message=Shitcode&color=7B5804)](https://github.com/trekhleb/state-of-the-art-shitcode)

> 自定义 osu!stable 主页背景脚本 (无需 Supporter 标签)

[Github](https://github.com/Windla/osuWRS) | [更新日志](https://github.com/Windla/osuWRS/releases) | [English README](README.en-US.md)

## 注意

- 仅支持Windows系统下的osu!stable版，不支持lazer。


## 下载

- [Releases (推荐)](https://github.com/Windla/osuWRS/releases)
- [Clone 源码](https://github.com/Windla/osuWRS/archive/refs/heads/master.zip)

## 使用

1. 将背景图片（支持 `.jpg`, `.jpeg`, `.png`）放入 `bg/` 文件夹。
2. 运行 `osuWRS.exe` (推荐) 或 `python osuWRS.py`。
3. 首次运行会自动寻找 osu! 路径并生成 `config.ini`，若寻找失败请手动修改[配置文件](https://github.com/Windla/osuWRS/tree/master?tab=readme-ov-file#配置)。

## 功能

- [x] **全自动**: 自动寻找路径、同步背景信息、完成替换。
- [x] **零依赖**: 纯标准库实现。
- [x] **多图替换**: 支持 jpg/jpeg/png 格式多图替换（需少于服务器下发图片数量）。
- [x] **锁定机制**: 强力锁定 Data/bg 目录，背景不再失效。
- [x] **代理支持**: 支持系统代理及自定义代理。
- [x] **无感启动**: 你甚至能当作 osu! 的启动器，osuWRS 会自动检测云端更新并自动替换。
## 配置

- `[osu] path`: osu! 安装根目录。
- `[osu] quickStart`: 替换完成后是否自动启动 osu!。
- `[osuWRS] proxy`: 代理设置 (`off`, `system`, 或具体地址)。
- 其他详见 `config.ini` 中的说明。

## 教程

- [v0.0 原理解析](https://www.bilibili.com/video/BV1zq4y1g7S4) (需要手动 **控制**/**还原**/**删除** `Data\bg` 文件夹请参考这个视频)
- ~~[v1.0 视频教程](https://www.bilibili.com/video/BV1eq4y1g7sT/)~~
- ~~[v2.0 视频教程](https://www.bilibili.com/video/BV1ub4y1v785/)~~
- [v3.0 文字教程](https://github.com/Windla/osuWRS/blob/master/README.md) (~~几乎~~**开箱即用**)

## 关注我

[Github](https://github.com/Windla) | [Bilibili](https://space.bilibili.com/358002685)

[![Star History Chart](https://api.star-history.com/svg?repos=Windla/osuWRS&type=Date)](https://star-history.com/#Windla/osuWRS&Date)


## 免责声明

本工具涉及对游戏目录权限的操作，请确保你有足够的权限运行。修改游戏文件可能违反某些服务条款，请自行承担风险。

## 致谢

- Gemini 3 Pro/Flash 和 Roo Code 协助我进行了本次重构。
- 某份 2022 年的存档，感谢B站网友的支持。


## 许可证

[GNU General Public License v3.0](LICENSE)
