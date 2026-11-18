param(
    [string]$Id,
    [switch]$CaptureOnly
)
$ErrorActionPreference = 'Stop'
$taskPointer = [IntPtr]::Zero
try {
    if ([string]::IsNullOrWhiteSpace($env:UC_USER)) {
        $env:UC_USER = Read-Host '云邮学号'
    }
    if ([string]::IsNullOrWhiteSpace($env:UC_PASS)) {
        $taskSecret = Read-Host '统一身份认证密码（不回显）' -AsSecureString
        $taskPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($taskSecret)
        $env:UC_PASS = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($taskPointer)
    }
    $taskArgs = @((Join-Path $PSScriptRoot 'run.mjs'))
    if ($Id) { $taskArgs += "--id=$Id" }
    if ($CaptureOnly) { $taskArgs += '--capture-only' }
    & node @taskArgs
    $taskExit = $LASTEXITCODE
} finally {
    Remove-Item Env:UC_PASS -ErrorAction SilentlyContinue
    Remove-Item Env:UC_USER -ErrorAction SilentlyContinue
    if ($taskPointer -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($taskPointer)
    }
    if ($taskSecret) { $taskSecret.Dispose() }
}
exit $taskExit
