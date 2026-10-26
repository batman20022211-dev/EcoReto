# Misión Eco-Reto

> Pequeñas acciones, grandes cambios.

Aplicación web para registrar, consultar, editar y eliminar las acciones ecológicas de cada persona (reciclaje, ahorro de agua, transporte y energía), ver el impacto que se logra y cumplir una meta semanal. Es el proyecto integrador de HTML, CSS, Jinja2, JavaScript, Flask y SQLite.

## Objetivo

Motivar a los estudiantes a cuidar el planeta mostrando, con datos propios, cuánto impacto tienen sus acciones del día a día.

## Integrantes del equipo

| Nombre                           
|----------------------------------|
| Saúl Alexis Vargas Andres        |
| Angélica Lizet Medina Rodriguez  |
| Esmeralda Yorlei Torres Trinidad |
| Amalia Guadalupe Santiago Olvera |

Grupo: 306
## Tecnologías utilizadas

- **HTML5**: estructura de las páginas con etiquetas semánticas.
- **CSS3**: diseño responsivo (se adapta a computadora y celular) con hojas de estilo externas.
- **JavaScript**: validación de formularios, buscador de la tabla, confirmación antes de eliminar y avisos con imágenes.
- **Python y Flask**: servidor web y rutas.
- **Jinja2**: plantillas con herencia (`base.html` → `panel.html` → cada página).
- **SQLite**: base de datos local con consultas SQL (`INSERT`, `SELECT`, `UPDATE`, `DELETE`).
- **PostgreSQL (Neon)**: base de datos en la nube para la versión publicada.
- **Render y GitHub**: publicación de la aplicación y control de versiones.

## Funcionalidades

- Registro de usuarios e inicio de sesión. Las contraseñas se guardan cifradas.
- Cada persona ve y modifica únicamente sus propias acciones.
- **Inicio**: tarjetas de resumen (acciones registradas, litros de agua ahorrados, materiales reciclados y CO₂ evitado), tabla de acciones y buscador.
- **Nueva acción** y **Editar acción**: formulario con validaciones.
- **Detalles**: información completa de una acción.
- **Eliminar**: con confirmación previa.
- **Estadísticas**:
  - Meta semanal de 5 acciones con barra de progreso (la semana va de lunes a domingo).
  - Filtro por periodo: últimos 7 días, este mes o todo.
  - Impacto total por tipo de acción.
- Avisos con imágenes de gatos al guardar, editar, eliminar o cuando hay un error.

> El CO₂ evitado por energía es una estimación aproximada (0.435 kg de CO₂ por cada kWh ahorrado).

## Estructura del proyecto

```
EcoReto/
├── .gitignore
├── README.md
├── requirements.txt
└── app/
    ├── routes.py          Rutas y lógica de la aplicación
    ├── base_datos.py      Conexión a SQLite o PostgreSQL y creación de tablas
    ├── schema.sql         Tablas para SQLite (uso local)
    ├── schema_postgres.sql Tablas para PostgreSQL (Neon)
    ├── static/
    │   ├── style.css      Estilos
    │   ├── script.js      Validaciones, buscador y avisos
    │   └── i/             Imágenes e íconos
    └── templates/
        ├── base.html      Plantilla base
        ├── panel.html     Barra lateral y barra superior
        ├── sesion.html    Inicio de sesión
        ├── registrar.html Registro de usuario
        ├── principal.html Inicio con resumen y tabla
        ├── formulario.html Nueva acción y editar acción
        ├── detalle.html   Detalles de una acción
        └── estadisticas.html Estadísticas
```

## Base de datos

La aplicación usa una base de datos distinta según dónde se ejecute:

- **En la computadora (local):** SQLite. El archivo `ecoreto.db` se crea solo la primera vez, a partir de `schema.sql`.
- **Publicada en Render:** PostgreSQL en Neon. Se activa cuando existe la variable de entorno `DATABASE_URL`, y las tablas se crean solas a partir de `schema_postgres.sql`.

Las dos versiones tienen las mismas tablas y columnas.

**usuarios**

| Columna | Tipo | Descripción |
|---|---|---|
| id | INTEGER | Clave primaria |
| usuario | TEXT | Nombre de usuario (único) |
| contrasena | TEXT | Contraseña cifrada |

**acciones**

| Columna | Tipo | Descripción |
|---|---|---|
| id | INTEGER | Clave primaria |
| usuario_id | INTEGER | Dueño de la acción (clave foránea a `usuarios`) |
| fecha | TEXT | Fecha en formato AAAA-MM-DD |
| tipo | TEXT | Reciclaje, Ahorro de agua, Transporte o Energía |
| descripcion | TEXT | Qué se hizo |
| impacto | TEXT | Cantidad y unidad, por ejemplo `5 kg` o `50 litros` |

## Requisitos

- Python 3.10 o superior
- Las dependencias de `requirements.txt` (Flask, gunicorn y psycopg)

## Instalación y ejecución

1. Descarga o clona el repositorio y abre una terminal en la carpeta `EcoReto`.

2. Crea y activa un entorno virtual.

   En Windows:

   ```
   python -m venv venv
   venv\Scripts\activate
   ```

   En macOS o Linux:

   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instala las dependencias:

   ```
   pip install -r requirements.txt
   ```

4. Entra a la carpeta `app` y ejecuta la aplicación:

   ```
   cd app
   python routes.py
   ```

5. Abre el navegador en `http://127.0.0.1:5000`.

### Primer uso

1. En la pantalla de inicio de sesión, pulsa **Regístrate** y crea una cuenta (usuario de al menos 3 caracteres y contraseña de al menos 6).
2. Inicia sesión con esa cuenta.
3. Usa **Nueva acción** para registrar tus acciones ecológicas.

### Probar en el celular

Con la computadora y el celular conectados a la misma red WiFi, abre en el celular `http://IP-DE-LA-COMPUTADORA:5000` (por ejemplo `http://192.168.1.20:5000`).

## Publicación en Render con Neon

1. En Neon, crea un proyecto y copia la cadena de conexión (Connection string).
2. En Render, crea un **Web Service** conectado a este repositorio con estos datos:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --chdir app routes:app`
3. En Render, en **Environment**, agrega estas variables:
   - `DATABASE_URL`: la cadena de conexión de Neon.
   - `SECRET_KEY`: una clave larga y aleatoria.
4. Cuando el despliegue termine, abre la URL pública, regístrate y crea una acción. Los datos se pueden comprobar en el SQL Editor de Neon con `SELECT * FROM acciones;`.

La cadena de conexión y la clave son secretos: nunca se escriben en el código ni se suben a GitHub.

## Seguridad

- Las contraseñas se guardan cifradas con `generate_password_hash` y se comparan con `check_password_hash`.
- Las consultas SQL usan parámetros para evitar inyección SQL.
- Cada consulta de acciones se filtra por el usuario que inició sesión.
- El archivo `.gitignore` evita subir la base de datos con las cuentas.
- La cadena de conexión de la base y la clave secreta se leen de variables de entorno (`DATABASE_URL` y `SECRET_KEY`). No se incluyen contraseñas ni claves reales en el repositorio.

## Enlace del proyecto

Repositorio: https://github.com/batman20022211-dev/EcoReto.git

Aplicación publicada: https://ecoreto-sas9.onrender.com
