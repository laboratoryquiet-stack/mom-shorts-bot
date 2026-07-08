# config.py
#
# Single source of truth for content data. Every "theme" key used anywhere
# in the pipeline (generate_script.py, trending_topics.py,
# audience_comments.py) MUST have a matching entry in: OPENERS,
# THEME_HASHTAGS, AMAZON_KEYWORDS. This file used to drift out of sync with
# the rest of the codebase (missing constants, wrong data shapes, a literal
# placeholder string that would have gone out in a real video) - the test
# suite's test_config_completeness.py now catches that class of bug
# automatically, so it can't happen silently again.

import random
import urllib.parse

# ---------------------------------------------------------------------------
# Video rendering
# ---------------------------------------------------------------------------
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

# Core search/discovery keywords required by the pipeline (Pexels queries).
# NOTE: do not pre-encode these - requests' `params=` already URL-encodes
# dict values. Encoding here too would double-encode ("mom life" ->
# "mom%2520life") and break every search.
VIDEO_KEYWORDS = ["parenting", "mom life", "shorts", "family", "working mom"]

# ---------------------------------------------------------------------------
# Theme identity
# ---------------------------------------------------------------------------
# These 8 keys are the canonical "emotional" themes. They MUST match the
# values used in trending_topics.KEYWORD_THEME_MAP and audience_comments.py's
# keyword mapping, since a real-world trend/comment nudge can hand back any
# of these to choose_theme().
THEMES = [
    "morning_guilt",
    "time_management",
    "exhaustion_relief",
    "self_care_permission",
    "asking_for_help",
    "letting_go_of_perfect",
    "career_confidence",
    "identity_beyond_mom",
]

# Non-affirmation content types layered into the rotation by generate_script.py.
# "spotlight" is also used as the FALLBACK_TAG (the theme value attached to
# spotlight posts specifically, since a real-woman story isn't tied to one
# single emotional theme).
FALLBACK_TAG = "spotlight"
CONTENT_TYPE_TAGS = ["tips", "support", "humor", "myth_bust", "hack_demo", "this_or_that"]

# ---------------------------------------------------------------------------
# Hashtags
# ---------------------------------------------------------------------------
# General discovery tags. 2026 guidance: 3 relevant hashtags outperforms a
# hashtag wall, so build_hashtags() below defaults to a small count.
HASHTAGS = [
    "#workingmom", "#momlife", "#workingmother", "#motherhood", "#momsupport",
    "#workingmomlife", "#momhacks", "#parenting", "#momcommunity", "#motherhoodunplugged",
]

THEME_HASHTAGS = {
    "morning_guilt": ["#momguilt", "#workingmomguilt", "#daycarelife", "#momencouragement"],
    "time_management": ["#momtips", "#workingmomtips", "#timemanagement", "#momhack"],
    "exhaustion_relief": ["#momburnout", "#tiredmom", "#momlifebelike", "#momrealtalk"],
    "self_care_permission": ["#selfcareformoms", "#momselfcare", "#mindfulmama", "#permissiontorest"],
    "asking_for_help": ["#mentalload", "#momsupportingmoms", "#askforhelp", "#momcommunity"],
    "letting_go_of_perfect": ["#imperfectmom", "#realmotherhood", "#doneperfect", "#momtruth"],
    "career_confidence": ["#workingwomen", "#momboss", "#careerandkids", "#womeninbusiness"],
    "identity_beyond_mom": ["#morethanamom", "#momidentity", "#selfbeyondmotherhood", "#realwomen"],
    "spotlight": ["#womensupportingwomen", "#inspiringwomen", "#realwomen", "#workingwomen"],
}

# Weighting configuration for the content calendar/scheduler.
# Keyed by calendar MONTH (1-12), value is a list of theme keys to lean into
# that month. Months not listed here simply skip the calendar-boost step in
# choose_theme() and fall through to normal rotation/weighted-by-performance
# selection - partial coverage is intentional, not a bug.
CALENDAR_THEME_BOOST = {
    1: ["career_confidence", "time_management"],           # New year, back-to-work energy
    5: ["identity_beyond_mom", "self_care_permission"],     # Mother's Day month
    8: ["morning_guilt", "time_management"],                # Back-to-school ramp-up
    9: ["morning_guilt", "time_management"],
    12: ["exhaustion_relief", "asking_for_help"],           # Holiday burnout
}


