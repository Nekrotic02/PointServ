from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kotf.db'
db = SQLAlchemy(app)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    points = db.Column(db.Integer, default=0)

class Flag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flag = db.Column(db.String(100), unique=True, nullable=False)
    submitted = db.Column(db.Boolean, default=False)  
    machine_id = db.Column(db.String(100), nullable=False)  

valid_machines = {
    'Team1Clinet1': '0de7dc34d37098e7a3eca9c7f087e56b',
    'Team1Client2': '3eadec8e42463b6dc726068d3e0f529e',
    'Team1DC': 'a2c3e5c1820c0ca23af2e6298b1a26ab',
    'Team1Linux': '439e7545dd9d777fcd2f1ede63bbffcf',
    'Team2Client1': '22ee6a82c8b3d985eaf0869e969dbad2',
    'Team2Client2': '3fa9f73101ade04ead64f03c0de1e75c',
    'Team2DC': '024b259cac7f1efcb038fc87d58810e4',
    'Team2Linux': '84c347021f6a26b604e0a74bbef14da0'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    teams = Team.query.all()
    return render_template('register.html', teams=teams)

@app.route('/teams')
def teams():
    teams = Team.query.all()
    teams_data = [{'name': team.name, 'points': team.points} for team in teams]
    return jsonify(teams_data)

@app.route('/flags')
def flags():
    return render_template('flags.html')

@app.route('/api/add_team', methods=['POST'])
def add_team():
    if request.method == 'POST':
        team_name = request.form['team_name']
        if team_name:
            new_team = Team(name=team_name)
            db.session.add(new_team)
            db.session.commit()
    return redirect(url_for('register'))

@app.route('/api/submit_flag', methods=['POST'])
def submit_flag():
    flag = request.form.get('Flag')

    if not flag:
        return jsonify({'error': 'Flag parameter is required'}), 400


    submitted_flag = Flag.query.filter_by(flag=flag).first()
    if submitted_flag:
        if submitted_flag.submitted:
            return jsonify({'error': 'Flag already submitted'}), 400


        machine_id = submitted_flag.machine_id
        opposing_team_id = 0 

        if 'Team1' in machine_id:
            team_identifier = 'Team1'
            opposing_team_identifier = 'Team2'
            opposing_team_id = 2
        elif 'Team2' in machine_id:
            team_identifier = 'Team2'
            opposing_team_identifier = 'Team1'
            opposing_team_id = 1
        else:
            return jsonify({'error': 'Invalid machine ID'}), 400


        opposing_team = Team.query.get(opposing_team_id)
    
        points_mapping = {
            'Client1': 150,
            'Client2': 150,
            'DC': 200,
            'Linux': 100
        }
        if opposing_team:

            machine_type = machine_id[5:]

            
            points = points_mapping.get(machine_type, 0)
            opposing_team.points += points

            submitted_flag.submitted = True
            db.session.commit()

            return jsonify({'message': 'Flag submitted successfully', 'TeamID': opposing_team.name, 'PointsAdded': points}), 200
        else:
            return jsonify({'error': 'Opposing team not found'}), 404
    else:
        return jsonify({'error': 'Flag not found'}), 404


@app.route('/api/post_data', methods=['POST'])
def post_data():
    data = request.get_json()

 
    if 'MachineID' in data and 'TeamID' in data:
        machine_id = data['MachineID']
        team_id = data['TeamID']

        api_key = request.headers.get('X-API-Key')

        if machine_id in valid_machines and api_key == valid_machines[machine_id]:
            team = Team.query.filter_by(name=team_id).first()
            if team:
                points_mapping = {
                    'Team1Clinet1': 20,
                    'Team1Client2': 20,
                    'Team1DC': 50,
                    'Team1Linux': 10,
                    'Team2Client1': 20,
                    'Team2Client2': 20,
                    'Team2DC': 50,
                    'Team2Linux': 10
                }
                points = points_mapping.get(machine_id, 0)
                team.points += points
                db.session.commit()

                return jsonify({'message': 'Points added successfully', 'TeamID': team_id, 'PointsAdded': points}), 200
            else:
                return jsonify({'error': 'TeamID not found'}), 404
        else:
            return jsonify({'error': 'Unauthorized'}), 401
    else:
        return jsonify({'error': 'MachineID and TeamID parameters are required'}), 400
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)