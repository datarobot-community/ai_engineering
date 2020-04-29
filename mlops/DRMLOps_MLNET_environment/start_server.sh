#!/bin/sh

export DOTNET_CLI_HOME="/tmp/DOTNET_CLI_HOME"
export DOTNET_CLI_TELEMETRY_OPTOUT="1"
export TMPDIR=/tmp/NuGetScratch/
mkdir -p ${TMPDIR}
rm -rf obj/ bin/
dotnet clean
dotnet build
dotnet run
tail -f /dev/null