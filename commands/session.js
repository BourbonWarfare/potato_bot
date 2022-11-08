const { SlashCommandBuilder } = require('@discordjs/builders');
var logger = require('../logger');

module.exports = {
    data : new SlashCommandBuilder()
        .setName('session')
        .setDescription('Get details regarding next session and other session time references'),
    async execute(interaction) {
        logger.info('[',interaction.commandName,'] called by [', interaction.user.username, ']');
        let str = client.tools.randomQuote;
        interaction.reply({
            content: str,  
            ephemeral: false
        });
    }
};
