from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import random

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///roulette.db')
db = SQLAlchemy(app)


class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participants = db.Column(db.Integer)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rounds_participated = db.Column(db.Integer)
    spins_per_round = db.Column(db.Float)


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cell = db.Column(db.Integer)


# Инициализация базы данных
with app.app_context():
    db.create_all()


def add_round(participants):
    round = Round(participants=participants)
    db.session.add(round)
    db.session.commit()


def add_user(user_id, rounds_participated, spins_per_round):
    user = User(id=user_id, rounds_participated=rounds_participated, spins_per_round=spins_per_round)
    db.session.add(user)
    db.session.commit()


def add_log(round_id, user_id, cell):
    log_entry = Log(round_id=round_id, user_id=user_id, cell=cell)
    db.session.add(log_entry)
    db.session.commit()


@app.route('/spin', methods=['POST'])
def spin_roulette():
    current_round = Round.query.order_by(Round.id.desc()).first()

    if not current_round or current_round.participants >= 10:
        current_round = Round(participants=0)
        db.session.add(current_round)

    user_id = request.json.get('user_id', None)

    if user_id:
        user = User.query.filter_by(id=user_id).first()

        if not user:
            user = User(id=user_id, rounds_participated=0, spins_per_round=0)
            db.session.add(user)
            db.session.commit()

        user.rounds_participated += 1
        user.spins_per_round = (user.spins_per_round * (user.rounds_participated - 1) + random.uniform(0,
                                                                                                       1)) / user.rounds_participated

        current_round.participants += 1
        db.session.commit()

        cell = spin_wheel()

        # Сохранение лога
        add_log(current_round.id, user.id, cell)

        return jsonify({'cell': cell}), 200
    else:
        return jsonify({'error': 'User ID is required in the request.'}), 400


@app.route('/stats', methods=['GET'])
def get_stats():
    rounds_data = [(round.id, round.participants) for round in Round.query.all()]

    users_data = [
        {'user_id': user.id, 'rounds_participated': user.rounds_participated, 'spins_per_round': user.spins_per_round}
        for user in User.query.all()]

    return jsonify({'rounds_data': rounds_data, 'users_data': users_data}), 200


def spin_wheel():
    weights = [20, 100, 45, 70, 15, 140, 20, 20, 140, 45]
    total_weight = sum(weights)
    rand_num = random.uniform(0, total_weight)

    cumulative_weight = 0
    for i, weight in enumerate(weights):
        cumulative_weight += weight
        if rand_num <= cumulative_weight:
            return i + 1


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
