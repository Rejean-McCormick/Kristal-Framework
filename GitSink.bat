@echo off
setlocal EnableExtensions DisableDelayedExpansion

REM GitSink - fail-fast, non-interactive, compatible with GitSink Runner V5.
REM Important: this script stages ALL changes in its own Git repository.
REM No pause: the caller reads the returned exit code.

set "commit_message=Automated-update"
if not "%~1"=="" set "commit_message=%~1"

pushd "%~dp0" >nul 2>&1
if errorlevel 1 (
    >&2 echo ERROR [GitSink]: Cannot enter the script directory.
    exit /b 10
)

REM A Git worktree may have a .git FILE, not a directory.
if not exist ".git" (
    >&2 echo ERROR [GitSink]: No .git marker next to GitSink.bat.
    popd
    exit /b 11
)

where git >nul 2>&1
if errorlevel 1 (
    >&2 echo ERROR [GitSink]: git.exe not found in PATH.
    popd
    exit /b 12
)

echo [GitSink] Repository: %CD%
echo [GitSink] Commit message: "%commit_message%"

REM core.longpaths helps on Windows but cannot fix all OS/path problems.
echo [GitSink] git add --all
 git -c core.longpaths=true add --all
if errorlevel 1 (
    >&2 echo ERROR [GitSink]: git add failed. No commit or push attempted.
    popd
    exit /b 20
)

REM Exit codes: 0 = no staged diff; 1 = staged diff; above 1 = error.
git diff --cached --quiet
if errorlevel 2 (
    >&2 echo ERROR [GitSink]: Could not inspect staged changes. No push attempted.
    popd
    exit /b 21
)
if errorlevel 1 (
    echo [GitSink] git commit
    git commit -m "%commit_message%"
    if errorlevel 1 (
        >&2 echo ERROR [GitSink]: git commit failed. No push attempted.
        popd
        exit /b 22
    )
) else (
    echo [GitSink] No staged changes to commit.
)

echo [GitSink] git push
git push
if errorlevel 1 (
    >&2 echo ERROR [GitSink]: git push failed.
    popd
    exit /b 23
)

echo [GitSink] SUCCESS: push completed.
popd
exit /b 0
