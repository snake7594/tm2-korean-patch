# -*- coding: utf-8 -*-
"""통일 워크플로 결과(ko_list)를 translation.json 에 병합.
사용: python merge_unify.py <워크플로결과.json>
- 각 배치 u_NNN.json 의 loc 순서와 ko_list 를 매칭해 해당 seg.ko 갱신.
"""
import json, sys, os, glob

result_path = sys.argv[1]
r = json.load(open(result_path, encoding="utf-8"))
res = r.get("result", r)
batches = {b["n"]: b["ko_list"] for b in res["results"] if b and b.get("ko_list")}

d = json.load(open("translation.json", encoding="utf-8"))
applied = 0; skipped_batches = []; mismatch = 0
for n in sorted(batches):
    inp = "unify_batches/u_%03d.json" % n
    if not os.path.isfile(inp):
        skipped_batches.append(n); continue
    jobs = json.load(open(inp, encoding="utf-8"))
    ko_list = batches[n]
    if len(ko_list) != len(jobs):
        # 길이 불일치 → 안전하게 그 배치 스킵(부분반영 위험)
        mismatch += 1; skipped_batches.append(n); continue
    for job, newko in zip(jobs, ko_list):
        fi, ei, si = job["loc"]
        seg = d["files"][fi]["entries"][ei]["segs"][si]
        if "jp" in seg and isinstance(newko, str) and newko != seg.get("ko"):
            seg["ko"] = newko; applied += 1

# 백업 후 저장
if not os.path.isfile("translation.json.preunify.bak"):
    json.dump(d, open("translation.json.preunify.bak", "w", encoding="utf-8"), ensure_ascii=False)
json.dump(d, open("translation.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("병합: %d개 세그먼트 ko 갱신" % applied)
print("결과 배치 %d개, 스킵(길이불일치/누락) %d개: %s" % (len(batches), len(skipped_batches), skipped_batches[:20]))
