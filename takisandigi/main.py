import os
import io

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

app = FastAPI()

# 📁 Proje ve klasör yolları
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_PATH = os.path.join(BASE_DIR, "docs")
FONTS_PATH = os.path.join(BASE_DIR, "fonts")
STATIC_PATH = os.path.join(BASE_DIR, "static")  # ✅ logo / banner buradan gelecek
STATIC_IMAGES_PATH = os.path.join(STATIC_PATH, "images")

# Gerekli klasörleri oluştur
os.makedirs(DOCS_PATH, exist_ok=True)
os.makedirs(FONTS_PATH, exist_ok=True)
os.makedirs(STATIC_PATH, exist_ok=True)
os.makedirs(STATIC_IMAGES_PATH, exist_ok=True)

print("BASE_DIR       =", BASE_DIR)
print("DOCS_PATH      =", DOCS_PATH)
print("FONTS_PATH     =", FONTS_PATH)
print("STATIC_PATH    =", STATIC_PATH)
print("IMAGES_PATH    =", STATIC_IMAGES_PATH)

try:
    print("DOCS İÇERİK:", os.listdir(DOCS_PATH))
    print(
        "STATİK PDF VAR MI?:",
        os.path.exists(os.path.join(DOCS_PATH, "taki_sandigi_sozlesme.pdf")),
    )
    print("IMAGES İÇERİK:", os.listdir(STATIC_IMAGES_PATH))
except Exception as e:
    print("DEBUG HATASI:", e)


# 🔤 Türkçe karakterler için font kaydı
def register_fonts():
    try:
        font_path = os.path.join(FONTS_PATH, "DejaVuSans.ttf")
        bold_path = os.path.join(FONTS_PATH, "DejaVuSans-Bold.ttf")

        pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
        pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", bold_path))

        default_font = "DejaVuSans"
        default_bold = "DejaVuSans-Bold"
        print("Fontlar yüklendi:", font_path, bold_path)
    except Exception as e:
        print("Font yüklenemedi, Helvetica kullanılacak:", e)
        default_font = "Helvetica"
        default_bold = "Helvetica-Bold"

    return default_font, default_bold


