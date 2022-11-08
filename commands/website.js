const { SlashCommandBuilder } = require('@discordjs/builders');
var logger = require('../logger');

module.exports = {
    data : new SlashCommandBuilder()
        .setName('website')
        .setDescription('Give me a link to the website'),
    async execute(interaction) {
        logger.info('[',interaction.commandName,'] called by [', interaction.user.username, ']');
        interaction.reply({
            content: await tools.randomQuote,
            ephemeral: false
        });
    }
};