def get_normalized_weights(theme_scores: dict) -> dict:
    """
    Normalizes a theme->raw_score dict into theme->probability (sums to 1.0),
    clamping negatives to 0 and falling back to a uniform distribution if
    every score is 0 (or the dict is empty). Used by choose_theme() as a
    safety wrapper around learn.py's raw EMA scores before feeding them to
    random.choices(), which raises if all weights are 0 or negative.
    """
    if not theme_scores:
        return {}
    sanitized = {k: max(0.0, float(v)) for k, v in theme_scores.items()}
    total = sum(sanitized.values())
    if total == 0:
        return {k: 1.0 / len(sanitized) for k in sanitized}
    return {k: v / total for k, v in sanitized.items()}


def build_hashtags(theme=None, count=3):
    """
    Combines general hashtags and theme-specific hashtags into a short,
    deduplicated, order-preserving string. 2026 guidance favors ~3 relevant
    hashtags over a hashtag wall, hence the small default count.
    """
    tags = []
    if theme and theme in THEME_HASHTAGS:
        tags.extend(THEME_HASHTAGS[theme])  # theme-specific tags first (higher relevance)
    tags.extend(HASHTAGS)

    unique_tags = list(dict.fromkeys(tags))  # de-dupe, preserve priority order
    return " ".join(unique_tags[:count])


def top_title_hashtags(theme=None):
    """
    Returns a short string of high-leverage hashtags for video titles.
    Prefers the theme's own top tag when available so the title reads as
    on-topic, not generic.
    """
    if theme and theme in THEME_HASHTAGS and THEME_HASHTAGS[theme]:
        return f"{THEME_HASHTAGS[theme][0]} #workingmom"
    return "#workingmom #momlife"


# ---------------------------------------------------------------------------
# Persona / sign-off
# ---------------------------------------------------------------------------
TAGLINE = "You're doing better than you think. Follow for your daily working mom support."

# Rotating closing CTAs. A single static tagline every post is a weaker
# algorithmic signal than variety - comments are reportedly weighted more
# heavily than subscribes in the 2026 Shorts feed, so several of these
# intentionally invite a comment/save rather than only a follow. Kept
# genuine and kind, never fake-giveaway engagement bait.
CTA_POOL = [
    "You're doing better than you think. Follow for your daily working mom support.",
    "If this is you today, drop a heart in the comments so I know you're out there.",
    "Save this for the morning you need it most.",
    "Comment your city if you're a working mom watching this at an insane hour.",
    "Tag a working mom who needs to hear this today.",
    "Which one hit different? Tell me in the comments.",
    "Follow along - new one of these every day, made for exactly this kind of day.",
]

# On-screen (not spoken) loop cue, shown briefly on the final frame to
# encourage a rewatch. Loops (last frame connecting back to the first) are
# reported to meaningfully boost re-watch rate in the current Shorts
# algorithm. This is intentionally honest, not manipulative - it's framed
# as genuine comfort/permission, matching the channel's voice.
LOOP_CUES = [
    "watch again when you need it",
    "save + rewatch on your hardest morning",
    "come back to this one",
]

