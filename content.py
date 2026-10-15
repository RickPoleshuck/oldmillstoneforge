SITE = {
    "name": "The Old Millstone Forge",
    "tagline": "Preserving the Blacksmith Shop and Museum in Millstone, NJ.",
    "address": ["9 North River Street", "Hillsborough Township", "New Jersey 08844"],
    "email": "info@oldmillstoneforge.org",
    "map_embed": (
        "https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d12134.829960467096"
        "!2d-74.5877766!3d40.5038509!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x89c3c1de08de3ba1"
        "%3A0x8a4bc1a0b3dc63d3!2sOld%20Millstone%20Forge!5e0!3m2!1sen!2sus!4v1690242304213!5m2!1sen!2sus"
    ),

    "calendar_embed": (
        "https://calendar.google.com/calendar/embed?height=600&wkst=1&showTz=0&showCalendars=0"
        # pylint: disable-next=line-too-long
        "&showTitle=0&src=Y18wNGFlYjU0NTQxN2U1ZjBjNjJlZGViYWZmNzNlNTg1MWU4MDg3M2RlYTdmOTMyZWEyMmU5YjMxMGNlMzMxYThhQGdyb3VwLmNhbGVuZGFyLmdvb2dsZS5jb20"
        "&color=%23616161&mode=agenda"
    ),
}

NAV = [
    {'endpoint': 'index', 'label': 'The Forge'},
    {'endpoint': 'about', 'label': 'About Us'},
    {'endpoint': 'donate', 'label': 'Donate'},
    {'endpoint': 'calendar', 'label': 'Calendar'},
    {'endpoint': 'gallery', 'label': 'Gallery'},
    {'endpoint': 'chronicles', 'label': 'Chronicles'},
    {'endpoint': 'signups', 'label': 'Members', 'children': [
        {'endpoint': 'login', 'label': 'Login', 'logged_out_only': True},
        {'endpoint': 'logout', 'label': 'Logout', 'members_only': True},
        {'endpoint': 'signups', 'label': 'Signups', 'members_only': True},
        {'endpoint': 'admin_slots', 'label': 'Admin Slots', 'admin_only': True},
        {'endpoint': 'admin_users', 'label': 'Admin Users', 'admin_only': True},
        {'endpoint': 'admin_chronicles', 'label': 'Admin Chronicles', 'admin_only': True},
        {'endpoint': 'admin_pictures', 'label': 'Admin Pictures', 'admin_only': True},
        {'endpoint': 'admin_history', 'label': 'Admin History', 'admin_only': True},
    ]},
]

HOURS = [("Sunday", "1 to 4 PM")]
EVENTS = ["Journey Through the Past - October 7th and 8th"]

ACTIVITIES = [
    "Promoting the education of industrial life in rural America",
    "Preserving a strong collection of historical tools and techniques",
    "Serving as a source of supplies and parts for other historic sites in Somerset County",
    "Providing training in a unique skillset to those interested",
    "Acting as a social center for the Borough of Millstone",
    "Displaying contributions from individuals, public or private groups for charitable, "
    "educational and historical purposes related to the above.",
]

DONATION_USES = [
    "Maintain the historic building and equipment",
    "Offer educational programs and blacksmithing demonstrations",
    "Keep this rare piece of our heritage accessible for future generations",
]
