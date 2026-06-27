@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

if "%~1"=="" (
  echo ============================================================
  echo  천외마경II 卍MARU 한글 통합 패치 ^(Windows^)
  echo ============================================================
  echo  사용법 1^) 이 창에 ROM 파일을 마우스로 끌어다 놓으세요.
  echo  사용법 2^) patch_windows.bat "입력롬.nds"
  echo  사용법 3^) python patch.py 입력롬.nds 출력롬.nds
  echo.
  echo  ROM 파일을 이 배치 파일 위로 드래그하면 자동 실행됩니다.
  echo ============================================================
  pause
  exit /b
)

echo 입력 ROM : %~1
echo 출력 ROM : %~dpn1_KR.nds
echo.
python "%~dp0patch.py" "%~1" "%~dpn1_KR.nds"
echo.
pause
endlocal
