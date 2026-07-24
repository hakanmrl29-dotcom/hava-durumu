from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import urllib.request
import json

# uygulamayı başlat
app = Flask(__name__)

# veritabanı ayarı - şehirleri kaydetmek için
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sehirler.db"
db = SQLAlchemy(app)

# şehir modeli
class Sehir(db.Model):
    id    = db.Column(db.Integer, primary_key=True)
    isim  = db.Column(db.String(100), nullable=False)

# hava durumu verisi çekme fonksiyonu
def hava_getir(sehir):
    try:
        url   = "https://wttr.in/" + sehir + "?format=j1"
        istek = urllib.request.urlopen(url, timeout=5)
        veri  = json.loads(istek.read().decode("utf-8"))
        return {
            "sehir"      : sehir,
            "sicaklik"   : veri["current_condition"][0]["temp_C"],
            "hissedilen" : veri["current_condition"][0]["FeelsLikeC"],
            "nem"        : veri["current_condition"][0]["humidity"],
            "ruzgar"     : veri["current_condition"][0]["windspeedKmph"],
            "durum"      : veri["current_condition"][0]["weatherDesc"][0]["value"],
        }
    except:
        # şehir bulunamazsa None döndür
        return None

# ana sayfa
@app.route("/")
def ana_sayfa():
    # veritabanındaki tüm şehirleri al
    sehirler = Sehir.query.all()

    # her şehir için hava durumu çek
    hava_listesi = []
    for s in sehirler:
        hava = hava_getir(s.isim)
        if hava:
            hava_listesi.append(hava)

    return render_template("index.html", hava_listesi=hava_listesi)

# şehir ekle
@app.route("/ekle", methods=["POST"])
def ekle():
    sehir_adi = request.form["sehir"].strip()
    if sehir_adi:
        yeni_sehir = Sehir(isim=sehir_adi)
        db.session.add(yeni_sehir)
        db.session.commit()
    return redirect(url_for("ana_sayfa"))

# şehir sil
@app.route("/sil/<int:id>", methods=["POST"])
def sil(id):
    silinecek = db.session.get(Sehir, id)
    db.session.delete(silinecek)
    db.session.commit()
    return redirect(url_for("ana_sayfa"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)