#!/usr/bin/env bash
# 천외마경II 卍MARU 한글 통합 패치 (Mac / Linux)
# 사용법: ./patch_mac_linux.sh 입력롬.nds [출력롬.nds]
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -z "$1" ]; then
  echo "============================================================"
  echo " 천외마경II 卍MARU 한글 통합 패치 (Mac / Linux)"
  echo "============================================================"
  echo " 사용법: ./patch_mac_linux.sh 입력롬.nds [출력롬.nds]"
  echo " 예    : ./patch_mac_linux.sh Tengai2.nds"
  echo "         (출력 이름 생략 시 '입력이름_KR.nds' 로 저장)"
  echo "============================================================"
  exit 1
fi

IN="$1"
OUT="${2:-${IN%.*}_KR.nds}"

# python3 우선, 없으면 python
PY="$(command -v python3 || command -v python || true)"
if [ -z "$PY" ]; then
  echo "[오류] Python 을 찾을 수 없습니다. Python 3.8+ 를 설치하세요."
  exit 1
fi

"$PY" "$DIR/patch.py" "$IN" "$OUT"
