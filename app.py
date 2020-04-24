import sqlite3
import os
from flask import Flask, render_template, redirect, session
from flask_wtf import FlaskForm
from wtforms import TextAreaField,validators,RadioField,SelectField
from wtforms.validators import DataRequired,Length
import datetime



app = Flask(__name__)
app.debug = True
app.secret_key = 'kascf ascfhasiocfhasiocfhasiocfh'

aktualni_adresar = os.path.abspath(os.path.dirname(__file__))
databaze = (os.path.join(aktualni_adresar, 'poznamky.db'))


class PoznamkaForm(FlaskForm):
    poznamka = TextAreaField("Poznamka",
                      validators=[DataRequired()])
    dulezitost = SelectField("Dulezitost",
                            choices=[("1", "Málo "), ("2", 'Středně'), ("3", 'Důležitá')] )

@app.route('/poznamka/vlozit', methods=['GET', 'POST'])
def vloz_poznamku():
    """Zobrazí formulář pro vložení poznámky."""
    delka=250
    form = PoznamkaForm()
    text = form.poznamka.data
    dulezitost = form.dulezitost.data

    if form.validate_on_submit():
        if len(text) > delka:
         return render_template('poznamky.html', form=form, error="Překročil jsi limit 250 znaků, tvých znaků: " + str(len(text)))
        else:
         conn = sqlite3.connect('poznamky.db')
         c = conn.cursor()
         x = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
         c.execute("insert into poznamky(pozn,datum,dulezitost) values (?,?,?)", (text,x,dulezitost,))
         conn.commit()
         conn.close()
    return render_template('poznamky.html', form=form)


@app.route('/', methods=['GET', 'POST'])
def zobraz_poznamky():
    """Zobrazí uložené poznámky."""
    conn = sqlite3.connect('poznamky.db')
    c = conn.cursor()
    c.execute('SELECT rowid,* FROM poznamky ORDER BY datum desc')
    poznamky2=c.fetchall()
    poznamky=[]
    datum=[]
    for row in poznamky2:
        poznamky.append(row[1])  
        datum.append(row[2])
    conn.close()
    return render_template('index.html', poznamky=poznamky2, datum=datum)

@app.route('/smaz/<int:poznamka_id>')
def smaz_poznamku(poznamka_id):
    """Smaže vybranou poznámku"""
    conn = sqlite3.connect('poznamky.db')
    c = conn.cursor()
    c.execute("DELETE FROM poznamky WHERE rowid=?", (poznamka_id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/uprav/<int:poznamka_id>', methods=['GET', 'POST'])
def uprav_poznamku(poznamka_id):
    """Upraví poznámku."""
    conn = sqlite3.connect('poznamky.db')
    c = conn.cursor()
    c.execute("SELECT pozn, dulezitost FROM poznamky WHERE rowid=?", (poznamka_id,))
    poznamka_tuple = c.fetchone()
    conn.close()
    form = PoznamkaForm(poznamka=poznamka_tuple[0],dulezitost=poznamka_tuple[1])
    poznamka_text = form.poznamka.data
    dulezitost = form.dulezitost.data
    if form.validate_on_submit():
        conn = sqlite3.connect('poznamky.db')
        c = conn.cursor()
        c.execute("UPDATE poznamky SET pozn=?,dulezitost=? WHERE rowid=?", (poznamka_text,dulezitost,poznamka_id,))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('poznamky.html', form=form)






if __name__ == '__main__':
    app.run()