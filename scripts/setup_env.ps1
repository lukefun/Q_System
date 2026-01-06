param(
    [switch]$Recreate
)

Set-StrictMode -Version Latest

function Write-Info([string]$s){ Write-Host "[信息] $s" -ForegroundColor Cyan }
function Write-Warn([string]$s){ Write-Host "[警告] $s" -ForegroundColor Yellow }
function Write-ErrorExit([string]$s){ Write-Host "[错误] $s" -ForegroundColor Red; exit 1 }

Write-Host "`n============================================================="
Write-Host "  Q_System 环境配置脚本 (PowerShell)"
Write-Host "=============================================================`n"

# 查找 conda / mamba
$condaCmd = $null
if (Get-Command conda -ErrorAction SilentlyContinue) { $condaCmd = 'conda' }
elseif (Get-Command mamba -ErrorAction SilentlyContinue) { $condaCmd = 'mamba' }

if (-not $condaCmd) {
    Write-ErrorExit "未检测到 conda 或 mamba，请先安装 Miniconda/Miniforge 或 mamba。下载: https://docs.conda.io/en/latest/miniconda.html"
}

Write-Info "使用 $condaCmd 管理环境"
& $condaCmd --version

# 检查 quants 环境是否存在
Write-Host "`n[步骤 1/6] 检查 quants 环境..."
try {
    $envList = & $condaCmd env list 2>$null | Out-String
} catch {
    Write-Warn "获取环境列表失败：$($_.Exception.Message)"
    $envList = ""
}
$envExists = $envList -match "(^|\s)quants(\s|$)"
if ($envExists) { Write-Info "quants 环境已存在" } else { Write-Info "quants 环境不存在" }

# 处理 --Recreate
if ($Recreate) {
    if ($envExists) {
        Write-Info "--Recreate 指定，正在删除现有 quants 环境..."
        & $condaCmd env remove -n quants -y
        if ($LASTEXITCODE -ne 0) { Write-ErrorExit "删除 quants 环境失败" }
        $envExists = $false
    } else {
        Write-Info "--Recreate 指定，但 quants 环境不存在，后续将创建新环境"
    }
}

# 创建或更新环境
if (-not $envExists) {
    Write-Host "`n[步骤 2/6] 创建 quants 环境..."
    if (Test-Path -Path "environment.yml") {
        Write-Info "使用 environment.yml 创建环境"
        & $condaCmd env create -f environment.yml -n quants
    } else {
        Write-Info "未找到 environment.yml，手动创建环境 (python=3.8)"
        & $condaCmd create -n quants python=3.8 -y
    }
    if ($LASTEXITCODE -ne 0) { Write-ErrorExit "环境创建失败" }
} else {
    if (Test-Path -Path "environment.yml") {
        Write-Host "`n[步骤 2/6] 使用 environment.yml 更新 quants 环境..."
        & $condaCmd env update -n quants -f environment.yml --prune
        if ($LASTEXITCODE -ne 0) { Write-Warn "使用 environment.yml 更新环境失败，请手动检查依赖" } else { Write-Info "环境更新完成" }
    }
}

# 安装 pip 依赖
Write-Host "`n[步骤 3/6] 安装/更新 pip 依赖..."
if (Test-Path -Path "requirements.txt") {
    & $condaCmd run -n quants pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { Write-Warn "pip install -r requirements.txt 失败" } else { Write-Info "requirements.txt 安装完成" }
} else {
    Write-Warn "requirements.txt 不存在，跳过依赖安装"
}

# 尝试安装本地包
if (Test-Path -Path "pyproject.toml") {
    Write-Info "检测到 pyproject.toml，尝试安装本地包（editable）"
    & $condaCmd run -n quants pip install -e .
    if ($LASTEXITCODE -ne 0) { Write-Warn "本地包安装失败" }
} elseif (Test-Path -Path "setup.py") {
    Write-Info "检测到 setup.py，尝试安装本地包（editable）"
    & $condaCmd run -n quants pip install -e .
    if ($LASTEXITCODE -ne 0) { Write-Warn "本地包安装失败" }
}

# 检查 xtquant
Write-Host "`n[步骤 4/6] 检查 xtquant..."
& $condaCmd run -n quants python -c "import xtquant; print('xtquant OK')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Warn "xtquant 未检测到，尝试通过 pip 安装 xtquant..."
    & $condaCmd run -n quants pip install xtquant
    if ($LASTEXITCODE -ne 0) { Write-Warn "xtquant pip 安装失败，可能需要通过 QMT 客户端或手动安装" }
    else {
        & $condaCmd run -n quants python -c "import xtquant; print('xtquant OK')" 2>$null
        if ($LASTEXITCODE -ne 0) { Write-Warn "xtquant 安装后导入失败，请手动检查" } else { Write-Info "xtquant 安装成功" }
    }
} else {
    Write-Info "xtquant 已安装"
}

# 运行环境验证脚本
Write-Host "`n============================================================="
Write-Host "  运行环境验证..."
Write-Host "=============================================================`n"

if (Test-Path -Path "scripts/check_env.py") {
    Write-Host "[步骤 5/6] 运行 scripts\check_env.py 验证环境..."
    & $condaCmd run -n quants python scripts\check_env.py
} else {
    Write-Warn "scripts\check_env.py 不存在，跳过验证"
}

# 最终提示
Write-Host "`n============================================================="
Write-Host "  配置完成！"
Write-Host "=============================================================\n"
Write-Host "激活环境: conda activate quants"
Write-Host "运行回测: python main.py"
Write-Host "运行实盘: python run_live.py\n"
Write-Host "如果需要强制重建环境，请重新运行： .\scripts\setup_env.ps1 -Recreate\n"

Write-Host "按任意键退出..." -NoNewline
[void][System.Console]::ReadKey($true)
