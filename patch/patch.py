#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch.py — 천외마경II 卍MARU (ATMJ) 한글 통합 패치 (대사 + 메뉴 이미지) 일괄 적용.

한 번에 두 가지를 적용합니다:
  1) 대사/폰트  — 본문 대사 35,000여 세그먼트 + 한글 폰트 + 시스템/전투 텍스트
                  (메뉴 그래픽은 건드리지 않음)
  2) 메뉴 이미지 — 메인/필드/하단 라벨 메뉴 + 전투 명령 16개 + 시작 선택 화면(起転)

사용법:
    python patch.py 입력롬.nds 출력롬.nds

  * 입력롬: 천외마경II 卍MARU (Japan, ATMJ) 원본 또는 기존 패치본 모두 가능.
  * 매번 '깨끗한' 입력롬에 적용하는 것을 권장합니다.

준비물: Python 3.8+, 패키지 numpy / pillow / ndspy
        ( pip install numpy pillow ndspy )
"""
import sys
import os
import subprocess

PKG = os.path.dirname(os.path.abspath(__file__))
DLG = os.path.join(PKG, "dialogue")
MENU = os.path.join(PKG, "menu")


def need(path, what):
    if not os.path.exists(path):
        sys.exit(f"[오류] {what} 파일을 찾을 수 없습니다: {path}")


def check_deps():
    missing = []
    for mod in ("numpy", "PIL", "ndspy"):
        try:
            __import__(mod)
        except ImportError:
            missing.append("pillow" if mod == "PIL" else mod)
    if missing:
        sys.exit("[오류] 다음 패키지가 필요합니다: " + ", ".join(missing) +
                 "\n  설치:  pip install " + " ".join(missing))


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit("[오류] 사용법: python patch.py 입력롬.nds 출력롬.nds")

    inp = os.path.abspath(sys.argv[1])
    out = os.path.abspath(sys.argv[2])
    need(inp, "입력 ROM")
    check_deps()

    py = sys.executable
    tmp = out + ".dialogue.tmp.nds"

    # ── 1단계: 대사 + 폰트 (메뉴 그래픽 제외) ──────────────────────────
    print("=" * 56)
    print("[1/2] 대사 + 폰트 패치 중... (메뉴 이미지는 건드리지 않음)")
    print("=" * 56)
    build = os.path.join(DLG, "build_ko.py")
    need(build, "대사 패치 스크립트(build_ko.py)")
    cmd1 = [
        py, build, inp, os.path.join(DLG, "translation.json"),
        "--out", tmp,
        "--bdf", os.path.join(DLG, "Galmuri11.bdf"),
        "--ks", os.path.join(DLG, "ks2350.txt"),
        "--arm9", os.path.join(DLG, "arm9_translation.json"),
        "--overlay", os.path.join(DLG, "overlay_translation.json"),
        "--no-menu",
    ]
    r = subprocess.run(cmd1)
    if r.returncode != 0 or not os.path.exists(tmp):
        sys.exit("[오류] 대사 패치 단계에서 실패했습니다.")

    # ── 2단계: 메뉴 이미지 (대사 패치본 위에 얹음) ────────────────────
    print("=" * 56)
    print("[2/2] 메뉴 이미지 패치 중... (메인/필드/전투/시작 화면)")
    print("=" * 56)
    patch_all = os.path.join(MENU, "patch_all.py")
    need(patch_all, "메뉴 패치 스크립트(patch_all.py)")
    r = subprocess.run([py, patch_all, tmp, out])
    if r.returncode != 0 or not os.path.exists(out):
        sys.exit("[오류] 메뉴 이미지 패치 단계에서 실패했습니다.")

    # 임시 파일 정리
    try:
        os.remove(tmp)
    except OSError:
        pass

    sz = os.path.getsize(out)
    print("=" * 56)
    print(f"[완료] 한글 통합 패치 적용 -> {out}")
    print(f"       파일 크기: {sz:,} 바이트")
    if sz != 134217728:
        print("       ※ 원본(128MiB=134,217,728)과 크기가 다릅니다. 입력 ROM을 확인하세요.")
    print("       에뮬레이터(멜론DS/DeSmuME)나 플래시카트에 올려 확인하세요.")
    print("=" * 56)


if __name__ == "__main__":
    main()
