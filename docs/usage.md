# 使用说明

## 目录结构

```
image/
├── images/          # 所有图片存放目录
├── docs/            # 文档目录
└── README.md
```

## 上传图片

1. 将图片文件放入 `images/` 目录
2. 文件名建议使用 `时间戳_描述` 格式，例如：`1771844313697_NVIDIA 免费模型薅羊毛.png`
3. 提交并推送到 `main` 分支

```bash
git add images/<filename>
git commit -m "Upload image: <filename>"
git push origin main
```

## 引用图片

上传后，可通过 GitHub raw URL 在博客或文章中引用：

```
https://raw.githubusercontent.com/haodafa/image/main/images/<filename>
```

Markdown 引用示例：

```markdown
![描述](https://raw.githubusercontent.com/haodafa/image/main/images/<filename>)
```
