@echo off
chcp 65001 >nul
:: 隔离模式启动 - 禁用用户级 site-packages
:: 使用方法: 双击此脚本启动 Python 环境

echo.
echo ============================================
echo   Q_System 隔离模式启动器
echo ============================================
echo.

:: 设置环境变量禁用用户级 site-packages
set PYTHONNOUSERSITE=1

:: 激活 conda 环境
call conda activate quants

echo [已启用] PYTHONNOUSERSITE=1 (禁用用户全局包)
echo [已激活] conda 环境: quants
echo.

:: 验证
python -c "import sys; sp=[p for p in sys.path if 'site-packages' in p and 'vendor' not in p]; print('site-packages 路径:'); [print(f'  {p}') for p in sp]"
echo.

:: 保持窗口打开，进入交互模式
cmd /k
