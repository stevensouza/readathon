"""
Scoreboards (Feature 39): data for the Daily Scoreboard and Prize Scoreboard pages.

Every figure comes from the existing ReportGenerator methods, "as of" a contest day:
- Day N is the Nth date uploaded to Daily_Logs (skipped weekends never appear).
- Reading data (minutes, participation, goals, color bonus) counts through day N; the
  latest day counts the whole contest, so it matches the Reports page exactly.
- Money comes from the Reader_Cumulative_History snapshot saved for day N. A day without
  a snapshot shows "Not available*" and wins no trophy.
See docs/features/feature-39-scoreboards.md and md/RULES.md (Scoreboards).
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from queries import (SELECT_DISTINCT_GRADE_LEVELS, SELECT_DISTINCT_TEAM_NAMES,
                     SELECT_TEACHERS_WITH_MULTIPLE_CLASSES, get_db_comparison_school_participation)

GRADE_LABELS = {'K': 'Kindergarten', '1': '1st Grade', '2': '2nd Grade', '3': '3rd Grade',
                '4': '4th Grade', '5': '5th Grade'}

# Prize wording the reports don't carry (design doc); the rest comes from each report's note
TEAM_PARTICIPATION_PRIZE = "losing team's captain does something silly"
GOAL_GETTER_PRIZE = 'A book for every Goal Getter'

NOT_AVAILABLE = 'Not available*'


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def format_grade_label(grade: str) -> str:
    """'K' -> 'Kindergarten', '1' -> '1st Grade'; unknown values -> '{grade} Grade'"""
    return GRADE_LABELS.get(str(grade), f'{grade} Grade')


def grade_sort_key(grade: str):
    """Kindergarten first, then numeric grades"""
    return (0, 0) if str(grade).upper() == 'K' else (1, int(grade)) if str(grade).isdigit() else (2, str(grade))


def team_display_name(team_name: str) -> str:
    """Team names come from the data; show them with the first letter capitalized"""
    return team_name[:1].upper() + team_name[1:]


def display_name(name: str) -> str:
    """Names are stored lowercase: 'mary o'neil-smith' -> 'Mary O'Neil-Smith'"""
    return re.sub(r"(^|[\s\-'])([a-z])", lambda m: m.group(1) + m.group(2).upper(), name or '')


def pct(value: Optional[float], decimals: int = 1) -> str:
    return f'{value:.{decimals}f}%' if value is not None else NOT_AVAILABLE


def money(value: Optional[float]) -> str:
    return f'${value:,.0f}' if value is not None else NOT_AVAILABLE


def last_name_key(name: str):
    """Sort 'First Last' names by last name, like a printed list"""
    parts = name.split()
    return (parts[-1].lower() if parts else '', name.lower())


def prize_text(note: Optional[str]) -> str:
    """'Prize: Book Store $25 Gift Card per grade level' -> 'Book Store $25 Gift Card'"""
    text = (note or '').replace('Prize:', '').strip()
    text = text.split('. ')[0].replace(' per grade level', '').strip()
    return text.rstrip('.')


def leaders(values: Dict[str, Optional[float]]) -> set:
    """Keys holding the highest value (all of them on a tie); nobody wins if any value is missing"""
    if not values or any(v is None for v in values.values()):
        return set()
    best = max(values.values())
    return {k for k, v in values.items() if v == best}


# ---------------------------------------------------------------------------
# Contest calendar
# ---------------------------------------------------------------------------

def contest_calendar(db, requested_day: Optional[int], contest_days_setting: int) -> Dict[str, Any]:
    """Day N <-> date mapping for the "As of" picker.

    total_days is the planned contest length (setting), never less than the days uploaded.
    """
    dates = sorted(db.get_all_dates())
    total_days = max(contest_days_setting, len(dates))
    if not dates:
        return {'dates': [], 'day': None, 'total_days': total_days, 'options': []}

    day = requested_day if requested_day and 1 <= requested_day <= len(dates) else len(dates)
    date = dates[day - 1]
    is_latest = day == len(dates)
    options = []
    for n, d in enumerate(dates, start=1):
        label = datetime.strptime(d, '%Y-%m-%d').strftime('%a %b %-d')
        options.append({'day': n, 'label': f"Day {n} — {label}{' (latest)' if n == len(dates) else ''}"})
    parsed = datetime.strptime(date, '%Y-%m-%d')
    return {
        'dates': dates,
        'day': day,
        'date': date,
        'previous_date': dates[day - 2] if day > 1 else None,
        'is_latest': is_latest,
        # Reading queries: latest day = whole contest (identical to the Reports page)
        'reading_as_of': None if is_latest else date,
        'total_days': total_days,
        'date_long': parsed.strftime('%B %-d, %Y'),
        'date_short': parsed.strftime('%b %-d'),
        'options': options,
    }


def event_year(db_info: Optional[Dict[str, Any]], calendar: Dict[str, Any]) -> Optional[int]:
    """Event year: from the registry, else from the first contest date (e.g. the sample database)"""
    if db_info and db_info.get('year'):
        return int(db_info['year'])
    if calendar['dates']:
        return int(calendar['dates'][0][:4])
    return None


def masthead(settings: Dict[str, str], year: Optional[int], calendar: Dict[str, Any]) -> Dict[str, Any]:
    school = settings.get('school_name', '').strip()
    return {
        'title': f'{school} Read-a-Thon' if school else 'Read-a-Thon',
        'year': year or '',
        'calendar': calendar,
        'generated': datetime.now().strftime('%b %-d, %Y'),
    }


# ---------------------------------------------------------------------------
# Shared sections
# ---------------------------------------------------------------------------

def team_sides(reports) -> List[Dict[str, str]]:
    """The two teams in alphabetical order: first = navy (blue), second = gold (md/RULES.md)"""
    names = sorted(r['team_name'] for r in reports.db.execute_query(SELECT_DISTINCT_TEAM_NAMES))
    if len(names) != 2:
        return []
    return [{'team_name': names[0], 'label': f'Team {team_display_name(names[0])}', 'css': 'team-blue', 'icon': 'bi-shield-fill'},
            {'team_name': names[1], 'label': f'Team {team_display_name(names[1])}', 'css': 'team-gold', 'icon': 'bi-stars'}]


def class_label(row: Dict[str, Any], multi_class_teachers: set) -> str:
    """How a class is named on the scoreboards: its teacher, plus the session if the class has one.

    Class prizes are decided per class (class_name). Half-day kindergarten classes are named
    '<teacher> am' / '<teacher> pm' and show as 'Smith AM' (as on the 2025 prize slides).
    A teacher with more than one class that doesn't follow that pattern gets the class name.
    """
    teacher = display_name(row['teacher_name'])
    class_name = row['class_name']
    if class_name.lower().startswith(row['teacher_name'].lower()):
        suffix = class_name[len(row['teacher_name']):].strip()
        return f'{teacher} {suffix.upper()}' if suffix else teacher
    if row['teacher_name'] in multi_class_teachers:
        return f'{teacher} ({class_name})'
    return teacher


def multi_class_teachers(reports) -> set:
    return {r['teacher_name'] for r in reports.db.execute_query(SELECT_TEACHERS_WITH_MULTIPLE_CLASSES)}


def prior_year_final_note(prior_year: int, prior_final_money: Optional[float], prior_snapshot_count: int,
                          day: int) -> str:
    """Footnote for a prior-year money value that isn't available for day N"""
    if prior_snapshot_count <= 1:
        note = f'* {prior_year} only kept final fundraising totals, not day-by-day amounts.'
    else:
        note = f'* {prior_year} has no saved fundraising total for Day {day}.'
    if prior_final_money is not None:
        note += f' {prior_year} finished with {money(prior_final_money)} raised.'
    return note


