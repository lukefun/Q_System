@echo off
chcp 65001 >nul
echo.
echo ============================================================
echo   Q_System 环境隔离修复工具
echo ============================================================
echo.

:: 检查 conda
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 conda
    pause
    exit /b 1
)

echo [问题] 当前包从用户全局目录加载，可能导致版本混乱
echo [方案] 将所有依赖重新安装到 conda 环境中
echo.

:: 确认操作
set /p confirm="是否继续修复? (y/n): "
if /i not "%confirm%"=="y" (
    echo 已取消
    pause
    exit /b 0
)

echo.
echo [步骤 1/4] 卸载 conda 环境中的旧包...
call conda run -n quants pip uninstall pandas numpy matplotlib -y 2>nul

echo.
echo [步骤 2/4] 重新安装核心包到 conda 环境...
call conda run -n quants pip install --no-user pandas==2.0.3 numpy==1.24.4 matplotlib==3.7.5

echo.
echo [步骤 3/4] 安装 xtquant 到 conda 环境...
call conda run -n quants pip install --no-user xtquant

echo.
echo [步骤 4/4] 验证安装位置...
call conda run -n quants python -c "import pandas; print('pandas:', pandas.__file__)"
call conda run -n quants python -c "import numpy; print('numpy:', numpy.__file__)"
call conda run -n quants python -c "import xtquant; print('xtquant:', xtquant.__file__)"

echo.
echo ============================================================
echo   修复完成！请验证包路径是否指向 conda 环境
echo ============================================================
echo.
pause
