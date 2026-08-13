@echo off
setlocal

pushd "%~dp0\..\.."

echo Generating the differential probe testbench...
uv run python experiments\state_probe\generate_probe.py
if errorlevel 1 goto failed

for /f "delims=" %%I in ('wsl wslpath -a "%CD%"') do set "WSL_REPOSITORY=%%I"

echo Compiling and running the probe with Icarus inside WSL and Nix...
wsl bash -lc "cd '%WSL_REPOSITORY%' && ~/.nix-profile/bin/nix develop . --command bash -lc 'iverilog -g2012 -o experiments/state_probe/results/probe.vvp sky130/cell_models.v puzzle/reversed_puzzle.v experiments/state_probe/results/probe_testbench.v && vvp experiments/state_probe/results/probe.vvp'"
if errorlevel 1 goto failed

echo Analyzing structural cones and cycle-by-cycle divergence...
uv run python experiments\state_probe\analyze_probe.py
if errorlevel 1 goto failed

popd
exit /b 0

:failed
set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%
