@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   Q_System 环境配置脚本
echo ============================================================
echo.

:: 检查 conda 是否可用
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 conda，请先安装 Miniconda
    echo 下载地址: https://docs.conda.io/en/latest/miniconda.html
    pause
    exit /b 1
)

echo [信息] 检测到 conda 已安装
conda --version

:: 检查 quants 环境是否存在
echo.
echo [步骤 1/4] 检查 quants 环境...
conda env list | findstr /C:"quants" >nul 2>&1
if %errorlevel% equ 0 (
    echo [信息] quants 环境已存在
    set CREATE_ENV=0
) else (
    echo [信息] quants 环境不存在，将创建新环境
    set CREATE_ENV=1
)

:: 创建或更新环境
if !CREATE_ENV! equ 1 (
    echo.
    echo [步骤 2/4] 创建 quants 环境 (Python 3.8)...

    :: 检查是否有 environment.yml
    if exist environment.yml (
        echo [信息] 使用 environment.yml 创建环境
        conda env create -f environment.yml
    ) else (
        echo [信息] 手动创建环境
        conda create -n quants python=3.8 -y
    )

    if %errorlevel% neq 0 (
        echo [错误] 环境创建失败
        pause
        exit /b 1
    )
)

:: 安装依赖
echo.
echo [步骤 3/4] 安装/更新依赖...
if exist requirements.txt (
    call conda run -n quants pip install -r requirements.txt
) else (
    echo [警告] requirements.txt 不存在，跳过依赖安装
)

:: 检查 xtquant
echo.
echo [步骤 4/4] 检查 xtquant...
conda run -n quants python -c "import xtquant; print('xtquant OK')" >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] xtquant 未安装，尝试安装...
    call conda run -n quants pip install xtquant

    conda run -n quants python -c "import xtquant" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [警告] xtquant 安装失败，可能需要通过 QMT 客户端安装
    ) else (
        echo [成功] xtquant 安装成功
    )
) else (
    echo [成功] xtquant 已安装
)

:: 运行环境检查
echo.
echo ============================================================
echo   运行环境验证...
echo ============================================================
echo.
if exist scripts\check_env.py (
    call conda run -n quants python scripts\check_env.py
) else (
    echo [警告] check_env.py 不存在，跳过验证
)

echo.
echo ============================================================
echo   配置完成！
echo ============================================================
echo.
echo 激活环境: conda activate quants
echo 运行回测: python main.py
echo 运行实盘: python run_live.py
echo.

pause
