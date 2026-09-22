# -*- coding: utf-8 -*-
"""
머신아트랩 핵심 성과보고 PPTX 생성기 (v2 - 초대형 폰트 & 도장 이미지 확대 & 산와 명칭 제거)
"""

import os
import sys
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# -------------------------------------------------------------
# Color Palette Constants
# -------------------------------------------------------------
COLOR_BG_LIGHT = RGBColor(248, 250, 252)     # #F8FAFC
COLOR_WHITE = RGBColor(255, 255, 255)        # #FFFFFF
COLOR_CARD_BORDER = RGBColor(226, 232, 240)  # #E2E8F0
COLOR_PRIMARY = RGBColor(15, 23, 42)         # #0F172A (Deep Slate)
COLOR_SECONDARY = RGBColor(30, 41, 59)       # #1E293B (Very crisp dark text)
COLOR_MUTED = RGBColor(100, 116, 139)        # #64748B
COLOR_BLUE_PRIMARY = RGBColor(37, 99, 235)   # #2563EB (Royal Blue)
COLOR_BLUE_DARK = RGBColor(30, 58, 138)      # #1E3A8A (Navy)
COLOR_CYAN = RGBColor(14, 165, 233)          # #0EA5E9
COLOR_TEAL = RGBColor(13, 148, 136)          # #0D9488
COLOR_EMERALD = RGBColor(16, 185, 129)       # #10B981
COLOR_AMBER = RGBColor(217, 119, 6)          # #D97706

