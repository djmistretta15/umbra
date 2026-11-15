# Umbra local server: serves this folder at http://localhost:8000 (no installs needed)
$ErrorActionPreference = "Stop"
try {
  $root = Split-Path -Parent $MyInvocation.MyCommand.Path
  $port = 8000
  $l = $null
  foreach ($try in 8000..8010) {
    $x = New-Object System.Net.HttpListener
    $x.Prefixes.Add("http://localhost:$try/")
    try { $x.Start(); $l = $x; $port = $try; break } catch { $x.Close() }
  }
  if (-not $l) { throw "No free port between 8000 and 8010." }
  Write-Host ""
  Write-Host "  Umbra is running at http://localhost:$port" -ForegroundColor Green
  Write-Host "  Keep this window open. Close it to stop Umbra."
  Write-Host ""
  Start-Process "http://localhost:$port/"
  $types = @{".html"="text/html; charset=utf-8";".js"="text/javascript";".css"="text/css";".json"="application/json";".png"="image/png";".csv"="text/csv";".tif"="image/tiff";".geojson"="application/json";".md"="text/plain; charset=utf-8";".srt"="text/plain; charset=utf-8";".txt"="text/plain; charset=utf-8"}
  while ($l.IsListening) {
    $c = $l.GetContext()
    try {
      $p = [Uri]::UnescapeDataString($c.Request.Url.AbsolutePath.TrimStart('/'))
      if ($p -eq "") { $p = "index.html" }
      $f = [IO.Path]::GetFullPath((Join-Path $root $p))
      if ($f.ToLower().StartsWith($root.ToLower()) -and (Test-Path -LiteralPath $f -PathType Leaf)) {
        $b = [IO.File]::ReadAllBytes($f); $ext = [IO.Path]::GetExtension($f).ToLower()
        $c.Response.ContentType = $(if ($types.ContainsKey($ext)) { $types[$ext] } else { "application/octet-stream" })
        $c.Response.ContentLength64 = $b.Length; $c.Response.OutputStream.Write($b, 0, $b.Length)
      } else { $c.Response.StatusCode = 404 }
    } catch { } finally { try { $c.Response.Close() } catch { } }
  }
} catch {
  Write-Host ""
  Write-Host "  Umbra server could not start: $($_.Exception.Message)" -ForegroundColor Yellow
  exit 1
}
