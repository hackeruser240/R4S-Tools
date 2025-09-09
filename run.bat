@echo off
echo ======================
echo Activating environment
echo ======================
call env.bat

echo ============================
echo Installing required packages
echo ============================

pip install -r requirements_alongTheWay.txt

echo ==================
echo Calling Extra help
echo ==================
call post_install.bat


echo =========
echo Completed
echo =========