# ---------------------------------------------------------------------------
# Openers (hooks), grouped by theme. Every theme in THEMES must have at
# least 3 openers here so the shuffle-bag has real variety.
# ---------------------------------------------------------------------------
OPENERS = {
    "morning_guilt": [
        "To the mom feeling guilty for dropping her crying toddler off at daycare this morning...",
        "If you felt a wave of guilt walking out the door while your baby reached for you...",
        "For the mom who felt like she chose her job over her kids before 9 AM today...",
        "To the working mom replaying this morning's chaotic goodbye on a loop...",
        "To the mom doing the chaotic daycare drop-off dash this morning...",
    ],
    "time_management": [
        "If you're trying to balance spreadsheets and a teething baby on your hip...",
        "If your to-do list is longer than your energy span today...",
        "For the working mama who just survived the bedtime chaos of a baby and a toddler...",
        "To the mom managing a toddler's meltdown while trying to answer work emails...",
    ],
    "exhaustion_relief": [
        "If you were up at 3 AM with a baby and still had to log in at 8 AM...",
        "A quick reminder for the mom running on dry shampoo and cold coffee...",
        "To the mom who is constantly exhausted but keeps showing up with so much love...",
        "If your coffee has been reheated three times already today...",
    ],
    "self_care_permission": [
        "To the mama hiding in the bathroom for two minutes of absolute peace...",
        "Stop scrolling for just a second. I need you to hear this.",
        "Take a deep breath. This message is exactly for you today.",
        "Here is your daily reminder that you are exactly what your kids need.",
    ],
    "asking_for_help": [
        "If you are feeling completely touched-out and overwhelmed right now...",
        "Hey mama, pause for a second. You really need to hear this.",
        "For the mom who feels like she has to do it all, alone...",
        "If you've never once asked for backup because you're 'supposed to' handle it all...",
    ],
    "letting_go_of_perfect": [
        "To the working mom who feels like she's dropping all the balls today...",
        "For the mom who feels like she's failing at work and at home...",
        "For the mom who cried in her car before walking into the office today...",
        "If you're feeling guilty about working today, listen to this.",
    ],
    "career_confidence": [
        "To the woman trying to give 100 percent to her boss and 100 percent to her kids...",
        "For the working mama juggling a big presentation and a sick kid at home...",
        "To the mom who negotiated for herself today and still made it to pickup on time...",
        "If you need some encouragement to keep pushing toward your career goals today...",
    ],
    "identity_beyond_mom": [
        "To the woman underneath the diaper bag and the laptop bag...",
        "If you sometimes forget what you liked to do before you became 'Mom'...",
        "For the woman who is so much more than just somebody's mother...",
        "To the ambitious woman balancing building a life and raising a family...",
    ],
}

# ---------------------------------------------------------------------------
# Affirmations / closers - theme-independent by design (drawn regardless of
# which theme was chosen, so the same warm bank supports every theme).
# ---------------------------------------------------------------------------
AFFIRMATIONS = [
    "Your worth is not measured by your productivity. You are allowed to rest.",
    "It is okay if the house is messy. You are building a beautiful life, not a museum.",
    "You are setting an incredible example of resilience and love for your little ones.",
    "Some days are just about surviving, and that is a massive, beautiful victory in itself.",
    "You do not have to be perfect to be a wonderful mother.",
    "The love you pour into your children matters so much more than a flawless schedule.",
    "It is normal to miss them when you work, and normal to crave work when you are with them.",
    "Your children don't need a perfect mom. They just need you.",
    "You are allowed to ask for help. You don't have to carry this entire mental load alone.",
    "You are balancing two full-time jobs, and you are doing it with so much grace.",
    "The hard days do not define your motherhood journey. Your persistent love does.",
    "Your career and your children both benefit from your dedication, even when it feels stretched thin.",
    "Taking time to breathe and recharge is not a luxury; it is how you keep your beautiful family running.",
    "You are doing a beautiful job, even when no one explicitly tells you.",
    "Your best looks different every single day, and today's best is wonderfully enough.",
    "It is okay to grieve the freedom you had before kids, while still fiercely loving the life you have now.",
    "You are allowed to be ambitious in your career and deeply devoted to your family.",
    "The guilt you feel just proves how much you care. Let it go; you are doing great.",
    "You are the absolute center of your children's universe, and you are doing beautifully.",
    "Even on the days you feel you are failing, your kids look at you and see a superhero.",
    "You are so deeply loved, needed, and appreciated, even when the little ones can't say it yet.",
]

