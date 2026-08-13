@echo off
setlocal

if "%~2"=="" goto usage
if not "%~3"=="" goto usage

set "NETLIST_WINDOWS=%~1"
set "OUTPUT_DIRECTORY_WINDOWS=%~2"
set "NETLIST=%NETLIST_WINDOWS%"
set "OUTPUT_DIRECTORY=%OUTPUT_DIRECTORY_WINDOWS%"
set "NETLIST=%NETLIST:\=/%"
set "OUTPUT_DIRECTORY=%OUTPUT_DIRECTORY:\=/%"
set "GATE_LIBRARY=.pdk/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"
set "REGISTER_GROUPS=%OUTPUT_DIRECTORY%/register_groups.json"

pushd "%~dp0"

for %%I in ("%NETLIST_WINDOWS%") do set "RECONSTRUCTION=%%~dpnI.json"

if not exist "%RECONSTRUCTION%" (
    echo Missing reconstruction JSON: %RECONSTRUCTION%
    popd
    exit /b 3
)

for /f "delims=" %%I in ('wsl wslpath -a "%CD%"') do set "WSL_REPOSITORY=%%I"

echo Finding register groups with HAL and DANA inside WSL and Nix...
wsl bash -lc "cd '%WSL_REPOSITORY%' && ~/.nix-profile/bin/nix develop . --command hal --python-script export_hal_netlist.py --python-args '%NETLIST% %GATE_LIBRARY% %REGISTER_GROUPS%' --volatile-mode --no-log"
if errorlevel 1 goto failed

echo Organizing the reconstruction around those register groups...
uv run python analyze_netlist.py "%RECONSTRUCTION%" "%OUTPUT_DIRECTORY_WINDOWS%\register_groups.json" "%OUTPUT_DIRECTORY_WINDOWS%\register_grouped.v"
if errorlevel 1 goto failed

popd
exit /b 0

:usage
echo Usage: %~nx0 ^<recovered-netlist.v^> ^<output-directory^>
echo Example: %~nx0 warmup/reversed_04_final.v warmup/netlist_analysis
exit /b 2

:failed
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%
