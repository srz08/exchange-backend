import datetime

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask import request
from flask import jsonify
from flask import abort
from flask_cors import CORS
import jwt
from flask_marshmallow import Marshmallow
from statistics import mean, median, mode, stdev, variance
import statistics

app = Flask(__name__)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:finally@localhost:3306/exchange'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:scout is on saturday@localhost:3306/exchange'
CORS(app)
db = SQLAlchemy(app)
SECRET_KEY = "b'|\xe7\xbfU3`\xc4\xec\xa7\xa9zf:}\xb5\xc7\xb9\x139^3@Dv'"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(30), unique=True)
    hashed_password = db.Column(db.String(128))

    def __init__(self, user_name, password):
        super(User, self).__init__(user_name=user_name)
        self.hashed_password = bcrypt.generate_password_hash(password)


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "user_name")
        model = User


user_schema = UserSchema()


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usd_amount = db.Column(db.Float)
    lbp_amount = db.Column(db.Float)
    usd_to_lbp = db.Column(db.Boolean)
    added_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return '<Transaction %r>' % self.id

    def __init__(self, usd_amount, lbp_amount, usd_to_lbp, user_id):
        super(Transaction, self).__init__(usd_amount=usd_amount,
                                          lbp_amount=lbp_amount, usd_to_lbp=usd_to_lbp,
                                          user_id=user_id,
                                          added_date=datetime.datetime.now())


class TransactionSchema(ma.Schema):
    class Meta:
        fields = ("id", "usd_amount", "lbp_amount", "usd_to_lbp", "added_date", "user_id")
        model = Transaction
        
transaction_schema = TransactionSchema()
transactions_schema = TransactionSchema(many=True)

        
class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usd_amount = db.Column(db.Float)
    lbp_amount = db.Column(db.Float)
    usd_to_lbp = db.Column(db.Boolean)
    completed=db.Column(db.Boolean)
    contact_info=db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return '<Transaction %r>' % self.id

    def __init__(self, usd_amount, lbp_amount, usd_to_lbp, user_id, completed, contact_info):
        super(Offer, self).__init__(usd_amount=usd_amount,
                                          lbp_amount=lbp_amount, usd_to_lbp=usd_to_lbp,
                                          user_id=user_id,
                                          completed=completed, contact_info=contact_info)


class OfferSchema(ma.Schema):
    class Meta:
        fields = ("id", "usd_amount", "lbp_amount", "usd_to_lbp", "completed","contact_info","user_id")
        model = Offer

offer_schema = OfferSchema()
offers_schema = OfferSchema(many=True)


def create_token(user_id):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=4),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm='HS256'
    )


def extract_auth_token(authenticated_request):
    auth_header = authenticated_request.headers.get('Authorization')
    if auth_header:
        return auth_header.split(" ")[1]
    else:
        return None


def decode_token(token):
    payload = jwt.decode(token, SECRET_KEY, 'HS256')
    return payload['sub']

@app.route('/offer', methods=['POST'])
def postOffer():
    usd_amount = request.json["usd_amount"]
    lbp_amount = request.json["lbp_amount"]
    usd_to_lbp = request.json["usd_to_lbp"]
    contact_info = request.json["contact_info"]

    token = extract_auth_token(request)

    if token == None:
        abort(403)
    try:
        user_id = decode_token(token)
    except:
        abort(403)

    offer=Offer(usd_amount=usd_amount, lbp_amount=lbp_amount, usd_to_lbp=usd_to_lbp, user_id=user_id, completed=False, contact_info=contact_info)
    db.session.add(offer)
    db.session.commit()
    return jsonify(offer_schema.dump(offer))

@app.route('/offer', methods=['GET'])
def getOffers():
    token = extract_auth_token(request)
    if token == None:
        abort(403)
    try:
        user_id = decode_token(token)
    except:
        abort(403)

    Offers = Offer.query.filter_by(completed=False)
    return jsonify(offers_schema.dump(Offers))
@app.route('/offeruser', methods=['GET'])
def getOffersuser():
    token = extract_auth_token(request)
    if token == None:
        abort(403)
    try:
        user_id = decode_token(token)
    except:
        abort(403)

    Offers = Offer.query.filter_by(completed=False).filter_by(user_id=user_id)
    return jsonify(offers_schema.dump(Offers))
