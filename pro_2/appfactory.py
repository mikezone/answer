# -*- coding: utf-8 -*-
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from numbers import Number
import json

app = Flask(__name__)
socketio = SocketIO()
socketio.init_app(app)

@socketio.on('devide', namespace='/ws')
def devide(data):
    emit_event = 'response_devide'
    if isinstance(data, unicode):
        try:
            input_dict = json.loads(data)
            first_number = input_dict.get('first_number')
            second_number = input_dict.get('second_number')
            if not all([first_number, second_number]):
                error = {'error': 'lack parameter'}
                emit(emit_event, json.dumps(error))
                return

            if not isinstance(first_number, Number) or not isinstance(second_number, Number):
                error = {'error': 'parameter must be number'}
                emit(emit_event, json.dumps(error))
                return

            if second_number == 0:
                error = {'error': 'parameter second_number must not be 0'}
                emit(emit_event, json.dumps(error))
                return

            result = {'result': float(first_number) / second_number}
            print result
            emit(emit_event, json.dumps(result))
            return
        except:
            import traceback
            print traceback.format_exc()
            error = {'error': 'data format error'}
            emit(emit_event, json.dumps(error))
            return

@app.route('/devide_test')
def devide_test():
    return render_template('client.html')


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)