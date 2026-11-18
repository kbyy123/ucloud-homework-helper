param([string]$Id, [switch]$CaptureOnly)
$ErrorActionPreference = 'Stop'
$taskExit = 1
try {
    . (Join-Path $PSScriptRoot 'credentials.ps1')
    $taskCredential = [BuptHomeworkVault]::Read()
    $env:UC_USER = $taskCredential.UserName
    $env:UC_PASS = $taskCredential.Password
    $taskArgs = @((Join-Path $PSScriptRoot 'run.mjs'))
    if ($Id) { $taskArgs += "--id=$Id" }
    if ($CaptureOnly) { $taskArgs += '--capture-only' }
    & node @taskArgs
    $taskExit = $LASTEXITCODE
} catch {
    # Do not emit the Secret object or PowerShell invocation context.
    Write-Output '{"ok":false,"error":"凭据读取或运行失败；请检查 Windows 凭据管理器中的 BUPT.HomeworkAssistant.Ucloud 及本机运行环境"}'
} finally {
    Remove-Item Env:UC_PASS -ErrorAction SilentlyContinue
    Remove-Item Env:UC_USER -ErrorAction SilentlyContinue
    if ($taskCredential) { $taskCredential.Password = $null; $taskCredential = $null }
}
exit $taskExit
