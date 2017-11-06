import os
import argparse
import collections
import random
import zipfile

MIN_SURNAME_COUNT = 100
MIN_FIRST_NAME_COUNT = 5

FirstNameStats = collections.namedtuple('FirstNameStats', ['name', 'gender', 'count'])

"""SurnameStats value definitions
    rank = Rank;
    count = Number of occurrences;
    prop100k = Proportion per 100,000 people for name;
    cum_prop100k = Cumulative proportion per 100,000 people;
    pctwhite = Percent Non-Hispanic White Only;
    pctblack = Percent Non-Hispanic Black Only;
    pctapi = Percent Non-Hispanic Asian and Pacific Islander Only;
    pctaian = Percent Non-Hispanic American Indian and Alaskan Native Only;
    pct2prace = Percent Non-Hispanic of Two or More Races;
    pcthispanic = Percent Hispanic Origin
"""
SurnameStats = collections.namedtuple('SurnameStats', ['name', 'rank', 'count', 'prop100k', 'cum_prop100k', 'pctwhite',
                                                       'pctblack', 'pctapi', 'pctaian', 'pct2prace', 'pcthispanic'])

race_arg_map = {
    'white': 'pctwhite',
    'black': 'pctblack',
    'api': 'pctapi',
    'indian': 'pctaian',
    'hispanic': 'pcthispanic',
    'multi': 'pct2prace',
}


def build_parser():
    argparser = argparse.ArgumentParser(description='Generate people names')
    argparser.add_argument('gender', type=str, help='gender')
    argparser.add_argument('year', type=int, help='year of birth')
    argparser.add_argument('count', type=int, help='number of names to generate')

    argparser.add_argument('--weighted', '-w', dest='weighted', action='store_true')
    argparser.add_argument('--first-initial', '-f', dest='first_initial', type=str, help='first initial')
    argparser.add_argument('--surname-initial', '-s', dest='surname_initial', type=str, help='surname initial')
    argparser.add_argument('--race', '-r', dest='race', type=str, help='race')

    return argparser


def race_percent(surname_stats, race):
    if race in race_arg_map:
        try:
            return float(surname_stats.__getattribute__(race_arg_map[race]))
        except ValueError:
            return 0.0
    else:
        print("No race found for {race}".format(race=race))
        return 1.0


def load_first_names_by_year(year, weighted=False, initial=None):
    first_name_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/first_names_by_year.zip")
    names_zip = zipfile.ZipFile(first_name_file)
    unzipped_filename = 'yob{year}.txt'.format(year=year)

    names = {'male': [], 'female': []}

    for line in names_zip.read(unzipped_filename).splitlines():
        name_stats = FirstNameStats(*line.decode().split(','))
        relative_name_count = int(int(name_stats.count) / MIN_FIRST_NAME_COUNT) if weighted else 1
        gender = 'female' if name_stats.gender == 'F' else 'male'

        if not initial or (initial and name_stats.name.lower().startswith(initial.lower())):
            names[gender] += [name_stats.name for _ in range(relative_name_count)]

    return names


def load_surnames(weighted=False, initial=None, race=None):
    surname_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/surnames_by_race.zip")
    surnames_zip = zipfile.ZipFile(surname_file)

    surnames = []

    for line in surnames_zip.read("app_c.csv").splitlines()[1:]:
        surname_stats = SurnameStats(*line.decode().split(','))
        relative_name_count = int(int(surname_stats.count) / MIN_SURNAME_COUNT) if weighted else 1
        relative_name_count *= race_percent(surname_stats, race) if race else 1

        if not initial or (initial and surname_stats.name.lower().startswith(initial.lower())):
            surnames += [surname_stats.name for _ in range(int(relative_name_count))]

    return surnames


def generate_names(args):
    surnames = load_surnames(weighted=args.weighted, initial=args.surname_initial, race=args.race)
    first_names = load_first_names_by_year(args.year, weighted=args.weighted, initial=args.first_initial)

    for _ in range(args.count):
        first = random.choice(first_names[args.gender])
        last = random.choice(surnames)

        print("{first} {last}".format(first=first.title(), last=last.title()))


if __name__ == "__main__":
    parsed_args = build_parser().parse_args()
    generate_names(parsed_args)
