# sweep_simulation.ps1
# PowerShell script to run the C simulator across A=1..20 and N=1..20.
# This script will:
#  - For each offered load A and number of channels N:
#    - compute arrival rate lambda = A / h (h = MEAN_CALL_DURATION in simparameters.h)
#    - temporarily write these values into a copy of simparameters.h
#    - build the simulator (assumes gcc is available) and run it
#    - parse the simulator output and append a CSV line: A,N,seed,blocked,arrivals,PB
#
# IMPORTANT: This script edits a temporary copy of simparameters.h and restores
# the original after the sweep. It also may be slow because it recompiles the C
# program for each (N) value. If you prefer, we can modify the C code to accept
# runtime arguments instead (recommended for speed).

param(
    [string]$ProjectDir = (Get-Location).Path,
    [string]$SimParameters = "$ProjectDir\simparameters.h",
    [string]$Backup = "$ProjectDir\simparameters.h.bak",
    [string]$ExeName = "simlab.exe",
    [int]$MaxA = 20,
    [int]$MaxN = 20
)

Set-StrictMode -Version Latest

# Read original simparameters.h and back it up
if (-Not (Test-Path $SimParameters)) { Write-Error "simparameters.h not found at $SimParameters"; exit 1 }
Copy-Item -Path $SimParameters -Destination $Backup -Force

# Read MEAN_CALL_DURATION from original file
$content = Get-Content $SimParameters -Raw
$meanMatch = [regex]::Match($content, 'MEAN_CALL_DURATION\s+([0-9]+)')
if (-not $meanMatch.Success) { Write-Error "Couldn't find MEAN_CALL_DURATION in simparameters.h"; exit 1 }
$h = [double]$meanMatch.Groups[1].Value
Write-Host "Mean call duration h = $h"

# CSV header
$outCsv = Join-Path $ProjectDir 'simulation_sweep_results.csv'
"A,N,seed,blocked,arrivals,PB" | Out-File -FilePath $outCsv -Encoding utf8

# Loop over A and N
for ($A = 1; $A -le $MaxA; $A++) {
    $lambda = $A / $h
    for ($N = 1; $N -le $MaxN; $N++) {
        Write-Host "Running A=$A, N=$N, lambda=$lambda"

    # Modify simparameters.h: set Call_ARRIVALRATE and NUMBER_OF_CHANNELS
    $modified = $content -replace 'define\s+Call_ARRIVALRATE\s+\S+', "#define Call_ARRIVALRATE $lambda"
    $modified = $modified -replace 'define\s+NUMBER_OF_CHANNELS\s+\S+', "#define NUMBER_OF_CHANNELS $N"
    $modified | Set-Content -Path $SimParameters -Encoding utf8

        # Build (assumes a simple gcc compile command; adapt if you use a Makefile)
        pushd $ProjectDir
        # Find .c files in directory (non-recursive)
        $cFiles = Get-ChildItem -Path $ProjectDir -Filter *.c | ForEach-Object { $_.FullName }
        $compileCmd = "gcc -O2 -std=c11 -o $ExeName " + ($cFiles -join ' ')
        Write-Host "Compiling: $compileCmd"
        cmd /c $compileCmd
        if ($LASTEXITCODE -ne 0) { Write-Error "Compilation failed for N=$N"; popd; continue }

        # Run the exe and capture output (we run once; the executable will loop over seeds defined in simparameters.h)
        $procOutput = & .\$ExeName 2>&1
        # Parse output lines for seed/blocked/arrivals
        # Expected format in output.c: "random seed = %d", "call arrival count = %ld", "blocked call count = %ld"
        $lines = $procOutput -split "`n"
        $seed = '' ; $arrivals = '' ; $blocked = ''
        foreach ($line in $lines) {
            if ($line -match 'random seed =\s*(\d+)') { $seed = $matches[1].Trim() }
            if ($line -match 'call arrival count =\s*(\d+)') { $arrivals = $matches[1].Trim() }
            if ($line -match 'blocked call count =\s*(\d+)') { $blocked = $matches[1].Trim() }
        }
        if ($arrivals -ne '' -and $blocked -ne '') {
            $PB = [double]$blocked / [double]$arrivals
            "$A,$N,$seed,$blocked,$arrivals,$PB" | Out-File -FilePath $outCsv -Append -Encoding utf8
            Write-Host "Saved result A=$A N=$N PB=$PB" 
        } else {
            Write-Warning "Could not parse simulation output for A=$A N=$N"
        }

        popd
    }
}

# Restore original simparameters.h
Copy-Item -Path $Backup -Destination $SimParameters -Force
Write-Host "Sweep complete. Results saved to $outCsv. Original simparameters.h restored."