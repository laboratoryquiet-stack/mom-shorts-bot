"""
Content configuration for the Working Moms Motivation shorts bot.
Everything here is a plain data bank so content generation needs
NO paid AI API — pure combinatorics keep it fresh for a very long time.
"""

# Broad rotating themes. main.py cycles through these in order (state.json tracks index).
THEMES = [
    "morning_guilt",
    "time_management",
    "self_care_permission",
    "career_confidence",
    "exhaustion_relief",
    "small_wins",
    "letting_go_of_perfect",
    "asking_for_help",
    "presence_over_perfection",
    "identity_beyond_mom",
]

# Opening lines, grouped by theme. Each is a short, punchy hook (first 3 seconds matter most).
OPENERS = {
    "morning_guilt": [
        "If you rushed out the door again this morning, this is for you.",
        "Feeling guilty about the school drop-off chaos? Listen.",
        "You forgot the lunchbox again. It's okay. Breathe.",
    ],
    "time_management": [
        "You don't need more hours. You need less guilt about the ones you have.",
        "Your to-do list will never be done. And that's fine.",
        "Busy is not the same as behind.",
    ],
    "self_care_permission": [
        "You are allowed to rest without earning it first.",
        "Taking five minutes for yourself is not selfish.",
        "Your cup has to be full before you can pour into anyone else's.",
    ],
    "career_confidence": [
        "Being a mom didn't make you less capable at work. It made you sharper.",
        "You run a household and a career. Act like the CEO you are.",
        "Doubting yourself today? You've survived every hard day before this one.",
    ],
    "exhaustion_relief": [
        "Tired isn't weakness. Tired is proof of how much you carry.",
        "It's okay to be touched out, talked out, and done by 7pm.",
        "You don't have to be everything today. Just enough.",
    ],
    "small_wins": [
        "Everyone fed. Everyone alive. That's a win today.",
        "You showed up again today. That counts more than you think.",
        "Small progress is still progress. Don't dismiss it.",
    ],
    "letting_go_of_perfect": [
        "The laundry can wait. Your peace can't.",
        "Perfect mom doesn't exist. Present mom does.",
        "Done is better than perfect. Every single time.",
    ],
    "asking_for_help": [
        "Asking for help is not failure. It's wisdom.",
        "You don't get a medal for doing it all alone.",
        "Let someone else carry it today. You're allowed.",
    ],
    "presence_over_perfection": [
        "Ten focused minutes beat two distracted hours.",
        "They won't remember the mess. They'll remember you sitting down with them.",
        "Put the phone down for five minutes. That's the whole trick.",
    ],
    "identity_beyond_mom": [
        "You were someone before 'mom' and you still are.",
        "Your dreams didn't expire when you became a parent.",
        "It's okay to want something just for you.",
    ],
}

# Affirmation body lines, theme-agnostic — mixed randomly into every script.
AFFIRMATIONS = [
    "I am doing better than I think I am.",
    "I don't have to carry this perfectly, I just have to carry it.",
    "My best today is enough, even if it looks different from yesterday.",
    "I am allowed to rest without guilt.",
    "I am raising my kids and building my career, and both matter.",
    "I release the guilt that isn't mine to hold.",
    "One hard morning does not define me as a mother.",
    "I am proud of how far I've come, even on the messy days.",
    "I don't need to prove my worth by exhaustion.",
    "I choose progress over perfection today.",
    "I am exactly the mom my kids need.",
    "I give myself the same grace I give everyone else.",
    "I am not behind. I am exactly where I need to be today.",
    "My worth isn't measured by how much I got done.",
    "I am allowed to change my mind about what I can handle today.",
    "I trust myself to figure it out, even when I don't have a plan.",
    "I am building a life my kids will be proud to look back on.",
    "It's okay if today looked nothing like I imagined.",
    "I don't have to be the calm one every single moment.",
    "I am learning, not failing.",
    "My effort counts even when the results are invisible.",
    "I can love this life and still find it hard.",
    "I am not responsible for everyone else's emotions today.",
    "I am allowed to say no without an explanation.",
    "I am more patient than I give myself credit for.",
    "The days that feel impossible still end, and I'm still standing.",
    "I don't need permission to put myself on the list.",
    "I am someone my younger self would be proud of.",
    "I can hold stress and still be a good mother.",
    "I am not failing them by needing a break.",
]

CLOSERS = [
    "Say it with me: I am enough today.",
    "Tag a mom who needs to hear this today.",
    "Save this for the mornings that feel too heavy.",
    "You've got this. One hour at a time.",
    "Follow for daily reminders you didn't know you needed.",
    "Send this to a mom who's had a rough week.",
    "Come back to this the next time it feels like too much.",
    "You're not alone in this. Not even close.",
    "Breathe. You are already doing enough.",
    "Bookmark this for tomorrow morning.",
]

# Pexels search terms — rotated so clips vary and match the vibe (calm, warm, real-life).
VIDEO_KEYWORDS = [
    "mother morning routine",
    "woman coffee sunrise",
    "busy mom kitchen",
    "mother child hug",
    "woman working laptop home",
    "sunrise city window",
    "woman journaling calm",
    "mother getting ready mirror",
    "parent walking child school",
    "woman stretching morning",
    "mother laughing child",
    "woman office smiling confident",
]

HASHTAGS = (
    "#workingmom #momlife #momaffirmations #momsofinstagram #mentalload "
    "#momtok #shortsfeed #motivation #selfcare #momguilt"
)

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30
