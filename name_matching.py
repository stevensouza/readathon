"""
Match the reader names in read-a-thon.com uploads to Roster names.

Parents type their child's name on read-a-thon.com, so the daily minutes and comprehensive
readers files contain first names only ("Mateo"), nicknames ("Joey Lambert" for Joseph),
typos and case differences ("Leo McKay" for Leo Mckay). The Teacher column comes from
read-a-thon.com's class list, so it is usually right and narrows the search to one class.

- NameMatcher.resolve() turns an uploaded name + teacher into a roster name for the uploads:
  exact roster name, a saved correction (Name_Alias), or the only roster name that differs just
  in case/spacing. Anything else stays unmatched: saved as "typed name (teacher)" (unmatched_label), with a warning.
- NameMatcher.suggest() ranks likely roster students for an unmatched name, for the Upload
  page's "Match names to the roster" panel. Only a single strong match in the same class, for a student
  with no data of their own in the upload, is a "strong match" (accepted for the user). Strong = same first and
  last name, first name only, a known nickname (NICKNAMES) + same last name, or nearly the same spelling; a guess
  from shared letters ("Sam Lee" for Samuel Lee - or a sibling?) is only a possible match.
See md/RULES.md -> "Roster name matching".
"""

import difflib
import re
import unicodedata
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

TEACHER_TITLES = {'mr', 'mrs', 'ms', 'miss', 'mx', 'dr'}

# Known nicknames: with the same last name these are strong matches. Names that only share letters
# (Ben/Benjamin, Abby/Abigail, Maggie/Margaret) are found by first_names_related() as possible matches.
NICKNAMES = {
    'bill': {'william'}, 'billy': {'william'}, 'will': {'william'}, 'liam': {'william'},
    'bob': {'robert'}, 'bobby': {'robert'}, 'rob': {'robert'}, 'robbie': {'robert'},
    'jack': {'john', 'jackson'}, 'johnny': {'john', 'jonathan'},
    'hank': {'henry'}, 'huck': {'henry'}, 'harry': {'henry', 'harrison'},
    'teddy': {'theodore', 'edward'}, 'ted': {'theodore', 'edward'}, 'ned': {'edward'},
    'chuck': {'charles'}, 'charlie': {'charles', 'charlotte'}, 'lottie': {'charlotte'},
    'peggy': {'margaret'}, 'molly': {'mary', 'margaret'}, 'polly': {'mary'},
    'betsy': {'elizabeth'}, 'betty': {'elizabeth'}, 'beth': {'elizabeth'}, 'libby': {'elizabeth'},
    'liz': {'elizabeth'}, 'lizzie': {'elizabeth'}, 'liza': {'elizabeth', 'eliza'},
    'ellie': {'eleanor', 'elizabeth', 'ellen', 'elena', 'eliana', 'gabrielle'},
    'nell': {'eleanor', 'helen'}, 'nellie': {'eleanor', 'helen'},
    'evie': {'evelyn', 'genevieve', 'eva', 'evangeline'},
    'sadie': {'sarah'}, 'sally': {'sarah'}, 'kate': {'katherine', 'catherine', 'kathryn'},
    'katie': {'katherine', 'catherine', 'kathryn', 'caitlin'}, 'kat': {'katherine', 'catherine'},
    'gabby': {'gabriella', 'gabrielle'}, 'izzy': {'isabel', 'isabella', 'isabelle'},
    'bella': {'isabella', 'arabella'}, 'xander': {'alexander'}, 'sasha': {'alexander', 'alexandra'},
    'drew': {'andrew'}, 'tony': {'anthony'}, 'gus': {'august', 'augustus', 'augustine'},
    'jamie': {'james'}, 'jim': {'james'}, 'jimmy': {'james'}, 'nate': {'nathan', 'nathaniel'},
    'zach': {'zachary'}, 'mikey': {'michael'}, 'ollie': {'oliver', 'olivia'}, 'rosie': {'rose', 'rosalind', 'rosalie'},
}

