<#
.SYNOPSIS
    启动 Vibe-Trading HTTP MCP 服务（后台模式，端口 8900）
.DESCRIPTION
    检查端口 8900 是否已被占用，如果没有则启动 vibe-trading-mcp
    作为后台 HTTP MCP 服务。服务启动后可通过 http://127.0.0.1:8900/mcp 连接。
.PARAMETER Restart
    强制重启：先杀掉已有进程再重新启动。
.PARAMETER Stop
    停止正在运行的 Vibe-Trading MCP 服务。
#>

param(
    [switch]$Restart,
    [switch]$Stop
)

$PORT = 8900
$PROCESS_NAME = "vibe-trading-mcp"

# 查找已运行的进程
$existing = Get-Process -Name $PROCESS_NAME -ErrorAction SilentlyContinue

if ($Stop) {
    if ($existing) {
        Write-Host "正在停止 Vibe-Trading MCP 服务 (PID: $($existing.Id))..."
        $existing | Stop-Process -Force
        Write-Host "已停止。"
    } else {
        Write-Host "Vibe-Trading MCP 服务未运行。"
    }
    return
}

if ($Restart -and $existing) {
    Write-Host "正在重启 Vibe-Trading MCP 服务..."
    $existing | Stop-Process -Force
    Start-Sleep -Seconds 2
    $existing = $null
}

if ($existing) {
    Write-Host "Vibe-Trading MCP 服务已在运行中 (PID: $($existing.Id))"
    Write-Host "  端口: $PORT"
    Write-Host "  如需重启请使用: .\start_vibe_trading.ps1 -Restart"
    return
}

Write-Host "正在启动 Vibe-Trading MCP HTTP 服务 (端口 $PORT)..."

# 启动后台进程，重定向输出到日志文件
$logDir = Join-Path $PSScriptRoot "logs"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$logFile = Join-Path $logDir "vibe-trading-mcp.log"

$startInfo = New-Object System.Diagnostics.ProcessStartInfo
$startInfo.FileName = "vibe-trading-mcp"
$startInfo.Arguments = "--transport http --port $PORT"
$startInfo.UseShellExecute = $false
$startInfo.CreateNoWindow = $true
$startInfo.RedirectStandardOutput = $true
$startInfo.RedirectStandardError = $true
$startInfo.WorkingDirectory = $PSScriptRoot

$process = New-Object System.Diagnostics.Process
$process.StartInfo = $startInfo

# 异步读取 stdout/stderr 到日志
$stdoutScript = {
    param($reader, $logPath)
    try {
        while (($line = $reader.ReadLine()) -ne $null) {
            Add-Content -Path $logPath -Value "[STDOUT] $line"
        }
    } catch {}
}
$stderrScript = {
    param($reader, $logPath)
    try {
        while (($line = $reader.ReadLine()) -ne $null) {
            Add-Content -Path $logPath -Value "[STDERR] $line"
        }
    } catch {}
}

$process.Start() | Out-Null

# 启动异步日志记录
$null = [System.Threading.Tasks.Task]::Run({ & $stdoutScript $process.StandardOutput $logFile })
$null = [System.Threading.Tasks.Task]::Run({ & $stderrScript $process.StandardError $logFile })

Write-Host "正在等待服务就绪（检测端口 $PORT）..."
$ready = $false
for ($i = 0; $i -lt 45; $i++) {
    Start-Sleep -Seconds 1
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.ConnectAsync("127.0.0.1", $PORT).Wait(2000) | Out-Null
        if ($tcp.Connected) {
            $tcp.Close()
            $ready = $true
            Write-Host "端口 $PORT 已监听，服务就绪！"
            break
        }
        $tcp.Close()
    } catch {
        # 还未就绪
    }
    if ($i % 10 -eq 0) {
        Write-Host "  等待中... ($($i+1)s)"
    }
}

$elapsed = $i + 1
if (-not $ready) {
    Write-Host "警告: 服务启动超时（45s），请检查日志: $logFile"
    Write-Host "可手动查看日志: Get-Content '$logFile' -Tail 20"
} else {
    Write-Host "Vibe-Trading MCP 服务已启动 (PID: $($process.Id), 耗时 ${elapsed}s)"
    Write-Host "  HTTP MCP 端点: http://127.0.0.1:$PORT/mcp"
    Write-Host "  日志文件: $logFile"
}
