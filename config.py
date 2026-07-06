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
        "You cried in the school drop-off line again. So did I.",
        "You forgot the permission slip. Again. It's not the end of the world.",
        "The mental load hit you before 7am and nobody clapped for it.",
    ],
    "time_management": [
        "You answered a work email while your kid asked you three questions. Twice.",
        "Your to-do list has 40 things on it and you did 6. That's not failure.",
        "You don't need a better schedule. You need to stop apologizing for the one you have.",
    ],
    "self_care_permission": [
        "You sat in the car for two extra minutes before going inside. That was self-care.",
        "You haven't showered without an audience in three days. This is for you.",
        "Nobody is coming to give you permission to rest. So take it anyway.",
    ],
    "career_confidence": [
        "You went from a diaper blowout to a client call in nine minutes flat.",
        "They don't know you closed that deal on two hours of sleep.",
        "You second-guessed yourself in that meeting today. You were still right.",
    ],
    "exhaustion_relief": [
        "You said 'I'm fine' four times today and meant it zero times.",
        "Bedtime finally happened and you just sat on the floor for a minute. Good.",
        "You're touched out, talked out, and it's only Tuesday.",
    ],
    "small_wins": [
        "Nobody died, everyone ate, and you're still upright. Ten out of ten.",
        "You packed a lunch, missed a meeting, and survived both. That's a full day.",
        "The laundry is still in the dryer from Monday. You are still doing great.",
    ],
    "letting_go_of_perfect": [
        "You served cereal for dinner. Nobody remembers that but you.",
        "The Pinterest version of motherhood was never real. Yours is.",
        "You apologized to your kid for snapping. That's not failing, that's parenting.",
    ],
    "asking_for_help": [
        "You said 'I can't do this alone' out loud today. That took guts.",
        "Someone offered to help and you almost said no out of habit. Don't.",
        "You are not less of a mom for needing backup.",
    ],
    "presence_over_perfection": [
        "You put the phone down for five minutes today. They noticed.",
        "You missed the email but caught the joke your kid told at dinner.",
        "Ten distracted minutes with them will never beat five real ones.",
    ],
    "identity_beyond_mom": [
        "You had a thought today that had nothing to do with anyone else's schedule.",
        "You used to have a hobby. She's still in there.",
        "Somewhere under the diaper bag is a person with her own dreams. Hi, her.",
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
    "Comment 'ME' if today was one of those days.",
    "Tag a mom who needs to hear this today.",
    "Save this for the mornings that feel too heavy.",
    "You've got this. One hour at a time.",
    "Subscribe for a daily reminder you're doing better than you think.",
    "Send this to a mom who's had a rough week.",
    "Comment your hardest part of today. I'll go first: mine was bedtime.",
    "You're not alone in this. Not even close.",
    "Follow along — new reminder every single day.",
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

HASHTAGS = "#workingmom #momlife #momtok #shortsfeed #momsofinstagram"

# Theme-specific tags layered on top of HASHTAGS — broad tags get you into
# general feeds, specific tags get you in front of people actively
# searching/engaging with that exact topic (usually higher-intent viewers).
# Kept to 2 per theme deliberately: YouTube ignores ALL hashtags on a video
# if the total (title + description combined) exceeds 15 — going wide with
# hashtags isn't free, it actively risks losing every one of them.
THEME_HASHTAGS = {
    "morning_guilt": ["#morningroutine", "#momguilt"],
    "time_management": ["#timemanagement", "#momhacks"],
    "self_care_permission": ["#selfcaretips", "#momselfcare"],
    "career_confidence": ["#careerwomen", "#bossmom"],
    "exhaustion_relief": ["#momburnout", "#mentalload"],
    "small_wins": ["#momwin", "#momlifebelike"],
    "letting_go_of_perfect": ["#perfectionism", "#realmomlife"],
    "asking_for_help": ["#momsupportingmoms", "#askforhelp"],    "presence_over_perfection": ["#presentparenting", "#putyourphonedown"],
    "identity_beyond_mom": ["#momidentity", "#morethanmom"],
    "spotlight": ["#womeninspiringwomen", "#successstory"],
    "tips": ["#momhacks", "#momtips"],
}


def build_hashtags(theme: str) -> str:
    """Full hashtag set for the description — kept to ~7 total + #Shorts in
    the title = 8, comfortably under YouTube's 15-hashtag limit."""
    extra = " ".join(THEME_HASHTAGS.get(theme, []))
    return f"{HASHTAGS} {extra}".strip()


def top_title_hashtags(theme: str, n=2) -> str:
    """The 1-2 MOST relevant hashtags, meant to go directly in the video
    title alongside #Shorts — title hashtags get the most visible/prominent
    placement (shown right above the title), so put your best ones there."""
    tags = THEME_HASHTAGS.get(theme, [])[:n]
    return " ".join(tags)

# --- Persona / consistent branding ---------------------------------------
# A recurring identity + sign-off, used on every video, builds recognition
# the way a jingle or a talk-show sign-off does — repetition is the point.
PERSONA_NAME = "The 6:47am Pep Talk"  # rename to whatever you want the account called
TAGLINE = "— from your 6:47am pep talk 💛"  # appended after every closer, verbatim, every time

# --- Calendar-aware theming ------------------------------------------------
# Real-world timing makes generic content feel specific. Maps month -> themes
# to weight more heavily that month (still falls back to normal rotation
# the rest of the time). Expand freely.
CALENDAR_THEME_BOOST = {
    1: ["identity_beyond_mom", "career_confidence"],      # New Year, back-to-routine
    3: ["exhaustion_relief"],                              # daylight saving time change
    5: ["identity_beyond_mom", "self_care_permission"],    # Mother's Day month (US)
    8: ["morning_guilt", "time_management"],               # back-to-school
    9: ["morning_guilt", "letting_go_of_perfect"],          # school year in full swing
    12: ["letting_go_of_perfect", "asking_for_help"],       # holiday overload
}

# --- Real-women spotlight bank ---------------------------------------------
# Unlike the affirmation banks, these are NOT freely recombined or invented —
# each is a fact-checked, sourced statement about a real public figure.
# Review/refresh this list by hand periodically; don't let it silently
# "generate" new claims about real people without a human checking sources.
# No images/video of the actual people are used (see build_video.py) — only
# generic stock b-roll — to avoid likeness/rights issues.
SPOTLIGHT_STORIES = [
    {
        "name": "Serena Williams",
        "lines": [
            "Serena Williams won the 2017 Australian Open, her 23rd Grand Slam title, while about eight weeks pregnant.",
            "She didn't tell anyone at the time. She just showed up and won anyway.",
        ],
        "source": "olympics.com, June 2025 / CNBC, June 2025",
    },
    {
        "name": "J.K. Rowling",
        "lines": [
            "J.K. Rowling wrote the first Harry Potter book as an unemployed single mother in Edinburgh.",
            "She wheeled her daughter's pram into cafes and wrote while the baby slept, with no idea it would become one of the best-selling book series in history.",
        ],
        "source": "Accio Quote interview archive; multiple contemporaneous press accounts",
    },
]

FALLBACK_TAG = "spotlight"  # theme key used when a spotlight story is selected

# --- Support content bank ---------------------------------------------
# A different register from AFFIRMATIONS on purpose: not a mantra recited AT
# her, but something closer to what her own mother might say if she sat down
# next to her right now — normalizing the chaos, reminding her she has a
# community, and nudging her to remember she's a whole person, not just "mom."
# Curated as coherent sets (like TIP_CONTENT), not freely recombined, because
# this needs to read as one continuous, sincere thought, not shuffled lines.
SUPPORT_CONTENT = [
    {
        "hook": "Nobody prepares you for how sudden it is — one day you're just you, and the next, you're someone's whole world.",
        "lines": [
            "That toddler losing it in the cereal aisle? That's not you failing. Every toddler is a tiny bomb in the cutest packaging, and that's just true for all of them.",
            "You are allowed to ask someone else to carry this with you today.",
            "There's a whole community of women who felt exactly this overwhelmed last week too. You are not doing this alone, even when it feels like it.",
        ],
        "theme": "asking_for_help",
    },
    {
        "hook": "If I could sit with you for five minutes today, here's what I'd want you to hear.",
        "lines": [
            "You're allowed to be a wonderful mother AND still want things just for you. Those aren't in competition.",
            "Your career, your health, your own happiness — none of that became less important the day you became someone's mom.",
            "Don't let 'good mother' quietly replace every other thing you are. You get to be a whole woman too.",
        ],
        "theme": "identity_beyond_mom",
    },
    {
        "hook": "You don't have to do this with a straight face all the time.",
        "lines": [
            "It's okay to call someone and just say 'today was too much.' That's not weakness, that's how you're supposed to do this.",
            "Somewhere, another mom is having the exact same day as you, right now, at the exact same time.",
            "You were never meant to carry all of this by yourself. Let someone in.",
        ],
        "theme": "exhaustion_relief",
    },
    {
        "hook": "I know some days it feels like you disappeared into 'mom' overnight.",
        "lines": [
            "You didn't. She's still there — the one with dreams, with a career she's building, with things she wants just for herself.",
            "Chase those things too. Not instead of being a great mom — alongside it.",
            "Being happy and whole is not selfish. It's part of what you're modeling for her.",
        ],
        "theme": "identity_beyond_mom",
    },
    {
        "hook": "Here's something I wish someone had told me sooner.",
        "lines": [
            "Every wild, chaotic, impossible toddler moment is developmentally completely normal — it is not a reflection of your parenting.",
            "You are allowed to find it hard AND love them completely at the same time. Both are true.",
            "Ask for help before you're desperate for it, not after. That's wisdom, not weakness.",
        ],
        "theme": "letting_go_of_perfect",
    },
]

# --- Practical tips bank -----------------------------------------------
# Unlike AFFIRMATIONS, these are curated as coherent sets (not freely mixed)
# because actionable tips need to relate to each other to make sense as a list.
TIP_CONTENT = [
    {
        "hook": "3 things that actually saved my mornings, not just sounded nice.",
        "tips": [
            "Pack lunches the night before, even half-asleep. Future you will be so relieved.",
            "Lay out everyone's clothes, including yours, before bed.",
            "Set one alarm ten minutes earlier than you think you need. That buffer changes everything.",
        ],
        "theme": "morning_guilt",
    },
    {
        "hook": "The one email trick that gave me back 20 real minutes a day.",
        "tips": [
            "Check email at set times, not constantly. Your inbox can wait, your coffee can't.",
            "Use templated replies for the questions you get every single week.",
            "Turn off notifications after 6pm. Nothing there is worth your evening.",
        ],
        "theme": "time_management",
    },
    {
        "hook": "3 tiny self-care moves that don't need a spa day.",
        "tips": [
            "Sit in the car for two extra minutes before going inside. Nobody needs to know.",
            "Keep one drawer that's just yours, with things that make you happy.",
            "Say no to one thing this week without an explanation attached.",
        ],
        "theme": "self_care_permission",
    },
    {
        "hook": "How I stopped apologizing for leaving work on time.",
        "tips": [
            "Block your calendar for pickup like it's a real meeting, because it is.",
            "Say 'I have a hard stop' instead of over-explaining why.",
            "Remember: the people judging you for leaving on time aren't paying your bills.",
        ],
        "theme": "career_confidence",
    },
    {
        "hook": "3 ways to reset when you're running on empty.",
        "tips": [
            "Drink the water before the coffee. It actually helps more.",
            "Step outside for two minutes, even in your work clothes.",
            "Lower the bar for dinner tonight. Cereal counts.",
        ],
        "theme": "exhaustion_relief",
    },
]

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

# --- Affiliate monetization ------------------------------------------------
# Maps each theme to a relevant product search term. affiliate.py turns this
# into a real Amazon Associates search-results link at runtime using your
# own associate tag — no manual link curation needed per post.
AMAZON_KEYWORDS = {
    "morning_guilt": "easy school lunch containers for kids",
    "time_management": "family command center organizer",
    "self_care_permission": "self care gift set for moms",
    "career_confidence": "planner for working moms",
    "exhaustion_relief": "calming aromatherapy diffuser",
    "small_wins": "reward candle self care",
    "letting_go_of_perfect": "stress relief tea gift set",
    "asking_for_help": "easy meal prep kit",
    "presence_over_perfection": "screen free family games",
    "identity_beyond_mom": "guided journal for moms",
    "spotlight": "biography books inspiring women",
}

# --- Hand-picked specific products ---------------------------------------
# These take priority over the generic keyword-search links above — a
# specific, chosen product converts better than a generic search results
# page, since it removes the extra step of the viewer having to browse and
# decide themselves. Only themes with an actual picked product are listed
# here; everything else falls back to the keyword search.
SPECIFIC_PRODUCTS = {
    "identity_beyond_mom": {
        "asin": "B0C6C63KXB",
        "label": "You're a Good Mom — a positive affirmations journal",
    },
    "letting_go_of_perfect": {
        "asin": "B0F1ZFZKSW",
        "label": "a calming tea for the nights that feel like too much",
    },
    "exhaustion_relief": {
        "asin": "B083L8RNJR",
        "label": "a percussion massager for when your body is as tired as you are",
    },
    "presence_over_perfection": {
        "asin": "B0CHHNX51G",
        "label": "a screen-free busy book for toddlers",
    },
}
