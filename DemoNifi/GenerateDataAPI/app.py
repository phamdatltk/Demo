import random
from flask import Flask
from flask_restful import Api, Resource
from datetime import datetime


app = Flask(__name__)
api = Api(app)


class HelloWorld(Resource):
    def get(self):
        time = str(datetime.now())
        listCity = ["HaNoi", "SaiGon", "Can Tho", "Hai Phong", "Da Nang", "Thanh Hoa", "Binh Duong", "Quang Binh",
                    "Quang Tri"]
        city = random.choice(listCity)
        id = random.randint(10000, 99999)
        listStatus = [True, False]
        status = random.choice(listStatus)

        data = {
            "city": city,
            "id": id,
            "time":  time,
            "status": status
        }

        return data

api.add_resource(HelloWorld, "/")

if __name__ == "__main__":
    app.run(debug=True)