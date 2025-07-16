# Agente IA en local para la gestión de horas médicas

Este proyecto implementa un agente de inteligencia artificial capaz de interactuar en lenguaje natural con los usuarios para gestionar citas médicas. Se ejecuta de manera local utilizando modelos LLM con Ollama, y está integrado con una base de datos MySQL y un bot de Telegram.

> ⚠️ Proyecto con fines exclusivamente educativos.

## 🛠 Herramientas utilizadas

- **[Ollama 0.9.2](https://ollama.com)**
- **Python 3.13.0**
- **MySQL 8.0.42**
- **Telegram Bot API**

## 📂 Estructura del proyecto

- `main.py`: Ejecuta el agente conectado con el bot de Telegram.
- `agent.py`: Contiene la lógica principal del agente (casos de uso, flujo conversacional).
- `api.py`: Maneja la lógica de conexión y consultas a la base de datos.
- `db.sql`: Script de creación de la base de datos y carga de datos de prueba.
- `requirements.txt`: Lista de dependencias necesarias para ejecutar el proyecto.

## 🚀 Instalación

1. **Clonar el repositorio:**

```bash
git clone https://github.com/mark3tmaker/agenteIA
cd agenteIA
```

2. **Instalar dependencias:**

```bash
pip install -r requirements.txt
```

3. **Instalar y ejecutar Ollama:**

```bash
ollama serve
ollama pull gemma3
ollama run gemma3
```

Verifica que la API de Ollama funcione accediendo a:

```
http://127.0.0.1:11434
```

Deberías ver: `Ollama is running`.

4. **Cargar la base de datos MySQL:**

```bash
mysql -u tu_usuario -p tu_basededatos < db.sql
```

5. **Configurar conexión a la base de datos en `api.py`:**

```python
# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'tu_usuario'
app.config['MYSQL_PASSWORD'] = 'tu_password'
app.config['MYSQL_DB'] = 'nombre_base_de_datos'
```

6. **Crear un bot de Telegram:**

Sigue este [tutorial para crear tu bot](https://core.telegram.org/bots/tutorial). Guarda tu token y chat ID.

En `main.py`, agrega:

```python
telegram_token = 'TOKEN_DEL_BOT'
chat_id = 'CHAT_ID_PRIVADO'
```

## 💬 Casos de uso implementados

| Caso de Uso | Descripción                                                |
|-------------|------------------------------------------------------------|
| CU 0        | Determina la intención del usuario (agendar, consultar, borrar). |
| CU 1        | Solicita doctor para agendar una cita.                     |
| CU 1.1      | Muestra disponibilidad del doctor.                         |
| CU 1.2      | Solicita RUT y agenda en base de datos.                    |
| CU 2        | Consulta citas según el RUT.                               |
| CU 2.1      | Informa al paciente sus citas agendadas.                   |
| CU 3        | Solicita RUT para anular cita médica.                      |
| CU 3.1      | Solicita fecha, hora y doctor para anular cita.           |
| CU 4        | Pregunta si desea realizar otra acción.                    |

> El caso de uso **Modificar** se interpreta como una combinación de agendar una nueva cita y eliminar la anterior.

## 🧠 Extracción de parámetros con salidas estructuradas

Este proyecto utiliza **salidas estructuradas de Ollama** para extraer parámetros como el RUT desde el historial de mensajes del usuario. Por ejemplo:

```python
prompt = "Considera los siguientes mensajes: {messages}. En base a estos, responde en formato JSON con el RUT del paciente."
```

El modelo responde:

```json
{"rut": "123456789"}
```

## 📊 Base de datos

El modelo relacional incluye las siguientes tablas:

- **médicos**
- **pacientes**
- **agenda**

Consulta y actualización se realizan vía endpoints API como `/disponibilidad`, `/agendar`, `/consultarcitas`, `/borrarcita`.

## 🤖 Funcionamiento general

El agente conversa con el usuario en Telegram, interpreta su intención, extrae los parámetros necesarios mediante un prompt de razonamiento y consulta la base de datos o realiza modificaciones según corresponda.

## 🧪 Pruebas y flujo

- Agendar: CU 0 → CU 1 → CU 1.1 → CU 1.2 → CU 4
- Consultar: CU 0 → CU 2 → CU 2.1 → CU 4
- Borrar: CU 0 → CU 3 → CU 3.1 → CU 4

## 🧭 Comentarios finales

Implementar LLMs en local ofrece ventajas como privacidad, control total del servicio y ahorro en costos a largo plazo. Aunque la inversión en hardware puede ser alta, este enfoque permite independencia de servicios externos y experimentación libre.

El uso de **cadenas de razonamiento** y salidas estructuradas hace posible construir agentes conversacionales funcionales sin depender de APIs de pago.

## 📘 Referencias

- [Ollama Structured Outputs](https://ollama.com/blog/structured-outputs)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Model Context Protocol (MCP)](https://github.com/modelcontext/protocol)

---

**Autor:** [@mark3tmaker](https://github.com/mark3tmaker)  
📅 Proyecto iniciado en

