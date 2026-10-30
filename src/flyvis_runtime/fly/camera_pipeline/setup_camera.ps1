$ErrorActionPreference = 'Stop'
$cameraRoot = $PSScriptRoot
$cameraPython = Join-Path (Split-Path $cameraRoot) '.venv/Scripts/python.exe'
& $cameraPython -m pip install --disable-pip-version-check --no-deps --target (Join-Path $cameraRoot '_vendor') opencv-python==4.10.0.84
if ($LASTEXITCODE -ne 0) { throw 'OpenCV installation failed' }
& $cameraPython -c "import sys; sys.path.insert(0,r'$cameraRoot/_vendor'); import cv2,numpy; print('OpenCV',cv2.__version__,'NumPy',numpy.__version__)"
