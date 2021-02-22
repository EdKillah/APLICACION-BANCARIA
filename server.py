from user import Usuario
import urllib.parse
from pymongo import MongoClient
import json
from datetime import datetime
from persistence.databases import *


templates = './templates/'

usuario_activo = None


'''
    Funciones reutilizables
'''


def render_template(template_name='index.html', context={}):
    html_str = ""
    with open(template_name, 'r') as f:
        html_str = f.read()
        html_str = html_str.format(**context)
    return html_str


def get_request_body_size(environ):
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0
    return request_body_size


def get_json_decoded(environ):
    request_body_size = get_request_body_size(environ)
    request_body = environ['wsgi.input'].read(request_body_size)
    json_body = urllib.parse.parse_qs(request_body)
    json_decode = {}
    for i in json_body:
        json_decode[i.decode('utf-8')] = json_body[i][0].decode('utf-8')
    return json_decode


def get_user_by_nit(nit):
    collections = init_db()
    result = collections.find_one({"user_nit": nit})
    return result


def get_user_by_mail(mail, db):
    
    if(db == 'administrators'):
        collections = administrators_db()
    elif(db == 'auditors'):
        collections = auditors_db()
    else:  # (db=='administators'):
        collections = users_db()


    result = collections.find_one({"user_mail": mail})
    return result


def get_client_by_nit(nit):
    collections = users_db()
    result = collections.find_one({"user_nit": nit})
    return result


def remove_value(json, field):
    r = dict(json)
    del r[field]
    return r


def compare_passwords(pwd1, pwd2):
    band = False
    if(pwd1 == pwd2):
        band = True
    return band


def validate_user():

    band = False
    if usuario_activo != None:
        band = True
    return band


def find_all(results):
    data = {}
    cont = 0
    for r in results:
        r.pop('_id')
        data[cont] = r
        cont += 1
    return data


'''
    Mapeadores de rutas
'''

# Unicamente gets


def home(environ):
    return render_template(
        template_name=templates+'index.html',
        context={'message': ''}
    )


def registro_usuario(environ):
    return render_template(
        template_name=templates+'create_account.html',
        context={}
    )


def get_registro_cliente(environ):
    return render_template(
        template_name=templates+'registro_cliente.html',
        context={}
    )


def get_login(environ):
    return render_template(
        template_name=templates+'login.html',
        context={}
    )


def get_movimientos_cliente(environ):

    collections = transactions_db()
    results = collections.find(
        {'cuenta_origen': usuario_activo['user_nit']})
    movimientos = find_all(results)
    retiros_collection = retiros_db()
    resultados = retiros_collection.find(
        {'usuario_retiro': usuario_activo['user_nit']})
    retiros = find_all(resultados)
    return render_template(
        template_name=templates+'movimientos_cliente.html',
        context={'movimientos': movimientos, 'retiros': retiros}
    )


def show_users(environ):

    collections = init_db()
    results = collections.find()

    users = find_all(results)

    return render_template(
        template_name=templates+'users.html',
        context={"usuarios": users}
    )


def get_user_info_by_nit(environ, nit):

    usuario = get_client_by_nit(nit)
    del usuario['_id']
    del usuario['user_password']
    return render_template(
        template_name=templates+'user_info.html',
        context={'user': usuario}
    )


def get_transaction_view(environ):
    user = ''
    user = 'Usuario: ' + \
        usuario_activo['user_name']+' '+usuario_activo['user_lastname']
    return render_template(
        template_name=templates+'transaction_form.html',
        context={'message': '', 'user': user, 'saldo': usuario_activo['saldo']}
    )


def get_movimientos():
    collections = transactions_db()
    results = collections.find()
    movimientos = find_all(results)
    total = 0

    for movimiento in movimientos:
        total += float(movimientos[movimiento]['monto'])

    return movimientos, total


def get_total_retiros():
    collection = retiros_db()
    results = collection.find()
    retiros = find_all(results)
    total = 0
    for retiro in retiros:
        total += float(retiros[retiro]['monto'])

    return retiros, total