# Suggestion scores (higher = more likely). A strong match (accepted for the user) needs STRONG or above.
SCORE_SAME_FIRST_AND_LAST = 95   # "Clara Wells" -> "Clara Rose Wells"
SCORE_FIRST_NAME_ONLY = 90       # "Mateo" -> "Mateo Ruiz"
SCORE_NICKNAME_SAME_LAST = 85    # "Teddy Lambert" -> "Theodore Lambert" (known nickname)
SCORE_CLOSE_SPELLING = 80        # "Ethan Brooks" -> "Ethan Brookes"
STRONG = 80
SCORE_LETTERS_SAME_LAST = 70     # "Sam Lee" -> "Samuel Lee" (shared letters only: nickname or a sibling?)
SCORE_NICKNAME_ONLY = 60         # "Ellie" -> "Eleanor Quill"
SCORE_SAME_LAST_ONLY = 55        # "Hudson Brookes" -> "Ethan Brookes" (preferred name, or a sibling?)
SCORE_SOME_SPELLING = 50
OWN_DATA_PENALTY = 30            # the student already has their own data in the upload (maybe another child)
OTHER_CLASS_PENALTY = 35         # the upload names a different teacher
MIN_SCORE = 35                   # lowest score suggested (e.g. a shared-letters guess in another class)
MAX_CANDIDATES = 5


def name_key(name: Optional[str]) -> str:
    """Name for comparing: lowercase, single spaces, no accents ("Zoë" = "Zoe"), no punctuation except - and '
    (a phone's curly apostrophe counts as ')"""
    text = unicodedata.normalize('NFKD', (name or '').replace('\u2019', "'").replace('\u2018', "'"))
    text = ''.join(c for c in text if not unicodedata.combining(c))
    cleaned = re.sub(r"[^a-z0-9' -]", ' ', text.lower())
    return ' '.join(cleaned.split())


def teacher_key(teacher: Optional[str]) -> str:
    """Teacher for comparing: "Mrs. Delgado" and "delgado" are the same teacher"""
    words = re.sub(r'[^a-z0-9 -]', ' ', (teacher or '').lower()).split()
    while len(words) > 1 and words[0] in TEACHER_TITLES:
        words = words[1:]
    return ' '.join(words)


def unmatched_label(typed: str, teacher: Optional[str]) -> str:
    """Name saved for an uploaded name that isn't on the roster: "Ellie (Hart)". Keeps two unmatched
    "Ellie"s from different classes apart, and remembers the class for matching them later."""
    return f"{typed} ({teacher})" if teacher else typed


def split_unmatched_label(saved_name: str) -> Tuple[str, str]:
    """"Ellie (Hart)" -> ("Ellie", "Hart"); a name saved without a teacher -> (name, "")"""
    found = re.match(r'^(.*\S) \(([^()]+)\)$', saved_name or '')
    return (found.group(1), found.group(2)) if found else (saved_name, '')


def known_nickname(typed: str, formal: str) -> bool:
    """Is `typed` `formal` or a nickname of it in NICKNAMES? (lowercase single words)"""
    return typed == formal or typed in NICKNAMES.get(formal, ()) or formal in NICKNAMES.get(typed, ())


def first_names_related(typed: str, formal: str) -> bool:
    """Could `typed` be `formal` or a nickname of it? Known nicknames, or names that share letters
    (lowercase single words)"""
    if known_nickname(typed, formal):
        return True
    return len(typed) >= 2 and len(formal) >= 2 and (typed[:2] == formal[:2]
                                                     or (len(typed) >= 3 and typed in formal))


def _score(typed: str, roster_name: str) -> Tuple[int, str]:
    """How likely the typed name (name_key) is this roster student, with the reason shown to the user"""
    words, roster_words = typed.split(), roster_name.split()
    if not words or not roster_words:
        return 0, ''
    first, roster_first, roster_last = words[0], roster_words[0], roster_words[-1]
    if len(words) == 1:
        if first == roster_first:
            return SCORE_FIRST_NAME_ONLY, 'first name only'
        if first_names_related(first, roster_first):
            return SCORE_NICKNAME_ONLY, 'nickname, first name only'
    else:
        last = words[-1]
        if last == roster_last:
            if first == roster_first:
                return SCORE_SAME_FIRST_AND_LAST, 'same first and last name'
            if known_nickname(first, roster_first):
                return SCORE_NICKNAME_SAME_LAST, 'nickname, same last name'
            if first_names_related(first, roster_first):
                return SCORE_LETTERS_SAME_LAST, 'first name starts the same, same last name (nickname or sibling?)'
            return SCORE_SAME_LAST_ONLY, 'same last name only (preferred name or sibling?)'
    similarity = difflib.SequenceMatcher(None, typed, roster_name).ratio()
    if similarity >= 0.85:
        return SCORE_CLOSE_SPELLING, 'spelled almost the same'
    if similarity >= 0.7:
        return SCORE_SOME_SPELLING, 'similar spelling'
    return 0, ''


