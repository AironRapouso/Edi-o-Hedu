"""Two-pass loudnorm of a rendered episode to -14 LUFS / -1.5 dBTP, video stream copied.
Usage: python -X utf8 loudnorm.py in.mp4 out.mp4"""
import json, subprocess, sys
src, dst = sys.argv[1], sys.argv[2]
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-vn", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
m = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
      f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-c:v", "copy", "-af", af, "-ar", "48000", "-c:a", "aac", "-b:a", "256k",
                "-movflags", "+faststart", dst], check=True)
print("input", m["input_i"], "LUFS ->", dst)
