import os
from flask import Flask, jsonify
from flask_cors import CORS

def create_app(config_name=None):
    app = Flask(__name__, instance_relative_config=True)

    CORS(
        app,
        resources={r"/api/*": {"origins": ["*"]}},
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    # Configuración básica
    # Configuración de base de datos dinámica
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME')

    if all([db_user, db_password, db_host, db_name]):
        database_uri = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    else:
        os.makedirs(app.instance_path, exist_ok=True)
        db_path = os.path.join(app.instance_path, 'booking.db')
        database_uri = f'sqlite:///{db_path}'

    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI=database_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    if config_name is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(config_name)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Healthcheck
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({"status": "healthy", "service": "booking"})

    # Base de datos
    from config.db import db
    db.init_app(app)
    
    # Modelos necesarios para la creación de tablas
    import modulos.reserva.infraestructura.dto
    import modulos.saga_reservas.infraestructura.dto
    
    with app.app_context():
        is_sqlite = str(app.config["SQLALCHEMY_DATABASE_URI"]).startswith("sqlite")
        if is_sqlite:
            db.create_all()
            from config.seed import seed_saga_reservas
            seed_saga_reservas()

    # Importar y registrar blueprints
    from modulos.reserva.infraestructura.api import reserva_api
    app.register_blueprint(reserva_api, url_prefix='/api')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
