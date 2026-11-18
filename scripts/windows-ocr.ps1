param([Parameter(Mandatory=$true)][string]$InputDirectory, [Parameter(Mandatory=$true)][string]$OutputDirectory, [string]$Language='zh-Hans-CN')
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType=WindowsRuntime] | Out-Null
[Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime] | Out-Null
[Windows.Storage.Streams.IRandomAccessStream, Windows.Storage.Streams, ContentType=WindowsRuntime] | Out-Null
[Windows.Globalization.Language, Windows.Globalization, ContentType=WindowsRuntime] | Out-Null
$taskAwaitMethod=([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetGenericArguments().Count -eq 1 -and $_.GetParameters().Count -eq 1
} | Select-Object -First 1)
function Await-Result($Operation,[Type]$ResultType) {
    $taskAwait=$taskAwaitMethod.MakeGenericMethod($ResultType).Invoke($null,@($Operation))
    $taskAwait.Wait()
    return $taskAwait.Result
}
$taskEngine=[Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage((New-Object Windows.Globalization.Language $Language))
if (-not $taskEngine) { throw "OCR language unavailable: $Language" }
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$taskCount=0
Get-ChildItem -LiteralPath $InputDirectory -File | Where-Object { $_.Extension -in '.png','.jpg','.jpeg' } | Sort-Object Name | ForEach-Object {
    $taskOut=Join-Path $OutputDirectory ($_.BaseName+'.json')
    if (Test-Path -LiteralPath $taskOut) { return }
    $taskFile=Await-Result ([Windows.Storage.StorageFile]::GetFileFromPathAsync($_.FullName)) ([Windows.Storage.StorageFile])
    $taskStream=Await-Result ($taskFile.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
    try {
        $taskDecoder=Await-Result ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($taskStream)) ([Windows.Graphics.Imaging.BitmapDecoder])
        $taskBitmap=Await-Result ($taskDecoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
        try {
            $taskResult=Await-Result ($taskEngine.RecognizeAsync($taskBitmap)) ([Windows.Media.Ocr.OcrResult])
            $taskLines=@($taskResult.Lines | ForEach-Object {
                $taskWords=@($_.Words | ForEach-Object {
                    [pscustomobject]@{text=$_.Text;x=$_.BoundingRect.X;y=$_.BoundingRect.Y;width=$_.BoundingRect.Width;height=$_.BoundingRect.Height}
                })
                [pscustomobject]@{text=$_.Text;words=$taskWords}
            })
            [pscustomobject]@{image=$taskFile.Name;width=$taskBitmap.PixelWidth;height=$taskBitmap.PixelHeight;language=$Language;text=$taskResult.Text;lines=$taskLines} |
                ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $taskOut -Encoding UTF8
        } finally { $taskBitmap.Dispose() }
    } finally { $taskStream.Dispose() }
    $taskCount++
    if ($taskCount % 10 -eq 0) { Write-Output "OCR completed $taskCount new pages" }
}
Write-Output "OCR finished: $taskCount new pages"
