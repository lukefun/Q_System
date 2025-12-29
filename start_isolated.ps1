# 隔离模式启动 - 禁用用户级 site-packages
# 使用方法: 在 PowerShell 中执行 .\start_isolated.ps1

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Q_System 隔离模式启动器 (PowerShell)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 设置环境变量禁用用户级 site-packages
$env:PYTHONNOUSERSITE = "1"

# 激活 conda 环境
conda activate quants

Write-Host "[已启用] PYTHONNOUSERSITE=1 (禁用用户全局包)" -ForegroundColor Green
Write-Host "[已激活] conda 环境: quants" -ForegroundColor Green
Write-Host ""

# 验证
python -c "import sys; sp=[p for p in sys.path if 'site-packages' in p and 'vendor' not in p]; print('site-packages 路径:'); [print(f'  {p}') for p in sp]"
Write-Host ""

Write-Host "环境已就绪，可以开始工作。" -ForegroundColor Yellow
