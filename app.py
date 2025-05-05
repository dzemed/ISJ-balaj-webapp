from flask import Flask, request, render_template
import sqlite3
import hashlib

app = Flask(__name__)

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




# PODSTRÁNKA NA ZOBRAZENIE KURZOV
@app.route('/kurzy')  # API endpoint
def zobraz_kurzy():
    conn = pripoj_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Kurzy")
    kurzy = cursor.fetchall()
    conn.close()
    return render_template("kurzy.html", kurzy=kurzy)




@app.route('/treneri')  # API endpoint
def zobraz_trenerov():
    conn = pripoj_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT T.ID_trenera, T.Meno || ' ' || T.Priezvisko as Trener, Nazov_kurzu
        FROM Treneri T LEFT JOIN Kurzy K ON T.ID_trenera = K.ID_trenera
    """)
    treneri = cursor.fetchall()
    conn.close()

    return render_template("treneri.html", treneri=treneri)
    
    




@app.route('/miesta')  # API endpoint
def zobraz_miesta():
    conn = pripoj_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Nazov_miesta FROM Miesta
    """)
    miesta = cursor.fetchall()

    conn.close()
    return render_template("miesta.html", miesta=miesta)




@app.route('/kapacity')  # API endpoint
def vypis_kapacity():
    conn = pripoj_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sum(Max_pocet_ucastnikov) FROM Kurzy where Nazov_kurzu LIKE 'p%'
    """)
    kapacity = cursor.fetchall()
    conn.close()
    return render_template("kapacita.html", kapacity=kapacity)




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
    return '''
        <h2>Tréner bol úspešne zaregistrovaný!</h2>
        <hr>
        <a href="/">Späť</a>
    '''


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


    return '''
        <h2>Kurz bol úspešne pridaný!</h2>
        <hr>
        <a href="/">Späť</a>
    '''



if __name__ == '__main__':
    app.run(debug=True)

# Aplikáciu spustíte, keď do konzoly napíšete "python app.py"