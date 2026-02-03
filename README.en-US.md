# osuWRS - a osu! Wallpaper Replace Script

[![GitHub](https://img.shields.io/github/license/windla/osuwrs)](https://github.com/Windla/osuWRS/blob/master/LICENSE)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/windla/osuwrs)
![GitHub file size in bytes](https://img.shields.io/github/size/Windla/osuWRS/dist/osuWRS.exe)
[![996.icu](https://img.shields.io/badge/link-996.icu-red.svg)](https://996.icu)
[![State-of-the-art Shitcode](https://img.shields.io/static/v1?label=State-of-the-art&message=Shitcode&color=7B5804)](https://github.com/trekhleb/state-of-the-art-shitcode)

> Custom osu!stable home background script (No Supporter tag required)

[Github](https://github.com/Windla/osuWRS) | [Releases](https://github.com/Windla/osuWRS/releases) | [中文 README](README.md)

## Notice

- Only supports the **osu!stable** version on Windows; **osu!lazer** is not supported.

## Download

- [Releases (Recommended)](https://github.com/Windla/osuWRS/releases)
- [Clone Source Code](https://github.com/Windla/osuWRS/archive/refs/heads/master.zip)

## Usage

1. Place your background images (supports `.jpg`, `.jpeg`, `.png`) into the `bg/` folder.
2. Run `osuWRS.exe` (recommended) or `python osuWRS.py`.
3. On the first run, it will automatically search for the osu! path and generate `config.ini`. If it fails, please manually edit the [configuration](https://github.com/Windla/osuWRS/tree/master?tab=readme-ov-file#configuration).

## Features

- [x] **Fully Automatic**: Automatically finds paths, synchronizes background info, and completes replacement.
- [x] **Zero Dependencies**: Pure standard library implementation.
- [x] **Multi-image Replacement**: Supports multi-image replacement for jpg/jpeg/png formats (should be fewer than the number of images issued by the server).
- [x] **Lock Mechanism**: Strongly locks the `Data/bg` directory so backgrounds never expire.
- [x] **Proxy Support**: Supports system proxy and custom proxies.
- [x] **Seamless Start**: You can even use it as an osu! launcher; osuWRS will automatically detect cloud updates and replace them.

## Configuration

- `[osu] path`: osu! installation root directory.
- `[osu] quickStart`: Whether to automatically start osu! after replacement.
- `[osuWRS] proxy`: Proxy settings (`off`, `system`, or specific address).
- See instructions in `config.ini` for more details.

## Tutorials

- [v0.0 Principle Analysis](https://www.bilibili.com/video/BV1zq4y1g7S4) (Refer to this video if you need to manually **control**/**restore**/**delete** the `Data\bg` folder)
- ~~[v1.0 Video Tutorial](https://www.bilibili.com/video/BV1eq4y1g7sT/)~~
- ~~[v2.0 Video Tutorial](https://www.bilibili.com/video/BV1ub4y1v785/)~~
- [v3.0 Text Tutorial](https://github.com/Windla/osuWRS/blob/master/README.md) (~~Almost~~ **Out of the box**)

## Follow Me

[Github](https://github.com/Windla) | [Bilibili](https://space.bilibili.com/358002685)

[![Star History Chart](https://api.star-history.com/svg?repos=Windla/osuWRS&type=Date)](https://star-history.com/#Windla/osuWRS&Date)

## Disclaimer

This tool involves operations on game directory permissions. Please ensure you have sufficient privileges. Modifying game files may violate certain terms of service; use at your own risk.

## Credits

- Gemini 3 Pro/Flash and Roo Code assisted me in this refactoring.
- An archive from 2022, thanks to Bilibili users for their support.

## License

[GNU General Public License v3.0](LICENSE)
