@echo off
:: 快速环境验证 - 双击运行
chcp 65001 >nul

echo Q_System 环境快速检查
echo.

:: 检查 conda
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Conda 未安装
    goto :end
)
echo [√] Conda 已安装

:: 检查 quants 环境
conda env list | findstr /C:"quants" >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] quants 环境不存在
    echo     运行 scripts\setup_env.bat 创建环境
    goto :end
)
echo [√] quants 环境存在

:: 检查 Python 版本
for /f "tokens=*" %%i in ('conda run -n quants python --version 2^>^&1') do set PYVER=%%i
echo [√] %PYVER%

:: 检查 xtquant
conda run -n quants python -c "import xtquant" >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] xtquant 未安装
    goto :end
)
echo [√] xtquant 可用

:: 检查项目导入
conda run -n quants python -c "from core.engine import BacktestEngine" >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] 项目模块导入失败
    goto :end
)
echo [√] 项目模块正常

echo.
echo ========================================
echo   环境检查通过！
echo ========================================
echo.
echo 使用方法:
echo   conda activate quants
echo   python main.py
echo.

:end
pause