CLOSERS = [
    "You've got this. Take a deep, loving breath and keep going.",
    "I see you, I hear you, and you are doing such a beautiful job.",
    "Wrap yourself in a little grace today. You absolutely earned it.",
    "Tomorrow is a fresh start. Rest your mind tonight.",
    "You are a force of nature. Have a beautiful, peaceful day.",
    "Remember, out of everyone in the world, you are the exact right mom for your kids.",
    "Hang in there, mama. You are doing so much better than you think.",
    "Take it one hour at a time, and remember how loved you are.",
    "Save this to remind yourself of your own strength when things get loud.",
    "Send this to another working mom who could use a digital hug today.",
    "Close your eyes, take a breath, and remember you are enough.",
    "Leave a heart in the comments if you needed this today.",
]

# ---------------------------------------------------------------------------
# Real-women spotlight stories (fact-based, used ~1 in 5 posts).
# Structured as {name, lines} - "lines" are the spoken/caption lines that
# follow the "Real story: {name}." opener.
# ---------------------------------------------------------------------------
SPOTLIGHT_STORIES = [
    {"name": "Sara Blakely, founder of Spanx", "lines": [
        "She started her billion-dollar business while selling fax machines door-to-door.",
        "She kept her day job for two years while building her empire at night.",
    ]},
    {"name": "Ursula Burns, first Black woman CEO of a Fortune 500 company", "lines": [
        "She grew up in a low-income housing project and started at Xerox as a summer intern.",
        "She worked her way up for 30 years to become the company's CEO.",
    ]},
    {"name": "Indra Nooyi, former CEO of PepsiCo", "lines": [
        "She spoke openly about the impossibility of perfect balance.",
        "She had to ruthlessly prioritize and build a strong support system to raise her daughters while leading a global company.",
    ]},
    {"name": "Kathryn Finney, founder of digitalundivided", "lines": [
        "She founded a pioneering lifestyle blog in the early 2000s while working full-time as an epidemiologist.",
        "She later sold it and founded digitalundivided to champion Black and Latina women entrepreneurs.",
    ]},
    {"name": "Reshma Saujani, founder of Girls Who Code", "lines": [
        "She ran for US Congress and lost.",
        "Instead of quitting, she used that exact failure to found Girls Who Code, which has taught over half a million girls to program.",
    ]},
    {"name": "Ruth Bader Ginsburg", "lines": [
        "She went to law school with a 14-month-old baby, managing the Harvard Law Review while her husband battled cancer.",
        "She still tied for first in her class.",
    ]},
    {"name": "Shonda Rhimes, creator of Grey's Anatomy and Bridgerton", "lines": [
        "She adopted her first daughter as a single working woman while building a television empire.",
        "She openly says she relies on a village and never pretends to balance it perfectly.",
    ]},
    {"name": "Serena Williams", "lines": [
        "She won the 2017 Australian Open while eight weeks pregnant.",
        "She returned to professional tennis after childbirth, showing the physical resilience of mothers.",
    ]},
    {"name": "Joy Mangano, inventor of the Miracle Mop", "lines": [
        "As a divorced working mother of three, she invented the Miracle Mop in her father's auto body shop.",
        "She sold 18,000 mops in 20 minutes on QVC, turning her practical mom-hack into a business empire.",
    ]},
    {"name": "J.K. Rowling, author of Harry Potter", "lines": [
        "Before writing Harry Potter, she was a single mother relying on state benefits.",
        "She wrote her early drafts in cafes while her baby slept in a stroller beside her.",
    ]},
]

