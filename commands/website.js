const { SlashCommandBuilder } = require('@discordjs/builders');
const logger = require('../logger');
const tools = require('../tools/bad');

module.exports = {
    data : new SlashCommandBuilder()
        .setName('website')
        .setDescription('Give me a link to the website'),
    async execute(interaction) {
        logger.info('[',interaction.commandName,'] called by [', interaction.user.username, ']');
        let str = tools.randomQuote();
        interaction.reply({
            content: str,  
            ephemeral: false
        });
    }
};
