# config.py
import random
import urllib.parse

# Broad discovery tags for general reach
HASHTAGS = [
    "#workingmom", "#momlife", "#workingmother", "#motherhood", "#momsupport", 
    "#workingmomlife", "#momhacks", "#parenting", "#momcommunity", "#motherhoodunplugged"
]
FALLBACK_TAG = "#workingmom"
# Supported video content categories/themes
THEMES = ["affirmation", "tips", "spotlight"]

TIP_TAG = "tips"

# Weighting configuration for the content calendar/scheduler
CALENDAR_THEME_BOOST = {
    "affirmation": 0.4,
    "tips": 0.4,
    "spotlight": 0.2
}

# Theme-specific tags for search intent
THEME_HASHTAGS = {
    "affirmation": ["#momquotes", "#dailyaffirmations", "#mindfulmama", "#momencouragement", "#wordsofaffirmation"],
    "tips": ["#momtips", "#workingmomtips", "#lifehacks", "#timemanagement", "#momhack"],
    "spotlight": ["#womensupportingwomen", "#realwomen", "#inspiringwomen", "#workingwomen", "#womeninbusiness"]
}

# Core search/discovery keywords required by the pipeline
VIDEO_KEYWORDS = ["parenting", "mom life", "shorts", "family", "working mom"]

def build_hashtags(theme=None, count=4):
    """
    Combines general hashtags and theme-specific hashtags.
    Returns a space-separated string of ordered, unique hashtags.
    """
    tags = list(HASHTAGS)
    if theme and theme in THEME_HASHTAGS:
        tags.extend(THEME_HASHTAGS[theme])
    
    # dict.fromkeys() removes duplicates while preserving the exact priority order
    unique_tags = list(dict.fromkeys(tags))
    return " ".join(unique_tags[:count])

def top_title_hashtags():
    """
    Returns a short string of high-leverage hashtags for video titles.
    """
    return "#workingmom #momlife"

def get_safe_content(pool, used_list):
    """
    Safely selects an item from a content pool. If all items have been used,
    it resets the tracking list to prevent empty pool index crashes.
    """
    # Guard against completely empty pools to prevent fatal crashes
    if not pool:
        return ""

    available = [item for item in pool if item not in used_list]
    
    if not available:
        used_list.clear()
        available = pool
        
    selected = random.choice(available)
    used_list.append(selected)
    return selected

def get_normalized_weights(custom_boosts=None):
    """
    Safely normalizes theme weights to ensure they sum to exactly 1.0
    and contain no negative numbers, preventing random.choices() crashes.
    """
    target_boosts = custom_boosts if custom_boosts is not None else CALENDAR_THEME_BOOST
    
    # Ensure no negative weights exist
    sanitized = {k: max(0.0, float(v)) for k, v in target_boosts.items()}
    total = sum(sanitized.values())
    
    # Fallback to equal distribution if all weights are zero
    if total == 0:
        return {k: 1.0 / len(sanitized) for k in sanitized}
        
    return {k: v / total for k, v in sanitized.items()}

def get_encoded_keywords():
    """
    Returns a list of safely URL-encoded keywords to prevent multi-word 
    space characters from breaking external stock footage API requests.
    """
    return [urllib.parse.quote(kw) for kw in VIDEO_KEYWORDS]

# Consistent persona tagline appended to every video
TAGLINE = "You're doing better than you think. Follow for your daily working mom support."

# Expanded pool of hooks (Openers)
OPENERS = [
    "To the working mom who feels like she's dropping all the balls today...",
    "If you were up at 3 AM with a baby and still had to log in at 8 AM...",
    "A quick reminder for the mom running on dry shampoo and cold coffee...",
    "To the mom managing a toddler's meltdown while trying to answer work emails...",
    "Stop scrolling for just a second. I need you to hear this.",
    "If you're feeling guilty about working today, listen to this.",
    "For the mom who feels like she's failing at work and at home...",
    "Take a deep breath. This message is exactly for you today.",
    "To the mom who is constantly exhausted but keeps showing up with so much love...",
    "Here is your daily reminder that you are exactly what your kids need.",
    "If you're trying to balance spreadsheets and a teething baby on your hip...",
    "For the working mama who just survived the bedtime chaos of a baby and a toddler...",
    "Hey mama, pause for a second. You really need to hear this.",
    "To the mom doing the chaotic daycare drop-off dash this morning...",
    "If you are feeling completely touched-out and overwhelmed right now...",
    "For the mom who cried in her car before walking into the office today...",
    "To the woman trying to give 100 percent to her boss and 100 percent to her kids...",
    "If your to-do list is longer than your energy span today...",
    "To the mama hiding in the bathroom for two minutes of absolute peace...",
    "If your coffee has been reheated three times already today..."
]

# Expanded pool of core messages (Affirmations)
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
    "Your baby's smile and your toddler's laugh are proof that you are getting the most important things exactly right.",
    "Even on the days you feel you are failing, your kids look at you and see a superhero.",
    "You are so deeply loved, needed, and appreciated, even when the little ones can't say it yet."
]

# Expanded pool of sign-offs (Closers)
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
    "Leave a heart in the comments if you needed this today."
]

