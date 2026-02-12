#!/usr/bin/env python3
"""
记录AI交互到日志文件
每次AI回复后自动执行
"""

import os
import json
from datetime import datetime

LOG_FILE = os.path.expanduser("~/.openclaw/logs/ai-interactions.log")

def main():
    context_json = os.environ.get("NEXUS_HOOK_CONTEXT", "{}")
    context = json.loads(context_json)
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "hook_type": "post-response",
        "context": context
    }
    
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

if __name__ == "__main__":
    main()
