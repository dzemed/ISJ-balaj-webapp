from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import hashlib
import os

app = Flask(__name__, instance_relative_config=True)

db_path = os.path.join(app.instance_path, "kurzy.db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}".replace("\\","/")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


def pripoj_db():
    conn = sqlite3.connect("kurzy.db")
    return conn


@app.route('/')  
def index():
    # Úvodná homepage s dvoma tlačidami ako ODKAZMI na svoje stránky - volanie API nedpointu
    return '''
        <h1>Výber z databázy</h1>
        <a href="/kurzy"><button>Zobraz všetky kurzy</button></a>
        <a href="/treneri"><button>Zobraz všetkých trénerov</button></a>
        <a href="/miesta"><button>Zobraz miesta</button></a>
        <a href="/kapacity"><button>Zobraz kapacitu</button></a>
        <a href="/registracia"><button>Registruj Trenéra</button></a>
        <a href="/prida_kurz"><button>Pridanie kurzu</button></a>
        <hr>
    '''

class Kurz(db.Model):
    __tablename__ = "Kurzy"
    ID_kurzu              = db.Column(db.Integer, primary_key=True)
    Nazov_kurzu           = db.Column(db.String, nullable=False)
    Typ_sportu            = db.Column(db.String)
    Max_pocet_ucastnikov  = db.Column(db.Integer)
    ID_trenera            = db.Column(db.Integer)

    def __repr__(self):
        return f"<Kurz {self.Nazov_kurzu}>"


# PODSTRÁNKA NA ZOBRAZENIE KURZOV
@app.route('/kurzy')  # API endpoint
def zobraz_kurzy():
    """
    conn = pripoj_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Kurzy")
    kurzy = cursor.fetchall()
    conn.close()
    return render_template("kurzy.html", kurzy=kurzy)
    """
    
    kurzy = Kurz.query.all()
    return render_template("kurzy.html",kurzy=kurzy)

class Trener(db.Model):
    __tablename__ = "Treneri"
    ID_trenera     = db.Column(db.Integer, primary_key=True)
    Meno           = db.Column(db.String, nullable=False)
    Priezvisko    = db.Column(db.String)
    Specializacia = db.Column(db.String)

    def __repr__(self):
        return f"<Trener {self.Meno}>"

@app.route('/treneri')  # API endpoint
def zobraz_trenerov():
    treneri = Trener.query.all()
    return render_template("treneri.html",treneri=treneri)
    

class Miesto(db.Model):
    __tablename__ = "Miesta"
    ID_miesta     = db.Column(db.Integer, primary_key=True)
    Nazov_miesta  = db.Column(db.String)
    Kapacita  = db.Column(db.String, nullable=False)


@app.route('/miesta')  # API endpoint
def zobraz_miesta():

    miesta = Miesto.query.all()
    return render_template("miesta.html",miesta=miesta)


@app.route('/kapacity')  # API endpoint
def vypis_kapacity():
    kurzy = Kurz.query.with_entities(Kurz.Nazov_kurzu, Kurz.Max_pocet_ucastnikov).filter(Kurz.Nazov_kurzu.like('p%')).all()
    return render_template("kapacita.html",kapacity=kurzy)




@app.route('/registracia', methods=['GET'])
def registracia_form():
    return render_template("registracia.html")


# API ENDPOINT NA SPRACOVANIE REGISTRÁCIE. Mapuje sa na mená elementov z formulára z predošlého requestu (pomocou request.form[...])
# Pozor - metóda je POST
@app.route('/registracia', methods=['POST'])
def registracia_trenera():

    meno = request.form['meno']
    priezvisko = request.form['priezvisko']
    specializacia = request.form['specializacia']
    telc = request.form['telefon']
    heslo = request.form['heslo']
    hashed = hashlib.sha256(heslo.encode()).hexdigest()


    # Zápis do databázy
    conn = pripoj_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Treneri (Meno, Priezvisko, Specializacia, Telefon, Heslo) VALUES (?, ?, ?, ?, ?)", 
                   (meno, priezvisko, specializacia, telc, hashed))
    conn.commit()
    conn.close()

    # Hlásenie o úspešnej registrácii
    return render_template("prid_trener.html")

@app.route('/prida_kurz', methods=['GET'])
def pridaj_form():
    return render_template("pridanie.html")


def sifrovanie(text):
    vety=""
    A=5
    B=8
    for X in text:
        X = X.upper()

        cislopismena = ord(X) - ord('A')

        sifrovanie = (A*cislopismena+B)%26

        pismeno = chr(sifrovanie+ ord('A'))
        vety+=pismeno

    return vety




@app.route('/prida_kurz', methods=['POST'])
def pridaj_kurz():


    nazov_kurzu = request.form['nazov_kurzu']
    typ_sportu = request.form['typ_sportu']
    max_pocet_ucastnikov = request.form['max_pocet_ucastnikov']
    id_trenera = request.form['id_trenera']
    sifra_nazov = sifrovanie(nazov_kurzu)
    sifra_typ = sifrovanie(typ_sportu)

    

    conn = pripoj_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Kurzy ( Nazov_kurzu, Typ_sportu, Max_pocet_ucastnikov, ID_trenera) VALUES ( ?, ?, ?, ?)", 
                   ( sifra_nazov, sifra_typ, max_pocet_ucastnikov, id_trenera))
    conn.commit()
    conn.close()


    return render_template("prid_kurz.html")



if __name__ == '__main__':
    app.run(debug=True)

# Aplikáciu spustíte, keď do konzoly napíšete "python app.py"