def get_total_movimientos(environ):

    movimientos, total_transacciones = get_movimientos()
    numero_transacciones = len(movimientos)
    retiros, total_retiros = get_total_retiros()
    numero_retiros = len(retiros)
    return render_template(
        template_name=templates+'movements.html',
        context={'movimientos': movimientos, 'numero_transacciones': numero_transacciones,
                 'total_transacciones': total_transacciones, 'retiros': retiros, 'total_retiros':total_retiros,'numero_retiros':numero_retiros}
    )


def get_retiro_view(environ):

    user = 'Usuario: ' + \
        usuario_activo['user_name']+' '+usuario_activo['user_lastname']
    collections = users_db()
    usuario = collections.find_one({'user_nit': usuario_activo['user_nit']})
    return render_template(
        template_name=templates+'retiro.html',
        context={'user': user, 'saldo': usuario['saldo'], 'message': ''}
    )


def get_sobregiro_view(environ):

    user = 'Usuario: ' + \
        usuario_activo['user_name']+' '+usuario_activo['user_lastname']
    collections = users_db()
    usuario = collections.find_one(
        {'user_nit': usuario_activo['user_nit']})
    return render_template(
        template_name=templates+'solicitar_sobregiro.html',
        context={'user': user, 'saldo': usuario['saldo'], 'message': ''}
    )


def get_sobregiros(environ):

    user = 'Usuario: '+usuario_activo['user_name']+' '+usuario_activo['user_lastname']
    collections = sobregiros_db()
    results = collections.find()
    sobregiros = find_all(results)
    return render_template(
        template_name=templates+'sobregiros.html',
        context={'user': user, 'message': '', 'sobregiros': sobregiros}
    )

def get_sobregiros_auditor(environ):
    user = 'Usuario: '+usuario_activo['user_name']+' '+usuario_activo['user_lastname']
    collections = sobregiros_db()
    results = collections.find()
    sobregiros = find_all(results)
    return render_template(
        template_name=templates+'sobregiros_auditor.html',
        context={'user': user, 'message': '', 'sobregiros': sobregiros}
    )


# POST UNICAMENTE
def registro_cliente(environ):

    json = get_json_decoded(environ)
    json['saldo'] = 100000
    collections = init_db()
    collections.insert_one(json)

    return render_template(
        template_name=templates+'index.html',
        context={'message': 'Cliente creado con exito'}
    )


def create_user(environ):

    json = get_json_decoded(environ)
    user = get_user_by_nit(json['nit'])

    if(user != None):
        collections = users_db()
        user['user_mail'] = json['email']
        user['user_password'] = json['password']
        collections.insert_one(user)
        return render_template(
            template_name=templates+'login.html',
            context={}
        )
    else:
        return render_template(
            template_name=templates+'index.html',
            context={"message": "Usuario no activo."}
        )


def login(environ):
    global usuario_activo
    json = get_json_decoded(environ)
    
    user = get_user_by_mail(json['user_mail'], 'users')
    message = {'message': 'Usuario o contraseña incorrectos!'}

    if(user != None):
        if(user['user_password'] == json['user_password']):
            message['message'] = 'Logueado con exito!'
            usuario_activo = user

        return render_template(
            template_name=templates+'index.html',
            context={'message': message['message']}
        )
    else:
        user = get_user_by_mail(json['user_mail'], 'administrators')
        if(user!=None):
            if(user['user_password'] == json['user_password']):
                message['message'] = 'Logueado con exito!'
                usuario_activo = user                
        else:
            user = get_user_by_mail(json['user_mail'], 'auditors')
            if(user!=None):
                if(user['user_password'] == json['user_password']):
                    message['message'] = 'Logueado con exito!'
                    usuario_activo = user                
        return render_template(
            template_name=templates+'index.html',
            context={'message': message['message']}
        )


def exists_user(user_nit):
    collections = users_db()
    result = collections.find_one({'user_nit': user_nit})
    band = False
    if result != None:
        band = True
    return band


def get_date_now():
    now = datetime.now()
    fecha = "{}/{}/{} - {}:{}:{}".format(now.day, now.month,
                                         now.year, now.hour, now.minute, now.second)
    return fecha


