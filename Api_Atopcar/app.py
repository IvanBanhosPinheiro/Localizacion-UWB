from flask import Flask, jsonify
from extensions import db, migrate, cors
from flasgger import Swagger

def create_app():
    # Inicializar la aplicación Flask
    app = Flask(__name__)

    # Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:abc123.@localhost/atopcar'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'clave_secreta_para_desarrollo'
    app.config['JSON_SORT_KEYS'] = False

    
    # Configuración mejorada de Swagger
    app.config['SWAGGER'] = {
        'title': 'API Atopcar',
        'version': '1.0',
        'description': 'API para el sistema de localización UWB en tiempo real',
        'uiversion': 3,
        'tags': [
            {'name': 'usuarios', 'description': 'Operaciones de usuarios'},
            {'name': 'talleres', 'description': 'Gestión de talleres'},
            {'name': 'zonas', 'description': 'Zonas dentro de los talleres'},
            {'name': 'anchors', 'description': 'Puntos fijos de referencia UWB'},
            {'name': 'tags', 'description': 'Dispositivos UWB móviles'},
            {'name': 'vehiculos', 'description': 'Información de vehículos'},
            {'name': 'posiciones', 'description': 'Registros de posicionamiento'},
            {'name': 'distancias', 'description': 'Mediciones entre dispositivos'},
            {'name': 'alertas', 'description': 'Sistema de notificaciones'},
        ],
        'specs': [
            {
                'endpoint': 'apispec',
                'route': '/apispec.json',
                'rule_filter': lambda rule: True,  # all in
                'model_filter': lambda tag: True,  # all in
            }
        ],
        'static_url_path': '/flasgger_static',
        'swagger_ui': True,
        'specs_route': '/apidocs/'
    }
    
    # Inicializar Swagger 
    swagger = Swagger(app)
    
    # Inicializar extensiones con app
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    with app.app_context():
        # Importación de modelos
        from models.usuario import Usuario
        from models.taller import Taller
        from models.zona import Zona
        from models.anchor import Anchor
        from models.tag import Tag
        from models.vehiculo import Vehiculo
        from models.posicion import Posicion
        from models.distancia import Distancia
        from models.alerta import Alerta

        # Importación de rutas
        from routes.usuarios import usuario_bp
        from routes.talleres import taller_bp
        from routes.zonas import zona_bp
        from routes.anchors import anchor_bp
        from routes.tags import tag_bp
        from routes.vehiculos import vehiculo_bp
        from routes.posiciones import posicion_bp
        from routes.distancias import distancia_bp
        from routes.alertas import alerta_bp

        # Registrar blueprints
        app.register_blueprint(usuario_bp)
        app.register_blueprint(taller_bp)
        app.register_blueprint(zona_bp)
        app.register_blueprint(anchor_bp)
        app.register_blueprint(tag_bp)
        app.register_blueprint(vehiculo_bp)
        app.register_blueprint(posicion_bp)
        app.register_blueprint(distancia_bp)
        app.register_blueprint(alerta_bp)
        
        # Crear tablas si no existen
        db.create_all()

    # Manejador de errores para recursos no encontrados
    @app.errorhandler(404)
    def resource_not_found(e):
        return jsonify(error=str(e)), 404

    # Manejador de errores para errores internos
    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify(error=str(e)), 500

    # Ruta inicial para probar que la API funciona
    @app.route('/')
    def index():
        """
        Endpoint principal de la API
        ---
        responses:
          200:
            description: Información general de la API
            schema:
              properties:
                mensaje:
                  type: string
                  example: API Atopcar funcionando correctamente
                version:
                  type: string
                  example: 1.0
                endpoints:
                  type: array
                  items:
                    type: string
                    example: /api/usuarios
        """
        return jsonify({
            'mensaje': 'API Atopcar funcionando correctamente',
            'version': '1.0',
            'endpoints': [
                '/api/usuarios',
                '/api/talleres',
                '/api/zonas',
                '/api/anchors',
                '/api/tags',
                '/api/vehiculos',
                '/api/posiciones',
                '/api/distancias',
                '/api/alertas'
            ]
        })
        
    return app

# Crear una instancia de la app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)