def build_contract_pdf(
    buffer,
    musteri_adi,
    tc_no,
    adres,
    telefon,
    email,
    urun_adi,
    toplam_tutar,
    pesinat,
    taksit_sayisi,
):
    """
    Verilen bilgilere göre PDF'e sözleşme metni yazar.
    """
    font, font_bold = register_fonts()
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        spaceAfter=18,
        fontName=font_bold,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading3"],
        spaceBefore=14,
        spaceAfter=8,
        fontName=font_bold,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        alignment=TA_JUSTIFY,
        leading=14,
        fontName=font,
    )
    small_style = ParagraphStyle(
        "Small",
        parent=styles["BodyText"],
        fontSize=9,
        fontName=font,
    )

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=36,
        bottomMargin=36,
    )

    story = []

    # Başlık
    story.append(
        Paragraph("TAKI SANDIĞI KATILIM VE TESLİM SÖZLEŞMESİ", title_style)
    )
    story.append(Spacer(1, 10))

    # Taraf Bilgileri
    story.append(Paragraph("TARAF BİLGİLERİ", section_style))

    satici_text = """
    <b>SATICI / ORGANİZATÖR:</b><br/>
    ART TOWER İNŞAAT VE SANAYİ A.Ş. — VD: Kartal — VN: 6211022407 — Tel: 0533 599 73 00<br/>
    Faaliyet Şubesi: Adelya Kuyumculuk (Yaman Evler Mah. Alemdağ Cad. No:155/A – Ümraniye/İstanbul)<br/>
    Şube: Yaman Evler Mah. Alemdağ Cad. No:143/A – Ümraniye/İstanbul
    """
    story.append(Paragraph(satici_text, body_style))
    story.append(Spacer(1, 6))

    musteri_text = f"""
    <b>MÜŞTERİ / KATILIMCI:</b><br/>
    Adı Soyadı: {musteri_adi}<br/>
    T.C./Vergi No: {tc_no}<br/>
    Adres: {adres}<br/>
    Telefon: {telefon}  E-posta: {email}
    """
    story.append(Paragraph(musteri_text, body_style))

    # Ürün Özeti
    story.append(Spacer(1, 10))
    story.append(Paragraph("SÖZLEŞME ÖZETİ", section_style))

    ozet_text = f"""
    Ürün: {urun_adi}<br/>
    Toplam Tutar: {toplam_tutar} TL<br/>
    Peşinat: {pesinat} TL<br/>
    Taksit Sayısı: {taksit_sayisi} Ay
    """
    story.append(Paragraph(ozet_text, body_style))

    # Maddeler (kısaltılmış versiyon)
    maddeler = [
        (
            "MADDE 1 – SÖZLEŞMENİN KONUSU",
            "Bu sözleşme; müşterinin seçtiği altın/takı ürününü, katılım tarihinde sabitlenen altın kuru "
            "esas alınarak %25 peşinat ve kalan kısmın taksitli ödenmesi suretiyle teslimine ilişkin "
            "hak ve yükümlülükleri düzenler.",
        ),
        (
            "MADDE 2 – SİSTEMİN İŞLEYİŞİ",
            "Katılım tarihinde altın fiyatı sabitlenir. Peşinat alınır; bakiye belirlenen vade boyunca eşit "
            "taksitlerle tahsil edilir. Ödemeler banka/POS yoluyla yapılır ve dekontlar müşterice saklanır.",
        ),
        (
            "MADDE 3 – SABİT FİYAT ESASI",
            "Sabitlenen fiyat sözleşme süresince geçerlidir. Fiyat artarsa fark talep edilmez; fiyat düşmesi "
            "halinde satıcının fiyatı yeniden belirleme zorunluluğu yoktur.",
        ),
        (
            "MADDE 4 – KATILIM BEDELİ",
            "Organizasyon ve operasyon giderleri karşılığı toplam bedel üzerinden %8 katılım bedeli alınır. "
            "Katılım bedeli hizmet niteliğinde olup iade edilmez.",
        ),
        (
            "MADDE 5 – TESLİM",
            "Taksitlerin tamamlanması ile ürün hazırlanarak müşteriye fatura düzenlenmek suretiyle teslim "
            "edilir. Mücbir sebepler nedeniyle oluşabilecek makul gecikmeler satıcının sorumluluğunda değildir.",
        ),
        (
            "MADDE 6 – GECİKME",
            "Taksit ödemelerinde gecikme yaşanması halinde geciken tutar, gecikmenin gerçekleştiği tarihteki "
            "güncel altın kuru üzerinden yeniden hesaplanır ve oluşan fark müşteri tarafından ödenir.",
        ),
        (
            "MADDE 7 – TEMERRÜT VE FESİH",
            "Müşterinin ardışık veya aralıklı olarak 2 ay ödeme yapmaması halinde temerrüt oluşur. Satıcı "
            "sözleşmeyi haklı nedenle feshedebilir. Fesih halinde katılım bedeli iade edilmez; yapılan "
            "ödemelerden masraflar ve kur farkları düşülerek kalan tutar müşteriye iade edilir.",
        ),
        (
            "MADDE 8 – KİŞİSEL VERİLER",
            "Taraflar KVKK hükümlerine uygun davranır. Veriler yalnızca sözleşmenin ifası amacıyla işlenir ve "
            "zorunlu haller dışında üçüncü kişilerle paylaşılmaz.",
        ),
        (
            "MADDE 9 – YETKİ",
            "Uyuşmazlıklarda satıcının merkezinin bulunduğu yer tüketici hakem heyetleri ve tüketici mahkemeleri yetkilidir.",
        ),
    ]

    for baslik, metin in maddeler:
        story.append(Spacer(1, 6))
        story.append(Paragraph(baslik, section_style))
        story.append(Paragraph(metin, body_style))

    story.append(Spacer(1, 14))

    # İmza alanları
    table = Table(
        [
            ["SATICI / ORGANİZATÖR", "MÜŞTERİ / KATILIMCI"],
            ["ART TOWER İNŞAAT VE SANAYİ A.Ş.\n(İmza – Kaşe)", f"{musteri_adi}\n(İmza)"],
        ],
        colWidths=[260, 260],
    )
    table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, -1), font),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            "Bu sözleşme iki nüsha olarak düzenlenmiş olup bir nüshası müşteriye teslim edilmiştir.",
            small_style,
        )
    )

    doc.build(story)


# 📂 Statik klasörleri yayınla
app.mount("/docs", StaticFiles(directory=DOCS_PATH), name="docs")
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")  # ✅ logo/banner


@app.get("/", response_class=HTMLResponse)
def serve_index():
    """Ana sayfa: index.html dosyasını döndürür."""
    index_file = os.path.join(BASE_DIR, "index.html")
    with open(index_file, "r", encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(content=html)


@app.get("/sozlesme-pdf")
def download_contract():
    """Statik sözleşme PDF'ini direkt indirme linki."""
    pdf_file = os.path.join(DOCS_PATH, "taki_sandigi_sozlesme.pdf")
    return FileResponse(
        pdf_file,
        media_type="application/pdf",
        filename="taki_sandigi_sozlesme.pdf",
    )


@app.get("/generate-contract")
def generate_contract(
    musteri_adi: str,
    tc_no: str,
    adres: str,
    telefon: str,
    email: str = "",
    urun_adi: str = "Altın / Takı Ürünü",
    toplam_tutar: float = 0.0,
    pesinat: float = 0.0,
    taksit_sayisi: int = 6,
):
    """
    URL parametreleriyle gelen bilgilere göre dinamik sözleşme PDF'i üretir.
    Örn:
    /generate-contract?musteri_adi=Ali+Yılmaz&tc_no=123...&adres=...
    """
    buffer = io.BytesIO()
    build_contract_pdf(
        buffer,
        musteri_adi=musteri_adi,
        tc_no=tc_no,
        adres=adres,
        telefon=telefon,
        email=email,
        urun_adi=urun_adi,
        toplam_tutar=toplam_tutar,
        pesinat=pesinat,
        taksit_sayisi=taksit_sayisi,
    )
    buffer.seek(0)

    headers = {
        "Content-Disposition": 'attachment; filename="taki_sandigi_sozlesme_dinamik.pdf"'
    }
    return StreamingResponse(
        buffer, media_type="application/pdf", headers=headers
    )
