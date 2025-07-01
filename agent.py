import requests
import json

class Agent():
    def __init__(self):
        self.readConfig()
        self.initParameters()
        self.urlChat = "http://localhost:11434/api/chat"
        self.urlGenerate = "http://localhost:11434/api/generate"
        self.messages = [{"role": "system", "content": ""}]
        self.currentUseCase = "0"
        self.inputParameters = None

    def readConfig(self):
        with open("config.json", "r", encoding="utf-8") as f:
            self.config = json.load(f)

    def initParameters(self):
        self.parameters = {}
        for useCase in self.config['useCases']:
            self.parameters[useCase] = {}
            for parameter in self.config['useCases'][useCase]['required']:
                self.parameters[useCase][parameter] = None

    def getParameters(self, prompt):
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
        if response.status_code == 200:
            data = json.loads(response.json()['response'].strip())
            for parameter in data:
                if data[parameter] == '':
                    pass

                else:
                    self.parameters[self.currentUseCase][parameter] = data[parameter]

        else:
            print("Error:", response.status_code, response.text)

    def runUseCase(self):
        print({"Current Use Case": self.currentUseCase, "Input Parameters": self.inputParameters})
        #Caso de uso 0
        if self.currentUseCase == "0":
            self.messages[0]["content"] = self.config["useCases"]["0"]["context"] #Actualizar contexto
            prompt = self.config["useCases"]["0"]["prompt"].format(messages=self.messages[1:]) #Prompt de razonamiento
            self.getParameters(prompt)
            print("Parameters: ",self.parameters[self.currentUseCase])
            #identificar caso de uso
            if self.parameters[self.currentUseCase]['agendar']:
                self.currentUseCase = "1"
                self.inputParameters=None
                self.runUseCase()

            elif self.parameters[self.currentUseCase]['modificar']:
                self.currentUseCase = "2"
                self.inputParameters=None
                self.runUseCase()

            elif self.parameters[self.currentUseCase]['consultar']:
                self.currentUseCase = "3"
                self.inputParameters=None
                self.runUseCase()

            elif self.parameters[self.currentUseCase]['borrar']:
                self.currentUseCase = "4"
                self.inputParameters=None
                self.runUseCase()

            return None

        #Agendar cita: (CU1)
        if self.currentUseCase == "1":
            #Leer base de datos consultando disponibilidad en base a nombre de doctor 
            self.messages[0]["content"] = self.config["useCases"][self.currentUseCase]["context"] #actualizar contexto
            prompt = self.config["useCases"][self.currentUseCase]["prompt"].format(messages=self.messages[1:]) #prompt de razonamiento
            self.getParameters(prompt)
            print("Parameters: ",self.parameters[self.currentUseCase])
            parameterCondition = (bool(self.parameters[self.currentUseCase]['nombreMedico']) and bool(self.parameters[self.currentUseCase]['apellidoMedico']))

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
            #obtener fecha y hora
            self.messages[0]["content"] = self.config["useCases"][self.currentUseCase]["context"].format(nombre_doctor=self.inputParameters["nombreDoctor"], disponibilidad=self.inputParameters["disponibilidad"]) #actualizar contexto
            prompt = self.config["useCases"][self.currentUseCase]["prompt"].format(messages=self.messages[1:]) #prompt de razonamiento
            self.getParameters(prompt)
            print("Parameters: ",self.parameters[self.currentUseCase])
            parameterCondition = (bool(self.parameters[self.currentUseCase]['fecha']) and bool(self.parameters[self.currentUseCase]['hora']))

            if parameterCondition:
                fecha = self.parameters[self.currentUseCase]['fecha']
                hora = self.parameters[self.currentUseCase]['hora']
                self.currentUseCase = "1.2"
                self.inputParameters={"fecha": fecha, "hora": hora, "nombreDoctor": self.inputParameters["nombreDoctor"]}
                self.runUseCase()
                
            else:
                pass

            return None

        if self.currentUseCase == "1.2":
            #obtener rut
            self.messages[0]["content"] = self.config["useCases"][self.currentUseCase]["context"] #actualizar contexto
            prompt = self.config["useCases"][self.currentUseCase]["prompt"].format(messages=self.messages[1:]) #prompt de razonamiento
            self.getParameters(prompt)
            print(self.parameters[self.currentUseCase])
            parameterCondition = bool(self.parameters[self.currentUseCase]['rut'])

            if parameterCondition:
                payload = {
                    "rut": self.parameters[self.currentUseCase]['rut'],
                    "nombreDoctor": self.inputParameters["nombreDoctor"],
                    "fecha": self.inputParameters["fecha"],
                    "hora": self.inputParameters["hora"]
                }
                response = requests.post("http://localhost:5000/agendar", json=payload)
                success = str(response.json())
                print(success)
                self.currentUseCase = "1.3" 
                
            else:
                pass

            return None
            #agendar según lo que indique el paciente

        #si modificar cita: (CU2)
            #obtener rut del paciente y consultar sus citas en la base de datos.
            #obtener disponibilidades del doctor
            #reagendar según lo que indique paciente

        #si consultar cita: (CU3)
            #consultar rut a paciente
            #leer base de datos, obtener datos en formato csv para procesar, responder al paciente en funcion de resultado

        #si borrar cita: (CU4)
            #solicitar rut
            #buscar en base de datos cita a eliminar
            #borrar cita
        
        #Respuesta al usuario. Payload con el modelo y los mensajes

    def userResponse(self):
        #Respuesta al usuario. Payload con el modelo y los mensajes
        payload = {
            "model": "gemma3",  
            "messages": self.messages,
            "stream": False  
        }

        response = requests.post(self.urlChat, json=payload)

        if response.status_code == 200:
            data = response.json()
            print(f'Agent: {data['message']['content']}')
            self.messages.append(data['message'])

        else:
            print("Error:", response.status_code, response.text)

if __name__ == '__main__':
    agent = Agent()
    while True:
        userInput = str(input("Your message: "))
        agent.messages.append({"role": "user", "content": userInput})
        agent.runUseCase()
        agent.userResponse()