def build_showdown(reports, prior_reports, year: int, calendar: Dict[str, Any], final: bool) -> Optional[Dict[str, Any]]:
    """This year vs last year, whole school: Day N vs the prior year's Day N (final vs final at the end).

    Participation = average daily participation incl. color bonus (same as the team card).
    """
    if prior_reports is None:
        return None
    prior_dates = sorted(prior_reports.db.get_all_dates())
    if not prior_dates:
        return None
    prior_year = year - 1
    day = calendar['day']

    # Prior year's own Nth contest date (same mapping as the database comparison page)
    prior_day = len(prior_dates) if final else min(day, len(prior_dates))
    prior_date = prior_dates[prior_day - 1]
    prior_as_of = None if prior_day == len(prior_dates) else prior_date

    now = reports.school_totals_as_of(calendar['reading_as_of'], calendar['date'])
    past = prior_reports.school_totals_as_of(prior_as_of, prior_date)

    rows = []
    notes = []
    for key, label, fmt in [('participation', 'Participation', pct),
                            ('minutes', 'Minutes Read', lambda v: f'{v:,}'),
                            ('donations', 'Money Raised', money)]:
        winners = leaders({'now': now[key], 'past': past[key]})
        rows.append({'label': label,
                     'now': fmt(now[key]), 'now_na': now[key] is None, 'now_trophy': 'now' in winners,
                     'past': fmt(past[key]), 'past_na': past[key] is None, 'past_trophy': 'past' in winners})

    if past['donations'] is None:
        prior_snapshots = prior_reports.db.get_snapshot_dates()
        prior_final = prior_reports.school_totals_as_of(None, prior_snapshots[-1])['donations'] if prior_snapshots else None
        notes.append(prior_year_final_note(prior_year, prior_final, len(prior_snapshots), day))
    if now['donations'] is None:
        notes.append(f'* No fundraising total was saved for {year} Day {day} (upload the cumulative file with that snapshot date).')

    return {'year': year, 'prior_year': prior_year, 'day': day, 'final': final, 'rows': rows, 'notes': notes}