# ---------------------------------------------------------------------------
# Practical tips content (used ~1 in 3 non-spotlight posts).
# Each entry: theme (for hashtags/affiliate matching), hook, and a short
# punchy list of tips. Kept to 3 tips max - long tip lists run the video
# length past the point where retention clears the algorithm's watch-time
# gate.
# ---------------------------------------------------------------------------
TIP_CONTENT = [
    {"theme": "time_management", "hook": "3 time hacks that saved my sanity as a working mom:", "tips": [
        "Batch-cook Sunday night, eat off it all week.",
        "Lay out clothes the night before - yours and theirs.",
        "Block 15 minutes each morning for exactly nothing.",
    ]},
    {"theme": "morning_guilt", "hook": "3 things that made our mornings feel less rushed:", "tips": [
        "Backpacks and shoes live by the door, always.",
        "One 'transition song' plays every morning - it's the 5-minute warning.",
        "We say goodbye the same way, every time. Predictability calms everyone down.",
    ]},
    {"theme": "exhaustion_relief", "hook": "3 tiny resets when you're running on empty:", "tips": [
        "Sit in the car for 60 seconds before you go inside. Just breathe.",
        "Keep a 'good enough' dinner on standby - cereal counts.",
        "Say the hard thing out loud to one person. You don't have to carry it silently.",
    ]},
    {"theme": "self_care_permission", "hook": "3 five-minute acts of self-care that actually fit real life:", "tips": [
        "Drink the coffee while it's hot, even if the dishes wait.",
        "Lock the bathroom door. Two minutes is allowed to be yours.",
        "Say no to one thing this week that isn't actually required.",
    ]},
    {"theme": "career_confidence", "hook": "3 phrases that help me sound confident, even when I don't feel it:", "tips": [
        "'Let me follow up on that by end of day' - buys you thinking time.",
        "'Here's what I'd recommend' - said plainly, no apology attached.",
        "'I can't take that on right now' - a full sentence, no explanation owed.",
    ]},
]

# ---------------------------------------------------------------------------
# Warm check-in / support content (used on alternating "regular" slots
# instead of a template affirmation, so not everything is a mantra).
# ---------------------------------------------------------------------------
SUPPORT_CONTENT = [
    {"theme": "asking_for_help", "hook": "If you need a safe space to vent, this is it.", "lines": [
        "Millions of working moms are balancing the exact same things you are, right now.",
        "You don't have to carry the mental load by yourself. It's okay to say that out loud.",
    ]},
    {"theme": "letting_go_of_perfect", "hook": "Give yourself permission to lower the bar today.", "lines": [
        "A happy mom matters infinitely more than a perfectly clean house.",
        "You made the best decisions you could with the energy and time you had.",
    ]},
    {"theme": "identity_beyond_mom", "hook": "You are so much more than just somebody's mother.", "lines": [
        "It's okay to miss the version of you that existed before kids.",
        "Wanting something just for yourself doesn't make you any less devoted to them.",
    ]},
    {"theme": "exhaustion_relief", "hook": "It's completely okay to feel overwhelmed.", "lines": [
        "Give yourself the same grace and kindness you endlessly pour into your kids.",
        "Resting isn't a sign of weakness. It's how you keep taking care of the people you love.",
    ]},
    {"theme": "morning_guilt", "hook": "That guilty feeling from this morning? Let it go.", "lines": [
        "That conflict you feel just shows how deeply you care.",
        "Your kids don't need a mom who never leaves. They need one who always comes back.",
    ]},
]

# ---------------------------------------------------------------------------
# Humor content (light, kind, self-deprecating - never mean-spirited).
# Used to add variety and personality; humor consistently drives shares
# and comments, both of which are meaningful algorithmic signals.
# ---------------------------------------------------------------------------
HUMOR_CONTENT = [
    {"theme": "exhaustion_relief", "hook": "Things I've said with 100% confidence while holding a toddler and a laptop:",
     "lines": [
        "'Yes, I'm on mute.' (I was not on mute.)",
        "'Sorry, can you repeat that?' (I have not been listening for four minutes.)",
        "'One sec, my kid just-' the kid has, in fact, just.",
    ]},
    {"theme": "letting_go_of_perfect", "hook": "Working mom achievements nobody's giving out medals for:",
     "lines": [
        "Answered an email and buttered toast at the same time. Simultaneously. With one hand.",
        "Attended a meeting with a sticker on my forehead and found out an hour later.",
        "Successfully pretended the WiFi cut out during a question I didn't want to answer.",
    ]},
    {"theme": "morning_guilt", "hook": "My toddler's negotiation tactics could run a Fortune 500 company:",
     "lines": [
        "'One more show' somehow means four more shows.",
        "The shoes he refused to wear are suddenly his favorite shoes the moment we're out the door.",
        "He will eat literally anything, as long as it is not what's currently on his plate.",
    ]},
]

