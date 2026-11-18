param([switch]$FromEnvironment)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'credentials.ps1')
$taskPointer = [IntPtr]::Zero
try {
    if (-not $FromEnvironment) {
        $env:UC_USER = Read-Host 'Student ID (UCloud)'
        $taskSecret = Read-Host 'Password (saved to Windows Credential Manager)' -AsSecureString
        $taskPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($taskSecret)
        $env:UC_PASS = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($taskPointer)
    }
    [BuptHomeworkVault]::Save($env:UC_USER, $env:UC_PASS)
    [pscustomobject]@{ stored = [BuptHomeworkVault]::Exists(); target = 'BUPT.HomeworkAssistant.Ucloud' } | ConvertTo-Json -Compress
} finally {
    Remove-Item Env:UC_PASS -ErrorAction SilentlyContinue
    Remove-Item Env:UC_USER -ErrorAction SilentlyContinue
    if ($taskPointer -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($taskPointer) }
    if ($taskSecret) { $taskSecret.Dispose() }
}
