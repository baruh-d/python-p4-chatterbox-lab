from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at.asc()).all()
        serialized_messages = [message.to_dict() for message in messages]
        return jsonify(serialized_messages), 200
    
    elif request.method == 'POST':
        data = request.get_json()
        
        if not data.get('body') or not data.get('username'):
            return jsonify({
                "message": "Please provide a body and username."
            }), 400

        new_message = Message(
            body=data["body"],
            username=data["username"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        db.session.add(new_message)
        db.session.commit()
        
        new_message_serialized = new_message.to_dict()

        return jsonify(new_message_serialized), 201

@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()
    
    if message is None:
        response_body = {
            "message": "This record does not exist in our database. Please try again."
        }
        return jsonify(response_body), 404
    
    else:
        if request.method == 'GET':
            message_dict = message.to_dict()
            return jsonify(message_dict), 200
        
        elif request.method == 'PATCH':
            data = request.get_json()
            for attr in data:
                setattr(message, attr, data[attr])

            db.session.add(message)
            db.session.commit()
            
            message_dict = message.to_dict()
            return jsonify(message_dict), 200

        elif request.method == 'DELETE':
            db.session.delete(message)
            db.session.commit()

            response_body = {
                "delete_successful": True,
                "message": "Message deleted."
            }
            return jsonify(response_body), 200

if __name__ == '__main__':
    app.run(port=5555, debug=True)
