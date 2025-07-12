import requests
import json

class Agent():
    def __init__(self):
        self.readConfig() #Carga la configuración desde un archivo config.json
        self.initParameters() #Inicializa los parámetros requeridos para cada caso de uso.
        self.urlChat = "http://localhost:11434/api/chat" #Define URLs base para endpoints del modelo
        self.urlGenerate = "http://localhost:11434/api/generate" #Define URLs base para endpoints del modelo
        self.messages = [{"role": "system", "content": ""}] #Inicializa los mensajes y el caso de uso actual.
        self.currentUseCase = "0" #Inicializa el sistema con el caso de uso 0
        self.inputParameters = None #Inicializa los parámetros de entrada para el caso de uso 0

    def readConfig(self):
    #Lee la configuración desde config.json, que contienen los casos de uso y los parámetros requeridos para cada uno.
        with open("config.json", "r", encoding="utf-8") as f:
            self.config = json.load(f)

    def initParameters(self):
    #Inicializa un diccionario self.parameters con los parámetros requeridos para cada caso de uso, todos con valor None.
        self.parameters = {}
        for useCase in self.config['useCases']:
            self.parameters[useCase] = {}
            for parameter in self.config['useCases'][useCase]['required']:
                self.parameters[useCase][parameter] = None

    def getParameters(self, prompt):
    #Envía un prompt al modelo LLM para obtener los parámetros requeridos definidos en el config.json usando un formato estructurado (tipo objeto).
        payload = {
            "model": "gemma3",  
            "prompt": prompt,
            "stream": False,
            "format": {
                "type": "object",
                "properties": self.config["useCases"][self.currentUseCase]["properties"],
                "required": self.config["useCases"][self.currentUseCase]["required"]
            }
        }

        response = requests.post(self.urlGenerate, json=payload)
        #Valida el estado de la respuesta
        if response.status_code == 200:
            data = json.loads(response.json()['response'].strip())
            #Asigna solo los parámetros que tienen contenido.
            for parameter in data:
                if data[parameter] == '':
                    pass

                else:
                    self.parameters[self.currentUseCase][parameter] = data[parameter]

        else:
            print("Error:", response.status_code, response.text)

    def runUseCase(self):
    #Maneja el flujo de conversación y decisiones según la variable currentUseCase.
    #Llama recursivamente a sí mismo para avanzar entre subcasos (1 → 1.1 → 1.2).
        print({"Current Use Case": self.currentUseCase, "Input Parameters": self.inputParameters})
        #Cada caso de uso representa una etapa de interacción (1. agendar, 2. consultar, 3. borrar)
        #Caso de uso 0: Se solicita a usuario si desea agendar, consultar o borrar una cita
        if self.currentUseCase == "0":
            self.messages[0]["content"] = self.config["useCases"]["0"]["context"] 
            prompt = self.config["useCases"]["0"]["prompt"].format(messages=self.messages[1:]) 
            self.getParameters(prompt)
            print("Parameters: ",self.parameters[self.currentUseCase])
            if self.parameters[self.currentUseCase]['agendar']:
                self.currentUseCase = "1"
                self.inputParameters=None
                self.runUseCase()

            elif self.parameters[self.currentUseCase]['consultar']:
                self.currentUseCase = "2"
                self.inputParameters=None
                self.runUseCase()

            elif self.parameters[self.currentUseCase]['borrar']:
                self.currentUseCase = "3"
                self.inputParameters=None
                self.runUseCase()

            return None

        #Caso de uso 1, 1.1, 1.2 - Agendamiento
        if self.currentUseCase == "1":
            #Obtener nombre de medico
            self.messages[0]["content"] = self.config["useCases"][self.currentUseCase]["context"]             prompt = self.config["useCases"][self.currentUseCase]["prompt"].format(messages=self.messages[1:]) #prompt de razonamiento
            self.getParameters(prompt)
            print("Parameters: ",self.parameters[self.currentUseCase])
            parameterCondition = (bool(self.parameters[self.currentUseCase]['nombreMedico']) and bool(self.parameters[self.currentUseCase]['apellidoMedico']))

            #Verifica si se cumplen condiciones mínimas antes de avanzar (como presencia de parámetros).
            if parameterCondition:
                payload = {
                    "nombreMedico": self.parameters[self.currentUseCase]['nombreMedico'],
                    "apellidoMedico": self.parameters[self.currentUseCase]['apellidoMedico']
                }
                response = requests.get("http://localhost:5000/disponibilidad", json=payload)
                disponibilidad = str(response.json())
                self.inputParameters={"disponibilidad": disponibilidad, "nombreDoctor": self.parameters[self.currentUseCase]['nombreMedico'] + ' ' + self.parameters[self.currentUseCase]['apellidoMedico']}
                self.currentUseCase = "1.1"
                self.runUseCase()
                
            else:
                pass

            return None

        if self.currentUseCase == "1.1":
            #Solicitar hora y fecha de agendamiento
            self.messages[0]["content"] = self.config["useCases"][self.currentUseCase]["context"].format(nombre_doctor=self.inputParameters["nombreDoctor"], disponibilidad=self.inputParameters["disponibilidad"]) #actualizar contexto
            prompt = self.config["useCases"][self.currentUseCase]["prompt"].format(messages=self.messages[1:]) #prompt de razonamiento
            self.getParameters(prompt)
            print("Parameters: ",self.parameters[self.currentUseCase])
            parameterCondition = (bool(self.parameters[self.currentUseCase]['fecha']) and bool(self.parameters[self.currentUseCase]['hora']))

            if parameterCondition:
                fecha = self.parameters[self.currentUseCase]['fecha']
                hora = self.parameters[self.currentUseCase]['hora']
                self.inputParameters={"fecha": fecha, "hora": hora, "nombreDoctor": self.inputParameters["nombreDoctor"]}
                self.currentUseCase = "1.2"
                self.runUseCase()
                
            else:
                pass

            return None

        if self.currentUseCase == "1.2":
            #Solicitar rut para agendar
            self.messages[0]["content"] = self.config["useCases"][self.currentUseCase]["context"] #actualizar contexto
            prompt = self.config["useCases"][self.currentUseCase]["prompt"].format(messages=self.messages[1:]) #prompt de razonamiento
            self.getParameters(prompt)
            print(self.parameters[self.currentUseCase])

            parameterCondition = bool(self.parameters[self.currentUseCase]['rut'])

            if parameterCondition:
                #Se hace la petición a la API que gestiona la base de datos para agendar
                payload = {
                    "rut": self.parameters[self.currentUseCase]['rut'],
                    "nombreDoctor": self.inputParameters["nombreDoctor"],
                    "fecha": self.inputParameters["fecha"],
                    "hora": self.inputParameters["hora"]
                }
                response = requests.post("http://localhost:5000/agendar", json=payload)
                success = response.json()
                print(success)
                print(type(success[0]['success']))
                if success[0]['success']:
                    self.messages = [self.messages[0]]    
                    self.currentUseCase = "4"
                    self.runUseCase() 
                
                else:
                    print("API has failed")
                    exit()
                
            else:
                pass

            return None
        
        #Caso de uso 2, 2.1 - Consulta de citas
        if self.currentUseCase == "2":
            #Solicitar a usuario el rut
            self.messages[0]["content"] = self.config["useCases"][self.currentUseCase]["context"] #actualizar contexto
            prompt = self.config["useCases"][self.currentUseCase]["prompt"].format(messages=self.messages[1:]) #prompt de razonamiento
            self.getParameters(prompt)
            print(self.parameters[self.currentUseCase])
            parameterCondition = bool(self.parameters[self.currentUseCase]['rut'])

            if parameterCondition:
                #Una vez solicitado el rut, se hace la petición a la API para consultar las citas asociadas al rut
                payload = {
                    "rut": self.parameters[self.currentUseCase]['rut']
                }
                response = requests.get("http://localhost:5000/consultarcitas", json=payload)
                citas = response.json()
                self.inputParameters = {"citas": str(citas)}
                self.currentUseCase = "2.1"
                self.runUseCase()

            return None

        if self.currentUseCase == "2.1":
            #Se le informan las citas al paciente
            self.messages[0]["content"] = self.config["useCases"][self.currentUseCase]["context"].format(citas=self.inputParameters["citas"],) #actualizar contexto
            prompt = self.config["useCases"][self.currentUseCase]["prompt"].format(messages=self.messages[1:]) #prompt de razonamiento
            
            return None

        #Caso de uso 3, 3.1 - Eliminación de cita
        if self.currentUseCase == "3":
            #Solicita RUT y muestra citas disponibles.
            self.messages[0]["content"] = self.config["useCases"][self.currentUseCase]["context"] 
            prompt = self.config["useCases"][self.currentUseCase]["prompt"].format(messages=self.messages[1:]) 
            self.getParameters(prompt)
            print(self.parameters[self.currentUseCase])
            parameterCondition = bool(self.parameters[self.currentUseCase]['rut'])

            if parameterCondition:
                #Consulta a la base de datos mediante la API las citas del paciente
                payload = {
                    "rut": self.parameters[self.currentUseCase]['rut']
                }
                response = requests.get("http://localhost:5000/consultarcitas", json=payload)
                citas = response.json()
                self.inputParameters = {"citas": str(citas), "rut": self.parameters[self.currentUseCase]['rut']}
                self.currentUseCase = "3.1"
                self.runUseCase()

            return None

        if self.currentUseCase == "3.1":
            #Se solicita al usuario fecha, hora y nombre del médico de la cita que quiere eliminar
            self.messages[0]["content"] = self.config["useCases"][self.currentUseCase]["context"].format(citas=self.inputParameters["citas"],) #actualizar contexto
            prompt = self.config["useCases"][self.currentUseCase]["prompt"].format(messages=self.messages[1:]) #prompt de razonamiento
            self.getParameters(prompt)
            print(self.parameters[self.currentUseCase])
            parameterCondition = bool(self.parameters[self.currentUseCase]['fecha']) and bool(self.parameters[self.currentUseCase]['hora']) and bool(self.parameters[self.currentUseCase]['nombreMedico'])
            if parameterCondition:
                payload = {
                    "fecha": self.parameters[self.currentUseCase]['fecha'],
                    "hora": self.parameters[self.currentUseCase]['hora'],
                    "nombreMedico": self.parameters[self.currentUseCase]['nombreMedico'],
                    "rut": self.inputParameters["rut"]
                }
                response = requests.delete("http://localhost:5000/borrarcita", json=payload)
                citas = response.json()

                self.messages = [self.messages[0]]
                self.currentUseCase = "4"
                self.runUseCase()

            return None

        #Caso de uso 4 - Confirmación final
        if self.currentUseCase == "4":
            #Confirma si el usuario desea realizar otra operación. Si es afirmativo, reinicia el flujo.
            self.messages[0]["content"] = self.config["useCases"][self.currentUseCase]["context"] #actualizar contexto
            prompt = self.config["useCases"][self.currentUseCase]["prompt"].format(messages=self.messages[1:]) #prompt de razonamiento
            self.getParameters(prompt)
            print(self.parameters[self.currentUseCase])
            parameterCondition = self.parameters[self.currentUseCase]['response']
            if parameterCondition:
                self.currentUseCase = "0"
                self.runUseCase()

            else:
                pass

            return None

    def userResponse(self, telegram_token, chat_id):
    #Envía la respuesta del modelo al usuario por Telegram.
        payload = {
            "model": "gemma3",  
            "messages": self.messages,
            "stream": False  
        }

        #Hace la llamada al modelo LLM con los mensajes actuales
        response = requests.post(self.urlChat, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f'Agent: {data['message']['content']}') #Imprime el resultado.
            self.messages.append(data['message'])
            url = f"https://api.telegram.org/bot{telegram_token}/sendMessage?chat_id={chat_id}&text={data['message']['content']}"
            requests.get(url) #Llama al endpoint de Telegram para enviar el mensaje generado.

        else:
            print("Error:", response.status_code, response.text)

