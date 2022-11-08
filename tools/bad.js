module.exports.randomQuote = async function () {
 
    const quote;
    const quotes = [
        '"Yer a wizard BadWolf." ― Juujuu',
        '"It is our choices, BadWolf, that show what we truly are, far more than our abilities." — Quiz',
        '"I’ll be in my bedroom, making no noise and pretending I’m not there." — BadWolf',
        '"Power is a fickle friend, BadWolf. Admin is as Admin does. Remember that." — Brady',
        '"I solemnly swear I am up to no good." ― BadWolf',
        '"Are you insane? Of course I want to leave the BW! Have you got a house? When can I move in?" — BadWolf',
        '"Mischief Managed!" — BadWolf',
        '"Anyone can speak Rumda. All you have to do is point and grunt." — Lato',
        '"And now, BadWolf, let us step out into the night and pursue that flighty temptress, adventure." — Quiz',
        '"BadWolf was left to ponder in silence the depths to which BW Members would sink to get revenge."',
        '"I’m going to keep going until I succeed—or I die. Don’t think I don’t know how this might end. I’ve known it for years." — BadWolf',
        '“Do not pity the dead, BadWolf. Pity the living, and, above all, those who live without love.” ― Quiz'
    ];

    const index = Math.floor(Math.random() * quotes.length);
    quote = quotes[index];

    return quote;
};
