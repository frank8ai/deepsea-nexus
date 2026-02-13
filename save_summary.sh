#!/bin/bash
# 快速保存对话摘要
# 用法: ./save_summary.sh "摘要内容"

SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$SOURCE_DIR/../../.venv-nexus/bin/python"

if [ -z "$1" ]; then
    echo "用法: ./save_summary.sh \"摘要内容\""
    echo "示例: ./save_summary.sh \"修复了向量库问题\""
    exit 1
fi

$VENV -c "
import sys
sys.path.insert(0, '$SOURCE_DIR')
from nexus_core import nexus_init, nexus_add

nexus_init(blocking=True)
result = nexus_add('$1', '摘要', 'summary')
print('✅ 已保存:', result)
"
