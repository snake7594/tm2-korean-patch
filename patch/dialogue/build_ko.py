#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_ko.py — 세그먼트 번역 파일(translation.json)로 한글 패치 ROM 빌드.

수행:
  1) 글꼴(fid 9138)에 한글 2,350자 글리프 삽입
  2) translation.json 의 번역된(ko 채워진) 세그먼트로 각 .scs 재조립
  3) 메뉴(fid 2766) 한글 교체
  4) 원본 용량으로 0xFF 패딩하여 저장

사용:
  python3 build_ko.py /경로/원본.nds ../output/translation.json \
      --out ../output/Tengai_KR.nds
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ndspy.rom
from tengai_cobj_font import decode_font, encode_into
from font_mapping import build_mapping
from galmuri_bdf import GalmuriBDF
from scs_repack import rebuild
from scs_segment import from_segments
import arm9_text

FONT_FID = 9138


def load_hangul(ks_path):
    return list(open(ks_path, encoding='utf-8').read().strip())


def insert_font(rom, mapping, bdf, log):
    raw = bytearray(rom.files[FONT_FID])
    assert len(raw) == 241920, f"폰트 크기 이상: {len(raw)}"
    missing = 0
    for syl, slot in mapping.syl2slot.items():
        if not bdf.has(syl):
            missing += 1
            continue
        encode_into(raw, slot, bdf.render_char(syl))
    assert len(raw) == 241920, f"폰트 크기 변경됨: {len(raw)}"
    rom.files[FONT_FID] = bytes(raw)
    log(f"  폰트: 한글 {len(mapping.syl2slot)-missing}자 기록"
        + (f" (갈무리에 없는 {missing}자 건너뜀)" if missing else ""))


def patch_dialogue(rom, doc, mapping, log):
    n_files = n_segs = 0
    for f in doc["files"]:
        # 번역된 세그먼트가 하나라도 있는 파일만 재조립
        has_ko = any((s.get("ko") or "").strip()
                     for e in f["entries"] for s in e["segs"] if "jp" in s)
        if not has_ko:
            continue
        bodies = []
        for e in sorted(f["entries"], key=lambda x: x["i"]):
            bodies.append(from_segments(e["segs"], mapping.syl2sjis))
            n_segs += sum(1 for s in e["segs"]
                          if "jp" in s and (s.get("ko") or "").strip())
        rom.files[f["file_id"]] = rebuild(f.get("reserved", 0), bodies)
        n_files += 1
    log(f"  대사: {n_files}개 파일 재조립 (번역 세그먼트 {n_segs}개 반영)")


def build(rom_path, trans_path, out_path, bdf_path, menu_font, ks_path,
          do_menu=True, arm9_path=None, overlay_path=None, log=print):
    log(f"ROM 로드: {rom_path}")
    rom = ndspy.rom.NintendoDSRom.fromFile(rom_path)
    orig_size = os.path.getsize(rom_path)

    glyphs = decode_font(rom.files[FONT_FID])
    hangul = load_hangul(ks_path)
    mapping = build_mapping(glyphs, hangul)
    log(f"  매핑: '가'->슬롯 {mapping.syl2slot['가']} (SJIS 0x{mapping.syl2sjis['가']:04X})")

    bdf = GalmuriBDF(bdf_path)
    insert_font(rom, mapping, bdf, log)

    doc = json.load(open(trans_path, encoding='utf-8'))
    patch_dialogue(rom, doc, mapping, log)

    if do_menu:
        import menu_patch
        menu_patch.patch_menu_in_rom(rom, menu_font)
        log("  메뉴 그래픽: 상태/도구/주문/무구/오의 교체")

    if arm9_path and os.path.exists(arm9_path):
        a9doc = json.load(open(arm9_path, encoding='utf-8'))
        a9 = bytearray(rom.arm9)
        applied, errors = arm9_text.apply_entries(a9, a9doc['entries'], mapping.syl2sjis)
        rom.arm9 = bytes(a9)
        log(f"  ARM9 텍스트(메뉴/시스템): {applied}개 적용" + (f", 오류 {len(errors)}" if errors else ""))
        for off, msg in errors[:10]:
            log(f"    ! 0x{off:06X}: {msg}")

    # 오버레이 패치 (배틀/저장 UI 등) — 비압축이므로 rom.files 에 직접 기록
    if overlay_path and os.path.exists(overlay_path):
        ovdoc = json.load(open(overlay_path, encoding='utf-8'))
        for oid, info in ovdoc.items():
            fid = info['fileID']
            ovdata = bytearray(rom.files[fid])
            applied, errors = arm9_text.apply_entries(ovdata, info['entries'], mapping.syl2sjis)
            rom.files[fid] = bytes(ovdata)
            log(f"  오버레이 ovl{oid}(fid{fid}): {applied}개 적용" + (f", 오류 {len(errors)}" if errors else ""))
            for off, msg in errors[:5]:
                log(f"    ! ovl{oid}+0x{off:X}: {msg}")

    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    rom.saveToFile(out_path)
    with open(out_path, 'r+b') as fp:
        fp.seek(0, 2)
        cur = fp.tell()
        if cur < orig_size:
            fp.write(b'\xff' * (orig_size - cur))
    log(f"저장: {out_path} ({os.path.getsize(out_path):,} 바이트)")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    base = os.path.dirname(here)
    ap = argparse.ArgumentParser(description="세그먼트 번역으로 한글 패치 ROM 빌드")
    ap.add_argument('rom')
    ap.add_argument('translation')
    ap.add_argument('--out', default=os.path.join(base, 'output', 'Tengai_KR.nds'))
    ap.add_argument('--bdf', default=os.path.join(base, 'fonts', 'Galmuri11.bdf'))
    ap.add_argument('--menu-font', default=os.path.join(base, 'fonts', 'Galmuri14.ttf'))
    ap.add_argument('--ks', default=os.path.join(base, 'data', 'ks2350.txt'))
    ap.add_argument('--arm9', default=os.path.join(base, 'data', 'arm9_translation.json'))
    ap.add_argument('--overlay', default=os.path.join(base, 'data', 'overlay_translation.json'))
    ap.add_argument('--no-menu', action='store_true')
    ap.add_argument('--no-arm9', action='store_true')
    ap.add_argument('--no-overlay', action='store_true')
    a = ap.parse_args()
    build(a.rom, a.translation, a.out, a.bdf, a.menu_font, a.ks,
          do_menu=not a.no_menu, arm9_path=None if a.no_arm9 else a.arm9,
          overlay_path=None if a.no_overlay else a.overlay)


if __name__ == '__main__':
    main()
