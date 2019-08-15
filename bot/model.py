from bot import db 


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_viber_id=db.Column(db.String(150), unique=True)
    quer = db.relationship('Query', backref='user', uselist=False)
    zakazi = db.relationship('Zakaz', backref='user', uselist=True)
    novaposhta = db.relationship('NP', backref='user', uselist=False)
    def __repr__(self):
        return f"User('{self.user_viber_id}')"

class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    query_number = db.Column(db.String(10))
    zakaz_num = db.Column(db.Integer)
    def __repr__(self):
        return f"Lol"

class Zakaz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.Text, nullable=True)
    type = db.Column(db.Text, nullable=True)
    name = db.Column(db.Text, nullable=True)
    size = db.Column(db.Text, nullable=True)
    color = db.Column(db.Text, nullable = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class NP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.Text, nullable = True)
    adress = db.Column(db.Text, nullable = True)
    phone_number = db.Column(db.Text, nullable = True)
    recip_name = db.Column(db.Text , nullable= True)
    price = db.Column(db.Text, nullable = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.Text, nullable= True)
    oplata_card = db.Column(db.Text, nullable= True)
    oplata_nalojeniy = db.Column(db.Text, nullable = True)
    doplata = db.Column(db.Text, nullable = True)
    back = db.Column(db.Text, nullable = True)
    oplata_dostavki = db.Column(db.Text, nullable = True)


