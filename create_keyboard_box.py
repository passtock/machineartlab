import socket
import json

FUSION_SCRIPT = """
import adsk.core, adsk.fusion, math

app = adsk.core.Application.get()
ui = app.userInterface
design = app.activeProduct
root = design.rootComponent

# 1. 치수 설정 (단위: cm)
# 30mm 버튼 10개용 인체공학 키보드형 인클로저
width = 32.0       # 가로 320mm
depth = 18.0       # 세로 180mm
height = 3.8       # 높이 38mm (아케이드 버튼 마이크로스위치 수납 충분)
wall_t = 0.3       # 벽 두께 3mm
btn_radius = 1.51  # 30.2mm 직경 (30mm 버튼 삽입 공차 0.2mm 포함)

# 2. 베이스 직육면체 스케치 (XY 평면)
xyPlane = root.xYConstructionPlane
sketches = root.sketches
baseSketch = sketches.add(xyPlane)

# 중심 기준 사각형 생성 (-width/2 ~ +width/2, -depth/2 ~ +depth/2)
p1 = adsk.core.Point3D.create(-width/2, -depth/2, 0)
p2 = adsk.core.Point3D.create(width/2, depth/2, 0)
baseSketch.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)

# 돌출 (Extrude) - 메인 바디 생성
prof = baseSketch.profiles.item(0)
extrudes = root.features.extrudeFeatures
extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
dist = adsk.core.ValueInput.createByReal(height)
extInput.setDistanceExtent(False, dist)
boxBodyFeature = extrudes.add(extInput)
mainBody = boxBodyFeature.bodies.item(0)
mainBody.name = "Keyboard_Box_Main"

# 3. 4개 모서리 버티컬 필렛 (반지름 1.5cm = 15mm)
verticalEdges = adsk.core.ObjectCollection.create()
for edge in mainBody.edges:
    pStart = edge.startVertex.geometry
    pEnd = edge.endVertex.geometry
    # Z축 방향 모서리 탐색 (x, y가 거의 같고 z가 다름)
    if abs(pStart.x - pEnd.x) < 0.01 and abs(pStart.y - pEnd.y) < 0.01 and abs(pStart.z - pEnd.z) > 1.0:
        verticalEdges.add(edge)

if verticalEdges.count > 0:
    fillets = root.features.filletFeatures
    filletInput = fillets.createInput()
    filletInput.addConstantRadiusEdgeSet(verticalEdges, adsk.core.ValueInput.createByReal(1.5), True)
    fillets.add(filletInput)

# 4. 상단 모서리 필렛 (반지름 0.4cm = 4mm, 손목 닿는 곳 부드럽게)
topEdges = adsk.core.ObjectCollection.create()
for edge in mainBody.edges:
    pStart = edge.startVertex.geometry
    pEnd = edge.endVertex.geometry
    if abs(pStart.z - height) < 0.01 and abs(pEnd.z - height) < 0.01:
        topEdges.add(edge)

if topEdges.count > 0:
    fillets = root.features.filletFeatures
    filletInput = fillets.createInput()
    filletInput.addConstantRadiusEdgeSet(topEdges, adsk.core.ValueInput.createByReal(0.35), True)
    fillets.add(filletInput)

# 5. 쉘(Shell) 처리 - 바닥면을 뚫어서 내부 부품 및 배선 수납 공간 형성
bottomFace = None
for face in mainBody.faces:
    # Z가 0 근처인 바닥면 찾기
    ptOnFace = face.pointOnFace
    if abs(ptOnFace.z) < 0.01:
        bottomFace = face
        break

if bottomFace:
    shells = root.features.shellFeatures
    facesToShell = adsk.core.ObjectCollection.create()
    facesToShell.add(bottomFace)
    shellInput = shells.createInput(facesToShell, False)
    shellInput.insideThickness = adsk.core.ValueInput.createByReal(wall_t)
    shells.add(shellInput)

# 6. 상단면 버튼 홀 스케치 및 컷팅 (인체공학적 10키 배치)
# z = height 평면에 오프셋 작업평면 생성
planes = root.constructionPlanes
planeInput = planes.createInput()
offsetVal = adsk.core.ValueInput.createByReal(height)
planeInput.setByOffset(xyPlane, offsetVal)
topPlane = planes.add(planeInput)

btnSketch = sketches.add(topPlane)

# 손가락 자연 곡선 좌표 (Left Hand)
# (Pinky, Ring, Middle, Index, Thumb)
left_buttons = [
    ("L_Pinky",  -11.2,  1.2),
    ("L_Ring",   -7.8,   3.2),
    ("L_Middle", -4.4,   4.2),
    ("L_Index",  -1.4,   2.2),
    ("L_Thumb",  -3.2,  -3.2),
]

# Right Hand (대칭)
right_buttons = [
    ("R_Index",   1.4,   2.2),
    ("R_Middle",  4.4,   4.2),
    ("R_Ring",    7.8,   3.2),
    ("R_Pinky",  11.2,   1.2),
    ("R_Thumb",   3.2,  -3.2),
]

all_buttons = left_buttons + right_buttons
circles = btnSketch.sketchCurves.sketchCircles

for name, cx, cy in all_buttons:
    cp = adsk.core.Point3D.create(cx, cy, 0)
    circles.addByCenterRadius(cp, btn_radius)

# 상단면 구멍 뚫기 (Extrude Cut)
btnCutInput = extrudes.createInput(btnSketch.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
profCol = adsk.core.ObjectCollection.create()
for i in range(btnSketch.profiles.count):
    p = btnSketch.profiles.item(i)
    # 프로파일 면적이 원형 홀 면적과 근접한 것들 선택
    area = p.areaProperties().area
    if abs(area - math.pi * btn_radius * btn_radius) < 0.5:
        profCol.add(p)

if profCol.count > 0:
    btnCutInput = extrudes.createInput(profCol, adsk.fusion.FeatureOperations.CutFeatureOperation)
    cutDist = adsk.core.ValueInput.createByReal(- (wall_t + 0.5))
    btnCutInput.setDistanceExtent(False, cutDist)
    extrudes.add(btnCutInput)

# 7. 후면 케이블 홀 (USB-C / 아두이노 배선 출구: 14mm x 8mm)
xzPlane = root.xZConstructionPlane
planeInput = planes.createInput()
planeInput.setByOffset(xzPlane, adsk.core.ValueInput.createByReal(depth/2))
rearPlane = planes.add(planeInput)

cableSketch = sketches.add(rearPlane)
cw = 1.4  # 14mm
ch = 0.8  # 8mm
cp1 = adsk.core.Point3D.create(-cw/2, 0.8, 0)
cp2 = adsk.core.Point3D.create(cw/2, 0.8 + ch, 0)
cableSketch.sketchCurves.sketchLines.addTwoPointRectangle(cp1, cp2)

cableProf = cableSketch.profiles.item(0)
cableCutInput = extrudes.createInput(cableProf, adsk.fusion.FeatureOperations.CutFeatureOperation)
cableCutInput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(- (wall_t + 0.5)))
extrudes.add(cableCutInput)

# 8. 카메라 뷰를 모델에 맞게 자동 줌
cam = app.activeViewport.camera
cam.isFitView = True
app.activeViewport.camera = cam

"성공적으로 10버튼 키보드 박스가 생성되었습니다!"
"""

def main():
    s = socket.socket()
    s.connect(('127.0.0.1', 9876))
    payload = json.dumps({'type': 'execute_code', 'params': {'code': FUSION_SCRIPT}}) + '\n'
    s.sendall(payload.encode('utf-8'))
    s.settimeout(15)
    
    buf = ""
    while True:
        chunk = s.recv(4096).decode('utf-8')
        if not chunk:
            break
        buf += chunk
        if '\n' in buf:
            break
    s.close()
    
    resp = json.loads(buf)
    print("Response Status:", resp.get("status"))
    print("Result:", resp.get("result", resp.get("message")))

if __name__ == '__main__':
    main()
