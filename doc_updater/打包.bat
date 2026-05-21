@echo off
chcp 65001 >nul
echo ========================================
echo    SWRT文档内容更新工具 - 打包脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [1/4] 检查并安装PyInstaller...
pip install pyinstaller -q

echo.
echo [2/4] 清理旧的打包文件...
if exist build (
    rd /s /q build
)
if exist dist (
    rd /s /q dist
)

echo.
echo [3/4] 开始打包...
echo.

pyinstaller --clean package.spec

echo.
echo [4/4] 创建发布包...
if not exist "..\发布包_v1.5" (
    mkdir "..\发布包_v1.5"
)

if exist "dist\文档内容更新工具_v1.4.exe" (
    copy "dist\文档内容更新工具_v1.4.exe" "..\发布包_v1.5\"
    echo 复制可执行文件完成
)

REM 创建使用说明
(
echo # SWRT文档内容更新工具 v1.5
echo.
echo ## 软件说明
echo 基于SWRT输入文档，自动在SWRT平台文档进行打点，生成更新后的文档。
echo.
echo ## 主要功能
echo 1. 文档导入 - 支持.xlsx/.docx/.pdf/.txt格式
echo 2. 文档检查 - 检测E列/P列空值
echo 3. 执行打点 - 根据规则自动更新
echo 4. 文档导出 - 导出文档+变更履历
echo.
echo ## 使用步骤
echo 1. 导入SWRT输入文档
echo 2. 导入SWRT平台文档
echo 3. 点击"执行打点"按钮
echo 4. 导出更新后的文档
echo.
echo ## 打点规则
echo 1. SWRT输入文档E列="否"时提取C列ID
echo 2. 在SWRT平台文档P列匹配ID（精确匹配）
echo 3. Q列设为NA，P列内容复制到R列
echo 4. "实现状态"列设为"No"
echo 5. "不能实现的原因"列设为P列内容
) > "..\发布包_v1.5\使用说明.md"

echo 创建使用说明完成
echo.
echo ========================================
echo    打包完成！
echo ========================================
echo.
echo 发布包位置: ..\发布包_v1.5\
echo 可执行文件: 文档内容更新工具_v1.4.exe
echo.
pause