@app.route('/offer', methods=['PATCH'])
def completeOffers():
    token = extract_auth_token(request)
    if token == None:
        
        abort(403)
    try:
        user_id = decode_token(token)
        offer=Offer.query.filter_by(id=request.json['id']).first();
        print(offer)
        if(offer==None):
            abort(404)
        if(str(offer.user_id)!=str(user_id)):
            abort(403)
        offer.completed=True
        db.session.commit()
    except:
        abort(403)
    Offers = Offer.query.all()
    return jsonify(offers_schema.dump(Offers))

@app.route('/transaction', methods=['POST'])
def postTransaction():
    usd_amount = request.json["usd_amount"]
    lbp_amount = request.json["lbp_amount"]
    usd_to_lbp = request.json["usd_to_lbp"]
    token = extract_auth_token(request)

    if token == None:
        transaction=Transaction(usd_amount=usd_amount, lbp_amount=lbp_amount, usd_to_lbp=usd_to_lbp, user_id=None)
        db.session.add(transaction)
        db.session.commit()
        return jsonify(transaction_schema.dump(transaction))
    try:
        user_id = decode_token(token)
    except:
        abort(403)
    
    transaction=Transaction(usd_amount=usd_amount, lbp_amount=lbp_amount, usd_to_lbp=usd_to_lbp, user_id=user_id)
    if(transaction.usd_amount==0 or transaction.lbp_amount==0):
        abort(400)
    db.session.add(transaction)
    db.session.commit()
    return jsonify(transaction_schema.dump(transaction))


@app.route('/transaction', methods=['GET'])
def getUserTransaction():
    token = extract_auth_token(request)

    if token == None:
        abort(403)
    try:
        user_id = decode_token(token)
    except:
        abort(403)

    userTransactions = Transaction.query.filter_by(user_id=user_id).all()
    return jsonify(transactions_schema.dump(userTransactions))


@app.route('/user', methods=['POST'])
def postUser():
    user_name = request.json["user_name"]
    password = request.json["password"]
    obji=User(user_name=user_name, password=password)
    db.session.add(obji)
    db.session.commit()
    return jsonify(user_schema.dump(obji))


@app.route('/authentication', methods=['POST'])
def authentication():
    if "user_name" not in request.json or "password" not in request.json:
        abort(400)

    user_name = request.json["user_name"]
    password = request.json["password"]
    user = User.query.filter_by(user_name=user_name).first()

    if user is None:
        abort(403)

    if not bcrypt.check_password_hash(user.hashed_password, password):
        abort(403)

    token = create_token(user.id)
    jsonResponse = {"token": token}
    return jsonify(jsonResponse)


@app.route('/exchangeRate', methods=['GET'])
def getExchangeRate():
    START_DATE = datetime.datetime.now() - datetime.timedelta(days=3)
    END_DATE = datetime.datetime.now()

    usd_to_lbp = Transaction.query.filter(Transaction.added_date.between(START_DATE, END_DATE),
                                          Transaction.usd_to_lbp == True).all()
    lbp_to_usd = Transaction.query.filter(Transaction.added_date.between(START_DATE, END_DATE),
                                          Transaction.usd_to_lbp == False).all()
    sellRate = 0
    buyRate = 0
    for t in usd_to_lbp:
        sellRate += t.lbp_amount / t.usd_amount

    for t in lbp_to_usd:
        buyRate += t.lbp_amount / t.usd_amount

    if len(usd_to_lbp) == 0:
        sellRate = "No rate available"
    else:
        sellRate = sellRate / len(usd_to_lbp)

    if len(lbp_to_usd) == 0:
        buyRate = "No rate available"
    else:
        buyRate = buyRate / len(lbp_to_usd)

    return jsonify(usd_to_lbp=sellRate, lbp_to_usd=buyRate)

@app.route('/valueChange', methods=['GET'])
def query1():
    date1 = datetime.datetime.now() - datetime.timedelta(days=1)
    date2 = datetime.datetime.now()
    beforeToday = Transaction.query.filter(Transaction.added_date < date1).all()
    today = Transaction.query.filter(Transaction.added_date < date2).all()
    before = 0
    after = 0
    
    for t in beforeToday:
        before += t.lbp_amount / t.usd_amount
        
    for t in today:
        after += t.lbp_amount / t.usd_amount
    
    if(len(beforeToday)==0):
        before = "None"
    else:
        before = before/len(beforeToday)
        
    if(len(today)==0):
        after  = "None"
    else:
        after = after/len(today)
    print(before, after)
    if(after=="None" or before=="None"):
        result = "Need more days"
    else:
        result = after - before
        
    return jsonify(result=result)


