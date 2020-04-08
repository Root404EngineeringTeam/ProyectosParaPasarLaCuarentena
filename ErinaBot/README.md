# ErinaBot

A cool discord chatbot.

## Instalación
Utiliza mongodb así que primero instala mongodb en tu sistema,eg. Debian:

    $ sudo apt install mongodb
Para instalar las dependencias:

    $ pip3 install -r requirements.txt 

Primero necesitas un *client_id* y *access_token* para el bot, lo consigues en [Discord Developers](https://discordapp.com/developers/applications/) y para el webhook también necesitas tokens de acceso, los cuales los consigues en la configuración del servidor discord en donde vayas a probar el bot [Discord Webhooks](https://support.discordapp.com/hc/es/articles/228383668-Usando-Webhooks). Cuando tengas estos datos, ponlos en [Este archivo](https://github.com/Root404EngineeringTeam/ProyectosParaPasarLaCuarentena/blob/master/ErinaBot/ErinaBot/__init__.py#L5).

Finalmente para ejecutarlo:

    $ sudo chmod +x start
    $ ./start
Para detenerlo:

    $ sudo chmod +x stop
    $ ./stop
