import socket
import json
import base64

UPDATE_SCRIPT = """
import adsk.core, adsk.fusion, math

app = adsk.core.Application.get()
ui = app.userInterface
design = app.activeProduct
root = design.rootComponent

# 이전 피처 및 바디 깔끔하게 전체 삭제
while root.features.count > 0:
    root.features.item(root.features.count - 1).deleteMe()
while root.sketches.count > 0:
    root.sketches.item(root.sketches.count - 1).deleteMe()
while root.constructionPlanes.count > 0:
    root.constructionPlanes.item(root.constructionPlanes.count - 1).deleteMe()

# -------------------------------------------------------------
# 1. 산와(Sanwa) OBSF-30 실측 스펙 기반 파라미터 (단위: cm)
# -------------------------------------------------------------
# 버튼 스펙:
# - 플랜지 림 외경: 33.5 mm (3.35 cm)
# - 하부 삽입 몸체 외경: 29.5 mm (2.95 cm)
# - 플랜지 아래 몸체+단자 총 깊이: 15 + 17 = 32 mm (3.2 cm)
# - 스냅인 래치 권장 패널 두께: 3.0 mm (0.3 cm)

width = 36.0        # 가로 360 mm
depth = 20.0        # 세로 200 mm (55mm 팜레스트)
height = 4.4        # 높이 44 mm (내부 깊이 41mm -> 32mm 버튼+110단자 배선 공간 충분)
wall_t = 0.3        # 상판 및 벽 두께 3.0 mm (스냅인 래치 완벽 결합 두께)

# 방수/밀착을 위해 유격을 최소화한 타공 직경: 29.8 mm (반경 1.49 cm)
# (몸체 29.5mm 대비 사방 0.15mm 초정밀 빡빡한 유격, 상단 33.5mm 림이 완벽 밀착 씰링)
btn_r = 1.49        

# 두껍게 묶은 20선 하네스 배선 출구 홀 (원형 직경 16 mm, M16/PG9 규격)
cable_hole_r = 0.8  # 반경 8mm = 직경 16mm

xyPlane = root.xYConstructionPlane
xzPlane = root.xZConstructionPlane
sketches = root.sketches
extrudes = root.features.extrudeFeatures

# -------------------------------------------------------------
# 2. 메인 베이스 직육면체 생성
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
mainBody.name = "Sanwa_10Key_Ergonomic_Enclosure"

# -------------------------------------------------------------
# 3. 모서리 필렛 (수직 모서리 15mm, 상단 테두리 3.0mm)
# -------------------------------------------------------------
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

tEdges = adsk.core.ObjectCollection.create()
for edge in mainBody.edges:
    pS = edge.startVertex.geometry
    pE = edge.endVertex.geometry
    if abs(pS.z - height) < 0.05 and abs(pE.z - height) < 0.05:
        tEdges.add(edge)

if tEdges.count > 0:
    fillets = root.features.filletFeatures
    fInput = fillets.createInput()
    # 버튼 림(33.5mm) 안착면과의 간섭이 없도록 외곽 테두리 3mm 필렛
    fInput.addConstantRadiusEdgeSet(tEdges, adsk.core.ValueInput.createByReal(0.3), True)
    fillets.add(fInput)

# -------------------------------------------------------------
# 4. 쉘(Shell) 처리 - 바닥면 제거 및 3.0mm 균일 두께 형성
# -------------------------------------------------------------
bottomFace = None
for face in mainBody.faces:
    if abs(face.pointOnFace.z) < 0.01:
        bottomFace = face
        break

if bottomFace:
    shells = root.features.shellFeatures
    fCol = adsk.core.ObjectCollection.create()
    fCol.add(bottomFace)
    shInput = shells.createInput(fCol, False)
    shInput.insideThickness = adsk.core.ValueInput.createByReal(wall_t)
    shells.add(shInput)

# -------------------------------------------------------------
# 5. 상단면 인체공학적 10버튼 정밀 타공 (29.8mm)
# -------------------------------------------------------------
planes = root.constructionPlanes
pInput = planes.createInput()
pInput.setByOffset(xyPlane, adsk.core.ValueInput.createByReal(height))
topPlane = planes.add(pInput)

btnSketch = sketches.add(topPlane)
circles = btnSketch.sketchCurves.sketchCircles

# 자연스러운 손가락 곡선 배치 좌표 (cm)
left_layout = [
    ("L_Pinky",  -13.5,  0.2),
    ("L_Ring",   -10.0,  2.6),
    ("L_Middle",  -6.4,  3.4),
    ("L_Index",   -2.8,  1.8),
    ("L_Thumb",   -4.5, -3.0),
]

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

targetArea = math.pi * btn_r * btn_r
holeProfiles = adsk.core.ObjectCollection.create()
for i in range(btnSketch.profiles.count):
    prof = btnSketch.profiles.item(i)
    if abs(prof.areaProperties().area - targetArea) < 0.6:
        holeProfiles.add(prof)

if holeProfiles.count > 0:
    cutInput = extrudes.createInput(holeProfiles, adsk.fusion.FeatureOperations.CutFeatureOperation)
    cutInput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(-0.8))
    extrudes.add(cutInput)

# -------------------------------------------------------------
# 6. 후면 케이블 하네스 출구 홀 (16mm 원형 홀, 그로밋/케이블그랜드 표준)
# -------------------------------------------------------------
# 바닥 침수 방지를 위해 지상 20mm 높이에 타공
cablePlaneInput = planes.createInput()
cablePlaneInput.setByOffset(xzPlane, adsk.core.ValueInput.createByReal(depth/2))
rearPlane = planes.add(cablePlaneInput)

rearSketch = sketches.add(rearPlane)
# 중심 X=0, Z=2.0cm 에 원형 홀 생성
rearSketch.sketchCurves.sketchCircles.addByCenterRadius(
    adsk.core.Point3D.create(0, 2.0, 0), cable_hole_r
)

rearProf = rearSketch.profiles.item(0)
rearCut = extrudes.createInput(rearProf, adsk.fusion.FeatureOperations.CutFeatureOperation)
# 벽 두께(3mm) 관통하여 컷 (-0.8cm)
rearCut.setDistanceExtent(False, adsk.core.ValueInput.createByReal(-0.8))
extrudes.add(rearCut)

# -------------------------------------------------------------
# 7. 모서리 4개 내부 나사 체결 보스 (M3 스탠드오프)
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
        adsk.core.Point3D.create(bx, by, 0), 0.45
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
# 8. 정리 및 뷰포트 맞춤
# -------------------------------------------------------------
for s in root.sketches:
    s.isVisible = False

cam = app.activeViewport.camera
cam.isFitView = True
app.activeViewport.camera = cam

"산와 30mm 버튼 스펙 맞춤 인클로저 모델링 완료!"
"""

def update_model():
    s = socket.socket()
    s.connect(('127.0.0.1', 9876))
    payload = json.dumps({'type': 'execute_code', 'params': {'code': UPDATE_SCRIPT}}) + '\n'
    s.sendall(payload.encode('utf-8'))
    s.settimeout(25)
    
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
    update_model()