def prepare_transaction(json):
    monto = int(json['monto'])
    if(usuario_activo['saldo'] >= monto):
        json["cuenta_origen"] = usuario_activo['user_nit']
        json["fecha"] = get_date_now()
        collection = users_db()
        collection.update_one({"user_nit": json['cuenta_destino']}, {
                              "$inc": {"saldo": monto}})
        collection.update_one({"user_nit": json['cuenta_origen']}, {
                              "$inc": {"saldo": -monto}})

        del json['password']
        return json
    return None


def make_transaction(environ):

    json = get_json_decoded(environ)
    if compare_passwords(json['password'], usuario_activo['user_password']):
        if exists_user(json['cuenta_destino']):
            json = prepare_transaction(json)
            if(json != None):
                collections = transactions_db()
                collections.insert_one(json)
        else:
            return render_template(
                template_name=templates+'transaction_form.html',
                context={'message': 'El destinatario no existe', 'user': usuario_activo['user_name']+usuario_activo['user_lastname']})
    else:
        return render_template(
            template_name=templates+'transaction_form.html',
            context={'message': 'Contraseña incorrecta.',
                     'user': usuario_activo['user_name']+usuario_activo['user_lastname']}
        )
    return render_template(
        template_name=templates+'index.html',
        context={'message': 'Realizo la transaccion'}
    )


def solicitar_sobregiro(environ):

    json = get_json_decoded(environ)
    json['solicitante'] = usuario_activo['user_nit']
    collections = sobregiros_db()
    collections.insert_one(json)

    return render_template(
        template_name=templates+'index.html',
        context={'message': 'Solicito un sobregiro'}
    )


def autorizar_sobregiro(environ):
    json = get_json_decoded(environ)
    collections = sobregiros_db()
    collections.update_one({"solicitante": json['nit_solicitante']}, {
        "$set": {"estado": json['estado_sobregiro']}})
    collections.update_one({"solicitante": json['nit_solicitante']}, {"$set": {
        "revisado_por": usuario_activo['user_name']+" "+usuario_activo['user_lastname']}})
    results = collections.find()
    sobregiros = find_all(results)
    return render_template(
        template_name=templates+'sobregiros.html',
        context={'message': '', 'sobregiros': sobregiros}
    )


def modificar_saldo(environ):
    
    json = get_json_decoded(environ)
    if(exists_user(json['user_nit'])):
        collections = users_db()
        cash = int(json['new_cash'])
        collections.update_one({"user_nit": json['user_nit']}, {
                               "$inc": {"saldo": cash}})
    else:
        return render_template(
            template_name=templates+'index.html',
            context={'message': 'Ha ocurrido un problema.'}
        )

    return render_template(
        template_name=templates+'index.html',
        context={'message': 'modifico un saldo.'}
    )


def hacer_retiro(environ):
    json = get_json_decoded(environ)

    user_collection = users_db()
    retiros_collection = retiros_db()
    cash = int(json['monto'])
    user_collection.update_one({"user_nit": usuario_activo['user_nit']}, {
                               "$inc": {"saldo": -cash}})

    json['usuario_retiro'] = usuario_activo['user_nit']
    json['monto'] = cash
    json['fecha'] = get_date_now()
    del json['password']
    retiros_collection.insert_one(json)
    return render_template(
        template_name=templates+'index.html',
        context={'message': 'Ha realizado un retiro.'}
    )


def create_administrator(environ):
    
    json = get_json_decoded(environ)
    #collection = administrators_db()
    collection = auditors_db()
    collection.insert_one(json)
    return render_template(
        template_name=templates+'index.html',
        context={'message': 'Se creo el auditor.'}
    )

def get_all_money(environ):

    collection = users_db()
    results = collection.find()
    dinero = find_all(results)
    dinero_total = 0
    for x in dinero:
        dinero_total += float(dinero[x]['saldo'])
    
    


    return render_template(
        template_name=templates+'dinero.html',
        context={'dinero_disponible': dinero_total}
    )




