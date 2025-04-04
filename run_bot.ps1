while ($true) {
    Write-Host "Bot ishga tushmoqda... $(Get-Date)"
    & "C:/Users/Assalomu Aleykum/AppData/Local/Programs/Python/Python313/python.exe" "D:/bot/bot.py"
    Write-Host "Bot to‘xtadi. 5 soniyadan so‘ng qayta ishga tushiriladi... $(Get-Date)"
    Start-Sleep -Seconds 5
}