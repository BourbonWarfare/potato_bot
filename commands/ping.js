const { SlashCommandBuilder } = require('@discordjs/builders');
var logger = require('../logger');

module.exports = {
    data : new SlashCommandBuilder()
        .setName('ping')
        .setDescription('Pong!'),
    async execute(interaction) {
        logger.info("{} called by {}", interaction.commandName, interaction.user.username)
        interaction.reply({
            content: 'Pong!',
            ephemeral: false
        });
    }
};
