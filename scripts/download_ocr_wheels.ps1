# 用 curl 下载 rapidocr_onnxruntime 及依赖 wheel，然后 pip 本地安装（绕开 pip 网络问题）
$ErrorActionPreference = "Stop"
$base = "https://pypi.tuna.tsinghua.edu.cn"
$tmp = "C:\Users\汤继潮\AppData\Roaming\reasonix\global-workspace\.ocr_wheels"
New-Item -ItemType Directory -Force -Path $tmp | Out-Null

# 包名 -> wheel 匹配模式（按优先级选）
$pkgs = @(
  @{ n = "rapidocr-onnxruntime"; pat = "py3-none-any.whl" },
  @{ n = "onnxruntime";          pat = "cp311-cp311-win_amd64.whl" },
  @{ n = "opencv-python-headless"; pat = "cp311-cp311-win_amd64.whl" },
  @{ n = "numpy";                pat = "cp311-cp311-win_amd64.whl" },
  @{ n = "Pillow";               pat = "cp311-cp311-win_amd64.whl" },
  @{ n = "PyYAML";               pat = "cp311-cp311-win_amd64.whl" },
  @{ n = "shapely";              pat = "cp311-cp311-win_amd64.whl" },
  @{ n = "pyclipper";            pat = "cp311-cp311-win_amd64.whl" },
  @{ n = "six";                  pat = "py2.py3-none-any.whl" },
  @{ n = "requests";             pat = "py3-none-any.whl" },
  @{ n = "certifi";              pat = "py3-none-any.whl" },
  @{ n = "charset-normalizer";   pat = "py3-none-any.whl" },
  @{ n = "idna";                 pat = "py3-none-any.whl" },
  @{ n = "urllib3";              pat = "py3-none-any.whl" }
)

$ok = 0; $fail = @()
foreach ($p in $pkgs) {
  $idx = (curl.exe --noproxy "*" -s -m 30 "$base/simple/$($p.n)/") -join "`n"
  if (-not $idx) { $fail += "$($p.n) (index empty)"; continue }
  $hrefs = [regex]::Matches($idx, 'href="([^"]+\.whl)') | ForEach-Object { ($_.Groups[1].Value -replace "#.*$", "") } | Select-Object -Unique
  $cand = $hrefs | Where-Object { $_ -match [regex]::Escape($p.pat) }
  if (-not $cand) { $cand = $hrefs | Where-Object { $_ -match "py3-none-any.whl" } }
  if (-not $cand) { $fail += "$($p.n) (no wheel match)"; continue }
  $href = ($cand | Select-Object -Last 1) -replace "^\.\./\.\./", "$base/"
  $file = Join-Path $tmp (Split-Path $href -Leaf)
  if (-not (Test-Path $file)) {
    curl.exe --noproxy "*" -s -m 120 -o $file $href
  }
  if (Test-Path $file) { $ok++; Write-Output "OK  $($p.n): $(Split-Path $href -Leaf) ($([math]::Round((Get-Item $file).Length/1MB,1)) MB)" }
  else { $fail += "$($p.n) (download fail)" }
}

Write-Output "---"
Write-Output "downloaded: $ok / $($pkgs.Count)"
if ($fail.Count) { Write-Output "FAILED: $($fail -join ', ')" }