@app.route('/percChange', methods=['GET'])
def query2():
    date1 = datetime.datetime.now() - datetime.timedelta(days=1)
    date2 = datetime.datetime.now()
    beforeToday = Transaction.query.filter(Transaction.added_date < date1).all()
    today = Transaction.query.filter(Transaction.added_date < date2).all()
    before = 0
    after = 0
    
    for t in beforeToday:
        before += t.lbp_amount / t.usd_amount
        
    for t in today:
        after += t.lbp_amount / t.usd_amount
    
    if(len(beforeToday)==0):
        before = "None"
    else:
        before = before/len(beforeToday)
        
    if(len(today)==0):
        after  = "None"
    else:
        after = after/len(today)
        
    if(after=="None" or before=="None"):
        result = "_"
    else:
        result = after - before
    
    if(result != "Need more days"):
        result = result / before
        result *= 100
        
    return jsonify(result=result)

@app.route('/usd_stats', methods=["GET"])
def query4():
    usd_to_lbp = Transaction.query.filter(Transaction.usd_to_lbp == True).all()
    values = []
    for t in usd_to_lbp:
        values.append(t.lbp_amount/t.usd_amount)
    if(len(values)==0):
        return jsonify(results="None")
    results = {}
    results["max"] = max(values)
    results['min'] = min(values)
    results['mean'] = statistics.mean(values)
    #results['mode'] = mode(values)
    results['median'] = median(values)
    results['stdev'] = 0
    results['variance'] = 0
    if(len(values)>=2):
        results['stdev'] = stdev(values)
        results['variance'] = variance(values)
    return jsonify(max=results["max"], min=results['min'],mean=results['mean'],median=results['median'], stdev=results['stdev'], variance=results['variance'])

@app.route('/lbp_stats', methods=["GET"])
def query5():
    usd_to_lbp = Transaction.query.filter(Transaction.usd_to_lbp == False).all()
    values = []
    for t in usd_to_lbp:
        values.append(t.lbp_amount/t.usd_amount)
    if(len(values)==0):
        return jsonify(results="None")
    results = {}
    results["max"] = max(values)
    results['min'] = min(values)
    results['mean'] = statistics.mean(values)
    #results['mode'] = mode(values)
    results['median'] = median(values)
    results['stdev'] = 0
    results['variance'] = 0
    if(len(values)>=2):
        results['stdev'] = stdev(values)
        results['variance'] = variance(values)
    return jsonify(max=results["max"], min=results['min'],mean=results['mean'],median=results['median'], stdev=results['stdev'], variance=results['variance'])


@app.route('/graphValuesUsd', methods=["GET"])
def query6():
    dt = datetime.datetime.now()-datetime.timedelta(days=7)
    dt.replace(minute=0, hour=0, second=0, microsecond=0)
    increment = datetime.timedelta(days=1)
    counter = 0
    x_axis=[]
    y_axis=[]
    while(counter<8):
        print(dt, dt-increment)
        usd_to_lbp = Transaction.query.filter(Transaction.added_date.between(dt-increment, dt), Transaction.usd_to_lbp == True).all()
        values = []
        for t in usd_to_lbp:
            values.append(t.lbp_amount/t.usd_amount)
        if(len(values)==0):
            element=0
        else:
            element = mean(values)
        x_axis.append(dt)
        y_axis.append(element)
        counter += 1
        dt+=increment
    return(jsonify(x=x_axis, y=y_axis))
    
@app.route('/graphValuesLbp', methods=["GET"])
def query7():
    dt = datetime.datetime.now()-datetime.timedelta(days=7)
    dt.replace(minute=0, hour=0, second=0, microsecond=0)
    increment = datetime.timedelta(days=1)
    counter = 0
    x_axis=[]
    y_axis=[]
    while(counter<8):
        print(dt, dt-increment)
        usd_to_lbp = Transaction.query.filter(Transaction.added_date.between(dt-increment, dt), Transaction.usd_to_lbp == False).all()
        values = []
        for t in usd_to_lbp:
            values.append(t.lbp_amount/t.usd_amount)
        if(len(values)==0):
            element=0
        else:
            element = mean(values)
        x_axis.append(dt)
        y_axis.append(element)
        counter += 1
        dt+=increment
    return(jsonify(x=x_axis, y=y_axis))
        


        

    
    
        
    
        
        
    
    