def posts(environ, path):

    if ((path == "/login")):
        data = login(environ)


    elif(path == "/make_transaction"):
        data = make_transaction(environ)

    elif(path == "/retiro"):
        data = hacer_retiro(environ)

    elif(path == "/solicitar_sobregiro"):
        data = solicitar_sobregiro(environ)

    return data


def posts_admin(environ, path):
    path = '/'+path
    if ((path == "/registrar_cliente") & (environ.get("REQUEST_METHOD") == 'POST')):
        data = registro_cliente(environ)
    
    elif(path == "/modificar_saldo"):
        data = modificar_saldo(environ)

    elif(path == "/autorizar_sobregiro"):
        data = autorizar_sobregiro(environ)

    return data


def gets(environ, path):
    if path == "":
        data = home(environ)

    elif path == "/login":
        data = get_login(environ)
    
    elif path == "/transferencia":
        data = get_transaction_view(environ)

    elif path == "/mis_movimientos":
        data = get_movimientos_cliente(environ)

    elif path == "/retiro":
        data = get_retiro_view(environ)

    elif path == "/solicitar_sobregiro":
        data = get_sobregiro_view(environ)

    else:
        data = render_template(template_name=templates +
                               '404.html', context={"path": path})

    return data


def gets_admin(environ, path):    
    path = '/'+path
    if path == "/registrar_cliente":
        data = get_registro_cliente(environ)

    # Los siguientes dos metodos pertenecen a los auditores tambien
    elif path == "/show_users":
        data = show_users(environ)

    elif path == "/movimientos":
        data = get_total_movimientos(environ)

    elif path == "/sobregiros":
        data = get_sobregiros(environ)

    elif path == "/informacion_dinero":
        data = get_all_money(environ)

    elif path.startswith("/client"):
        params = path.split("/")
        data = get_user_info_by_nit(environ, params[-1])

    else:
        data = render_template(template_name=templates +
                               '404.html', context={"path": path})

    return data


def gets_auditor(environ, path):

    path = '/'+path        

    if path == "/movimientos":
        data = get_total_movimientos(environ)

    elif path == "/sobregiros":
        data = get_sobregiros_auditor(environ)

    elif path == "/informacion_dinero":
        data = get_all_money(environ)    

    else:
        data = render_template(template_name=templates +
                               '404.html', context={"path": path})

    return data    




# Ejecutor de aplicacion


def app(environ, start_response):

    path = environ.get("PATH_INFO")
    print("path: ", path)
    if path.endswith("/"):
        path = path[:-1]
    if(environ.get("REQUEST_METHOD") == 'POST') & (path == '/login') & (usuario_activo == None):
        data = login(environ)
    
    elif(validate_user()):

        if(environ.get("REQUEST_METHOD") == 'POST'):
            if(path.startswith("/admin") & (usuario_activo['rol_user'] == 'admin')):
                params = path.split("/")
                ruta = params[-1]
                data = posts_admin(environ, ruta)                            

            else:
                data = posts(environ, path)

        elif(environ.get("REQUEST_METHOD") == 'GET'):            
            if(path.startswith("/admin") & (usuario_activo['rol_user'] == 'admin')):
                params = path.split("/")
                if((len(params) > 3) & (params[2] == 'client')):
                    ruta = params[2]+'/'+params[3]                    
                else:
                    ruta = params[-1]
                data = gets_admin(environ, ruta)

            elif(path.startswith("/auditor") & (usuario_activo['rol_user'] == 'auditor')):
                params = path.split("/")
                ruta = params[-1]
                data = gets_auditor(environ, ruta)
            else:
                data = gets(environ, path)

    else:
        if path == "/registrar_cuenta":
            data = registro_usuario(environ)
        elif ((path == "/create_account")):            
            data = create_user(environ)
            #data = create_administrator(environ)
        else:
            data = data = render_template(
                template_name=templates+'login.html', context={})

    data = data.encode("utf-8")
    start_response(
        f"200 OK", [
            ("Content-Type", "text/html"),
            ("Content-Length", str(len(data)))
        ]
    )
    return iter([data])
