@echo off
chcp 65001 >nul
echo ================================
echo   Agent直聘 - 启动脚本
echo ================================
echo.

:: 进入脚本所在目录（项目根目录）
cd /d "%~dp0"

echo [1/3] 拉取最新代码...
git pull origin master
echo.

echo [2/3] 更新依赖...
pip install -r requirements.txt -q
echo.

echo [3/3] 启动服务...
echo 访问地址: http://localhost:8000/docs
echo 按 Ctrl+C 停止服务
echo.
python start.py
pause
