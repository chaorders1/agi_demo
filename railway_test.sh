#!/bin/bash

# Railway本地测试便捷脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 显示帮助信息
show_help() {
    echo "Railway本地测试工具"
    echo ""
    echo "用法:"
    echo "  ./railway_test.sh [选项] [命令]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示帮助信息"
    echo "  -t, --test     运行完整测试"
    echo "  -r, --run      模拟railway run命令"
    echo "  -s, --script   指定启动脚本"
    echo ""
    echo "示例:"
    echo "  ./railway_test.sh --test                    # 运行完整测试"
    echo "  ./railway_test.sh --run python start.py    # 模拟railway run"
    echo "  ./railway_test.sh --script minimal_start.py # 使用指定脚本测试"
    echo ""
}

# 检查Python环境
check_python() {
    if ! command -v python &> /dev/null; then
        print_error "Python未安装或不在PATH中"
        exit 1
    fi
    
    python_version=$(python --version 2>&1)
    print_info "Python版本: $python_version"
}

# 运行完整测试
run_full_test() {
    print_info "开始Railway完整测试..."
    
    if [ -n "$1" ]; then
        python railway_local_test.py --script "$1"
    else
        python railway_local_test.py
    fi
}

# 模拟railway run命令
run_railway_command() {
    print_info "模拟railway run命令..."
    
    if [ $# -eq 0 ]; then
        print_error "请提供要运行的命令"
        echo "例如: ./railway_test.sh --run python start.py"
        exit 1
    fi
    
    python railway_run.py "$@"
}

# 主函数
main() {
    # 检查Python环境
    check_python
    
    # 解析参数
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        -t|--test)
            shift
            run_full_test "$@"
            ;;
        -r|--run)
            shift
            run_railway_command "$@"
            ;;
        -s|--script)
            shift
            if [ -z "$1" ]; then
                print_error "请指定脚本名称"
                exit 1
            fi
            run_full_test "$1"
            ;;
        "")
            print_warning "未指定操作，显示帮助信息"
            show_help
            ;;
        *)
            print_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@" 