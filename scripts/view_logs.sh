#!/bin/bash
# Script to view application logs

LOG_FILE="logs/app.log"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================="
echo "PRD助手 - 日志查看工具"
echo "========================================="
echo ""

# Check if log file exists
if [ ! -f "$LOG_FILE" ]; then
    echo "❌ 日志文件不存在: $LOG_FILE"
    exit 1
fi

# Menu
echo "选择查看模式："
echo "1) 实时查看日志 (tail -f)"
echo "2) 查看最近 50 条日志"
echo "3) 查看最近 100 条日志"
echo "4) 只看请求日志 (✅/❌)"
echo "5) 只看错误日志 (ERROR)"
echo "6) 只看 AI 相关日志"
echo "7) 搜索日志"
echo ""
read -p "请选择 (1-7): " choice

case $choice in
    1)
        echo -e "${GREEN}实时查看日志...${NC}"
        tail -f "$LOG_FILE"
        ;;
    2)
        echo -e "${GREEN}最近 50 条日志:${NC}"
        tail -50 "$LOG_FILE"
        ;;
    3)
        echo -e "${GREEN}最近 100 条日志:${NC}"
        tail -100 "$LOG_FILE"
        ;;
    4)
        echo -e "${GREEN}请求日志:${NC}"
        grep "→" "$LOG_FILE" | tail -50
        ;;
    5)
        echo -e "${RED}错误日志:${NC}"
        grep "ERROR" "$LOG_FILE" | tail -50
        ;;
    6)
        echo -e "${BLUE}AI 相关日志:${NC}"
        grep -E "(gemini|Gemini|analyze|Analysis)" "$LOG_FILE" | tail -50
        ;;
    7)
        read -p "输入搜索关键词: " keyword
        echo -e "${YELLOW}搜索结果:${NC}"
        grep -i "$keyword" "$LOG_FILE" | tail -50
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

