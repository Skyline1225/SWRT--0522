@echo off
chcp 65001 >nul
echo ========================================
echo    推送代码到GitHub
echo ========================================
echo.
echo 当前目录: %cd%
echo 仓库地址: https://github.com/Skyline1225/SWRT--0522
echo.
echo [1/2] 检查Git状态...
git status
echo.
echo [2/2] 开始推送代码...
git push -u origin main
echo.
if %errorlevel% equ 0 (
    echo ========================================
    echo    推送成功！
    echo ========================================
    echo 请访问: https://github.com/Skyline1225/SWRT--0522
) else (
    echo ========================================
    echo    推送失败
    echo ========================================
    echo 请检查网络连接或GitHub认证
    echo.
    echo 提示: 如果使用HTTPS方式需要GitHub Personal Access Token
    echo 或者可以使用SSH方式:
    echo git remote set-url origin git@github.com:Skyline1225/SWRT--0522.git
    echo git push -u origin main
)
echo.
pause