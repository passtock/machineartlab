import socket
import json
import base64

MODELING_CODE = """
import adsk.core, adsk.fusion, math

app = adsk.core.Application.get()
ui = app.userInterface
design = app.activeProduct
root = design.rootComponent

# -------------------------------------------------------------
# 1. 치수 및 파라미터 정의 (단위: cm)
# -------------------------------------------------------------
width = 36.0       # 가로 360mm (양손 10손가락 편안한 배치)
depth = 20.0       # 세로 200mm (손목 팜레스트 55mm 확보)
height = 3.8       # 높이 38mm (30mm 아케이드 버튼 깊이 충분)
wall_t = 0.3       # 벽 두께 3mm
btn_r = 1.51       # 30mm 버튼용 반경 15.1mm (3D프린팅 조립 공차 포함)

xyPlane = root.xYConstructionPlane
xzPlane = root.xZConstructionPlane
sketches = root.sketches
extrudes = root.features.extrudeFeatures

# -------------------------------------------------------------
# 2. 메인 바디 생성 (베이스 박스)
# -------------------------------------------------------------
baseSketch = sketches.add(xyPlane)
p1 = adsk.core.Point3D.create(-width/2, -depth/2, 0)
p2 = adsk.core.Point3D.create(width/2, depth/2, 0)
baseSketch.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)

prof0 = baseSketch.profiles.item(0)
extInput = extrudes.createInput(prof0, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
extInput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(height))
boxFeature = extrudes.add(extInput)
mainBody = boxFeature.bodies.item(0)
mainBody.name = "Ergonomic_10Key_Box"

# -------------------------------------------------------------
# 3. 모서리 필렛 (수직 모서리 15mm, 상단 테두리 3.5mm)
# -------------------------------------------------------------
# 수직 모서리 4개
vEdges = adsk.core.ObjectCollection.create()
for edge in mainBody.edges:
    pS = edge.startVertex.geometry
    pE = edge.endVertex.geometry
    if abs(pS.x - pE.x) < 0.05 and abs(pS.y - pE.y) < 0.05 and abs(pS.z - pE.z) > (height * 0.8):
        vEdges.add(edge)

if vEdges.count > 0:
    fillets = root.features.filletFeatures
    fInput = fillets.createInput()
    fInput.addConstantRadiusEdgeSet(vEdges, adsk.core.ValueInput.createByReal(1.5), True)
    fillets.add(fInput)

# 상단 모서리 (손목 보호용 부드러운 필렛)
tEdges = adsk.core.ObjectCollection.create()
for edge in mainBody.edges:
    pS = edge.startVertex.geometry
    pE = edge.endVertex.geometry
    if abs(pS.z - height) < 0.05 and abs(pE.z - height) < 0.05:
        tEdges.add(edge)

if tEdges.count > 0:
    fillets = root.features.filletFeatures
    fInput = fillets.createInput()
    fInput.addConstantRadiusEdgeSet(tEdges, adsk.core.ValueInput.createByReal(0.35), True)
    fillets.add(fInput)

# -------------------------------------------------------------
# 4. 쉘 (Shell) 처리 - 바닥면을 뚫어 내부 공간 형성
# -------------------------------------------------------------
bottomFace = None
for face in mainBody.faces:
    if abs(face.pointOnFace.z) < 0.01:
        bottomFace = face
        break

if bottomFace:
    shells = root.features.shellFeatures
    fCollection = adsk.core.ObjectCollection.create()
    fCollection.add(bottomFace)
    shInput = shells.createInput(fCollection, False)
    shInput.insideThickness = adsk.core.ValueInput.createByReal(wall_t)
    shells.add(shInput)

# -------------------------------------------------------------
# 5. 상단면 인체공학적 10버튼 배치 및 타공
# -------------------------------------------------------------
planes = root.constructionPlanes
pInput = planes.createInput()
pInput.setByOffset(xyPlane, adsk.core.ValueInput.createByReal(height))
topPlane = planes.add(pInput)

btnSketch = sketches.add(topPlane)
circles = btnSketch.sketchCurves.sketchCircles

# 자연스러운 손가락 곡선 배치 좌표 (cm)
# 왼손 5키 (Pinky, Ring, Middle, Index, Thumb)
left_layout = [
    ("L_Pinky",  -13.5,  0.2),
    ("L_Ring",   -10.0,  2.6),
    ("L_Middle",  -6.4,  3.4),
    ("L_Index",   -2.8,  1.8),
    ("L_Thumb",   -4.5, -3.0),
]

# 오른손 5키 (대칭 미러링)
right_layout = [
    ("R_Index",    2.8,  1.8),
    ("R_Middle",   6.4,  3.4),
    ("R_Ring",    10.0,  2.6),
    ("R_Pinky",   13.5,  0.2),
    ("R_Thumb",    4.5, -3.0),
]

for name, cx, cy in (left_layout + right_layout):
    pt = adsk.core.Point3D.create(cx, cy, 0)
    circles.addByCenterRadius(pt, btn_r)

# 10개 원형 프로파일 수집 및 컷팅
targetArea = math.pi * btn_r * btn_r
holeProfiles = adsk.core.ObjectCollection.create()
for i in range(btnSketch.profiles.count):
    prof = btnSketch.profiles.item(i)
    if abs(prof.areaProperties().area - targetArea) < 0.6:
        holeProfiles.add(prof)

if holeProfiles.count > 0:
    cutInput = extrudes.createInput(holeProfiles, adsk.fusion.FeatureOperations.CutFeatureOperation)
    # 상단면 두께(3mm) 관통하여 컷 (-0.8cm)
    cutInput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(-0.8))
    extrudes.add(cutInput)

# -------------------------------------------------------------
# 6. 후면 케이블 출구 홀 (USB-C / 아두이노 배선용 14mm x 8mm)
# -------------------------------------------------------------
# XY 평면에서 후면 벽을 관통하는 컷팅 스케치 생성
cableSketch = sketches.add(xyPlane)
cw = 1.4  # 14mm
# Y = depth/2 - wall_t - 0.2 에서 Y = depth/2 + 0.2 영역
cb_p1 = adsk.core.Point3D.create(-cw/2, (depth/2) - wall_t - 0.2, 0)
cb_p2 = adsk.core.Point3D.create(cw/2, (depth/2) + 0.2, 0)
cableSketch.sketchCurves.sketchLines.addTwoPointRectangle(cb_p1, cb_p2)

cableProf = cableSketch.profiles.item(0)
cbCut = extrudes.createInput(cableProf, adsk.fusion.FeatureOperations.CutFeatureOperation)
# Z = 0.5cm 부터 Z = 1.4cm 까지 컷팅 (높이 9mm)
extentFrom = adsk.fusion.FromEntityStartDefinition.create(
    adsk.core.ValueInput.createByReal(0.5)
)
# 간편하게 양방향 돌출컷 또는 0.5cm 시작 + 0.9cm 거리
cbCut.setDistanceExtent(False, adsk.core.ValueInput.createByReal(1.4))
extrudes.add(cbCut)

# -------------------------------------------------------------
# 7. 모서리 4개 내부 볼트 기둥 (스크류 보스 M3)
# -------------------------------------------------------------
bossSketch = sketches.add(xyPlane)
boss_pts = [
    (-width/2 + 1.8, -depth/2 + 1.8),
    ( width/2 - 1.8, -depth/2 + 1.8),
    (-width/2 + 1.8,  depth/2 - 1.8),
    ( width/2 - 1.8,  depth/2 - 1.8),
]
for bx, by in boss_pts:
    bossSketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(bx, by, 0), 0.45  # 9mm 외경
    )

bossProfs = adsk.core.ObjectCollection.create()
targetBossArea = math.pi * 0.45 * 0.45
for i in range(bossSketch.profiles.count):
    bp = bossSketch.profiles.item(i)
    if abs(bp.areaProperties().area - targetBossArea) < 0.2:
        bossProfs.add(bp)

if bossProfs.count > 0:
    bossExt = extrudes.createInput(bossProfs, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    bossExt.setDistanceExtent(False, adsk.core.ValueInput.createByReal(height - wall_t))
    extrudes.add(bossExt)

# -------------------------------------------------------------
# 8. 스케치 숨기기 및 카메라 맞춤
# -------------------------------------------------------------
for s in root.sketches:
    s.isVisible = False

cam = app.activeViewport.camera
cam.isFitView = True
app.activeViewport.camera = cam

"인체공학적 10키 키보드 박스 모델링이 완벽하게 완료되었습니다!"
"""

def run():
    s = socket.socket()
    s.connect(('127.0.0.1', 9876))
    payload = json.dumps({'type': 'execute_code', 'params': {'code': MODELING_CODE}}) + '\n'
    s.sendall(payload.encode('utf-8'))
    s.settimeout(20)
    
    raw = b""
    while True:
        chunk = s.recv(65536)
        if not chunk:
            break
        raw += chunk
        if b'\n' in raw:
            break
    s.close()
    
    res = json.loads(raw.decode('utf-8'))
    print("Execute Status:", res.get("status"))
    print("Result:", res.get("result", {}).get("result", res.get("message")))

if __name__ == '__main__':
    run()
