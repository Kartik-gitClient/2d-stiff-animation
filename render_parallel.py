# -*- coding: utf-8 -*-
"""
Parallel renderer for Horror Shorts (ep02 through ep10)
Uses 3 parallel worker processes on 8 CPU cores.
"""
import os, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from render_suite import render_episode

REMAINING_EPS = [
    "ep02_antim_bus",
    "ep03_gudiya",
    "ep04_chhaaya",
    "ep05_phone_call",
    "ep06_kuan",
    "ep07_train",
    "ep08_tasveer",
    "ep09_pustakalaya",
    "ep10_manzil",
]

def render_worker(ep):
    t0 = time.time()
    try:
        out = render_episode(ep)
        elapsed = round(time.time() - t0, 1)
        return (ep, True, out, elapsed)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return (ep, False, str(e), round(time.time() - t0, 1))

if __name__ == "__main__":
    workers = 3
    print(f"Starting parallel render of {len(REMAINING_EPS)} episodes with {workers} workers...")
    t_start = time.time()
    
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(render_worker, ep): ep for ep in REMAINING_EPS}
        for future in as_completed(futures):
            ep = futures[future]
            name, success, info, elapsed = future.result()
            status = "✓ DONE" if success else "✗ FAILED"
            print(f"[{status}] {name} in {elapsed}s: {info}", flush=True)

    total_time = round(time.time() - t_start, 1)
    print(f"\nAll {len(REMAINING_EPS)} episodes finished in {total_time}s!")
