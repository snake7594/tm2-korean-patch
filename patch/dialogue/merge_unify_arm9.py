# -*- coding: utf-8 -*-
import json, sys, os
r = json.load(open(sys.argv[1], encoding="utf-8")); res = r.get("result", r)
batches = {b["n"]: b["ko_list"] for b in res["results"] if b and b.get("ko_list")}
d = json.load(open("arm9_translation.json", encoding="utf-8"))
applied = 0; skip = []
for n in sorted(batches):
    inp = "unify_arm9/a_%03d.json" % n
    if not os.path.isfile(inp): skip.append(n); continue
    jobs = json.load(open(inp, encoding="utf-8")); ko_list = batches[n]
    if len(ko_list) != len(jobs): skip.append(n); continue
    for job, newko in zip(jobs, ko_list):
        i = job["loc"][0]; seg = d["entries"][i]
        if "jp" in seg and isinstance(newko, str) and newko != seg.get("ko"):
            seg["ko"] = newko; applied += 1
if not os.path.isfile("arm9_translation.json.preunify.bak"):
    json.dump(d, open("arm9_translation.json.preunify.bak", "w", encoding="utf-8"), ensure_ascii=False)
json.dump(d, open("arm9_translation.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("arm9 병합: %d 갱신, 스킵 %s" % (applied, skip))
