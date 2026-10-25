"""Regression check for the visible torso/hand jolt and uneven GIF cadence."""
from pathlib import Path
import json
from PIL import Image
here=Path(__file__).resolve().parent
p=here/'previews/run'
data=json.loads((p/'motion_analysis.json').read_text())
motion=json.loads((p/'motion.json').read_text())
fps=motion['fps']; summary=data['summary']
pelvis=max(summary['pelvis']['second_difference_m'])*fps*fps
hand=max(max(summary[n]['second_difference_m']) for n in ('hand_l','hand_r') if n in summary)*fps*fps
gif=Image.open(here/'previews/officer_v2_run.gif'); durations=[]
for i in range(gif.n_frames): gif.seek(i); durations.append(gif.info['duration'])
print(json.dumps({'pelvis_peak_acceleration_m_s2':pelvis,'hand_peak_acceleration_m_s2':hand,'gif_duration_range_ms':[min(durations),max(durations)]}))
assert pelvis<15, f'Torso jolt remains: {pelvis:.1f} m/s²'
assert hand<35, f'Wrist jolt remains: {hand:.1f} m/s²'
speed=summary['stance_foot_velocity_m_s']
assert max(speed)-min(speed)<.015, 'Planted foot speeds up or slows down instead of moving steadily'
assert min(durations)==max(durations), 'GIF has uneven frame timing'
print('MOTION_SMOOTHNESS_PASSED')