# ---------------------------------------------------------------------------
# Daily Scoreboard
# ---------------------------------------------------------------------------

def build_daily_scoreboard(reports, calendar: Dict[str, Any], drawing_number: int,
                           prior_reports=None, year: Optional[int] = None) -> Dict[str, Any]:
    """Everything the Daily Scoreboard shows for contest day calendar['day']"""
    db = reports.db
    date, as_of = calendar['date'], calendar['reading_as_of']

    # Medallion: % of students who read (minutes > 0) at least one day so far
    medallion = db.execute_query(get_db_comparison_school_participation(as_of or 'all'))[0]['participation_pct'] or 0

    # Students: seeded daily drawing (same winners for the same date + drawing #)
    drawing = reports.q4_prize_drawing(date, drawing_number)['data']
    by_grade = {w['grade_level']: w for w in drawing}
    grades = sorted({r['grade_level'] for r in db.execute_query(SELECT_DISTINCT_GRADE_LEVELS)}, key=grade_sort_key)
    winners = [{'grade': format_grade_label(g),
                'student_name': display_name(by_grade[g]['student_name']) if g in by_grade else None} for g in grades]

    # Classes: highest avg participation (with color) per grade; school-wide leader(s) tagged
    teachers = multi_class_teachers(reports)
    school_top = {r['class_name'] for r in reports.q13_overall_best_class_simplified(as_of)['data']}
    classes = [{'grade': format_grade_label(r['grade_level']),
                'class_label': class_label(r, teachers),
                'participation': pct(r['avg_participation_rate_with_color']),
                'school_top': r['class_name'] in school_top}
               for r in sorted(reports.q18_lead_class_by_grade(as_of)['data'],
                               key=lambda r: (grade_sort_key(r['grade_level']), r['class_name']))]

    # Teams: cumulative with "today" figures
    sides = team_sides(reports)
    teams = None
    money_note = None
    if sides:
        participation = {r['team_name']: r['avg_participation_rate_with_color'] for r in reports.q14_team_participation(as_of)['data']}
        minutes = {r['team_name']: r['total_minutes_with_color'] for r in reports.q19_team_minutes(as_of)['data'] if r['team_name'] != 'TOTAL'}
        donations_report = reports.q20_team_donations(date)
        donations = ({r['team_name']: r['total_donations'] for r in donations_report['data']}
                     if donations_report['available'] else {s['team_name']: None for s in sides})
        today = reports.team_day_figures(date, calendar['previous_date'])
        names = [s['team_name'] for s in sides]
        won = {'participation': leaders({t: participation.get(t) for t in names}),
               'minutes': leaders({t: minutes.get(t) for t in names}),
               'donations': leaders({t: donations.get(t) for t in names})}
        teams = []
        for side in sides:
            t = side['team_name']
            day_figures = today.get(t, {})
            added = day_figures.get('donations_added')
            teams.append({**side, 'rows': [
                {'label': 'Participation', 'value': pct(participation.get(t)), 'na': participation.get(t) is None,
                 'delta': f"{day_figures.get('participation', 0):.0f}% today", 'trophy': t in won['participation']},
                {'label': 'Minutes Read', 'value': f"{minutes.get(t, 0):,}", 'na': False,
                 'delta': f"+{day_figures.get('minutes', 0):,} today", 'trophy': t in won['minutes']},
                {'label': 'Money Raised', 'value': money(donations.get(t)), 'na': donations.get(t) is None,
                 'delta': f'+{money(added)} today' if added is not None else None, 'trophy': t in won['donations']},
            ]})
        if not donations_report['available']:
            money_note = f'* No fundraising total was saved for Day {calendar["day"]} (upload the cumulative file with that snapshot date).'

    return {
        'medallion': f'{medallion:.0f}%',
        'drawing_number': drawing_number,
        'winners': winners,
        'classes': classes,
        'teams': teams,
        'teams_money_note': money_note,
        'showdown': build_showdown(reports, prior_reports, year, calendar, final=False) if year else None,
    }


