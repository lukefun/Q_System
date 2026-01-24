@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 支持参数 --recreate 强制重建环境
set RECREATE=0
if "%~1"=="--recreate" set RECREATE=1

echo.
echo ============================================================
echo   Q_System 环境配置脚本
echo ============================================================
echo.

:: 检查 conda / mamba 是否可用，优先使用 conda
where conda >nul 2>&1
if %errorlevel% neq 0 (
    where mamba >nul 2>&1
    if %errorlevel% equ 0 (
        set CONDA_CMD=mamba
    ) else (
        echo [错误] 未检测到 conda 或 mamba，请先安装 Miniconda/Miniforge 或 mamba
        echo Miniconda 下载: https://docs.conda.io/en/latest/miniconda.html
        pause
        exit /b 1
    )
) else (
    set CONDA_CMD=conda
)

echo [信息] 使用 %CONDA_CMD% 管理环境
%CONDA_CMD% --version

:: 检查 quants 环境是否存在
echo.
echo [步骤 1/6] 检查 quants 环境...
%CONDA_CMD% env list | findstr /C:"quants" >nul 2>&1
if %errorlevel% equ 0 (
    echo [信息] quants 环境已存在
    set CREATE_ENV=0
) else (
    echo [信息] quants 环境不存在
    set CREATE_ENV=1
)

if %RECREATE% equ 1 (
    if %CREATE_ENV% equ 0 (
        echo [信息] --recreate 指定，删除现有 quants 环境...
        %CONDA_CMD% env remove -n quants -y
        if %errorlevel% neq 0 (
            echo [错误] 删除 quants 环境失败
            pause
            exit /b 1
        )
        set CREATE_ENV=1
    ) else (
        echo [信息] --recreate 指定，但 quants 环境不存在，将创建新环境
    )
)

:: 创建或更新环境
if %CREATE_ENV% equ 1 (
    echo.
    echo [步骤 2/6] 创建 quants 环境 (建议 Python 3.8 或 environment.yml 中指定的版本)...

    if exist environment.yml (
        echo [信息] 使用 environment.yml 创建环境
        %CONDA_CMD% env create -f environment.yml -n quants
    ) else (
        echo [信息] environment.yml 不存在，将手动创建环境（Python 3.8）
        %CONDA_CMD% create -n quants python=3.8 -y
    )

    if %errorlevel% neq 0 (
        echo [错误] 环境创建失败
        pause
        exit /b 1
    )
) else (
    :: 环境已存在且未指定 --recreate，尝试用 environment.yml 更新（如果存在）
    if exist environment.yml (
        echo.
        echo [步骤 2/6] 使用 environment.yml 更新 quants 环境...
        %CONDA_CMD% env update -n quants -f environment.yml --prune
        if %errorlevel% neq 0 (
            echo [警告] 使用 environment.yml 更新环境失败，继续但请检查依赖
        ) else (
            echo [信息] 环境更新完成
        )
    )
)

:: 安装依赖
echo.
echo [步骤 3/6] 安装/更新 pip 依赖...
if exist requirements.txt (
    call %CONDA_CMD% run -n quants pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [警告] pip install -r requirements.txt 失败，请手动检查
    ) else (
        echo [信息] requirements.txt 安装完成
    )
) else (
    echo [警告] requirements.txt 不存在，跳过依赖安装
)

:: 尝试安装本地包（如果仓库是可安装的 Python 包）
if exist pyproject.toml (
    echo [信息] 检测到 pyproject.toml，尝试安装本地包
    call %CONDA_CMD% run -n quants pip install -e .
    if %errorlevel% neq 0 echo [警告] 本地包安装失败
) else if exist setup.py (
    echo [信息] 检测到 setup.py，尝试安装本地包
    call %CONDA_CMD% run -n quants pip install -e .
    if %errorlevel% neq 0 echo [警告] 本地包安装失败
)

:: 检查 xtquant
echo.
echo [步骤 4/6] 检查 xtquant...
call %CONDA_CMD% run -n quants python -c "import xtquant; print('xtquant OK')" >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] xtquant 未检测到，尝试通过 pip 安装 xtquant...
    call %CONDA_CMD% run -n quants pip install xtquant

    call %CONDA_CMD% run -n quants python -c "import xtquant; print('xtquant OK')" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [警警] xtquant 安装失败，部分功能可能需要通过 QMT 客户端安装或手动配置
    ) else (
        echo [成功] xtquant 安装成功
    )
) else (
    echo [成功] xtquant 已安装
)

:: 运行环境检查脚本
echo.
echo ============================================================
echo   运行环境验证...
echo ============================================================
echo.
if exist scripts\check_env.py (
    echo [步骤 5/6] 运行 scripts\check_env.py 验证环境...
    call %CONDA_CMD% run -n quants python scripts\check_env.py
) else (
    echo [警告] scripts\check_env.py 不存在，跳过验证
)

:: 最终提示
echo.
echo ============================================================
echo   配置完成！
echo ============================================================
echo.
echo 激活环境: conda activate quants
echo 运行回测: python main.py
echo 运行实盘: python run_live.py
echo.

echo 如果需要强制重建环境，请重新运行：
	echo   setup_env.bat --recreate

echo.

pause
