# 启动 doubao2api 服务（OpenAI 兼容豆包 API，端口 9090）
# 用 WMI 启动（脱离进程组，不被 bash 清理）；幂等——已在跑则跳过。
# 用法: powershell -ExecutionPolicy Bypass -File scripts\start_doubao2api.ps1
$ErrorActionPreference = "Stop"
$port = 9090

# 已在监听则跳过
if (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue) {
    Write-Output "doubao2api already running on :$port"
    exit 0
}

$dir = "C:\Users\汤继潮\AppData\Roaming\reasonix\global-workspace\doubao2api"
$py = "C:\python\python.exe"
if (-not (Test-Path $py)) { $py = (Get-Command python).Source }

$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
    CommandLine = "`"$py`" -m doubao2api"
    CurrentDirectory = $dir
}
if ($r.ReturnValue -ne 0) {
    Write-Error "WMI start failed: return=$($r.ReturnValue)"
    exit 1
}
Write-Output "doubao2api starting (pid $($r.ProcessId))... wait ~40s for login check"
