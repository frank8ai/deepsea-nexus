# Batch Indexing Rules - 批量索引详细规则
# 按需层 - 批量索引 Obsidian 笔记时加载

## 概述

将 Obsidian 笔记批量转换为向量，建立可检索的知识库。

## 支持的格式

- Markdown (.md)
- 文本文件 (.txt)
- 代码文件 (.py, .js, .ts 等)

## 工作原理

```
扫描目录 → 解析文件 → 提取内容 → 生成向量 → 存入 ChromaDB
```

## API 使用

### 批量索引目录

```python
from nexus_core import nexus_init, nexus_add_documents
from pathlib import Path
import os

nexus_init()

def index_obsidian_vault(vault_path: str, tags: str = "obsidian"):
    """索引整个 Obsidian 仓库"""
    documents = []
    vault = Path(vault_path)
    
    for md_file in vault.rglob("*.md"):
        try:
            content = md_file.read_text(encoding='utf-8')
            # 跳过过小的文件
            if len(content) < 100:
                continue
                
            documents.append({
                "content": content,
                "title": md_file.stem,
                "tags": tags,
                "metadata": {
                    "source": str(md_file.relative_to(vault)),
                    "file_size": len(content)
                }
            })
        except Exception as e:
            print(f"跳过 {md_file}: {e}")
    
    # 批量添加
    ids = nexus_add_documents(documents, batch_size=100)
    print(f"索引了 {len(ids)} 个文档")
    return ids

# 使用
index_obsidian_vault("/path/to/Obsidian")
```

### 增量索引

```python
def incremental_index(vault_path: str, last_index_time: float):
    """只索引新文件或修改过的文件"""
    documents = []
    vault = Path(vault_path)
    
    for md_file in vault.rglob("*.md"):
        mtime = md_file.stat().st_mtime
        if mtime > last_index_time:
            # 添加到 documents...
            pass
    
    return nexus_add_documents(documents)
```

## 配置参数

```yaml
batch_indexing:
  batch_size: 100           # 每批处理的文档数
  min_file_size: 100        # 最小文件大小（字符）
  max_file_size: 50000      # 最大文件大小（字符）
  skip_patterns:            # 跳过的文件模式
    - "*.tmp"
    - "*.bak"
    - ".trash/*"
    - ".git/*"
  include_extensions:       # 包含的文件扩展名
    - ".md"
    - ".txt"
    - ".py"
    - ".js"
    - ".ts"
```

## 文件处理

### Markdown 处理

```python
def process_markdown(content: str) -> str:
    """清理 Markdown 格式"""
    import re
    
    # 移除 YAML frontmatter
    content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
    
    # 移除代码块标记，保留内容
    content = re.sub(r'```[\w]*\n', '', content)
    content = content.replace('```', '')
    
    # 简化链接
    content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
    
    return content.strip()
```

### 元数据提取

```python
def extract_metadata(file_path: Path, content: str) -> dict:
    """从 YAML frontmatter 提取元数据"""
    import re
    import yaml
    
    metadata = {}
    
    # 提取 YAML frontmatter
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if match:
        try:
            frontmatter = yaml.safe_load(match.group(1))
            metadata.update(frontmatter)
        except:
            pass
    
    return metadata
```

## 性能优化

### 并行处理

```python
from concurrent.futures import ProcessPoolExecutor

def parallel_index(file_list, max_workers=4):
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(process_file, file_list)
    return list(results)
```

### 进度显示

```python
from tqdm import tqdm

def index_with_progress(file_list):
    documents = []
    for file_path in tqdm(file_list, desc="索引中"):
        doc = process_file(file_path)
        if doc:
            documents.append(doc)
    return documents
```

## 最佳实践

1. **先小批量测试**: 先用少量文件测试
2. **分批处理**: 大量文件分批，防止内存溢出
3. **增量索引**: 定期执行，只处理新文件
4. **清理旧数据**: 索引前可清理旧的重复数据

## 故障排查

### 索引失败

```python
# 检查文件权限
try:
    content = file_path.read_text(encoding='utf-8')
except PermissionError:
    print(f"无权限读取: {file_path}")
except UnicodeDecodeError:
    print(f"编码错误: {file_path}")
```

### 内存溢出

```python
# 减小 batch_size
nexus_add_documents(docs, batch_size=50)  # 而不是 100
```