# ---------------------------------------------------------------------------
# Myth-bust content - short factual/reassuring corrections framed kindly.
# Deliberately general and non-clinical (no specific studies cited, since
# this content isn't fact-checked against a citation) - the goal is honest
# reassurance, not medical/psychological claims.
# ---------------------------------------------------------------------------
MYTH_BUST_CONTENT = [
    {"theme": "asking_for_help", "hook": "Myth: good moms never need help.", "lines": [
        "Truth: every mom in history has relied on someone else - a partner, a parent, a friend, a village.",
        "Needing support isn't a parenting failure. It's how humans have always raised kids.",
    ]},
    {"theme": "morning_guilt", "hook": "Myth: your kids will remember every rushed goodbye.", "lines": [
        "Truth: kids remember warmth and consistency, not the exact pace of a Tuesday morning.",
        "One chaotic drop-off doesn't undo a childhood of being loved.",
    ]},
    {"theme": "letting_go_of_perfect", "hook": "Myth: a good mom has it all figured out.", "lines": [
        "Truth: nobody has it all figured out. The moms who look like they do are just better at hiding the chaos.",
        "You're not behind. You're just seeing everyone else's highlight reel.",
    ]},
]

# ---------------------------------------------------------------------------
# Quick hack demo content - a single, very concrete tip delivered fast.
# ---------------------------------------------------------------------------
HACK_DEMO_CONTENT = [
    {"theme": "time_management", "hook": "The one hack that fixed our chaotic mornings:", "lines": [
        "A cheap over-the-door shoe organizer by the entryway - one pocket per kid, snacks and essentials pre-packed the night before.",
        "No more searching for anything at 7:45 AM.",
    ]},
    {"theme": "self_care_permission", "hook": "The 10-minute rule that protects my sanity:", "lines": [
        "Every night, I get 10 minutes that are just mine - no phone, no chores, just sitting.",
        "It sounds tiny. It changed everything.",
    ]},
]

# ---------------------------------------------------------------------------
# "This or that" - a light engagement format that genuinely invites a
# comment rather than faking a giveaway. Comments are a strong 2026 Shorts
# ranking signal.
# ---------------------------------------------------------------------------
THIS_OR_THAT_CONTENT = [
    {"theme": "exhaustion_relief", "hook": "Working mom this-or-that:", "lines": [
        "Coffee before drop-off, or coffee after drop-off?",
        "Comment your answer - I need to know I'm not the only 'after' person.",
    ]},
    {"theme": "time_management", "hook": "Working mom this-or-that:", "lines": [
        "Meal prep Sunday, or wing it every single day?",
        "No judgment either way. Just curious what camp you're in.",
    ]},
]

# ---------------------------------------------------------------------------
# Affiliate content
# ---------------------------------------------------------------------------
AMAZON_KEYWORDS = {
    "morning_guilt": "working mom guilt books mindfulness journal daily affirmations",
    "time_management": "time blocking planner for moms",
    "exhaustion_relief": "energy support self care gifts for tired moms",
    "self_care_permission": "self care gift set for moms",
    "asking_for_help": "mental load planner for moms",
    "letting_go_of_perfect": "cozy loungewear for moms",
    "career_confidence": "work bag for working moms",
    "identity_beyond_mom": "journal for moms",
    "spotlight": "inspiring books for working women",
    "default": "working mom essentials daily organization tools",
}

# Targeted product picks per theme. Each value is a LIST of {label, asin} so
# amazon_link_for_theme() can rotate between a few options instead of
# hammering the same one every time. IMPORTANT: these ASINs are illustrative
# placeholders - swap in products you've actually vetted before relying on
# this for income; don't trust ASINs from an LLM as verified/current.
SPECIFIC_PRODUCTS = {
    # Intentionally left for you to fill in with real, vetted products.
    # Example shape:
    # "time_management": [
    #     {"label": "Weekly family planner", "asin": "REPLACE_WITH_REAL_ASIN"},
    # ],
}
