require('dotenv').config();
const fs = require('fs');
const { REST } = require('@discordjs/rest');
const { Routes } = require('discord-api-types/v9');
const { Client, Intents, Collection } = require ('discord.js');
const mongoose = require('mongoose');
const log4js = require("log4js");

log4js.sconfigure({
  appenders: { out: { type: "stdout" } },
  categories: { default: { appenders: ["out"], level: "info" } },
  pm2: true,
});

const logger = log4js.getLogger("out");

const client = new Client({
    intents: [
        Intents.FLAGS.GUILDS,
        Intents.FLAGS.GUILD_MESSAGES],
})

const commandFiles = fs.readdirSync('./commands').filter(file => file.endsWith('.js'));

const commands = [];

client.commands = new Collection();

for (const file of commandFiles) {
    const command = require(`./commands/${file}`);
    commands.push(command.data.toJSON());
    client.commands.set(command.data.name, command);
}


client.once('ready', () => {
    logger.info("POTATO is Online");

    const CLIENT_ID = client.user.id;

    const rest = new REST({
        version: '9'
    }).setToken(process.env.TOKEN);

    (async () => {
        try {
            if(process.env.ENV === 'Production') {
                await rest.put(Routes.applicationCommands(CLIENT_ID), {
                    body: commands
                });
                logger.info('Successfully registered commands globally.')
            } else {
                await rest.put(Routes.applicationGuildCommands(CLIENT_ID, process.env.GUILD_ID), {
                    body: commands
                });
                logger.info('Successfully registered commands locally.');
            }
        } catch (err) {
            if (err) logger.error(err);
        }
    })()
});

client.on('interactionCreate', async interaction => {
    if(!interaction.isCommand()) return;

    const command = client.commands.get(interaction.commandName);

    if(!command) return;

    try {
        await command.execute(interaction);
    } catch(err) {
        if (err) logger.error(err);

        await interaction.reply({
            content: 'An error occured while executing that command',
            ephemeral: true,
        })
    }
});

client.login(process.env.TOKEN)
