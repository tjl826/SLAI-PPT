# 贡献指南

欢迎通过 Issue 反馈问题，或通过 Pull Request 提交改进。

## 报告问题

请注明模板编号（01–05）、语言、页码、所用软件及版本，并附截图。文件打不开、字体替代、图表错位和源文件错字应分别说明。

## 提交更改

尽量只修改与本次问题相关的文件。提交 PPTX 更改时，请同步更新对应 PDF 与截图，不要提交 `.DS_Store`、`__MACOSX/`、PowerPoint 临时文件、私人信息、凭据或字体文件。

新素材请附可核查的来源与许可说明；不要将机构标识或第三方图片笼统归为 MIT。MIT 适用范围见 `NOTICE.md`。

## 预览与检查

```bash
python3 -m pip install -r scripts/requirements-preview.txt
python3 scripts/build_previews.py
python3 scripts/verify_repository.py
```

`SOURCE_MANIFEST.json` 是首次导入快照。修改 PPTX 后校验出现不一致是预期行为，应在 PR 中说明源文件变更，并由维护者决定是否更新快照；不要仅为通过校验而静默覆盖记录。
