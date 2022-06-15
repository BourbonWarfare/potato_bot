const { SlashCommandBuilder } = require('@discordjs/builders');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('upload')
        .setDescription('Use to upload a mission to the mission server and database'),
    async execute(interaction) {
        interaction.reply({
            content: 'Upload',
            ephemeral: false
        });
    }
};
