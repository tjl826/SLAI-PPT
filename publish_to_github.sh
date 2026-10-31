#!/usr/bin/env bash
# Publish to existing empty tjl826/SLAI-PPT. Never modifies unrelated repositories.
# Default visibility: public. Use --private to create a private repository instead.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
OWNER="tjl826"
REPO="$OWNER/SLAI-PPT"
REMOTE="https://github.com/$REPO.git"
DESCRIPTION="深圳河套学院学术汇报PPT模板｜5种风格 · 中英文10套 · 可编辑PPTX · 168页预览 · Logo与标准色｜非官方整理"
VISIBILITY="--public"
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --public|--private) VISIBILITY="$arg" ;;
    --dry-run) DRY_RUN=1 ;;
    -h|--help)
      printf '%s\n' '用法: bash publish_to_github.sh [--public|--private] [--dry-run]' \
        '默认新建公开仓库 tjl826/SLAI-PPT；不覆盖同名已有非空仓库；不强制推送。' \
        '依赖: Git 与 GitHub CLI (gh)。登录通过浏览器完成，不需要向聊天发送密码或 Token。'
      exit 0 ;;
    *) printf '未知参数: %s\n' "$arg" >&2; exit 2 ;;
  esac
done
cd "$ROOT"
[[ -f SOURCE_MANIFEST.json && -f README.md && -f catalog.json ]] || { echo '仓库包不完整。' >&2; exit 1; }
if [[ "$DRY_RUN" -eq 1 ]]; then
  printf '目标账号: %s\n目标仓库: %s\n新仓库可见性: %s\n' "$OWNER" "$REPO" "${VISIBILITY#--}"
  printf '%s\n' '计划: 校验文件 → 浏览器登录/核对账号 → 本地提交 → 新建仓库 → 普通推送 main → 核对提交。' \
    '不会覆盖其他仓库，不会强制推送，不会自动创建 Release 或启用 GitHub Pages。' \
    '此为预演；没有创建远程仓库或上传文件。'
  exit 0
fi
command -v git >/dev/null 2>&1 || { echo '未安装 Git。macOS 可先运行 xcode-select --install。' >&2; exit 1; }
command -v gh >/dev/null 2>&1 || { echo '未安装 GitHub CLI。已安装 Homebrew 的 Mac 可运行 brew install gh，然后重试。' >&2; exit 1; }
export GH_HOST=github.com
printf '即将向 %s 发布此模板包（新仓库可见性: %s）。\n' "$REPO" "${VISIBILITY#--}"
if command -v python3 >/dev/null 2>&1; then
  python3 scripts/verify_repository.py
else
  echo '提示：未找到 python3，跳过本地完整性复检；此包已在制作时校验。'
fi
if ! gh auth status --hostname github.com --active >/dev/null 2>&1; then
  gh auth login --hostname github.com --git-protocol https --web
fi
LOGIN="$(gh api --hostname github.com user --jq .login)"
if [[ "$LOGIN" != "$OWNER" ]]; then
  printf '当前登录账号是 %s，不是 %s。为避免发错账号，操作已停止。\n' "$LOGIN" "$OWNER" >&2
  printf '请运行 gh auth switch --hostname github.com --user %s 后重试。\n' "$OWNER" >&2
  exit 1
fi
LOCAL_OWNED=0
if [[ -e .git ]]; then
  [[ -d .git && -f .git/slai-ppt-publish ]] || { echo '检测到不是本脚本初始化的 Git 仓库，停止以免影响已有项目。' >&2; exit 1; }
  EXISTING_REMOTE="$(git config --get remote.origin.url 2>/dev/null || true)"
  [[ -z "$EXISTING_REMOTE" || "$EXISTING_REMOTE" == "$REMOTE" ]] || { echo 'origin 指向其他仓库，已停止。' >&2; exit 1; }
  if [[ "$EXISTING_REMOTE" == "$REMOTE" ]] && git rev-parse --verify HEAD >/dev/null 2>&1; then
    LOCAL_OWNED=1
  fi
fi
EXISTS=0
if gh repo view "$REPO" --json nameWithOwner >/dev/null 2>&1; then
  EXISTS=1
  EMPTY="$(gh repo view "$REPO" --json isEmpty --jq .isEmpty)"
  PRIVATE="$(gh repo view "$REPO" --json isPrivate --jq .isPrivate)"
  if [[ "$PRIVATE" == true && "$VISIBILITY" == --public ]] || [[ "$PRIVATE" == false && "$VISIBILITY" == --private ]]; then
    echo '已有仓库的可见性与参数不一致。本脚本不会擅自更改可见性，请用匹配参数重试。' >&2; exit 1
  fi
  if [[ "$EMPTY" != true && "$LOCAL_OWNED" -ne 1 ]]; then
    echo '同名仓库已存在且非空；已停止，不会覆盖。请先检查该仓库内容。' >&2; exit 1
  fi
fi
if [[ ! -d .git ]]; then
  git init -b main
  printf '%s\n' "$REPO" > .git/slai-ppt-publish
fi
BRANCH="$(git symbolic-ref --short HEAD)"
[[ "$BRANCH" == main ]] || { echo '当前分支不是 main，已停止；请先检查本地分支。' >&2; exit 1; }
# Use a public GitHub no-reply identity only inside this new repository.
if ! git config user.name >/dev/null; then git config --local user.name "$OWNER"; fi
if ! git config user.email >/dev/null; then git config --local user.email '150494364+tjl826@users.noreply.github.com'; fi
# Explicitly stage only this package's known content, not arbitrary local files.
git add -- README.md README_EN.md LICENSE NOTICE.md CONTRIBUTING.md \
  SOURCE_MANIFEST.json catalog.json .gitignore .gitattributes index.html \
  publish_to_github.sh scripts docs imgs previews .github \
  ./*.pptx ./标准色.pdf ./深圳河套学院logo
if ! git diff --cached --quiet; then
  git commit -m 'Add SLAI academic PPT templates, bilingual previews and documentation'
fi
if [[ "$EXISTS" -eq 0 ]]; then
  gh repo create "$REPO" "$VISIBILITY" --description "$DESCRIPTION"
fi
if ! git remote get-url origin >/dev/null 2>&1; then git remote add origin "$REMOTE"; fi
# GitHub CLI configures the standard HTTPS credential helper; it does not expose a token.
gh auth setup-git --hostname github.com
git push --set-upstream origin main
if ! gh repo edit "$REPO" --default-branch main --description "$DESCRIPTION" \
  --add-topic powerpoint --add-topic ppt-template --add-topic academic-presentation --add-topic hetao; then
  echo '文件已推送；仓库描述或 Topics 设置失败，可稍后在 GitHub 页面调整。' >&2
fi
LOCAL_SHA="$(git rev-parse HEAD)"
REMOTE_SHA="$(gh api --hostname github.com "repos/$REPO/git/ref/heads/main" --jq .object.sha)"
[[ "$LOCAL_SHA" == "$REMOTE_SHA" ]] || { echo '远端提交校验不一致，请检查仓库。' >&2; exit 1; }
printf '\n发布成功，远端 main 已核对: %s\n' "$REMOTE_SHA"
gh repo view "$REPO" --json url --jq .url
printf '%s\n' 'README 将直接展示模板封面、下载索引及截图；index.html 可在本地打开浏览。' \
  '没有启用 GitHub Pages，也没有自动创建 Release。'