# ---------------------------------------------------------------------------
# Prize Scoreboard
# ---------------------------------------------------------------------------

def _student_cell(rows: List[Dict[str, Any]], value_key: str, fmt, available: bool = True) -> Dict[str, Any]:
    """Winners for one grade/prize: every tied student is listed"""
    if not available:
        return {'names': [], 'display_names': [], 'value': NOT_AVAILABLE, 'na': True, 'tie': 0}
    if not rows:
        return {'names': [], 'display_names': [], 'value': '—', 'na': False, 'tie': 0}
    names = sorted((r['student_name'] for r in rows), key=last_name_key)
    return {'names': names, 'display_names': [display_name(n) for n in names],
            'value': fmt(rows[0][value_key]), 'na': False, 'tie': len(names) if len(names) > 1 else 0}


def build_prize_scoreboard(reports, calendar: Dict[str, Any], prior_reports=None,
                           year: Optional[int] = None) -> Dict[str, Any]:
    """Everything the Prize Scoreboard shows, as of calendar['day'] (final once the last day is reached)"""
    db = reports.db
    date, as_of = calendar['date'], calendar['reading_as_of']
    final = calendar['day'] >= calendar['total_days']
    prize_winners = set()
    notes = []

    # 1. Teams: Team Participation + Top Student Earner
    sides = team_sides(reports)
    teams = None
    earner_report = reports.q16_top_earner_per_team(date)
    if sides:
        participation = {r['team_name']: r['avg_participation_rate_with_color'] for r in reports.q14_team_participation(as_of)['data']}
        won = leaders({s['team_name']: participation.get(s['team_name']) for s in sides})
        teams = []
        for side in sides:
            t = side['team_name']
            earners = [r for r in earner_report['data'] if r['team_name'] == t]
            prize_winners.update(r['student_name'] for r in earners)
            if not earner_report['available']:
                earner = {'names': [], 'detail': NOT_AVAILABLE, 'na': True}
            elif earners:
                grades = sorted({format_grade_label(r['grade_level']) for r in earners})
                earner = {'names': [display_name(n) for n in sorted((r['student_name'] for r in earners), key=last_name_key)],
                          'detail': f"{', '.join(grades)} · {money(earners[0]['donation_amount'])}", 'na': False}
            else:
                earner = {'names': [], 'detail': '—', 'na': False}
            teams.append({**side, 'participation': pct(participation.get(t)), 'participation_trophy': t in won,
                          'earner': earner})
        if not earner_report['available']:
            notes.append(f'* No fundraising total was saved for Day {calendar["day"]} (upload the cumulative file with that snapshot date).')

    # 2. Classes: Highest Class Participation (all tied classes win) + Grade Level Participation
    teachers = multi_class_teachers(reports)
    best_class = reports.q13_overall_best_class_simplified(as_of)
    spotlight = [{'class_label': class_label(r, teachers), 'grade': format_grade_label(r['grade_level']),
                  'participation': pct(r['avg_participation_rate_with_color'])} for r in best_class['data']]
    grade_level = reports.q12_best_class_by_grade_simplified(as_of)
    grade_rows = [{'grade': format_grade_label(r['grade_level']), 'class_label': class_label(r, teachers),
                   'participation': pct(r['avg_participation_rate_with_color'])}
                  for r in sorted(grade_level['data'], key=lambda r: (grade_sort_key(r['grade_level']), r['class_name']))]

    # 3. Students: Top Minutes / Donations / Sponsors per grade (ties all win)
    minutes_report = reports.q10_most_minutes_by_grade(as_of)
    donations_report = reports.q9_most_donations_by_grade(date)
    sponsors_report = reports.q11_most_sponsors_by_grade(date)
    grades = sorted({r['grade_level'] for r in db.execute_query(SELECT_DISTINCT_GRADE_LEVELS)}, key=grade_sort_key)

    def rows_for(report, grade):
        return [r for r in report['data'] if r['grade_level'] == grade]

    students = []
    for g in grades:
        cells = [_student_cell(rows_for(minutes_report, g), 'total_minutes_capped', lambda v: f'{v:,} min'),
                 _student_cell(rows_for(donations_report, g), 'donation_amount', money, donations_report['available']),
                 _student_cell(rows_for(sponsors_report, g), 'sponsor_count', lambda v: f'{v:,} sponsors', sponsors_report['available'])]
        for cell in cells:
            prize_winners.update(cell['names'])
        students.append({'grade': format_grade_label(g), 'cells': cells})
    if not donations_report['available'] and not notes:
        notes.append(f'* No fundraising total was saved for Day {calendar["day"]} (upload the cumulative file with that snapshot date).')

    # 5. Goal Getters: met the grade goal every day so far
    goal_rows = reports.q15_goal_getters(as_of)['data']
    goal_getters = []
    for g in grades:
        names = sorted((r['student_name'] for r in goal_rows if r['grade_level'] == g), key=last_name_key)
        if names:
            goal_getters.append({'grade': format_grade_label(g), 'names': [display_name(n) for n in names],
                                 'rows': -(-len(names) // 6)})  # names run down 6 columns
    prize_winners.update(r['student_name'] for r in goal_rows)

    return {
        'final': final,
        'medallion': len(prize_winners),
        'teams': teams,
        'team_prizes': [f'Team Participation: {TEAM_PARTICIPATION_PRIZE}',
                        f"Top Student Earner: {prize_text(earner_report['note'])}"],
        'spotlight': spotlight,
        'spotlight_prize': prize_text(best_class['note']),
        'grade_rows': grade_rows,
        'grade_prize': prize_text(grade_level['note']),
        'students': students,
        'student_prizes': [prize_text(minutes_report['note']), prize_text(donations_report['note']),
                           prize_text(sponsors_report['note'])],
        'goal_getters': goal_getters,
        'goal_getter_total': len(goal_rows),
        'goal_getter_prize': GOAL_GETTER_PRIZE,
        'notes': notes,
        'showdown': build_showdown(reports, prior_reports, year, calendar, final=final) if year else None,
    }