FONT_FAMILY = "Malgun Gothic"

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide, color):
        bg_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5)
        )
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = color
        bg_shape.line.fill.background()
        return bg_shape

    def add_header(slide, tag, title, subtitle):
        # Category Tag
        tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.38), Inches(11.7), Inches(0.35))
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = True
        tf_tag.margin_left = tf_tag.margin_right = tf_tag.margin_top = tf_tag.margin_bottom = 0
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = tag.upper()
        p_tag.font.name = FONT_FAMILY
        p_tag.font.size = Pt(14)
        p_tag.font.bold = True
        p_tag.font.color.rgb = COLOR_BLUE_PRIMARY

        # Big Title (30pt)
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.74), Inches(11.7), Inches(0.7))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_right = tf_title.margin_top = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.name = FONT_FAMILY
        p_title.font.size = Pt(30)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_PRIMARY

        # Subtitle (16pt)
        if subtitle:
            sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.45), Inches(11.7), Inches(0.35))
            tf_sub = sub_box.text_frame
            tf_sub.word_wrap = True
            tf_sub.margin_left = tf_sub.margin_right = tf_sub.margin_top = tf_sub.margin_bottom = 0
            p_sub = tf_sub.paragraphs[0]
            p_sub.text = subtitle
            p_sub.font.name = FONT_FAMILY
            p_sub.font.size = Pt(16)
            p_sub.font.color.rgb = COLOR_MUTED

    def add_card(slide, left, top, width, height, bg_color=COLOR_WHITE, border_color=COLOR_CARD_BORDER):
        card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height
        )
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)
        return card

    # Image adder with perfect aspect ratio preservation & zero distortion
    def add_fitted_image(slide, img_path, box_left, box_top, box_width, box_height, caption="", bg_card=True):
        if not os.path.exists(img_path):
            return
        
        im = Image.open(img_path)
        im_w, im_h = im.size
        aspect = im_w / float(im_h)

        pad = Inches(0.08)
        cap_h = Inches(0.4) if caption else Inches(0.0)
        avail_w = box_width - (pad * 2)
        avail_h = box_height - (pad * 2) - cap_h

        box_aspect = avail_w / avail_h
        if aspect > box_aspect:
            final_w = avail_w
            final_h = avail_w / aspect
        else:
            final_h = avail_h
            final_w = avail_h * aspect

        img_left = box_left + pad + (avail_w - final_w) / 2
        img_top = box_top + pad + (avail_h - final_h) / 2

        if bg_card:
            add_card(slide, box_left, box_top, box_width, box_height, COLOR_WHITE, COLOR_CARD_BORDER)
        
        slide.shapes.add_picture(img_path, img_left, img_top, width=final_w, height=final_h)

        if caption:
            cap_box = slide.shapes.add_textbox(box_left + pad, box_top + box_height - Inches(0.38), box_width - pad*2, Inches(0.32))
            tf = cap_box.text_frame
            tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            p = tf.paragraphs[0]
            p.text = caption
            p.font.name = FONT_FAMILY
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = COLOR_SECONDARY
            p.alignment = PP_ALIGN.CENTER

    # =========================================================
    # SLIDE 1: 표지 (Cover Slide - Extra Big Fonts)
    # =========================================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1, RGBColor(15, 23, 42))

    accent_bar = slide1.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.8), Inches(0.18), Inches(3.6)
    )
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = COLOR_BLUE_PRIMARY
    accent_bar.line.fill.background()

    t_box = slide1.shapes.add_textbox(Inches(1.4), Inches(1.7), Inches(10.9), Inches(3.8))
    tf1 = t_box.text_frame
    tf1.word_wrap = True

    p_badge = tf1.paragraphs[0]
    p_badge.text = "MACHINE ART LAB  •  CORE PROJECT REPORT"
    p_badge.font.name = FONT_FAMILY
    p_badge.font.size = Pt(16)
    p_badge.font.bold = True
    p_badge.font.color.rgb = COLOR_CYAN
    p_badge.space_after = Pt(16)

    p_main = tf1.add_paragraph()
    p_main.text = "머신아트랩 핵심 프로젝트 성과 보고"
    p_main.font.name = FONT_FAMILY
    p_main.font.size = Pt(42)
    p_main.font.bold = True
    p_main.font.color.rgb = COLOR_WHITE
    p_main.space_after = Pt(14)

    p_sub = tf1.add_paragraph()
    p_sub.text = "컨트롤러 케이스  |  사이보그 볼트 도장  |  10채널 핸드 제어 회로"
    p_sub.font.name = FONT_FAMILY
    p_sub.font.size = Pt(22)
    p_sub.font.bold = True
    p_sub.font.color.rgb = RGBColor(226, 232, 240)
    p_sub.space_after = Pt(22)

    p_meta = tf1.add_paragraph()
    p_meta.text = "연구원: 이재용  |  소속: 머신아트랩  |  2026년 9월"
    p_meta.font.name = FONT_FAMILY
    p_meta.font.size = Pt(17)
    p_meta.font.color.rgb = COLOR_MUTED

    # =========================================================
    # SLIDE 2: 3대 핵심 프로젝트 개요 (Overview - Big Font Cards)
    # =========================================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2, COLOR_BG_LIGHT)
    add_header(slide2, "CORE TRACKS", "3대 핵심 하드웨어 및 제어 프로젝트 개요", "자체 기구설계, 3D 모델링 및 10채널 로봇 핸드 펌웨어/회로 시스템 요약")

    core_tracks = [
        ("TRACK 01", "10키 버튼 케이스 설계", 
         [
             "30mm 버튼 10구 실측 반영",
             "Fusion 360 파라메트릭 CAD 모델링",
             "판금(SheetMetal) 절곡 전개도(DXF)",
             "손목 55mm 팜레스트 공간 확보"
         ], COLOR_BLUE_PRIMARY),
        ("TRACK 02", "사이보그 볼트 도장 디자인", 
         [
             "볼트 헤드 + 사이보그 아트 융합",
             "D30mm & D40mm (v13) 규격화",
             "상단 일체형 키링 고리(Loop) 설계",
             "0.2mm 노즐 특화: 최소선폭 보강"
         ], COLOR_TEAL),
        ("TRACK 03", "10채널 핸드 제어 시스템", 
         [
             "button_10_servos.ino 기반 1:1 제어",
             "10개 버튼 내부 풀업 직결 배선",
             "논블로킹 부드러운 각도 스무딩",
             "D12 릴레이 & 5V 대전류 독립 전원"
         ], COLOR_AMBER)
    ]

    card_w = Inches(3.75)
    card_h = Inches(5.1)
    gap = Inches(0.24)
    start_x = Inches(0.8)
    start_y = Inches(1.9)

    for i, (tag_t, title_t, points, col) in enumerate(core_tracks):
        x = start_x + i * (card_w + gap)
        add_card(slide2, x, start_y, card_w, card_h, COLOR_WHITE, COLOR_CARD_BORDER)

        # Tag
        tb = slide2.shapes.add_textbox(x + Inches(0.25), start_y + Inches(0.25), card_w - Inches(0.5), Inches(0.35))
        p = tb.text_frame.paragraphs[0]
        p.text = tag_t
        p.font.name = FONT_FAMILY
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = col

        # Title (22pt)
        tb_t = slide2.shapes.add_textbox(x + Inches(0.25), start_y + Inches(0.65), card_w - Inches(0.5), Inches(0.8))
        tf_t = tb_t.text_frame
        tf_t.word_wrap = True
        p = tf_t.paragraphs[0]
        p.text = title_t
        p.font.name = FONT_FAMILY
        p.font.size = Pt(21)
        p.font.bold = True
        p.font.color.rgb = COLOR_PRIMARY

        # Divider
        div = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, x + Inches(0.25), start_y + Inches(1.5), card_w - Inches(0.5), Inches(0.03))
        div.fill.solid()
        div.fill.fore_color.rgb = col
        div.line.fill.background()

        # Points (Large Font 16pt)
        tb_p = slide2.shapes.add_textbox(x + Inches(0.25), start_y + Inches(1.68), card_w - Inches(0.5), Inches(3.2))
        tf_p = tb_p.text_frame
        tf_p.word_wrap = True
        tf_p.margin_left = tf_p.margin_right = tf_p.margin_top = tf_p.margin_bottom = 0

        for p_idx, pt_text in enumerate(points):
            p = tf_p.paragraphs[0] if p_idx == 0 else tf_p.add_paragraph()
            p.text = "• " + pt_text
            p.font.name = FONT_FAMILY
            p.font.size = Pt(16)
            p.font.bold = True if p_idx == 0 else False
            p.font.color.rgb = COLOR_SECONDARY
            p.space_after = Pt(14)

    # =========================================================
    # SLIDE 3: 10키 버튼 케이스 - Fusion 360 (Big Fonts)
    # =========================================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3, COLOR_BG_LIGHT)
    add_header(slide3, "TRACK 01 : CONTROLLER CASE", "10키 버튼 컨트롤러 케이스 (Fusion 360 CAD)", "30mm 규격 버튼 실측 스펙을 반영한 고정밀 인체공학 인클로저")

    # Left: Details Card (Large Font 16~19pt)
    add_card(slide3, Inches(0.8), Inches(1.9), Inches(6.0), Inches(5.1), COLOR_WHITE, COLOR_CARD_BORDER)
    tb_left3 = slide3.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(5.4), Inches(4.7))
    tf3 = tb_left3.text_frame
    tf3.word_wrap = True
    tf3.margin_left = tf3.margin_right = tf3.margin_top = tf3.margin_bottom = 0

    points_c3 = [
        ("30mm 규격 버튼 실측 정밀 반영", "외경 33.5mm, 장착부 29.5mm 기준 0.2mm 조립 공차를 포함한 30.2mm 홀 정밀 가공"),
        ("360 × 200 × 38 mm 와이드 바디", "양손 10손가락 조작 시 손목 피로를 최소화하는 55mm 팜레스트(Wrist Rest) 영역 확보"),
        ("스냅인 래치 최적 패널 두께 3.0mm", "버튼 흔들림 없는 완벽한 스냅 결합 및 하부 배선 수납 공간(깊이 38mm) 충분히 확보")
    ]

    for idx, (head_t, body_t) in enumerate(points_c3):
        p = tf3.paragraphs[0] if idx == 0 else tf3.add_paragraph()
        p.text = f"■ {head_t}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(19)
        p.font.bold = True
        p.font.color.rgb = COLOR_BLUE_PRIMARY
        p.space_after = Pt(4)

        p_b = tf3.add_paragraph()
        p_b.text = body_t
        p_b.font.name = FONT_FAMILY
        p_b.font.size = Pt(16)
        p_b.font.color.rgb = COLOR_SECONDARY
        p_b.space_after = Pt(20)

    # Right: Render Showcase (2 images, fitted with exact aspect ratio)
    img_iso = r"c:\Users\passp\Desktop\univercity\4-2\머신아트랩\fusion_render_sanwa_iso.png"
    img_top = r"c:\Users\passp\Desktop\univercity\4-2\머신아트랩\fusion_render_sanwa_top.png"
    add_fitted_image(slide3, img_iso, Inches(7.0), Inches(1.9), Inches(5.533), Inches(2.55), "Fusion 360 3D 렌더링 (360×200×38mm)")
    add_fitted_image(slide3, img_top, Inches(7.0), Inches(4.55), Inches(5.533), Inches(2.45), "Top View (30mm 10구 버튼 배열 & 팜레스트)")

    # =========================================================
    # SLIDE 4: 케이스 - 판금(SheetMetal) 절곡 및 패키징
    # =========================================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide4, COLOR_BG_LIGHT)
    add_header(slide4, "TRACK 01 : SHEET METAL & 3D PRINTING", "판금(SheetMetal) 절곡 도면 및 제작 패키지", "FreeCAD 기반 상·하판 판금 절곡 설계, 2D Flat Pattern DXF 전개도 및 조립 구조")

    add_card(slide4, Inches(0.8), Inches(1.9), Inches(6.0), Inches(5.1), COLOR_WHITE, COLOR_CARD_BORDER)
    tb_left4 = slide4.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(5.4), Inches(4.7))
    tf4 = tb_left4.text_frame
    tf4.word_wrap = True
    tf4.margin_left = tf4.margin_right = tf4.margin_top = tf4.margin_bottom = 0

    points_c4 = [
        ("상판(TopCover) & 하판(BottomBase) 2피스 구조", "정밀 결합 및 내부 기판 유지보수가 용이하도록 상단 조작 패널과 하단 베이스 분리 설계"),
        ("1.0mm 판금 절곡 파라미터 적용", "소재 두께 1.0mm, K-Factor 0.44를 정밀 반영하여 절곡 후 오차 제로화 및 2D DXF 도면 추출"),
        ("3D 프린팅 보강 리브 & 체결 보스(Boss)", "판금 외에도 FDM 3D 프린터로 즉시 출력할 수 있도록 스크루 결합용 보강 기둥 모델 병행 구축")
    ]

    for idx, (head_t, body_t) in enumerate(points_c4):
        p = tf4.paragraphs[0] if idx == 0 else tf4.add_paragraph()
        p.text = f"■ {head_t}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(19)
        p.font.bold = True
        p.font.color.rgb = COLOR_BLUE_PRIMARY
        p.space_after = Pt(4)

        p_b = tf4.add_paragraph()
        p_b.text = body_t
        p_b.font.name = FONT_FAMILY
        p_b.font.size = Pt(16)
        p_b.font.color.rgb = COLOR_SECONDARY
        p_b.space_after = Pt(20)

    img_sm_iso = r"c:\Users\passp\Desktop\univercity\4-2\머신아트랩\개인\01_컨트롤러_3D도면_CAD\SheetMetal_3D_Isometric_Render.png"
    img_sm_guide = r"c:\Users\passp\Desktop\univercity\4-2\머신아트랩\개인\01_컨트롤러_3D도면_CAD\SheetMetal_Enclosure_3D_Folding_Guide.png"
    add_fitted_image(slide4, img_sm_iso, Inches(7.0), Inches(1.9), Inches(5.533), Inches(2.55), "FreeCAD SheetMetal 3D 절곡 결합 렌더링")
    add_fitted_image(slide4, img_sm_guide, Inches(7.0), Inches(4.55), Inches(5.533), Inches(2.45), "3D Folding Guide (단계별 절곡 순서 가이드)")

    # =========================================================
    # SLIDE 5: 사이보그 볼트 도장 3D 모델링 (도장 그림 대폭 확대!)
    # =========================================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide5, COLOR_BG_LIGHT)
    add_header(slide5, "TRACK 02 : STAMP DESIGN", "사이보그 볼트 도장 3D 모델링 (v13)", "기계식 볼트 헤드 형태와 사이보그 아트 그래픽을 결합한 시그니처 3D 도장 설계")

    # Left: Details Card (Text widened and enlarged: 19pt title, 16pt body)
    add_card(slide5, Inches(0.8), Inches(1.9), Inches(5.8), Inches(5.1), COLOR_WHITE, COLOR_CARD_BORDER)
    tb_left5 = slide5.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(5.2), Inches(4.7))
    tf5 = tb_left5.text_frame
    tf5.word_wrap = True
    tf5.margin_left = tf5.margin_right = tf5.margin_top = tf5.margin_bottom = 0

    points_c5 = [
        ("볼트 헤드 메커니즘 + 사이보그 아트", "기계식 볼트 헤드의 외형에 사이보그 페이스 그래픽을 음각/양각으로 조화롭게 융합"),
        ("D30mm & D40mm 이원화 규격 설계", "휴대 및 서명용 소형 D30mm 규격과 전시 및 정밀 날인용 대형 D40mm 규격 2종 파라메트릭 완성"),
        ("상단 일체형 키링/스트랩 루프(Loop)", "도장 상단에 키링/스트랩 연결 고리를 솔리드로 일체 설계하여 분실 방지 및 휴대성 극대화"),
        ("Python 파이프라인 기반 자동 생성", "build_bolt_stamp_30_40_v13.py 스크립트로 바디, 널링, 음각, 루프를 100% 자동 생성 및 패키징")
    ]

    for idx, (head_t, body_t) in enumerate(points_c5):
        p = tf5.paragraphs[0] if idx == 0 else tf5.add_paragraph()
        p.text = f"■ {head_t}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = COLOR_TEAL
        p.space_after = Pt(3)

        p_b = tf5.add_paragraph()
        p_b.text = body_t
        p_b.font.name = FONT_FAMILY
        p_b.font.size = Pt(15.5)
        p_b.font.color.rgb = COLOR_SECONDARY
        p_b.space_after = Pt(15)

    # Right: Stamp 3D Render - HUGE SIZE (1:1 Ratio, 5.7" wide, 5.1" high!)
    img_stamp_3d = r"c:\Users\passp\Desktop\univercity\4-2\머신아트랩\개인\02_볼트도장_3D모델링_CAD\output_v13\Bolt_Stamp_3D_Preview_D40mm_v13.png"
    add_fitted_image(slide5, img_stamp_3d, Inches(6.8), Inches(1.9), Inches(5.733), Inches(5.1), "Bolt Stamp D40mm v13 3D 프리뷰 (키링 루프 & 널링 바디)")

    # =========================================================
    # SLIDE 6: 도장 0.2mm 노즐 최적화 & 단면 해석 (단면 그림 대폭 확대!)
    # =========================================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide6, COLOR_BG_LIGHT)
    add_header(slide6, "TRACK 02 : DETAIL", "0.2mm 정밀 노즐 3D 프린팅 최적화 & 단면 해석", "미세 음각 선폭 보강, 챔퍼링 및 CAD 단면 강도 검증")

    # Left: Details Card (Large Font 19pt title, 16pt body)
    add_card(slide6, Inches(0.8), Inches(1.9), Inches(5.8), Inches(5.1), COLOR_WHITE, COLOR_CARD_BORDER)
    tb_left6 = slide6.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(5.2), Inches(4.7))
    tf6 = tb_left6.text_frame
    tf6.word_wrap = True
    tf6.margin_left = tf6.margin_right = tf6.margin_top = tf6.margin_bottom = 0

    points_c6 = [
        ("0.2mm 초정밀 노즐 압출비(1:1.2) 최적화", "초미세 선폭 분해능에 맞춰 음각 라인 폭과 깊이비를 1:1.2 최적 비율로 정밀 재설계"),
        ("최소 선폭 보강 (0.35mm ~ 0.5mm)", "도장 날인 시 얇은 벽면이 뭉개지거나 파손되지 않도록 모든 선폭을 0.35mm 이상으로 강제 보강"),
        ("탈형 경사각(Draft Angle) & 0.2mm 챔퍼", "날인 후 잉크/점토가 도장 틈새에 끼지 않고 깨끗하게 떨어지도록 모든 음각 벽면에 모따기 적용"),
        ("CAD 정밀 단면 해석(Cross-Section)", "stamp_sections.png 분석을 통해 상부 가압 시 하중 전달 솔리드 충진도와 바닥 날인면 평탄도 검증")
    ]

    for idx, (head_t, body_t) in enumerate(points_c6):
        p = tf6.paragraphs[0] if idx == 0 else tf6.add_paragraph()
        p.text = f"■ {head_t}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = COLOR_TEAL
        p.space_after = Pt(3)

        p_b = tf6.add_paragraph()
        p_b.text = body_t
        p_b.font.name = FONT_FAMILY
        p_b.font.size = Pt(15.5)
        p_b.font.color.rgb = COLOR_SECONDARY
        p_b.space_after = Pt(15)

    # Right: Stamp Section Images - LARGE SIZE WITH CORRECT ASPECT RATIO
    # Upper image: Wide 3:1 section
    img_section = r"c:\Users\passp\Desktop\univercity\4-2\머신아트랩\개인\02_볼트도장_3D모델링_CAD\output_v13\Bolt_Stamp_D40mm_v13_stamp_sections.png"
    # Lower image: 2D Cyborg Graphic
    img_stamp_2d = r"c:\Users\passp\Desktop\univercity\4-2\머신아트랩\개인\02_볼트도장_3D모델링_CAD\cyborg_stamp_design_normal.png"
    add_fitted_image(slide6, img_section, Inches(6.8), Inches(1.9), Inches(5.733), Inches(2.65), "CAD 정밀 단면 해석 (음각 깊이 & 솔리드 충진도)")
    add_fitted_image(slide6, img_stamp_2d, Inches(6.8), Inches(4.65), Inches(5.733), Inches(2.35), "사이보그 도장 원본 벡터 그래픽 디자인")

    # =========================================================
    # SLIDE 7: 로봇 핸드 10채널 제어 시스템 (Big Fonts)
    # =========================================================
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide7, COLOR_BG_LIGHT)
    add_header(slide7, "TRACK 03 : HAND CONTROLLER", "로봇 핸드 10 서보 모터 제어 시스템 (button_10_servos.ino)", "10개 푸시 버튼과 10개 서보 모터 1:1 매칭, 내부 풀업 배선 및 논블로킹 가감속 제어")

    # Left: Core Logic Card (Large Font 19pt title, 16pt body)
    add_card(slide7, Inches(0.8), Inches(1.9), Inches(6.0), Inches(5.1), COLOR_WHITE, COLOR_CARD_BORDER)
    tb_left7 = slide7.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(5.4), Inches(4.7))
    tf7 = tb_left7.text_frame
    tf7.word_wrap = True
    tf7.margin_left = tf7.margin_right = tf7.margin_top = tf7.margin_bottom = 0

    points_c7 = [
        ("10버튼 - 10서보 1:1 완벽 독립 매핑", "왼손 5개(A0~A11 → D2~D6), 오른손 5개(A5~A9 → D7~D11) 개별 손가락 완전 독립 구동"),
        ("내부 풀업 (INPUT_PULLUP) 직결 배선", "외장 저항 없이 버튼의 한쪽은 아두이노 핀, 다른 쪽은 공통 GND에 연결 (누르면 LOW, 떼면 HIGH)"),
        ("15ms 논블로킹 타이머 각도 스무딩", "1도씩 부드럽게 가감속 추종하여 모터의 튕김 및 과부하를 방지하고 실시간 자연스러운 모션 구현"),
        ("핀 12 전원 릴레이/MOSFET 안전 제어", "POWER_SERVO_PIN(12) 제어로 비상 정지 및 전원 인가/차단을 소프트웨어로 완벽 제어")
    ]

    for idx, (head_t, body_t) in enumerate(points_c7):
        p = tf7.paragraphs[0] if idx == 0 else tf7.add_paragraph()
        p.text = f"■ {head_t}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = COLOR_AMBER
        p.space_after = Pt(3)

        p_b = tf7.add_paragraph()
        p_b.text = body_t
        p_b.font.name = FONT_FAMILY
        p_b.font.size = Pt(15.5)
        p_b.font.color.rgb = COLOR_SECONDARY
        p_b.space_after = Pt(16)

    # Right: Pin Mapping & Mode Table Card (Big Font 17~22pt)
    add_card(slide7, Inches(7.0), Inches(1.9), Inches(5.533), Inches(5.1), COLOR_WHITE, COLOR_CARD_BORDER)
    tb_r7 = slide7.shapes.add_textbox(Inches(7.3), Inches(2.1), Inches(5.0), Inches(4.7))
    tf_r7 = tb_r7.text_frame
    tf_r7.word_wrap = True
    tf_r7.margin_left = tf_r7.margin_right = tf_r7.margin_top = tf_r7.margin_bottom = 0

    p_rt = tf_r7.paragraphs[0]
    p_rt.text = "[하드웨어 핀맵 & 각도 설정값]"
    p_rt.font.name = FONT_FAMILY
    p_rt.font.size = Pt(21)
    p_rt.font.bold = True
    p_rt.font.color.rgb = COLOR_PRIMARY
    p_rt.space_after = Pt(14)

    pin_specs = [
        ("왼손 5개 손가락 (SG1 ~ SG5)", "• 버튼 입력: A0, A3, A4, A10, A11\n• 서보 PWM: D2, D3, D4, D5, D6\n• 펴짐 각도: 0°  /  쥠 각도: 150° (소지 180°)"),
        ("오른손 5개 손가락 (SD1 ~ SD5)", "• 버튼 입력: A5, A6, A7, A8, A9\n• 서보 PWM: D7, D8, D9, D10, D11\n• 펴짐 각도: 100°~120°  /  쥠 각도: 0°"),
        ("전원 및 안전 제어부", "• 전원 릴레이 제어: 디지털 12번 핀\n• 외부 전원: DC 5V 5A~10A 독립 공급\n• 동작 모드: MODE 1 (즉각 반응) / MODE 2 (토글)")
    ]

    for title_s, body_s in pin_specs:
        p_s = tf_r7.add_paragraph()
        p_s.text = f"▶ {title_s}"
        p_s.font.name = FONT_FAMILY
        p_s.font.size = Pt(16.5)
        p_s.font.bold = True
        p_s.font.color.rgb = COLOR_BLUE_PRIMARY
        p_s.space_after = Pt(3)

        p_sb = tf_r7.add_paragraph()
        p_sb.text = body_s
        p_sb.font.name = FONT_FAMILY
        p_sb.font.size = Pt(14.5)
        p_sb.font.color.rgb = COLOR_SECONDARY
        p_sb.space_after = Pt(14)

    # =========================================================
    # SLIDE 8: 핸드 제어 - 하드웨어 회로도 (Full Showcase)
    # =========================================================
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide8, COLOR_BG_LIGHT)
    add_header(slide8, "CIRCUIT SCHEMATIC", "10-Servo & 10-Button Controller 회로도 (Schematic)", "button_10_servos.ino 실측 핀맵 기반 아두이노 메가, 10개 버튼, 10개 서보, 릴레이 및 독립 전원 배선도")

    img_schematic = r"c:\Users\passp\Desktop\univercity\4-2\머신아트랩\hand_controller_pack\circuit_schematic_button_10_servos.png"
    add_fitted_image(slide8, img_schematic, Inches(0.8), Inches(1.85), Inches(11.733), Inches(5.2), "아두이노 메가 2560 - 10개 버튼(내부풀업) - 10개 서보 - 릴레이(D12) - 외장 5V 10A 전원 통합 회로도")

    # =========================================================
    # SLIDE 9: 종합 성과 요약 및 향후 제작 일정 (Big Fonts)
    # =========================================================
    slide9 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide9, COLOR_BG_LIGHT)
    add_header(slide9, "MILESTONES & NEXT STEPS", "핵심 성과 요약 및 향후 제작·조립 일정", "버튼 케이스, 볼트 도장, 로봇 핸드 제어기 제작 현황 및 향후 실행 계획")

    add_card(slide9, Inches(0.8), Inches(1.9), Inches(11.733), Inches(5.1), COLOR_WHITE, COLOR_CARD_BORDER)
    tb_m9 = slide9.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(11.133), Inches(4.7))
    tf_m9 = tb_m9.text_frame
    tf_m9.word_wrap = True
    tf_m9.margin_left = tf_m9.margin_right = tf_m9.margin_top = tf_m9.margin_bottom = 0

    p_mh = tf_m9.paragraphs[0]
    p_mh.text = "주요 개발 항목별 성과 및 향후 추진 계획"
    p_mh.font.name = FONT_FAMILY
    p_mh.font.size = Pt(21)
    p_mh.font.bold = True
    p_mh.font.color.rgb = COLOR_PRIMARY
    p_mh.space_after = Pt(16)

    milestones = [
        ("01. 10키 버튼 케이스", 
         "Fusion 360 모델링 완료, 판금 전개도(DXF) 및 렌더링 완료", 
         "3D 프린터 시제품 출력, 버튼 장착 및 조립 공차 검증", 
         "설계 완료 (100%)", COLOR_BLUE_PRIMARY),
        ("02. 사이보그 볼트 도장", 
         "D30/D40 v13 파라메트릭 완료, 키링 루프 일체화, 0.2mm 노즐 최적화", 
         "레진(SLA) 및 FDM 3D 프린팅 출력, 인주 날인 시인성 및 디테일 테스트", 
         "설계 완료 (100%)", COLOR_TEAL),
        ("03. 10채널 핸드 제어기", 
         "button_10_servos.ino 완성, 10버튼-10서보 1:1 매칭, 전원 회로도 수립", 
         "아두이노 메가 보드 배선 실장, 로봇 핸드 기구부 링크 결합 및 동작 시연", 
         "회로·코드 완료 (100%)", COLOR_AMBER)
    ]

    for track_num, done_text, next_text, stat_text, col in milestones:
        p_row = tf_m9.add_paragraph()
        p_row.text = f"■ {track_num} : "
        p_row.font.name = FONT_FAMILY
        p_row.font.size = Pt(18)
        p_row.font.bold = True
        p_row.font.color.rgb = col

        run_stat = p_row.add_run()
        run_stat.text = f"[{stat_text}]\n"
        run_stat.font.name = FONT_FAMILY
        run_stat.font.size = Pt(17)
        run_stat.font.bold = True
        run_stat.font.color.rgb = COLOR_EMERALD

        p_det = tf_m9.add_paragraph()
        p_det.text = f"   • 완료 성과: {done_text}\n   • 차주 계획: {next_text}"
        p_det.font.name = FONT_FAMILY
        p_det.font.size = Pt(15.5)
        p_det.font.color.rgb = COLOR_SECONDARY
        p_det.space_after = Pt(18)

    # =========================================================
    # SLIDE 10: 엔딩 (Conclusion / Q&A)
    # =========================================================
    slide10 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide10, RGBColor(15, 23, 42))

    t_end = slide10.shapes.add_textbox(Inches(1.5), Inches(2.2), Inches(10.333), Inches(3.2))
    tf10 = t_end.text_frame
    tf10.word_wrap = True

    p_e1 = tf10.paragraphs[0]
    p_e1.text = "MACHINE ART LAB  •  CORE PROJECT REPORT"
    p_e1.font.name = FONT_FAMILY
    p_e1.font.size = Pt(16)
    p_e1.font.bold = True
    p_e1.font.color.rgb = COLOR_CYAN
    p_e1.alignment = PP_ALIGN.CENTER
    p_e1.space_after = Pt(18)

    p_e2 = tf10.add_paragraph()
    p_e2.text = "감사합니다"
    p_e2.font.name = FONT_FAMILY
    p_e2.font.size = Pt(48)
    p_e2.font.bold = True
    p_e2.font.color.rgb = COLOR_WHITE
    p_e2.alignment = PP_ALIGN.CENTER
    p_e2.space_after = Pt(16)

    p_e3 = tf10.add_paragraph()
    p_e3.text = "버튼 케이스 · 볼트 도장 · 10채널 핸드 제어기 실물 조립 및 테스트를 추진하겠습니다."
    p_e3.font.name = FONT_FAMILY
    p_e3.font.size = Pt(20)
    p_e3.font.bold = True
    p_e3.font.color.rgb = RGBColor(226, 232, 240)
    p_e3.alignment = PP_ALIGN.CENTER
    p_e3.space_after = Pt(20)

    p_e4 = tf10.add_paragraph()
    p_e4.text = "질의응답 (Q&A)  |  발표자: 이재용"
    p_e4.font.name = FONT_FAMILY
    p_e4.font.size = Pt(16)
    p_e4.font.color.rgb = COLOR_MUTED
    p_e4.alignment = PP_ALIGN.CENTER

    # Save to both target locations
    output_path1 = r"c:\Users\passp\Desktop\univercity\4-2\머신아트랩\머신아트랩_프로젝트_성과보고.pptx"
    output_path2 = r"c:\Users\passp\Desktop\univercity\4-2\머신아트랩\머신아트랩_핵심성과보고.pptx"
    prs.save(output_path1)
    prs.save(output_path2)
    print(f"[SUCCESS] Presentation saved to {output_path1} and {output_path2}!")

if __name__ == "__main__":
    build_presentation()
