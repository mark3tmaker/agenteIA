from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from agent import Agent

telegram_token = ''
chat_id = ''
agent = Agent()

async def recibir_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Función que recibe los mensajes y aplica la lógica del agente
    user_input = update.message.text
    print(f'User: {user_input}')
    agent.messages.append({"role": "user", "content": user_input})
    agent.runUseCase()
    agent.userResponse(telegram_token, chat_id)
    
#Ejecuta el bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(telegram_token).build()

    handler = MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_mensaje)
    app.add_handler(handler)
    print("Bot is running...")
    app.run_polling()
