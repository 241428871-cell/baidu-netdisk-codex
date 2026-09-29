# Codex 百度网盘插件

通过本地 stdio 桥连接[百度网盘官方 MCP 服务](https://github.com/baidu-netdisk/mcp)，让 Codex 列出、搜索和管理百度网盘文件。插件自带一个通用操作工作流和一个图书去重整理工作流。

本项目是社区实现，不是百度或 OpenAI 的官方产品。百度网盘授权令牌保存在本机凭据管理器中，不写入插件文件或 GitHub 仓库。

## 安装

需要 Python 3.11 或更新版本，且在 PATH 中可通过 python 调用。首次启动会在 Codex 插件数据目录建立独立虚拟环境，并从 PyPI 安装固定版本的 mcp 和 keyring。

从 GitHub 安装：

    codex plugin marketplace add 241428871-cell/baidu-netdisk-codex
    codex plugin add baidu-netdisk-codex@baidu-netdisk-community

也可以先克隆仓库，再安装本地市场：

    git clone https://github.com/241428871-cell/baidu-netdisk-codex.git
    codex plugin marketplace add ./baidu-netdisk-codex
    codex plugin add baidu-netdisk-codex@baidu-netdisk-community

安装后新开一个 Codex 对话，使插件的工具与工作流被加载。

## 授权

如果已有先前的 Codex 百度网盘授权，本插件会从同一个本机凭据项读取令牌，无须重复粘贴。检查状态：

    python plugins/baidu-netdisk-codex/scripts/bootstrap.py auth --status

新用户可先按[百度官方说明](https://github.com/baidu-netdisk/mcp)取得授权链接。使用自己在百度网盘开放平台创建的应用时，将应用 ID 传给本地授权窗口：

    python plugins/baidu-netdisk-codex/scripts/bootstrap.py auth --client-id YOUR_BAIDU_APP_ID

授权成功页不会自动回填 Codex。在本地授权窗口点击“开始等待复制地址”，然后在成功页按 Ctrl+L、Ctrl+C。窗口会提取令牌、保存到系统凭据管理器并清空剪贴板。也可在窗口内手动粘贴。**不要把成功地址或令牌发到聊天、Issue 或仓库。**

授权页显示的应用名称由百度开放平台中的应用配置决定。要显示“Codex”，请将自己创建的百度应用命名为 Codex；本插件不会修改百度账号中的应用名称。

在仓库根目录进行只读连接检查：

    python plugins/baidu-netdisk-codex/scripts/bootstrap.py check

检查只输出是否连接成功和工具数量，不输出令牌或个人文件名。

## 使用

安装并授权后，可在新对话中直接说：

- “列出百度网盘某个文件夹下的文件。”
- “将 A 文件夹中的 PDF 复制到 B 文件夹，保留原件。”
- “按书名去重整理这个书库，每本书优先保留最容易转成 TXT 的格式，保留中英文两种版本。”

大规模操作应先完整扫描和生成计划，之后分批执行、保存进度，并核对目标目录。遇到百度频率控制时暂停和降低并发，再从进度记录继续。本插件的工作流包含这些规则。

该连接使用百度官方 SSE MCP 接口。百度官方说明指出，本地文件上传需要另外使用其 stdio SDK，本插件未包含上传工具。

## 代码与安全

    .agents/plugins/marketplace.json       Codex 市场入口
    plugins/baidu-netdisk-codex/plugin.json
    plugins/baidu-netdisk-codex/mcp.json
    plugins/baidu-netdisk-codex/scripts/   本地授权、启动和 MCP 连接桥
    plugins/baidu-netdisk-codex/skills/    网盘操作与图书整理工作流

令牌可由 BAIDU_NETDISK_ACCESS_TOKEN 环境变量或系统凭据管理器提供。环境变量适合无图形界面的环境；不要将它提交到配置文件。连接桥不会打印含令牌的百度 SSE URL 或异常详情。

这个仓库不包含用户网盘清单、复制计划或任何真实令牌。发现凭据泄露时，请在[百度授权管理](https://passport.baidu.com/v6/appAuthority)解除关联后重新授权。

## 开发验证

    python -m unittest discover -s tests -v
    python PATH_TO_PLUGIN_CREATOR/scripts/validate_plugin.py plugins/baidu-netdisk-codex

第二条是 Codex 本机内置的插件验证器；也可以直接运行 codex plugin add 验证插件加载。

## License

MIT
