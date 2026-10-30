a_r4 independent video-to-local-direction CPU package

Requires Python, NumPy and OpenCV (cv2). No PyTorch, FlyVis install, GPU,
original Full network, full-network a0, or saved neural trajectory is required.

From this directory:
  python -I -B predict_video.py --video demo.mp4 --output new_result
  python -I -B predict_video.py --video YOUR_CLIP.mp4 --output another_result --profile own

shared (default): frozen readout calibrated on Full design data; primary comparison.
own: preregistered separate calibration on a_r4 design data; secondary usability.
Both are new local readouts, not official DecoderGAVP and not optical flow.
Original neural parameters are unchanged. No automatic fallback or profile selection.

Contract: constant-frame-rate decodable video >=2s. Only the first two seconds
are used. 224x224 grayscale conversion, aspect-preserving gray letterbox if needed,
3x3 mean at fixed61 retinal positions, 5ms causal zero-order-hold input.
Clip design has a static first0.5s; fixed baseline outputs[60:100], response[100:400].
200 gray warmup +400 movie steps all computed on own3865 states,110794 edges.
One direction is produced after the2s clip. It is not a per-frame live tracker.

Angle0=right,90=up,180=left,270=down, in the displayed image coordinate frame.
NO_CONFIDENT_MOTION is abstention; it does not prove that the scene is static.
Vector norm is not probability. The output directory must not already exist.
The included demo is the FIRST heldout clip by preregistered order, not a best case.

Validated scope: synthetic single moving luminance edge and listed controls only.
Natural video, camera shake, multiple objects, occlusion, other sizes/contrasts,
variable frame rates, arbitrary onset time, speed estimation and hardware are untested.
Changing field of view or rescaling an object changes the stimulus domain.
See parent REPORT.md and SUMMARY.json for actual failures and retained limitations.
