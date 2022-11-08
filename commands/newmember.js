const { SlashCommandBuilder } = require('@discordjs/builders');
var logger = require('../logger');

module.exports = {
    data : new SlashCommandBuilder()
        .setName('newmember')
        .setDescription('Make this person a member and give them the deets.'),
    async execute(interaction) {
        logger.info('[',interaction.commandName,'] called by [', interaction.user.username, ']');
        let str = client.tools.randomQuote;
        interaction.reply({
            content: str,  
            ephemeral: false
        });
    }
};

