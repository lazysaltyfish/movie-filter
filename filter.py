import shutil
import requests
import logging
import argparse
import pprint
import json
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

_parser = argparse.ArgumentParser(description='Move movie to specific directory by file name.')
_parser.add_argument('--token', type=str, required=True, help='TMDB API token.')
_parser.add_argument('--src', type=str, required=True, help='Source directory.')
_parser.add_argument('--dst', type=str, required=True, help='Destination directory.')
_parser.add_argument('--dryrun', type=bool, required=False, default=False, help='Dry run.')

_args = _parser.parse_args()

def move_dir(orig_dir, dest_dir):
    logging.info("Move {} to {}".format(orig_dir, dest_dir))
    if _args.dryrun:
        return True
    real_dst = shutil.move(orig_dir, dest_dir)
    if real_dst:
        return True
    else:
        return False

def is_movie(name: str, year: str):
    headers = {'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.3497.92 Safari/537.36"}

    if len(year) != 4:
        logging.error("Year format error: " + year)
        return False
    name_tag = '{} ({})'.format(name, year)
    logging.info("Search {}".format(name_tag))
    
    URL = r'https://api.themoviedb.org/3/search/movie?api_key={token}&query={name}&year={year}'.format(token=_args.token, name=name, year=year)
    r = requests.get(URL, headers=headers)
    if r.status_code != 200:
        logging.error("Error on get page")
        return False
    meta_data = json.loads(r.text)
    # pprint.pprint(meta_data)
    if meta_data['total_results'] == 0:
        logging.info("Cannot find result when searching {}".format(name))
        return False
    if meta_data['total_results'] > 1:
        logging.info("More than one result when searching {}".format(name))
    original_title = meta_data['results'][0]['original_title']
    logging.info("Got movie meta-data: {} ------ {}".format(name_tag, original_title))
    return True


def parse_beAst_string(filename: str) -> (str, str):
    # Split by dot in default
    g = filename.split('.')
    if len(g) == 1:
        # Try split by space.
        g = filename.split(' ')
    if len(g) < 2:
        return filename, ''

    for idx, word in enumerate(g):
        if len(word) == 4 and word.isdigit() and int(word) < 3000 and int(word) > 1000:
            return ' '.join(g[:idx]), word
    return filename, ''


def main():
    src_dir = _args.src
    dst_dir = _args.dst
    if not os.path.exists(src_dir) or not os.path.exists(dst_dir):
        logging.error("src or dst directory is not a avaliable directory")
    logging.info("Start: src {}, dst {}".format(src_dir, dst_dir))
    filename_list = os.listdir(src_dir)
    logging.info("Find {} objects".format(len(filename_list)))
    for f in filename_list:
        logging.info("Working on --- {}".format(f))
        src_path = os.path.join(src_dir, f)
        dst_path = os.path.join(dst_dir, f)
        name, year = parse_beAst_string(f)
        if is_movie(name, year):
            move_dir(src_path, dst_path)
        else:
            logging.info("Not a movie, pass")

if __name__ == '__main__':
    main()