class NameMatcher:
    """Roster names and saved corrections for one contest database"""

    def __init__(self, roster: Iterable[Dict[str, Any]], aliases: Iterable[Dict[str, Any]] = ()):
        """roster: dicts with student_name, teacher_name, class_name.
        aliases: Name_Alias rows (name_key, teacher_key, student_name; student_name None = not a student).
        A correction to a student no longer on the roster is ignored (the name is unmatched again)."""
        self.roster = [dict(r) for r in roster]
        self.roster_names = {r['student_name'] for r in self.roster}
        self.by_name_key = defaultdict(list)
        for r in self.roster:
            r['name_key'], r['teacher_key'] = name_key(r['student_name']), teacher_key(r['teacher_name'])
            self.by_name_key[r['name_key']].append(r)
        self.aliases = {(a['name_key'], a['teacher_key']): a['student_name'] for a in aliases
                        if a['student_name'] is None or a['student_name'] in self.roster_names}

    def resolve(self, name: str, teacher: Optional[str]) -> Tuple[Optional[str], str]:
        """Roster name for an uploaded name + teacher, and how it was found:
        'exact', 'alias', 'skip' (saved as not a roster student - don't import), 'normalized'
        (only case/spacing differed) or 'unmatched' (returns the name as typed)"""
        if name in self.roster_names:
            return name, 'exact'
        key, tkey = name_key(name), teacher_key(teacher)
        if (key, tkey) in self.aliases:
            target = self.aliases[(key, tkey)]
            return (target, 'alias') if target else (None, 'skip')
        same_name = self.by_name_key.get(key, [])
        same_class = [r for r in same_name if r['teacher_key'] == tkey]
        for found in (same_class, same_name):
            if len(found) == 1:
                return found[0]['student_name'], 'normalized'
        return name, 'unmatched'

    def resolve_any_teacher(self, name: str, teachers: Iterable[str] = ()) -> Tuple[Optional[str], str]:
        """Like resolve() for saved rows that don't keep the teacher (Daily_Logs): 'ambiguous' when
        saved corrections for this name point to different students, or when one of `teachers` (classes known
        to have uploaded this name) has no correction for it - the row may hold another class's child"""
        if name in self.roster_names:
            return name, 'exact'
        key = name_key(name)
        corrected = {tkey: target for (alias_key, tkey), target in self.aliases.items() if alias_key == key}
        targets = set(corrected.values())
        uncorrected = {teacher_key(t) for t in teachers if t} - set(corrected)
        if len(targets) > 1 or (targets and uncorrected):
            return name, 'ambiguous'
        if targets:
            target = targets.pop()
            return (target, 'alias') if target else (None, 'skip')
        same_name = self.by_name_key.get(key, [])
        return (same_name[0]['student_name'], 'normalized') if len(same_name) == 1 else (name, 'unmatched')

    def suggest(self, name: str, teacher: Optional[str], has_data: Set[str] = frozenset()) -> Dict[str, Any]:
        """Likely roster students for an unmatched name, best first.
        has_data: roster students with their own minutes/money in the upload (less likely to be this child).
        confident = strong match, accepted for the user: the only strong match in the same class, without data of its own."""
        typed, tkey = name_key(name), teacher_key(teacher)
        candidates = []
        for r in self.roster:
            score, reason = _score(typed, r['name_key'])
            if not score:
                continue
            same_class = r['teacher_key'] == tkey
            strong_in_class = same_class and score >= STRONG
            if r['student_name'] in has_data:
                score -= OWN_DATA_PENALTY
                reason += '; already has their own data in this upload'
            if not same_class:
                score -= OTHER_CLASS_PENALTY
                reason += f"; in {r['teacher_name']}'s class, not {teacher or 'the uploaded teacher'}'s"
            if score >= MIN_SCORE:
                candidates.append({'student_name': r['student_name'], 'class_name': r['class_name'],
                                   'teacher_name': r['teacher_name'], 'score': score, 'reason': reason,
                                   'strong_in_class': strong_in_class})
        candidates.sort(key=lambda c: (-c['score'], c['student_name']))
        candidates = candidates[:MAX_CANDIDATES]
        strong = [c for c in candidates if c['strong_in_class']]
        confident = (len(strong) == 1 and strong[0] is candidates[0]
                     and strong[0]['student_name'] not in has_data)
        return {'candidates': candidates,
                'suggestion': candidates[0]['student_name'] if candidates else None,
                'confident': confident}

    def class_students(self, teacher: Optional[str]) -> List[str]:
        """Roster students of the uploaded teacher (all of a teacher's classes, e.g. AM and PM kindergarten)"""
        tkey = teacher_key(teacher)
        return sorted(r['student_name'] for r in self.roster if r['teacher_key'] == tkey)
