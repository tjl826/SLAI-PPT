# 上传到已创建的 tjl826/SLAI-PPT 空仓库

本文件说明如何发布已准备好的完整仓库包。**拥有这个压缩包不代表 GitHub 上已经创建了仓库。**

## 推荐方式：Mac / Linux 终端

需要 Git 与 GitHub CLI。Mac 已安装 Homebrew 时，可运行：

```bash
brew install gh
```

解压仓库包后，在终端进入 `SLAI-PPT` 目录。例如解压在下载目录时：

```bash
cd ~/Downloads/SLAI-PPT
bash publish_to_github.sh
```

脚本会校验文件（存在 Python 3 时）、检查 GitHub 登录状态，并通过浏览器引导登录。请使用 `tjl826` 账号。无需向聊天发送密码、访问令牌或 SSH 私钥。

已存在的空公开仓库 `tjl826/SLAI-PPT` 将被直接使用（若不存在才会尝试创建）。公开仓库里的 PPTX、Logo、PDF 与预览可被任何人访问。脚本核对账号后创建仓库、上传到 `main`，设置描述和 Topics，并核对远端提交。

如希望新仓库为私有：

```bash
bash publish_to_github.sh --private
```

只查看操作计划，不执行任何 GitHub 操作：

```bash
bash publish_to_github.sh --dry-run
```

## 安全与重试

脚本不会强制推送，不会更改已有仓库可见性，不会覆盖同名非空仓库，也不会写入其他项目。第一次成功初始化后的中断可在同一文件夹重试；若远端产生冲突，普通 `git push` 会拒绝，而不会自动覆盖。

脚本通过 `gh auth setup-git` 配置 GitHub CLI 的 HTTPS 凭据辅助程序。凭据由 GitHub CLI 管理，脚本不会显示或收集令牌。

新增的仓库级 `git user.name` / `git user.email` 仅在没有已有 Git 身份配置时设置，使用 GitHub 的公开 noreply 邮箱。不会更改全局提交身份。

## 不用脚本时

若已在 GitHub 网页创建空仓库 `SLAI-PPT`，可以直接运行脚本将此文件夹初始化为本地 Git 仓库并推送。不要只上传整个 ZIP：GitHub README 中的相对图片路径要求目录被真正解压并提交。文件较多，建议使用 Git 或 GitHub Desktop，而不是分批网页拖拽。

## 展示方式

上传后，仓库首页自动展示 `README.md`，包括双语模板封面、下载链接、截图、Logo 与标准色。

`index.html` 是额外的静态浏览页面：本地双击即可筛选语言和风格、逐页翻看，也可通过左右方向键翻页。点击 GitHub 仓库中的 HTML 文件通常看到的是源码；本脚本不会启用 GitHub Pages、创建 Release 或宣称网站已上线。

## 参考命令文档

- https://cli.github.com/manual/gh_repo_create
- https://cli.github.com/manual/gh_auth_login
- https://cli.github.com/manual/gh_auth_setup-git
- https://cli.github.com/manual/gh_repo_edit

仓库包中的预览已构建，无需安装 LibreOffice 或 Python 依赖才能上传；它们只在重新生成预览时需要。
