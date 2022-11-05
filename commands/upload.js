const { SlashCommandBuilder } = require('@discordjs/builders');
var logger = require('../logger');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('upload')
        .setDescription('Use to upload a mission to the mission server and database'),
    async execute(interaction) {
        logger.info('[',interaction.commandName,'] called by [', interaction.user.username, ']');
        interaction.reply({
            content: 'Upload',
            ephemeral: false
        });
    }
};