# Fact-checked real-women spotlight bank (used every 5th post)
SPOTLIGHT_STORIES = [
    "Did you know Sara Blakely, the founder of Spanx, started her billion-dollar business while selling fax machines door-to-door? She kept her day job for two years while building her empire at night.",
    "Ursula Burns grew up in a low-income housing project and started at Xerox as a summer intern. She worked her way up for 30 years to become the first Black woman CEO of a Fortune 500 company.",
    "Indra Nooyi, former CEO of PepsiCo, spoke openly about the impossibility of perfect balance, admitting she had to ruthlessly prioritize and build a strong support system to raise her daughters while leading a global company.",
    "Kathryn Finney founded a pioneering lifestyle blog in the early 2000s while working as an epidemiologist. She later sold it and founded digitalundivided to champion and fund Black and Latina women entrepreneurs.",
    "Reshma Saujani ran for US Congress and lost spectacularly. Instead of quitting, she used that exact failure to found Girls Who Code, which has now taught over half a million girls to program.",
    "Ruth Bader Ginsburg went to law school with a 14-month-old baby, managing the prestigious Harvard Law Review while her husband battled cancer. She still tied for first in her class.",
    "Shonda Rhimes, the creator of Grey's Anatomy and Bridgerton, adopted her first daughter as a single working woman while building a television empire. She openly says she relies on a village and never pretends to balance it perfectly.",
    "Serena Williams won the 2017 Australian Open while eight weeks pregnant, and returned to professional tennis after childbirth, showing the world the absolute physical resilience of mothers.",
    "Joy Mangano, a divorced working mother of three, invented the Miracle Mop in her father's auto body shop. She sold 18,000 mops in 20 minutes on QVC, turning her practical mom-hack into a massive business empire.",
    "Before writing Harry Potter, J.K. Rowling was a single mother relying on state benefits. She wrote her early drafts in cafes while her baby slept in a stroller beside her, eventually building a literary phenomenon."
]

# Practical productivity, time-management, and life hacks for working moms
TIP_CONTENT = [
    "Prep breakfast the night before. Overnight oats or pre-chopped fruit smoothies save 15 minutes of morning chaos.",
    "Block out the final 15 minutes of your workday to organize tomorrow's tasks. It stops evening mental tracking loops.",
    "Use the 2-minute rule: If a household task takes under two minutes, do it immediately to prevent messy compounding clutter.",
    "Create a hidden WFH 'sick day box' filled with new coloring books and toys to keep kids busy during emergency work calls.",
    "Implement a strict shared family calendar. If an appointment or task isn't logged digitally, it does not exist.",
    "Batch cook your core proteins on Sunday. Pre-shredded chicken or browned beef slashes weekday dinner prep time in half.",
    "Keep a duplicate set of essential device chargers, wipes, and shelf-stable snacks permanently inside your car trunk.",
    "Try a 5-minute 'one-room sweep' before bed. Resetting just the main living space prevents waking up to chaotic clutter.",
    "Say no to non-essential volunteer commitments. Guard your weekend downtime as fiercely as you guard major work deadlines.",
    "Set up automated recurring deliveries for household staples like diapers, wipes, laundry detergent, and trash bags.",
    "Establish a 10-minute quiet transition gap between shutting down your laptop and stepping back into high-energy parenting mode.",
    "Sort your kids' weekly outfits into a 5-compartment hanging closet organizer on Sunday night to eliminate morning wardrobe battles.",
    "Mute personal social notifications and non-urgent group text threads during core deep-work hours to protect your focus.",
    "Use phone voice notes to quickly capture content ideas or grocery list updates while commuting or multitasking.",
    "Pick your outfit and lay out your house keys, work badge, and bags the night before. Morning-you will thank you.",
    "Lower your baseline standard for non-critical chores. The dust can wait; your physical rest and mental peace cannot.",
    "Combine tasks efficiently: listen to professional growth podcasts or audiobooks during your daily commute or laundry runs.",
    "Designate a specific 'drop zone' by the front door for backpacks, shoes, and work bags to prevent last-minute scrambles.",
    "Set firm communication boundaries with your team regarding after-hours emails. Consistency prevents systemic burnout.",
    "Don't carry the load alone. Delegate age-appropriate tasks to toddlers, like putting toys into a basket or discarding trash."
]

# Community messages and emotional support content for the pipeline
SUPPORT_CONTENT = [
    "Remember you are not alone in this journey. Millions of working moms are balancing the same daily struggles right alongside you.",
    "If you need a safe space to vent, drop a comment below. This community stands together, completely free of judgment.",
    "Give yourself permission to lower the bar today. A happy mom matters infinitely more than a perfectly clean house.",
    "Check in on your working mom friends this week. A quick text message can completely turn someone's stressful day around.",
    "It is completely okay to feel overwhelmed. Give yourself the same grace and kindness you endlessly pour into your kids.",
    "You are doing a wonderful job matching your career ambitions with your family goals, even when it feels messy.",
    "Your worth is not defined by how much you checked off your to-do list today. You are enough exactly as you are.",
    "Be proud of how hard you show up every single day. Your kids see your dedication, and it is shaping them beautifully.",
    "If nobody told you today: you are appreciated, you are valued, and the work you do at home and job matters.",
    "Take comfort in knowing that this chaotic phase with a baby and a toddler is temporary. You will make it through.",
    "You don't have to carry the entire mental load by yourself. It is okay to speak up and protect your energy.",
    "Give yourself credit for the million tiny things you handle correctly, instead of focusing on the one thing that went wrong.",
    "It's completely normal to feel torn between work commitments and home life. That conflict just shows how deeply you care.",
    "Resting is not a sign of weakness; it's an essential strategy to help you take care of the people you love most.",
    "Your children don't need a superhero who never makes mistakes. They just need a mom who loves them fiercely.",
    "Let go of the guilt from today. You made the best decisions you could with the energy and time you had.",
    "You are building a secure foundation and a beautiful future for your family through your hard work.",
    "Take a deep breath and let go of external expectations. Run your home and your schedule your own way.",
    "Celebrate your small victories today, whether it was nailing a presentation or surviving a bedtime routine.",
    "You are stronger than you think, more resilient than you know, and doing much better than you realize."
]
