# -*- coding: utf-8 -*-
"""
머신아트랩 프로젝트 종합 성과 보고서 PPTX 생성기
Author: Antigravity
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# -------------------------------------------------------------
# Color Palette Constants
# -------------------------------------------------------------
COLOR_BG_LIGHT = RGBColor(248, 250, 252)     # #F8FAFC
COLOR_WHITE = RGBColor(255, 255, 255)        # #FFFFFF
COLOR_CARD_BORDER = RGBColor(226, 232, 240)  # #E2E8F0
COLOR_PRIMARY = RGBColor(15, 23, 42)         # #0F172A (Deep Slate)
COLOR_SECONDARY = RGBColor(71, 85, 105)      # #475569 (Slate Gray)
COLOR_MUTED = RGBColor(148, 163, 184)        # #94A3B8
COLOR_BLUE_PRIMARY = RGBColor(37, 99, 235)   # #2563EB (Royal Blue)
COLOR_BLUE_DARK = RGBColor(30, 58, 138)      # #1E3A8A (Navy)
COLOR_BLUE_LIGHT = RGBColor(239, 246, 255)   # #EFF6FF (Tag BG)
COLOR_CYAN = RGBColor(14, 165, 233)          # #0EA5E9
COLOR_TEAL = RGBColor(13, 148, 136)          # #0D9488
COLOR_EMERALD = RGBColor(16, 185, 129)       # #10B981
COLOR_AMBER = RGBColor(217, 119, 6)          # #D97706
COLOR_PURPLE = RGBColor(124, 58, 237)        # #7C3AED

FONT_HEADING = "Malgun Gothic"
FONT_BODY = "Malgun Gothic"

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Helper: Set background color of slide
    def set_slide_background(slide, color):
        bg_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5)
        )
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = color
        bg_shape.line.fill.background()
        return bg_shape

    # Helper: Add Header
    def add_header(slide, tag, title, subtitle):
        # Tag
        tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(8), Inches(0.35))
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = True
        tf_tag.margin_left = tf_tag.margin_right = tf_tag.margin_top = tf_tag.margin_bottom = 0
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = tag.upper()
        p_tag.font.name = FONT_HEADING
        p_tag.font.size = Pt(10)
        p_tag.font.bold = True
        p_tag.font.color.rgb = COLOR_BLUE_PRIMARY

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.7), Inches(0.6))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_right = tf_title.margin_top = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.name = FONT_HEADING
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_PRIMARY

        # Subtitle
        if subtitle:
            sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.48), Inches(11.7), Inches(0.4))
            tf_sub = sub_box.text_frame
            tf_sub.word_wrap = True
            tf_sub.margin_left = tf_sub.margin_right = tf_sub.margin_top = tf_sub.margin_bottom = 0
            p_sub = tf_sub.paragraphs[0]
            p_sub.text = subtitle
            p_sub.font.name = FONT_BODY
            p_sub.font.size = Pt(12)
            p_sub.font.color.rgb = COLOR_SECONDARY

    # Helper: Add Card Box
    def add_card(slide, left, top, width, height, bg_color=COLOR_WHITE, border_color=COLOR_CARD_BORDER):
        card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height
        )
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1)
        return card

    # Helper: Add Image with Border Frame & Caption
    def add_framed_image(slide, img_path, left, top, width, height, caption=""):
        if os.path.exists(img_path):
            # Frame card
            card = add_card(slide, left, top, width, height, COLOR_WHITE, COLOR_CARD_BORDER)
            # Inner picture with margin
            pad = Inches(0.08)
            img_top = top + pad
            img_height = height - (Inches(0.35) if caption else (pad * 2))
            img_left = left + pad
            img_width = width - (pad * 2)

            slide.shapes.add_picture(img_path, img_left, img_top, width=img_width, height=img_height)

            if caption:
                cap_box = slide.shapes.add_textbox(left + pad, top + height - Inches(0.32), width - pad*2, Inches(0.25))
                tf = cap_box.text_frame
                tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
                p = tf.paragraphs[0]
                p.text = caption
                p.font.name = FONT_BODY
                p.font.size = Pt(9.5)
                p.font.color.rgb = COLOR_SECONDARY
                p.alignment = PP_ALIGN.CENTER
        else:
            # Fallback if image not found
            add_card(slide, left, top, width, height, RGBColor(241, 245, 249), COLOR_CARD_BORDER)
            tbox = slide.shapes.add_textbox(left, top + height/2 - Inches(0.3), width, Inches(0.6))
            p = tbox.text_frame.paragraphs[0]
            p.text = f"[Image: {os.path.basename(img_path)}]"
            p.font.name = FONT_BODY
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_MUTED
            p.alignment = PP_ALIGN.CENTER

    # =========================================================
    # SLIDE 1: 표지 (Cover Slide)
    # =========================================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1, RGBColor(15, 23, 42)) # Deep Navy Background

    # Subtle decorative shape
    accent_bar = slide1.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), Inches(0.12), Inches(3.2)
    )
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = COLOR_BLUE_PRIMARY
    accent_bar.line.fill.background()

    # Title & Subtitle Box
    t_box = slide1.shapes.add_textbox(Inches(1.2), Inches(1.7), Inches(11.2), Inches(3.4))
    tf1 = t_box.text_frame
    tf1.word_wrap = True

    p_badge = tf1.paragraphs[0]
    p_badge.text = "MACHINE ART LAB  •  HARDWARE & INTERACTION RESEARCH"
    p_badge.font.name = FONT_HEADING
    p_badge.font.size = Pt(11)
    p_badge.font.bold = True
    p_badge.font.color.rgb = COLOR_CYAN
    p_badge.space_after = Pt(14)

    p_main = tf1.add_paragraph()
    p_main.text = "머신아트랩 프로젝트 종합 성과 보고"
    p_main.font.name = FONT_HEADING
    p_main.font.size = Pt(36)
    p_main.font.bold = True
    p_main.font.color.rgb = COLOR_WHITE
    p_main.space_after = Pt(10)

    p_sub = tf1.add_paragraph()
    p_sub.text = "하드웨어 CAD 기구설계 · 도장 3D 모델링 · 아티스트 협업 인터랙티브 시스템"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(16)
    p_sub.font.color.rgb = RGBColor(203, 213, 225)
    p_sub.space_after = Pt(24)

    p_tags = tf1.add_paragraph()
    p_tags.text = "아케이드 컨트롤러 케이스  |  사이보그 볼트 도장  |  비너스 15등분  |  인터랙티브 수조  |  ESP32 전시 시스템"
    p_tags.font.name = FONT_BODY
    p_tags.font.size = Pt(12)
    p_tags.font.color.rgb = COLOR_MUTED

    # Bottom Info Card
    meta_box = slide1.shapes.add_textbox(Inches(1.2), Inches(5.8), Inches(11.2), Inches(0.8))
    tf_meta = meta_box.text_frame
    p_meta = tf_meta.paragraphs[0]
    p_meta.text = "작성자: 이재용 연구원  |  소속: 머신아트랩 (Machine Art Lab)  |  일자: 2026년 9월"
    p_meta.font.name = FONT_BODY
    p_meta.font.size = Pt(13)
    p_meta.font.color.rgb = RGBColor(226, 232, 240)

    # =========================================================
    # SLIDE 2: 전체 프로젝트 개요 (Executive Summary / Overview)
    # =========================================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2, COLOR_BG_LIGHT)
    add_header(slide2, "EXECUTIVE SUMMARY", "프로젝트 주요 연구 및 제작 성과 개요", "머신아트랩에서 진행된 자체 하드웨어 개발 및 3인 작가 협업 프로젝트 총괄")

    tracks = [
        ("01", "10키 아케이드 컨트롤러 케이스", "Fusion 360 파라메트릭 CAD 모델링\n산와(Sanwa) 30mm 버튼 10구 실측 반영\n판금(SheetMetal) 절곡 도면 및 DXF 전개도\n3D 프린팅 보강 리브 & 하우징 패키징", COLOR_BLUE_PRIMARY),
        ("02", "사이보그 볼트 도장 3D 모델링", "기계 미학 접목 사이보그 도장 디자인\nD30mm & D40mm 파라메트릭 규격화\n0.2mm 정밀 노즐 3D 프린팅 선폭 보강\n키링 루프 일체형 하우징 및 단면 해석", COLOR_TEAL),
        ("03", "예술가(Artist) 협업 프로젝트", "장수익 작가님: 비너스 조각상 15등분 분할 및 Z축/평면 정렬\n변카카 작가님: 인터랙티브 수조 2축/3축 키네틱 & 점성 댐핑\n박건 작가님: ESP32 올인원 디스플레이 & 로드셀/룰렛 연출", COLOR_PURPLE),
        ("04", "로봇 핸드 제어 & 인프라 구축", "10 서보 모터 컨트롤러 팩 구축 (VarSpeedServo)\n가변저항 노브 및 버튼 스위치 연동 회로 설계\n전원 분배, Fritzing 배선도 및 매뉴얼 패키징\n1차 부품 정리 및 대체 부품 리스트 수립", COLOR_AMBER)
    ]

    card_w = Inches(2.78)
    card_h = Inches(4.9)
    gap = Inches(0.2)
    start_x = Inches(0.8)
    start_y = Inches(1.95)

    for i, (num, title, desc, col) in enumerate(tracks):
        x = start_x + i * (card_w + gap)
        add_card(slide2, x, start_y, card_w, card_h, COLOR_WHITE, COLOR_CARD_BORDER)

        # Number badge
        nb = slide2.shapes.add_textbox(x + Inches(0.2), start_y + Inches(0.2), Inches(0.8), Inches(0.4))
        p = nb.text_frame.paragraphs[0]
        p.text = num
        p.font.name = FONT_HEADING
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.color.rgb = col

        # Card Title
        tb = slide2.shapes.add_textbox(x + Inches(0.2), start_y + Inches(0.65), card_w - Inches(0.4), Inches(0.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_HEADING
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = COLOR_PRIMARY

        # Divider line
        div = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, x + Inches(0.2), start_y + Inches(1.5), card_w - Inches(0.4), Inches(0.02))
        div.fill.solid()
        div.fill.fore_color.rgb = col
        div.line.fill.background()

        # Description
        db = slide2.shapes.add_textbox(x + Inches(0.2), start_y + Inches(1.65), card_w - Inches(0.4), Inches(3.0))
        tf_d = db.text_frame
        tf_d.word_wrap = True
        tf_d.margin_left = tf_d.margin_right = tf_d.margin_top = tf_d.margin_bottom = 0
        
        lines = desc.split('\n')
        for l_idx, line in enumerate(lines):
            p = tf_d.paragraphs[0] if l_idx == 0 else tf_d.add_paragraph()
            p.text = "• " + line
            p.font.name = FONT_BODY
            p.font.size = Pt(10.5)
            p.font.color.rgb = COLOR_SECONDARY
            p.space_after = Pt(6)

    # =========================================================
    # SLIDE 3: 10키 컨트롤러 케이스 - Fusion 360 모델링
    # =========================================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3, COLOR_BG_LIGHT)
    add_header(slide3, "HARDWARE TRACK 01", "10키 아케이드 컨트롤러 케이스 설계 (Fusion 360 CAD)", "산와(Sanwa) OBSF-30 아케이드 버튼 실측 스펙을 반영한 고정밀 인체공학 인클로저 개발")

    # Left: Details Card
    add_card(slide3, Inches(0.8), Inches(1.95), Inches(5.8), Inches(5.0), COLOR_WHITE, COLOR_CARD_BORDER)
    tb_left = slide3.shapes.add_textbox(Inches(1.1), Inches(2.15), Inches(5.2), Inches(4.6))
    tf = tb_left.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    points_slide3 = [
        ("산와(Sanwa) OBSF-30 실측 정밀 반영", "플랜지 외경 33.5mm, 하부 바디 직경 29.5mm 기준 3D프린팅 및 가공 공차 0.2mm를 포함한 직경 30.2mm(반경 15.1mm) 홀 정밀 가공."),
        ("인체공학적 치수 및 팜레스트 확보", "가로 360mm × 세로 200mm × 높이 38mm 규격으로, 양손 10손가락 조작 시 손목 피로도를 최소화하는 55mm 하단 팜레스트(Wrist Rest) 영역 확보."),
        ("스냅인(Snap-in) 래치 최적 패널 두께", "산와 버튼 제조사 권장 패널 두께인 3.0mm를 상판 장착부에 정확히 적용하여 흔들림 없는 완벽한 스냅 결합 구현."),
        ("내부 마이크로스위치 & 단자 수납 최적화", "버튼 플랜지 하부 단자 깊이(32mm) 및 컨트롤러 내부 배선 하네스를 충분히 수용하도록 38mm 높이 및 바닥 공간 확보."),
        ("Fusion 360 파이썬 자동화 스크립트 구축", "model_sanwa_box.py를 통해 치수 변경 시 모든 피처가 연동되는 파라메트릭 모델링 및 자동 렌더링 파이프라인 구현.")
    ]

    for idx, (title_p, desc_p) in enumerate(points_slide3):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.text = f"[{title_p}]"
        p.font.name = FONT_HEADING
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = COLOR_BLUE_PRIMARY
        p.space_after = Pt(2)

        p_body = tf.add_paragraph()
        p_body.text = desc_p
        p_body.font.name = FONT_BODY
        p_body.font.size = Pt(10)
        p_body.font.color.rgb = COLOR_SECONDARY
        p_body.space_after = Pt(10)

    # Right: Render Showcase (2 images)
    img_iso = r"c:\Users\passp\Desktop\univercity\4-2\머신아트랩\fusion_render_sanwa_iso.png"
    img_top = r"c:\Users\passp\Desktop\univercity\4-2\머신아트랩\fusion_render_sanwa_top.png"
    add_framed_image(slide3, img_iso, Inches(6.8), Inches(1.95), Inches(5.7), Inches(2.6), "Fusion 360 3D Isometric View (360x200x38mm)")
    add_framed_image(slide3, img_top, Inches(6.8), Inches(4.7), Inches(5.7), Inches(2.25), "Top View (산와 OBSF-30 10구 인체공학 레이아웃 & 팜레스트)")

    # =========================================================
    # SLIDE 4: 판금(SheetMetal) 절곡 및 3D 하우징 패키지
    # =========================================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide4, COLOR_BG_LIGHT)
    add_header(slide4, "HARDWARE TRACK 01 - DETAIL", "판금(SheetMetal) 절곡 전개도 및 3D 하우징 제작 패키지", "FreeCAD 기반 상·하판 판금 절곡 설계, 2D Flat Pattern DXF 도면 및 조립 가이드 구축")

    # Left: Details Card
    add_card(slide4, Inches(0.8), Inches(1.95), Inches(5.8), Inches(5.0), COLOR_WHITE, COLOR_CARD_BORDER)
    tb_left4 = slide4.shapes.add_textbox(Inches(1.1), Inches(2.15), Inches(5.2), Inches(4.6))
    tf4 = tb_left4.text_frame
    tf4.word_wrap = True
    tf4.margin_left = tf4.margin_right = tf4.margin_top = tf4.margin_bottom = 0

    points_slide4 = [
        ("상판(TopCover) & 하판(BottomBase) 분리 구조", "정밀 결합 및 내부 기판 유지보수를 위해 상단 조작 패널과 하단 베이스를 분리형 인클로저 구조로 설계."),
        ("1.0mm 판금 벤딩 공정 파라미터 적용", "소재 두께 1.0mm (알루미늄/스틸), Bending Radius 1.0mm, K-Factor 0.44를 정밀 반영하여 절곡 후 치수 오차 제로화."),
        ("레이저 커팅용 2D Flat Pattern DXF 추출", "절곡 전 평면 전개도(Flat Pattern DXF)를 완전 자동 생성하여 레이저 커팅 및 CNC 가공 즉시 발주 가능."),
        ("단계별 3D 절곡 가이드(Folding Guide) 제작", "작업자가 한눈에 절곡 순서와 각도(90도 플랜지)를 인지할 수 있는 시각화 다이어그램 및 청사진 도면 렌더링."),
        ("3D 프린팅용 보강 리브 & 볼트 체결 마운트", "판금 외에도 FDM/SLA 3D 프린터로 즉시 출력할 수 있도록 스크루 체결 보강 기둥(Boss) 및 강성 리브(Rib) 모델 병행 개발.")
    ]

    for idx, (title_p, desc_p) in enumerate(points_slide4):
        p = tf4.paragraphs[0] if idx == 0 else tf4.add_paragraph()
        p.text = f"[{title_p}]"
        p.font.name = FONT_HEADING
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = COLOR_BLUE_PRIMARY
        p.space_after = Pt(2)

        p_body = tf4.add_paragraph()
        p_body.text = desc_p
        p_body.font.name = FONT_BODY
        p_body.font.size = Pt(10)
        p_body.font.color.rgb = COLOR_SECONDARY
        p_body.space_after = Pt(10)

    # Right: Render Showcase (SheetMetal)
    img_sm_iso = r"c:\Users\passp\Desktop\univercity\4-2\머신아트랩\개인\01_컨트롤러_3D도면_CAD\SheetMetal_3D_Isometric_Render.png"
    img_sm_guide = r"c:\Users\passp\Desktop\univercity\4-2\머신아트랩\개인\01_컨트롤러_3D도면_CAD\SheetMetal_Enclosure_3D_Folding_Guide.png"
    add_framed_image(slide4, img_sm_iso, Inches(6.8), Inches(1.95), Inches(5.7), Inches(2.6), "FreeCAD SheetMetal 3D 절곡 결합 렌더링")
    add_framed_image(slide4, img_sm_guide, Inches(6.8), Inches(4.7), Inches(5.7), Inches(2.25), "SheetMetal 3D Folding Guide (단계별 절곡 순서 및 전개도)")

    # =========================================================
    # SLIDE 5: 사이보그 볼트 도장 3D 모델링 및 규격화
    # =========================================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide5, COLOR_BG_LIGHT)
    add_header(slide5, "HARDWARE TRACK 02", "사이보그 볼트 도장 3D 모델링 및 규격화 (v13)", "기계공학적 볼트 헤드 형태와 사이보그 아트 그래픽을 결합한 시그니처 3D 도장 설계")

    # Left: Details Card
    add_card(slide5, Inches(0.8), Inches(1.95), Inches(5.8), Inches(5.0), COLOR_WHITE, COLOR_CARD_BORDER)
    tb_left5 = slide5.shapes.add_textbox(Inches(1.1), Inches(2.15), Inches(5.2), Inches(4.6))
    tf5 = tb_left5.text_frame
    tf5.word_wrap = True
    tf5.margin_left = tf5.margin_right = tf5.margin_top = tf5.margin_bottom = 0

    points_slide5 = [
        ("볼트 헤드 메커니즘 접목 아트 디자인", "표준 볼트 헤드의 육각/원형 기계적 실루엣에 머신아트랩 특유의 사이보그 페이스 그래픽을 양각/음각으로 조화롭게 융합."),
        ("D30mm & D40mm 이원화 규격 설계", "사용 목적에 맞춘 2종 크기 표준화: 휴대 및 서명용 소형 D30mm 규격과 전시 및 정밀 스탬핑용 대형 D40mm 규격 파라메트릭 완성."),
        ("상단 일체형 키링/스트랩 루프(Loop) 추가", "v13 최종 버전에서 도장 손잡이 상단에 스트랩/키링을 연결할 수 있는 루프 홀더를 일체형 솔리드로 설계하여 분실 방지 및 휴대성 향상."),
        ("FreeCAD + Python 자동 생성 스크립트", "build_bolt_stamp_30_40_v13.py 스크립트를 통해 치수 파라미터만으로 3D 솔리드 바디, 음각 형상, 키링 루프를 100% 자동 생성."),
        ("다양한 출력 포맷 완벽 패키징", "STL, STEP(CAD 호환), 3MF(Bambu Lab/Prusa 다색 슬라이싱 호환) 및 FCStd 원본 파일 아카이빙 완료.")
    ]

    for idx, (title_p, desc_p) in enumerate(points_slide5):
        p = tf5.paragraphs[0] if idx == 0 else tf5.add_paragraph()
        p.text = f"[{title_p}]"
        p.font.name = FONT_HEADING
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = COLOR_TEAL
        p.space_after = Pt(2)

        p_body = tf5.add_paragraph()
        p_body.text = desc_p
        p_body.font.name = FONT_BODY
        p_body.font.size = Pt(10)
        p_body.font.color.rgb = COLOR_SECONDARY
        p_body.space_after = Pt(10)

    # Right: Render Showcase (Stamp)
    img_stamp_3d = r"c:\Users\passp\Desktop\univercity\4-2\머신아트랩\개인\02_볼트도장_3D모델링_CAD\output_v13\Bolt_Stamp_3D_Preview_D40mm_v13.png"
    img_stamp_2d = r"c:\Users\passp\Desktop\univercity\4-2\머신아트랩\개인\02_볼트도장_3D모델링_CAD\cyborg_stamp_design_normal.png"
    add_framed_image(slide5, img_stamp_3d, Inches(6.8), Inches(1.95), Inches(5.7), Inches(3.2), "Bolt Stamp D40mm v13 3D 프리뷰 (키링 루프 & 볼트 널링 바디)")
    add_framed_image(slide5, img_stamp_2d, Inches(6.8), Inches(5.3), Inches(5.7), Inches(1.65), "사이보그 도장 원본 그래픽 벡터 디자인 (정방향/반전 벡터)")

    # =========================================================
    # SLIDE 6: 도장 CAD 단면 해석 및 0.2mm 노즐 최적화
    # =========================================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide6, COLOR_BG_LIGHT)
    add_header(slide6, "HARDWARE TRACK 02 - DETAIL", "0.2mm 정밀 노즐 3D 프린팅 최적화 및 단면 해석", "미세 음각 형상 뭉개짐 방지를 위한 선폭 보강, 챔퍼링 및 CAD 단면 강도 검증")

    # Left: Details Card
    add_card(slide6, Inches(0.8), Inches(1.95), Inches(5.8), Inches(5.0), COLOR_WHITE, COLOR_CARD_BORDER)
    tb_left6 = slide6.shapes.add_textbox(Inches(1.1), Inches(2.15), Inches(5.2), Inches(4.6))
    tf6 = tb_left6.text_frame
    tf6.word_wrap = True
    tf6.margin_left = tf6.margin_right = tf6.margin_top = tf6.margin_bottom = 0

    points_slide6 = [
        ("0.2mm 초정밀 노즐 압출 특성 반영", "일반 0.4mm 노즐 대비 0.2mm 노즐의 초미세 선폭 분해능에 맞춰 음각 라인 폭과 깊이비를 1:1.2 최적 비율로 재설계."),
        ("최소 선폭 보강 (Minimum Wall Thickness)", "도장 인쇄 시 선이 부러지거나 뭉개지지 않도록 외곽선 및 내부 세부 라인의 최소 두께를 0.35mm ~ 0.5mm 이상으로 강제 보강."),
        ("탈형 경사각(Draft Angle) 및 챔퍼링(Chamfer)", "도장 날인 후 잉크/점토가 끼어 남지 않고 깨끗하게 떨어지도록 모든 음각 벽면에 미세 탈형 경사 및 0.2mm 챔퍼 모따기 적용."),
        ("CAD 정밀 단면 해석(Cross-Section Analysis)", "stamp_sections.png 분석을 통해 상부 압력 전달 경로의 솔리드 충진도와 바닥 날인면의 평탄도(Flatness) 정밀 사전 검증."),
        ("Bambu Lab / Prusa 최적 슬라이싱 프로파일", "초기 레이어 속도 15mm/s, 인필 100% 솔리드, 아라크네(Arachne) 가변 선폭 엔진 적용 권장 가이드 수립.")
    ]

    for idx, (title_p, desc_p) in enumerate(points_slide6):
        p = tf6.paragraphs[0] if idx == 0 else tf6.add_paragraph()
        p.text = f"[{title_p}]"
        p.font.name = FONT_HEADING
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = COLOR_TEAL
        p.space_after = Pt(2)

        p_body = tf6.add_paragraph()
        p_body.text = desc_p
        p_body.font.name = FONT_BODY
        p_body.font.size = Pt(10)
        p_body.font.color.rgb = COLOR_SECONDARY
        p_body.space_after = Pt(10)

    # Right: Cross-section visual showcase
    img_section = r"c:\Users\passp\Desktop\univercity\4-2\머신아트랩\개인\02_볼트도장_3D모델링_CAD\output_v13\Bolt_Stamp_D40mm_v13_stamp_sections.png"
    add_framed_image(slide6, img_section, Inches(6.8), Inches(1.95), Inches(5.7), Inches(5.0), "CAD 단면 해석 (날인면 음각 깊이, 솔리드 충진도 및 루프 체결부 단면)")

    # =========================================================
    # SLIDE 7: 장수익 작가님 협업 - 비너스 조각상 15등분 분할 및 정렬
    # =========================================================
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide7, COLOR_BG_LIGHT)
    add_header(slide7, "ARTIST COLLABORATION 01", "장수익 작가님: 비너스 조각상 3D 모델 15등분 분할 및 정렬", "대형 3D 스캔 메쉬 데이터 정밀 슬라이싱, 절단면 수밀화 캡핑 및 전시·가공용 OBJ 파이프라인 개발")

    # Left: Details Card
    add_card(slide7, Inches(0.8), Inches(1.95), Inches(5.8), Inches(5.0), COLOR_WHITE, COLOR_CARD_BORDER)
    tb_left7 = slide7.shapes.add_textbox(Inches(1.1), Inches(2.15), Inches(5.2), Inches(4.6))
    tf7 = tb_left7.text_frame
    tf7.word_wrap = True
    tf7.margin_left = tf7.margin_right = tf7.margin_top = tf7.margin_bottom = 0

    points_slide7 = [
        ("고해상도 비너스 3D 스캔 메쉬 분석", "원본 비너스 모델(비너스1.obj, 약 50만 정점)의 Z축 바운딩 박스를 정밀 측정하여 높이 기준 정확한 등간격(dz) 계산."),
        ("Trimesh 기반 수평 15등분 정밀 슬라이싱", "slice_venus.py를 통해 각 레이어 평면 절단 후 열린 단면을 삼각망으로 자동 메꿔주는 수밀화(Watertight Solid Capping) 알고리즘 구현."),
        ("Z축 10mm / 20mm 간격 전개 OBJ 생성", "조각상 내부 단면과 유기적 분해 과정을 시각화하기 위해 각 레이어를 Z축 방향으로 10mm, 20mm씩 띄워 정렬한 분해 조립도 OBJ 구축."),
        ("평면 5×3 그리드 배치 OBJ 개발", "3D 프린터 베드 일괄 출력 및 CNC 조각 가공 편의를 위해 15개 파트를 바닥 평면에 5행 3열 매트릭스로 정렬 배치한 통합 파일 생성."),
        ("단일 통합 OBJ 및 파트별 데이터 패키징", "전체 15개 파트를 하나의 파일로 다루면서도 파트별 오브젝트 그룹이 분리된 비너스_15등분_통합.obj 완성.")
    ]

    for idx, (title_p, desc_p) in enumerate(points_slide7):
        p = tf7.paragraphs[0] if idx == 0 else tf7.add_paragraph()
        p.text = f"[{title_p}]"
        p.font.name = FONT_HEADING
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = COLOR_PURPLE
        p.space_after = Pt(2)

        p_body = tf7.add_paragraph()
        p_body.text = desc_p
        p_body.font.name = FONT_BODY
        p_body.font.size = Pt(10)
        p_body.font.color.rgb = COLOR_SECONDARY
        p_body.space_after = Pt(10)

    # Right: Render Showcase (Venus)
    img_venus = r"c:\Users\passp\Desktop\univercity\4-2\머신아트랩\장수익작가님\venus_15_render.png"
    add_framed_image(slide7, img_venus, Inches(6.8), Inches(1.95), Inches(5.7), Inches(5.0), "비너스 15등분 Z축 20mm 간격 정렬 분해 3D 렌더링 (49.5만 정점)")

    # =========================================================
    # SLIDE 8: 변카카 작가님 협업 - 인터랙티브 수조 키네틱
    # =========================================================
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide8, COLOR_BG_LIGHT)
    add_header(slide8, "ARTIST COLLABORATION 02", "변카카 작가님: 인터랙티브 수조 키네틱 설치물 기구 설계", "수조 내부 매달린 오브제의 유기적 유영을 위한 2축/3축 메커니즘 비교 및 물속 점성 댐핑 알고리즘 구현")

    # Left: Details Card
    add_card(slide8, Inches(0.8), Inches(1.95), Inches(5.8), Inches(5.0), COLOR_WHITE, COLOR_CARD_BORDER)
    tb_left8 = slide8.shapes.add_textbox(Inches(1.1), Inches(2.15), Inches(5.2), Inches(4.6))
    tf8 = tb_left8.text_frame
    tf8.word_wrap = True
    tf8.margin_left = tf8.margin_right = tf8.margin_top = tf8.margin_bottom = 0

    points_slide8 = [
        ("관람객 조작형 수중 키네틱 컨셉 도출", "관람객이 레버를 조작하면 투명 와이어에 매달린 오브제가 수조 속에서 마치 살아있는 유기체처럼 부드럽게 유영하는 인터랙션 연출."),
        ("2축 vs 3축 인형뽑기 크레인 메커니즘 심층 비교", "X-Z 2축(수평 이동+승강) 방식과 X-Y-Z 3축 공간 이동 방식의 제작 복잡도, 모터 토크, 전시 안정성 및 관람객 몰입도 다각도 분석 가이드 수립."),
        ("구동계 하드웨어 선정 및 BOM 수립", "소형 수조(깊이 25cm)용 고토크 메탈 서보(MG996R/DS3218) 방식과 깊은 수조용 NEMA 17 스텝모터 + TMC2208 무소음 드라이버 방식 비교 및 부품 목록화."),
        ("물속 점성(Damping) 시뮬레이션 알고리즘 개발", "관람객이 레버를 급격히 당겨도 소프트웨어 지수이동평균(EMA) 필터를 거쳐 물속 저항을 받듯 우아하고 부드럽게 감속하는 펌웨어 코드 개발."),
        ("줄 끊김 및 모터 과부하 방지 안전 로직", "소프트웨어적 상·하한선 리밋 및 급가속 방지 로직을 내장하여 전시 중 고장 위험 원천 차단.")
    ]

    for idx, (title_p, desc_p) in enumerate(points_slide8):
        p = tf8.paragraphs[0] if idx == 0 else tf8.add_paragraph()
        p.text = f"[{title_p}]"
        p.font.name = FONT_HEADING
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = COLOR_PURPLE
        p.space_after = Pt(2)

        p_body = tf8.add_paragraph()
        p_body.text = desc_p
        p_body.font.name = FONT_BODY
        p_body.font.size = Pt(10)
        p_body.font.color.rgb = COLOR_SECONDARY
        p_body.space_after = Pt(10)

    # Right: Mechanism Architecture Box
    add_card(slide8, Inches(6.8), Inches(1.95), Inches(5.7), Inches(5.0), COLOR_WHITE, COLOR_CARD_BORDER)
    tb_r8 = slide8.shapes.add_textbox(Inches(7.1), Inches(2.15), Inches(5.1), Inches(4.6))
    tf_r8 = tb_r8.text_frame
    tf_r8.word_wrap = True
    tf_r8.margin_left = tf_r8.margin_right = tf_r8.margin_top = tf_r8.margin_bottom = 0

    p_rt = tf_r8.paragraphs[0]
    p_rt.text = "[시스템 인터랙션 및 구동 파이프라인]"
    p_rt.font.name = FONT_HEADING
    p_rt.font.size = Pt(13)
    p_rt.font.bold = True
    p_rt.font.color.rgb = COLOR_PRIMARY
    p_rt.space_after = Pt(12)

    flow_items = [
        ("1. 관람객 입력부", "아날로그 1축/2축 조작 레버 (0~100% 가변 저항 입력)"),
        ("2. 제어 컨트롤러 (MCU)", "Arduino Uno / ESP32 실시간 ADC 샘플링 (10ms 주기)"),
        ("3. 소프트웨어 댐핑 필터", "Target = Target * α + Input * (1 - α) (물속 점성 모사)"),
        ("4. 액추에이터 구동부", "20kg 메탈기어 서보 or NEMA17 + TMC2208 스텝모터"),
        ("5. 수조 내부 연출부", "투명 나일론 와이어 + 밸런스 웨이트 + 유기적 오브제 유영")
    ]

    for stage, sdesc in flow_items:
        p_s = tf_r8.add_paragraph()
        p_s.text = f"▶ {stage}"
        p_s.font.name = FONT_HEADING
        p_s.font.size = Pt(11)
        p_s.font.bold = True
        p_s.font.color.rgb = COLOR_BLUE_PRIMARY
        p_s.space_after = Pt(2)

        p_sd = tf_r8.add_paragraph()
        p_sd.text = sdesc
        p_sd.font.name = FONT_BODY
        p_sd.font.size = Pt(9.5)
        p_sd.font.color.rgb = COLOR_SECONDARY
        p_sd.space_after = Pt(8)

    # =========================================================
    # SLIDE 9: 박건 작가님 협업 - ESP32 스마트 디스플레이 All-in-One
    # =========================================================
    slide9 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide9, COLOR_BG_LIGHT)
    add_header(slide9, "ARTIST COLLABORATION 03", "박건 작가님: ESP32 스마트 디스플레이 All-in-One 전시 시스템", "별도 외장 아두이노 없이 고성능 ESP32 단독으로 센서 감지, 초고속 사진 표출 및 카지노 룰렛 연출")

    # Left: Details Card
    add_card(slide9, Inches(0.8), Inches(1.95), Inches(5.8), Inches(5.0), COLOR_WHITE, COLOR_CARD_BORDER)
    tb_left9 = slide9.shapes.add_textbox(Inches(1.1), Inches(2.15), Inches(5.2), Inches(4.6))
    tf9 = tb_left9.text_frame
    tf9.word_wrap = True
    tf9.margin_left = tf9.margin_right = tf9.margin_top = tf9.margin_bottom = 0

    points_slide9 = [
        ("단일 ESP32 All-in-One 심플 아키텍처", "외장 컨트롤러 간 복잡한 통신 배선 없이, 고성능 ESP32 스마트 디스플레이 보드 1대에 센서와 액추에이터를 5가닥 직결하여 전시 안정성 극대화."),
        ("100mm 원판 + 5kg 로드셀(HX711) 하중 감지", "관람객이 손을 얹는 미세한 하중(100g 이상)을 24비트 정밀 ADC로 0.05초 만에 즉각 감지."),
        ("SD 카드 고해상도 무작위 이미지 0.1초 고속 렌더링", "LovyanGFX 및 TJpg_Decoder 라이브러리를 적용하여 손을 댈 때마다 SD 카드의 /images 무작위 사진을 800x480 풀화면에 0.1초 내 출력."),
        ("8자리 세그먼트 카지노 슬롯머신 감속 연출", "MAX7219 세그먼트 숫자가 촤라락 고속 회전하다가 왼쪽부터 '탁! 탁! 탁!' 멈추며 속도가 점차 줄어드는 극적 룰렛 애니메이션 펌웨어 개발."),
        ("상승 피치 피에조 부저 사운드 & 부품 리스트 수립", "하중 감지 시 600Hz에서 2400Hz로 피치가 급상승하는 효과음 연동 및 1차 부품 리스트(Excel/Docx) 납품 완료.")
    ]

    for idx, (title_p, desc_p) in enumerate(points_slide9):
        p = tf9.paragraphs[0] if idx == 0 else tf9.add_paragraph()
        p.text = f"[{title_p}]"
        p.font.name = FONT_HEADING
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = COLOR_PURPLE
        p.space_after = Pt(2)

        p_body = tf9.add_paragraph()
        p_body.text = desc_p
        p_body.font.name = FONT_BODY
        p_body.font.size = Pt(10)
        p_body.font.color.rgb = COLOR_SECONDARY
        p_body.space_after = Pt(10)

    # Right: Wiring & Interaction Spec Card
    add_card(slide9, Inches(6.8), Inches(1.95), Inches(5.7), Inches(5.0), COLOR_WHITE, COLOR_CARD_BORDER)
    tb_r9 = slide9.shapes.add_textbox(Inches(7.1), Inches(2.15), Inches(5.1), Inches(4.6))
    tf_r9 = tb_r9.text_frame
    tf_r9.word_wrap = True
    tf_r9.margin_left = tf_r9.margin_right = tf_r9.margin_top = tf_r9.margin_bottom = 0

    p_r9t = tf_r9.paragraphs[0]
    p_r9t.text = "[하드웨어 배선 및 연출 시나리오]"
    p_r9t.font.name = FONT_HEADING
    p_r9t.font.size = Pt(13)
    p_r9t.font.bold = True
    p_r9t.font.color.rgb = COLOR_PRIMARY
    p_r9t.space_after = Pt(12)

    scenarios = [
        ("1. 대기 모드 (STATE_IDLE)", "LCD 대기 화면 출력, 세그먼트에 '--------' 점멸 대기"),
        ("2. 손 올림 감지 (STATE_TRIGGERED)", "로드셀 하중 감지 즉시 트리거 -> 부저 상승음 피치 출력"),
        ("3. 동시 다중 연출 (Simultaneous Event)", "• LCD: SD카드 무작위 사진 0.1초 고속 렌더링\n• 세그먼트: 8자리 카지노 슬롯머신 감속 롤링"),
        ("4. 결과 확정 (STATE_RESULT)", "세그먼트에 최종 행운의 숫자 고정, 사운드 완료"),
        ("5. 5가닥 직결 하드웨어 핀맵", "• HX711: GPIO 2(DT), GPIO 3(SCK)\n• MAX7219: GPIO 17(DIN), 18(CLK), 19(CS)\n• 부저: GPIO 10(PWM)")
    ]

    for stitle, sbody in scenarios:
        p_st = tf_r9.add_paragraph()
        p_st.text = f"■ {stitle}"
        p_st.font.name = FONT_HEADING
        p_st.font.size = Pt(10.5)
        p_st.font.bold = True
        p_st.font.color.rgb = COLOR_BLUE_PRIMARY
        p_st.space_after = Pt(2)

        p_sb = tf_r9.add_paragraph()
        p_sb.text = sbody
        p_sb.font.name = FONT_BODY
        p_sb.font.size = Pt(9.5)
        p_sb.font.color.rgb = COLOR_SECONDARY
        p_sb.space_after = Pt(7)

    # =========================================================
    # SLIDE 10: 로봇 핸드 10 서보 모터 컨트롤러 팩
    # =========================================================
    slide10 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide10, COLOR_BG_LIGHT)
    add_header(slide10, "SUPPORTING TRACK 04", "로봇 핸드 10 서보 모터 컨트롤러 팩 구축", "10자유도(DoF) 로봇 손가락 구동을 위한 다채널 서보 제어기, 가변저항 회로 및 패키지 개발")

    # Left: Details Card
    add_card(slide10, Inches(0.8), Inches(1.95), Inches(5.8), Inches(5.0), COLOR_WHITE, COLOR_CARD_BORDER)
    tb_left10 = slide10.shapes.add_textbox(Inches(1.1), Inches(2.15), Inches(5.2), Inches(4.6))
    tf10 = tb_left10.text_frame
    tf10.word_wrap = True
    tf10.margin_left = tf10.margin_right = tf10.margin_top = tf10.margin_bottom = 0

    points_slide10 = [
        ("10개 서보 모터 독립/연동 제어 시스템", "양손 또는 10개 관절을 정밀 구동하기 위해 아두이노 메가/우노 기반 다채널 PWM 서보 제어 파이프라인 수립."),
        ("VarSpeedServo 라이브러리 가감속 궤적 제어", "일반 Servo 라이브러리의 모터 튕김 현상을 해결하고, 속도(Speed)와 위치(Position)를 부드럽게 비동기 제어하는 알고리즘 탑재."),
        ("포텐셔미터(가변저항) 노브 & 버튼 하이브리드 제어", "회전형 아날로그 노브를 통한 미세 각도 실시간 수동 조작 및 원터치 버튼을 통한 프리셋 파지(Grasp) 모션 지원."),
        ("외부 전원 분배 회로(5V 5A~10A) 안정화", "다수의 서보 모터 동시 구동 시 발생하는 MCU 전압 강하(Brown-out)를 방지하기 위해 신호선과 동력선을 완전 분리한 배선도 설계."),
        ("상세 사용설명서 & Fritzing 회로도 아카이빙", "hand_controller_pack 내 모드 변경 방법, 핀 연결표 및 회로도(knob_schem.png) 패키지화.")
    ]

    for idx, (title_p, desc_p) in enumerate(points_slide10):
        p = tf10.paragraphs[0] if idx == 0 else tf10.add_paragraph()
        p.text = f"[{title_p}]"
        p.font.name = FONT_HEADING
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = COLOR_AMBER
        p.space_after = Pt(2)

        p_body = tf10.add_paragraph()
        p_body.text = desc_p
        p_body.font.name = FONT_BODY
        p_body.font.size = Pt(10)
        p_body.font.color.rgb = COLOR_SECONDARY
        p_body.space_after = Pt(10)

    # Right: Render Showcase (Knob Schematics)
    img_knob = r"c:\Users\passp\Desktop\univercity\4-2\머신아트랩\hand_controller_pack\handv.0\knob_schem.png"
    add_framed_image(slide10, img_knob, Inches(6.8), Inches(1.95), Inches(5.7), Inches(5.0), "서보 모터 & 가변저항 노브 입력 제어 회로도 (Schematic)")

    # =========================================================
    # SLIDE 11: 종합 성과 요약 및 향후 계획 (Milestones & Next Steps)
    # =========================================================
    slide11 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide11, COLOR_BG_LIGHT)
    add_header(slide11, "PROJECT ROADMAP & NEXT STEPS", "종합 성과 요약 및 향후 추진 계획", "각 트랙별 현 진행 상태(Status) 점검 및 하드웨어 제작·조립·실장 일정")

    # Table Card
    add_card(slide11, Inches(0.8), Inches(1.95), Inches(11.733), Inches(4.9), COLOR_WHITE, COLOR_CARD_BORDER)

    tb_t = slide11.shapes.add_textbox(Inches(1.1), Inches(2.15), Inches(11.133), Inches(4.5))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0

    p_th = tf_t.paragraphs[0]
    p_th.text = "주요 개발 항목별 성과 현황 (Milestone Matrix)"
    p_th.font.name = FONT_HEADING
    p_th.font.size = Pt(14)
    p_th.font.bold = True
    p_th.font.color.rgb = COLOR_PRIMARY
    p_th.space_after = Pt(12)

    matrix_rows = [
        ("10키 아케이드 케이스", "Fusion 360 CAD 완료, 판금 전개도(DXF) 및 렌더링 완료", "3D 프린터 시제품 출력, 산와 버튼 10구 장착 및 조립 공차 실측 검증", "100% (설계완료)"),
        ("사이보그 볼트 도장", "D30/D40 v13 파라메트릭 완성, 루프 일체화, 0.2mm 노즐 최적화", "레진(SLA) 및 FDM 3D 프린팅 출력, 인주/잉크 날인 시인성 및 디테일 테스트", "100% (설계완료)"),
        ("장수익 작가님 비너스", "15등분 슬라이싱 완료, Z축 간격 분해도 & 평면 5x3 그리드 생성", "작가님 최종 데이터 전달, 조각 설치 구조물 반영 및 가공 지원", "100% (데이터납품)"),
        ("변카카 작가님 키네틱 수조", "2축/3축 비교 가이드, 서보/스텝 제어 펌웨어 및 점성 댐핑 로직 개발", "소형 프로토타입 수조에 메탈 서보 & 낚싯줄 기구부 결합 및 동작 테스트", "90% (제어완료)"),
        ("박건 작가님 디스플레이", "ESP32 단독 제어 아키텍처, 로드셀+고속사진+세그먼트 룰렛 코드 완성", "ESP32 스마트 디스플레이 보드 펌웨어 업로드, 센서 하니스 납땜 및 패키징", "95% (펌웨어완료)"),
        ("로봇 핸드 제어 팩", "10 서보 모터 VarSpeedServo 코드, 회로도, 사용자 설명서 패키징", "로봇 핸드 기구부 링크 연결, 10채널 동작 캘리브레이션 및 전시 시연", "100% (패키징완료)")
    ]

    for item, done, next_step, status in matrix_rows:
        p_row = tf_t.add_paragraph()
        p_row.text = f"• [{item}] "
        p_row.font.name = FONT_HEADING
        p_row.font.size = Pt(10.5)
        p_row.font.bold = True
        p_row.font.color.rgb = COLOR_BLUE_PRIMARY

        run_done = p_row.add_run()
        run_done.text = f"완료: {done}  |  "
        run_done.font.name = FONT_BODY
        run_done.font.size = Pt(10)
        run_done.font.bold = False
        run_done.font.color.rgb = COLOR_SECONDARY

        run_next = p_row.add_run()
        run_next.text = f"차주 계획: {next_step}  "
        run_next.font.name = FONT_BODY
        run_next.font.size = Pt(10)
        run_next.font.bold = False
        run_next.font.color.rgb = COLOR_PRIMARY

        run_stat = p_row.add_run()
        run_stat.text = f"[{status}]"
        run_stat.font.name = FONT_HEADING
        run_stat.font.size = Pt(10)
        run_stat.font.bold = True
        run_stat.font.color.rgb = COLOR_EMERALD

        p_row.space_after = Pt(7)

    # =========================================================
    # SLIDE 12: 결론 및 엔딩 (Conclusion / Q&A)
    # =========================================================
    slide12 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide12, RGBColor(15, 23, 42)) # Deep Navy

    # Center card
    t_end = slide12.shapes.add_textbox(Inches(1.5), Inches(2.2), Inches(10.333), Inches(3.2))
    tf12 = t_end.text_frame
    tf12.word_wrap = True

    p_e1 = tf12.paragraphs[0]
    p_e1.text = "MACHINE ART LAB  •  HARDWARE & INTERACTION RESEARCH"
    p_e1.font.name = FONT_HEADING
    p_e1.font.size = Pt(12)
    p_e1.font.bold = True
    p_e1.font.color.rgb = COLOR_CYAN
    p_e1.alignment = PP_ALIGN.CENTER
    p_e1.space_after = Pt(16)

    p_e2 = tf12.add_paragraph()
    p_e2.text = "감사합니다"
    p_e2.font.name = FONT_HEADING
    p_e2.font.size = Pt(38)
    p_e2.font.bold = True
    p_e2.font.color.rgb = COLOR_WHITE
    p_e2.alignment = PP_ALIGN.CENTER
    p_e2.space_after = Pt(14)

    p_e3 = tf12.add_paragraph()
    p_e3.text = "하드웨어 정밀 설계부터 예술가 인터랙티브 시스템까지 실물 구현을 완성해 나가겠습니다."
    p_e3.font.name = FONT_BODY
    p_e3.font.size = Pt(14)
    p_e3.font.color.rgb = RGBColor(203, 213, 225)
    p_e3.alignment = PP_ALIGN.CENTER
    p_e3.space_after = Pt(20)

    p_e4 = tf12.add_paragraph()
    p_e4.text = "문의 및 질의응답 (Q&A)  |  발표자: 이재용"
    p_e4.font.name = FONT_BODY
    p_e4.font.size = Pt(12)
    p_e4.font.color.rgb = COLOR_MUTED
    p_e4.alignment = PP_ALIGN.CENTER

    # Save presentation
    output_path = r"c:\Users\passp\Desktop\univercity\4-2\머신아트랩\머신아트랩_프로젝트_성과보고.pptx"
    prs.save(output_path)
    print(f"[SUCCESS] Presentation saved to: {output_path}")

if __name__ == "__main__":
    create_presentation()
