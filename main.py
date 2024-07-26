from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, func

app = Flask(__name__)


# CREATE DB
class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'

db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        dictionary = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return dictionary


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# Get Random Cafe
@app.route("/random", methods=["GET"])
def get_random_cafe():
    random_cafe = db.session.query(Cafe).order_by(func.random()).first()
    return random_cafe.to_dict()


# Get All Cafes
@app.route("/all", methods=["GET"])
def all_cafes():
    cafes = db.session.execute(db.select(Cafe)).scalars().all()
    cafe_list = [cafe.to_dict() for cafe in cafes]
    return jsonify(cafe_list)


# Search Cafe By Location
@app.route("/search", methods=["GET"])
def search_cafe_by_loc():
    query_location = request.args.get('loc')
    cafes = db.session.execute(db.select(Cafe).where(Cafe.location == query_location)).scalars().all()
    if not cafes:
        return jsonify({"error": "Sorry, we don't have a cafe at that location."}), 404
    else:
        cafe_list = [cafe.to_dict() for cafe in cafes]
        return jsonify(cafe_list)




# Post New Cafe
@app.route("/add", methods=["POST"])
def add_new_cafe():
    cafe_name = request.form.get("name")
    map_url = request.form.get("map_url")
    img_url = request.form.get("img_url")
    location = request.form.get("location")
    seats = request.form.get("seats")
    toilet = request.form.get("has_toilet")
    wi_fi = request.form.get("has_wifi")
    sockets = request.form.get("has_sockets")
    calls = request.form.get("can_take_calls")
    coffee = request.form.get("coffee_price")
    new_cafe = Cafe(name=cafe_name,
                    map_url = map_url,
                    img_url=img_url,
                    location = location,
                    seats = seats,
                    has_toilet= bool(toilet),
                    has_wifi=bool(wi_fi),
                    has_sockets=bool(sockets),
                    can_take_calls=bool(calls),
                    coffee_price=coffee)
    db.session.add(new_cafe)
    db.session.commit()

    return {"response":
                {"success": "Successfuly Added New Cafe"}
            }

# Udate Coffee Price
@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def update_coffee_price(cafe_id):
    cafe = db.get_or_404(Cafe, cafe_id)
    if cafe:
        new_price = request.args.get("new_price")
        if new_price:
            cafe.coffee_price = new_price
            db.session.commit()
            return {"success": "Successfuly updated the price"}, 200
        else:
            return {"error": "No new price provided"}, 400
    else:
        return {"error":
                {"Not Found": "Sorry a cafe with that id was not found in the database"},
            }, 400


API_KEY = "TopSecretAPIKey"
# Delete Cafe If Closed
@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def delete_closed_cafe(cafe_id):
    api_key = request.args.get("api_key")
    if api_key != API_KEY:
        return jsonify({"error": "Invalid API key"}), 403
    cafe = db.get_or_404(Cafe, cafe_id)
    if cafe:
        db.session.delete(cafe)
        db.session.commit()
        return jsonify({'message': f'Cafe {cafe_id} deleted successfully'}), 200
    else:
        return {"error":
                    {"Not Found": "Sorry a cafe with that id was not found in the database"},
                }, 400


if __name__ == '__main__':
    app.run(debug=True, port=2000)
