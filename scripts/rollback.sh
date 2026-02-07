#!/bin/bash
# Deep-Sea Nexus v2.0 Rollback Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Config
PROJECT_DIR="${HOME}/.openclaw/workspace/DEEP_SEA_NEXUS_V2"
BACKUP_DIR="${PROJECT_DIR}/backups"

echo -e "${YELLOW}🔙 Deep-Sea Nexus v2.0 Rollback${NC}"
echo ""

# Check if git is available
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git not found${NC}"
    exit 1
fi

cd "${PROJECT_DIR}"

# Get available tags
echo "📋 可用的回滚点:"
git tag -l | tail -10

echo ""
read -p "输入要回滚到的版本 (tag 或 commit): " TARGET

# Check if target exists
if ! git rev-parse --verify "${TARGET}" &> /dev/null; then
    echo -e "${RED}❌ 版本不存在: ${TARGET}${NC}"
    exit 1
fi

# Create backup before rollback
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="rollback_${TIMESTAMP}"
echo -e "${YELLOW}📦 创建备份: ${BACKUP_NAME}${NC}"

mkdir -p "${BACKUP_DIR}"
git archive HEAD | tar -x -C "${BACKUP_DIR}/${BACKUP_NAME}"

# Show what will change
echo ""
echo -e "${YELLOW}⚠️  将要回滚到: ${TARGET}${NC}"
echo "变更的文件:"
git diff --name-only "${TARGET}" HEAD 2>/dev/null || echo "(首次部署，无历史变更)"

echo ""
read -p "确认回滚? (y/n): " CONFIRM

if [ "${CONFIRM}" != "y" ] && [ "${CONFIRM}" != "Y" ]; then
    echo "已取消"
    exit 0
fi

# Perform rollback
echo -e "${GREEN}🔄 执行回滚...${NC}"

if git rev-parse --verify "${TARGET}" &> /dev/null; then
    git reset --hard "${TARGET}"
    echo -e "${GREEN}✅ 已回滚到 ${TARGET}${NC}"
else
    # Try as commit
    git reset --hard "${TARGET}"
    echo -e "${GREEN}✅ 已回滚${NC}"
fi

echo ""
echo -e "${GREEN}✅ 回滚完成!${NC}"
echo -e "备份位置: ${BACKUP_DIR}/${BACKUP_NAME}"
echo ""
echo "如需恢复备份:"
echo "  cd ${PROJECT_DIR}"
echo "  git reset --hard HEAD"
