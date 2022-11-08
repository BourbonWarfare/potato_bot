const { SlashCommandBuilder } = require('@discordjs/builders');
var logger = require('../logger');

module.exports = {
    data : new SlashCommandBuilder()
        .setName('schedule')
        .setDescription('Pong!'),
    async execute(interaction) {
        logger.info('[',interaction.commandName,'] called by [', interaction.user.username, ']');
        interaction.reply({
            content: await client.tools.randomQuote,
            ephemeral: false
        });
    }
};
