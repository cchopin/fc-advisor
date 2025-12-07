"""
FC-Advisor Tags
Functions to manage tags from database
"""

# Default tags to seed the database
DEFAULT_TAGS = {
    'logi_anchor': {
        'name': 'Logi anchor',
        'emoji': '⚓',
        'description': 'The fleet backbone'
    },
    'content_generator': {
        'name': 'Content generator',
        'emoji': '🎬',
        'description': 'Always brings the content'
    },
    'free_burn': {
        'name': 'Free burn pls',
        'emoji': '🔥',
        'description': 'The direct approach'
    },
    'adm_baiter': {
        'name': 'ADM baiter',
        'emoji': '🎣',
        'description': 'Master of strategic baiting'
    },
    'f1_whisperer': {
        'name': 'F1 monkey whisperer',
        'emoji': '🐵',
        'description': 'Clear comms with the fleet'
    },
    'comms_dj': {
        'name': 'Comms DJ',
        'emoji': '🎧',
        'description': 'Good vibes on channel'
    },
    'patience_buddha': {
        'name': 'Patience level: Buddha',
        'emoji': '🧘',
        'description': 'Zen even in chaos'
    },
    'cloak_dagger': {
        'name': 'Cloak & dagger',
        'emoji': '🗡️',
        'description': 'Stealth tactician'
    },
    'micro_gang': {
        'name': 'Micro gang legend',
        'emoji': '⚔️',
        'description': 'Small but deadly'
    },
    'blob_commander': {
        'name': 'Blob commander',
        'emoji': '🌊',
        'description': 'Strength in numbers'
    },
    'exit_cyno': {
        'name': 'Exit cyno hero',
        'emoji': '🚪',
        'description': 'Saves the day with style'
    },
    'doctrine_guru': {
        'name': 'Doctrine guru',
        'emoji': '📚',
        'description': 'Respected theorist'
    },
    'newbro_friendly': {
        'name': 'Newbro friendly',
        'emoji': '🐣',
        'description': 'Patient with beginners'
    },
    'dank_frags': {
        'name': 'Dank frags dealer',
        'emoji': '💎',
        'description': 'Delivers the killmails'
    },
    'tz_warrior': {
        'name': 'Timezone warrior',
        'emoji': '🌍',
        'description': 'Available 24/7'
    },
    'keepstar_killer': {
        'name': 'Keepstar killer',
        'emoji': '💀',
        'description': 'Has dropped the big stuff'
    },
    'capitals_hunter': {
        'name': 'Capitals hunter',
        'emoji': '🦈',
        'description': 'Hunts the big fish'
    },
    'comms_quiet': {
        'name': 'Comms are quiet?',
        'emoji': '🔇',
        'description': 'The legendary radio silence'
    },
    'mist_french': {
        'name': 'Mist is French',
        'emoji': '🇫🇷',
        'description': 'The French touch'
    },
    'spacework': {
        'name': 'Spacework to do',
        'emoji': '🛠️',
        'description': 'Always something to prepare'
    },
    'anchor_up': {
        'name': 'Anchor up!',
        'emoji': '⬆️',
        'description': 'The rallying voice'
    },
    'warp_to_me': {
        'name': 'Warp to me',
        'emoji': '🌀',
        'description': 'The magnetic FC'
    },
    'bubble_wrap': {
        'name': 'Bubble wrap expert',
        'emoji': '🫧',
        'description': 'Master of interdictors'
    },
    'intel_mvp': {
        'name': 'Intel channel MVP',
        'emoji': '📡',
        'description': 'Always in the know'
    },
    'extra_salty': {
        'name': 'Extra salty',
        'emoji': '🧂',
        'description': 'Needs less sodium'
    },
    'first_degree': {
        'name': 'First degree only',
        'emoji': '😐',
        'description': 'Humor.exe not found'
    },
    'pipe_bomber': {
        'name': 'Pipe bomber',
        'emoji': '💣',
        'description': 'Explosive personality'
    },
    'read_motd': {
        'name': 'Read the MOTD',
        'emoji': '📜',
        'description': 'It says everything!'
    },
    'no_catchup': {
        'name': 'No catch up',
        'emoji': '❌',
        'description': 'You snooze, you lose'
    },
    'no_caps': {
        'name': 'No caps in my fleet',
        'emoji': '🚫',
        'description': 'Subcaps only, thank you'
    },
    'qrf_pinger': {
        'name': 'QRF pinger',
        'emoji': '🚨',
        'description': 'Emergency responder'
    },
    'who_is_this': {
        'name': 'Who is this FC?',
        'emoji': '🤷',
        'description': 'New phone who dis'
    },
}


def init_default_tags():
    """Initialize default tags in the database"""
    from app import db
    from app.models import Tag
    
    for tag_id, tag_data in DEFAULT_TAGS.items():
        existing = Tag.query.get(tag_id)
        if not existing:
            tag = Tag(
                id=tag_id,
                name=tag_data['name'],
                emoji=tag_data['emoji'],
                description=tag_data['description'],
                is_active=True
            )
            db.session.add(tag)
    
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()


def get_all_tags():
    """Return all active tags from database"""
    from app.models import Tag
    tags = Tag.query.filter_by(is_active=True).all()
    return {tag.id: tag.to_dict() for tag in tags}


def get_tag(tag_id):
    """Get a specific tag by ID"""
    from app.models import Tag
    tag = Tag.query.get(tag_id)
    if tag and tag.is_active:
        return tag.to_dict()
    return None


def get_random_tags(count=4, exclude=None):
    """Get random active tags for voting"""
    from app.models import Tag
    import random
    
    query = Tag.query.filter_by(is_active=True)
    if exclude:
        query = query.filter(Tag.id.notin_(exclude))
    
    all_tags = query.all()
    count = min(count, len(all_tags))
    
    if count == 0:
        return {}
    
    selected = random.sample(all_tags, count)
    return {tag.id: tag.to_dict() for tag in selected}
