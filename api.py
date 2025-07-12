<<<<<<< HEAD
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configuración de la base de datos 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'clinica'

mysql = MySQL(app)

#Ruta para verificar la disponibilidad
@app.route('/disponibilidad', methods=['GET'])
def verificar_disponibilidad():
    data = request.get_json()
    nombreMedico = data.get("nombreMedico")
    apellidoMedico = data.get("apellidoMedico")
    cursor = mysql.connection.cursor()
    #obtener medicoId
    nombre_completo = f"{nombreMedico} {apellidoMedico}"
    print(nombre_completo)
    cursor.execute("SELECT medicoId FROM medicos WHERE nombre = %s", (nombre_completo,))
    datos = cursor.fetchall()
    medicoId = datos[0][0]

    #Verificar disponibilidad
    cursor.execute("SELECT * from agenda WHERE medicoId=%s AND estado='disponible'", (medicoId,))
    datos = cursor.fetchall()
    print(datos)

    agenda = []

    for fila in datos:
        agenda.append({
            "medico": nombre_completo,
            "fecha": fila[3].isoformat(),
            "hora": str(fila[4]),
            "estado": fila[5]
        })

    return jsonify(agenda)

#Ruta para agendar hora
@app.route('/agendar', methods=['POST'])
def agendar_hora():
    data = request.get_json()
    rut = data.get("rut")
    nombreDoctor = data.get("nombreDoctor")
    fecha = data.get("fecha")
    hora = data.get("hora")
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT medicoId FROM medicos WHERE nombre = %s", (nombreDoctor,))
    datos = cursor.fetchall()
    medicoId = datos[0][0]
    cursor.execute("select consultaId from agenda where medicoId = %s and fecha = %s and hora = %s and estado = 'disponible';", (medicoId, fecha, hora))
    idConsulta = cursor.fetchall()[0][0]
    print(idConsulta)

    try:
        cursor.execute("UPDATE agenda SET pacienteId = %s WHERE fecha = %s AND hora = %s AND medicoId = %s AND estado = 'disponible';", (rut, fecha, hora, medicoId))
        mysql.connection.commit()
        cursor.execute("UPDATE agenda SET estado = 'agendada' WHERE fecha = %s AND hora = %s AND medicoId = %s AND pacienteId = %s;", (fecha, hora, medicoId, rut))
        mysql.connection.commit()
        print("success")
        success = True

    except Exception as e:
        print("fail: ", e)
        success = False

    response = [{
        "success": success
    }]

    return jsonify(response)

#Ruta para consulta de citas
@app.route('/consultarcitas', methods=["GET"])
def consultar_citas():
    data = request.get_json()
    rut = data.get("rut")
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT m.nombre AS nombreMedico, a.fecha, a.hora FROM agenda a JOIN medicos m on a.medicoId = m.medicoId WHERE pacienteId = %s;", (rut,))
    datos = cursor.fetchall()
    citas = []

    for fila in datos:
        citas.append({
            "medico": fila[0],
            "fecha": fila[1].isoformat(),
            "hora": str(fila[2])
        })

    return jsonify(citas)

@app.route('/borrarcita', methods=["DELETE"])
def borrar_cita():
    data = request.get_json()
    rut = data.get("rut")
    nombreDoctor = data.get("nombreMedico")
    fecha = data.get("fecha")
    hora = data.get("hora")
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT medicoId FROM medicos WHERE nombre = %s", (nombreDoctor,))
    datos = cursor.fetchall()
    medicoId = datos[0][0]

    try:
        cursor.execute("UPDATE agenda SET estado = 'disponible' WHERE pacienteId = %s and medicoId = %s and fecha = %s and hora = %s;", (rut, medicoId, fecha, hora))
        mysql.connection.commit()
        cursor.execute("UPDATE agenda SET pacienteId = NULL WHERE pacienteId = %s and medicoId = %s and fecha = %s and hora = %s;", (rut, medicoId, fecha, hora))
        mysql.connection.commit()
        print('Success')
        success = True

    except Exception as e:
        print("fail: ", e)
        success = False
    
    response = [{
        "success": success
    }]

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)