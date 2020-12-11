from flask import Flask, render_template, request, json, redirect, session, jsonify
from flaskext.mysql import MySQL

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'secreto'
# MySQL configuracion
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'clinica'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['DEBUG'] = True
mysql.init_app(app)

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/index")
def inicio():
    return redirect('/')

@app.route('/conocenos')
def conocenos():
    return render_template('conocenos.html')

@app.route('/cita')
def cita():
    return render_template('cita.html')

@app.route('/buscarCitas', methods=['POST'])
def buscarCitas():
    global cursor, conn
    try:
        _DNI = request.form['inputDNI']
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('verCitas', (_DNI,)) #OBTENER TODAS LAS CITAS PENDIENTES DE UN DETERMINADO PACIENTE
        citas = cursor.fetchall()
        if len(citas) > 0:
            return render_template('cita.html', citasrender=citas[0])
        else:
            return render_template('cita.html', error='No tiene ninguna cita pendiente')
    except Exception as e:
        return render_template('cita.html', error=str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/intranet')
def intranet():
    return render_template('intranet.html')

@app.route('/sistema')
def sistema():
    if session.get('user'):
        return render_template('sistema.html')

@app.route('/validarLogin', methods=['POST'])
def validarLogin():
    global cursor, conn
    try:
        _username = request.form['inputUser']
        _password = request.form['inputPassword']
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('validaLogin', (_username,)) #VALIDAR USUARIO
        data = cursor.fetchall()
        if len(data) > 0:
            if str(data[0][1]) == _password:
                session['user'] = data[0][0]
                return redirect('/sistema' )
            else:
                return render_template('intranet.html', error='ERROR: Contraseña es Incorrecta')
        else:
            return render_template('intranet.html', error='ERROR: Usuario No existe')
    except Exception as e:
        return render_template('intranet.html', error=str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/mantUsuario')
def mantUsuario():
    if session.get('user'):
        return render_template('mantUsuario.html')

@app.route('/conseguirUsuario')
def conseguirUsuario():
    global mantus_dict
    try:
        if session.get('user'):
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM USUARIO') #CONSEGUIR TODA LA TABLA USUARIO
            mantus = cursor.fetchall()
            if len(mantus) > 0:
                return jsonify(mantus)
    except Exception as e:
        return render_template('mantUsuario.html', error=str(e))

@app.route('/agregarUsuario', methods=['POST'])
def agregarUsuario():
    try:
        if session.get('user'):
            _us = request.form['inputU']
            _pass = request.form['inputP']
            conn = mysql.connect()
            cursor = conn.cursor()
            data = cursor.callproc('agregarUsuario', (_us, _pass))#AGREGAR NUEVO USUARIO
            conn.commit()
            print(data)
            return render_template('mantUsuario.html', mensaje="Se creo el usuario satisfactoriamente")
    except Exception as e:
        return render_template('mantUsuario.html', error=str(e))

@app.route('/editarUsuario', methods=['POST'])
def editarUsuario():
    try:
        if session.get('user'):
            _usss = request.form['inputU']
            _passs = request.form['inputP']
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('modificarUsuario', (_usss, _passs))#MODIFICAR DATOS DEL USUARIO
            conn.commit()
            return redirect('/mantUsuario')
    except Exception as e:
        return render_template('mantUsuario.html', error=str(e))

@app.route('/eliminaUsuario', methods=['POST'])
def eliminaUsuario():
    try:
        if session.get('user'):
            _uss = request.form['inputU']
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('eliminarUsuario', (_uss,))#ELIMINAR A UN DETERMINADO USUARIO
            conn.commit()
            return redirect('/mantUsuario')
    except Exception as e:
        return render_template('mantUsuario.html', error=str(e))

@app.route('/mantPaciente')
def mantPaciente():
    if session.get('user'):
        return render_template('mantPaciente.html')

@app.route('/conseguirPaciente')
def conseguirPaciente():
    global mantpac_dict
    try:
        if session.get('user'):
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM PACIENTE') #CONSEGUIR TODA LA TABLA PACIENTE
            mantpac = cursor.fetchall()
            if len(mantpac) > 0:
                return jsonify(mantpac)
    except Exception as e:
        return render_template('mantPaciente.html', error=str(e))

@app.route('/agregarPaciente', methods=['POST'])
def agregarPaciente():
    try:
        if session.get('user'):
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT max(HCLinica)+1 FROM PACIENTE')#SUMAR +1 AL MAYOR DEL CAMPO HCLINICA
            _h = cursor.fetchall()
            _ap = request.form['inputApeP']
            _am = request.form['inputApeM']
            _nom = request.form['inputNom']
            _td = request.form['inputTipo']
            _nd = request.form['inputNumDoc']
            _ntel = request.form['inputTelf']
            _dir = request.form['inputDir']
            _dis = request.form['inputDistr']
            _fn = request.form['inputFechNac']
            _sex = request.form['inputSex']
            _tseg = request.form['inputTipSeg']
            _vig = request.form['inputVig']
            datas = cursor.callproc('agregarPac', (_h, _ap, _am, _nom, _td, _nd, _ntel, _dir, _dis, _fn, _sex, _tseg, _vig))
            #AGREGAR A UN NUEVO PACIENTE
            conn.commit()
            print(datas)
            return render_template('mantPaciente.html', datos=datas)
    except Exception as e:
        return render_template('mantPaciente.html', error=str(e))

@app.route('/editarPaciente', methods=['POST'])
def editarPaciente():
    try:
        if session.get('user'):
            _h = request.form['inputHCli']
            _ap = request.form['inputApeP']
            _am = request.form['inputApeM']
            _nom = request.form['inputNom']
            _td = request.form['inputTipo']
            _nd = request.form['inputNumDoc']
            _ntel = request.form['inputTelf']
            _dir = request.form['inputDir']
            _dis = request.form['inputDistr']
            _fn = request.form['inputFechNac']
            _sex = request.form['inputSex']
            _tseg = request.form['inputTipSeg']
            _vig = request.form['inputVig']
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('modificarPaciente', (_h, _ap, _am, _nom, _td, _nd, _ntel, _dir, _dis, _fn, _sex, _tseg, _vig))
            conn.commit()
            return redirect('/mantPaciente')
    except Exception as e:
        return render_template('mantPaciente.html', error=str(e))

@app.route('/eliminaPaciente', methods=['POST'])
def eliminaPaciente():
    try:
        if session.get('user'):
            _h = request.form['inputHCli']
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('eliminarPaciente', (_h,)) #ELIMINAR A UN DETERMINADO PACIENTE
            conn.commit()
            return redirect('/mantPaciente')
    except Exception as e:
        return render_template('mantPaciente.html', error=str(e))

@app.route('/mantServicio')
def mantServicio():
    if session.get('user'):
        return render_template('mantServicio.html')

@app.route('/conseguirServicio')
def conseguirServicio():
    global mantus_dict
    try:
        if session.get('user'):
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM SERVICIO') #CONSEGUIR TODA LA TABLA SERVICIO
            mantus = cursor.fetchall()
            if len(mantus) > 0:
                return jsonify(mantus)
    except Exception as e:
        return render_template('mantServicio.html', error=str(e))

@app.route('/agregarServicio', methods=['POST'])
def agregarServicio():
    try:
        if session.get('user'):
            _cod = request.form['inputCod']
            _nom = request.form['inputNom']
            conn = mysql.connect()
            cursor = conn.cursor()
            datos = cursor.callproc('agregarServ', (_cod, _nom))#AGREGAR UN NUEVO SERVICIO
            conn.commit()
            return render_template('mantServicio.html', datos=datos)
    except Exception as e:
        return render_template('mantServicio.html', error=str(e))

@app.route('/editarServicio', methods=['POST'])
def editarServicio():
    try:
        if session.get('user'):
            _cod = request.form['inputCod']
            _nom = request.form['inputNom']
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('modificarServicio', (_cod, _nom))#MODIFICAR NOMBRE DEL SERVICIO
            conn.commit()
            return redirect('/mantServicio')
    except Exception as e:
        return render_template('mantServicio.html', error=str(e))

@app.route('/eliminaServicio', methods=['POST'])
def eliminaServicio():
    try:
        if session.get('user'):
            _cod = request.form['inputCod']
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('eliminarservicio', (_cod,))#ELIMINAR A UN DETERMINADO SERVICIO
            conn.commit()
            return redirect('/mantServicio')
    except Exception as e:
        return render_template('mantServicio.html', error=str(e))

@app.route('/mantMedico')
def mantMedico():
    if session.get('user'):
        return render_template('mantMedico.html')

@app.route('/conseguirMedico')
def conseguirMedico():
    global mantus_dict
    try:
        if session.get('user'):
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT MEDICO.*,SERVICIO.NOMBRE FROM MEDICO,SERVICIO WHERE SERVICIO.CODIGO = MEDICO.CODSERV')
            mantus = cursor.fetchall()
            if len(mantus) > 0:
                return jsonify(mantus)
    except Exception as e:
        return render_template('mantMedico.html', error=str(e))

@app.route('/agregarMedico', methods=['POST'])
def agregarMedico():
    try:
        if session.get('user'):
            _serv = request.form['inputServ']
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT CODIGO FROM SERVICIO WHERE NOMBRE= %s', _serv)#OBTENER CODICO DE LA TABLA SERVICIO
            _cod = cursor.fetchall()
            _cmp = request.form['inputCMP']
            _ap = request.form['inputApe']
            _nom = request.form['inputNom']
            _dir = request.form['inputDir']
            _dis = request.form['inputDis']
            _tef = request.form['inputTelf']
            datos = cursor.callproc('agregarMed', (_cmp, _ap, _nom, _dir, _dis, _tef, _cod))#AGREGAR UN NUEVO MEDICO
            conn.commit()
            return render_template('mantMedico.html', datos=datos)
    except Exception as e:
        return render_template('mantMedico.html', error=str(e))

@app.route('/editarMedico', methods=['POST'])
def editarMedico():
    try:
        if session.get('user'):
            _serv = request.form['inputServ']
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT CODIGO FROM SERVICIO WHERE NOMBRE= %s', _serv)  # OBTENER CODIGO DE LA TABLA SERVICIO
            _cod = cursor.fetchall()
            _cmp = request.form['inputCMP']
            _ap = request.form['inputApe']
            _nom = request.form['inputNom']
            _dir = request.form['inputDir']
            _dis = request.form['inputDis']
            _tef = request.form['inputTelf']
            cursor.callproc('modificarMedico', (_cmp, _ap, _nom, _dir, _dis, _tef, _cod))#MODIFICAR DATOS DE MEDICO
            conn.commit()
            return redirect('/mantMedico')
    except Exception as e:
            return render_template('mantMedico.html', error=str(e))

@app.route('/eliminaMedico', methods=['POST'])
def eliminaMedico():
    try:
        if session.get('user'):
            _cmp = request.form['inputCMP']
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('eliminarMedico', (_cmp,))#ELIMINAR A UN DETERMINADO MEDICO
            conn.commit()
            return redirect('/mantMedico')
    except Exception as e:
        return render_template('mantMedico.html', error=str(e))

@app.route('/progrConsultorio')
def progrConsultorio():
    if session.get('user'):
        return render_template('progrConsultorio.html')

@app.route('/conseguirProgrCons')
def conseguirProgrCons():
    global mantus_dict
    try:
        if session.get('user'):
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT P.CMP,M.APELLIDOS,S.NOMBRE,P.FECHA,P.HORA,P.TURNO,P.CUPOS '
                           'FROM PROGR_CONSULTORIO AS P,MEDICO AS M, SERVICIO AS S '
                           'WHERE P.CMP=M.CMP AND M.CODSERV = S.CODIGO') #OBTENER PROGRAMACION DE CITAS
            mantus = cursor.fetchall()
            if len(mantus) > 0:
                return jsonify(mantus)
    except Exception as e:
        return render_template('progrConsultorio.html', error=str(e))

@app.route('/agregarProgCons', methods=['POST'])
def agregarProgCons():
    try:
        if session.get('user'):
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT max(ID_PROGCONS)+1 FROM PROGR_CONSULTORIO')
            _cod = cursor.fetchall()
            _med = request.form['inputCMP']
            cursor.execute('SELECT CMP FROM MEDICO WHERE APELLIDOS= %s', _med)
            _cmp = cursor.fetchall()
            _fec = request.form['inputFec']
            _hor = request.form['inputHor']
            _tur = request.form['inputTur']
            _cup = request.form['inputCup']
            datos = cursor.callproc('agregarProgCons', (_cod, _cmp, _fec, _hor, _tur, _cup))#AGREGAR UNA NUEVA PROGRAMACION
            conn.commit()
            return render_template('progrConsultorio.html', datos=datos)
    except Exception as e:
        return render_template('progrConsultorio.html', error=str(e))

@app.route('/eliminaProgCons', methods=['POST'])
def eliminaProgCons():
    try:
        if session.get('user'):
            conn = mysql.connect()
            cursor = conn.cursor()
            _med = request.form['inputCMP']
            cursor.execute('SELECT CMP FROM MEDICO WHERE APELLIDOS= %s', _med)
            _cmp = cursor.fetchall()
            _fec = request.form['inputFec']
            _hor = request.form['inputHor']
            cursor.callproc('eliminarProgCons', (_cmp,_fec,_hor))#ELIMINAR A UNA PROGRAMACION DE CITA
            conn.commit()
            return redirect('/progrConsultorio')
    except Exception as e:
        return render_template('progrConsultorio.html', error=str(e))

@app.route('/crearCita')
def crearCita():
    if session.get('user'):
        return render_template('crearCita.html')

@app.route('/buscarCitasPaciente', methods=['POST'])
def buscarCitasPaciente():
    global cursor, conn
    try:
        _DNI = request.form['inputDNI']
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc('verEstCitas', (_DNI,))#OBTENER TODAS LAS CITAS DE UN PACIENTE
        citas = cursor.fetchall()
        if len(citas) > 0:
            return jsonify(citas)
        else:
            return render_template('crearCita.html', error='No tiene ninguna cita pendiente')
    except Exception as e:
        return render_template('crearCita.html', error=str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/agregarCitaPaciente', methods=['POST'])
def agregarCitaPaciente():
    try:
        if session.get('user'):
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT max(ACTOMEDICO)+1 FROM CITA_MEDICA')
            _actmed = cursor.fetchall()

            _DNI = request.form['inputDNI']
            cursor.execute('SELECT HCLINICA FROM PACIENTE WHERE NUMDOCUMENTO = %s', _DNI)#OBTENER EL NRO DE HCL DEL DNI
            _hisclin = cursor.fetchall()

            _fec = request.form['inputFech']
            _hor = request.form['inputHor']
            _cmp = request.form['inputCMP']
            cursor.callproc('IDProg', (_fec, _hor, _cmp))#OBTENER EL IDPROG  A PARTIR DE 3 CAMPOS:FECHA,HORA,CMP
            _idprog = cursor.fetchall()

            _cup = request.form['inputCup']
            _cp = int(_cup) - 1
            if _cp > 0:
                cursor.callproc('agregarCitaMed', (_actmed, _hisclin, _idprog, _cp, 1))#AGREGAR CITA Y CAMBIAR CUPOS
            else:
                cursor.callproc('agregarCitaMed', (_actmed, _hisclin, _idprog, 0, 0))#AGREGAR CITA Y CAMBIAR CUPOS
            conn.commit()
            return redirect('/crearCita')
    except Exception as e:
        return render_template('crearCita.html', error=str(e))

@app.route('/listarServicio')
def listarServicio():
    global mantus_dict
    try:
        if session.get('user'):
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT NOMBRE FROM SERVICIO') #CONSEGUIR LOS NOMBRES DE LOS SERVICIOS
            mantus = cursor.fetchall()
            if len(mantus) > 0:
                return jsonify(mantus)
    except Exception as e:
        return render_template('crearCita.html', error=str(e))

@app.route('/buscarMedicoServicio', methods=['POST'])
def buscarMedicoServicio():
    global cursor, conn
    try:
        _Serv = request.form['inputServ']
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT CMP,concat(APELLIDOS,' ',NOMBRES) '
                       'FROM MEDICO AS M,SERVICIO AS S '
                       'WHERE M.CODSERV = S.CODIGO AND S.NOMBRE=', _Serv)#OBTENER CMP Y NOMBRE DE MEDICOS SEGUN SERVICIO
        citas = cursor.fetchall()
        if len(citas) > 0:
            return jsonify(citas)
        else:
            return render_template('crearCita.html', error='No tiene ninguna cita pendiente')
    except Exception as e:
        return render_template('crearCita.html', error=str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/buscarFechaTurnoMedico', methods=['POST'])
def buscarFechaTurnoMedico():
    global cursor, conn
    try:
        _CMP = request.form['inputCMP']
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT FECHA,HORA,TURNO,CUPOS '
                       'FROM PROGR_CONSULTORIO '
                       'WHERE ESTADO=1 AND CMP=', _CMP)#OBTENER FECHA HORA TURNO CUPOS DEL CMP
        citas = cursor.fetchall()
        if len(citas) > 0:
            return jsonify(citas)
        else:
            return render_template('crearCita.html', error='No tiene ninguna cita pendiente')
    except Exception as e:
        return render_template('crearCita.html', error=str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/eliminaCitaMedica', methods=['POST'])
def eliminaCitaMedica():
    try:
        if session.get('user'):
            conn = mysql.connect()
            cursor = conn.cursor()
            _actom = request.form['inputPaciente']
            _idprog = request.form['inputMed']
            cursor.execute('SELECT CUPOS FROM PROGR_CONSULTORIO WHERE ID_PROGCONS = %s', _idprog,)  # OBTENER EL NRO DE CUPOS
            _cup = cursor.fetchall()
            cursor.callproc('eliminarCitaMedica', (_actom, _idprog, _cup, 1,))  # ELIMINAR CITA Y CAMBIAR CUPOS
            conn.commit()
            return redirect('/crearCita')
    except Exception as e:
        return render_template('crearCita.html', error=str(e))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/intranet')

if __name__ == "__main__":
    app.run()