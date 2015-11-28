#!/usr/local/bin/python2.7
# encoding: utf-8
"""
sub_syncer -- shortdesc

sub_syncer is a description

It defines classes_and_methods

@author:     user_name

@copyright:  2015 organization_name. All rights reserved.

@license:    license

@contact:    user_email
@deffield    updated: Updated
"""

import sys
import os
import re
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2015-01-18'
__updated__ = '2015-01-18'

TESTRUN = 0
PROFILE = 0


class CLIError(Exception):
    """Generic exception to raise and log different fatal errors."""

    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg


def main(argv=None):  # IGNORE:C0111
    """Command line options."""

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = """%s

  Created by user_name on %s.
  Copyright 2015 organization_name. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
""" % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument(dest="path", help="paths to folder(s) with source file(s) [default: %(default)s]",
                            metavar="path")

        # Process arguments
        args = parser.parse_args()

        path = args.path

        sync_sub(path)
        return 0
    except KeyboardInterrupt:
        # handle keyboard interrupt
        return 0
    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2


def sync_sub(path):
    video_info_list = []
    sub_info_list = []
    rename_list = []
    for item in os.listdir(path):
        item = item.decode(sys.getfilesystemencoding())
        print item
        if os.path.isdir(item): continue
        if item.endswith(".mkv"):
            video_info_list.append(init_video_info(item))
        elif item.endswith(".srt") or item.endswith(".ass"):
            sub_info_list.append(init_sub_info(item))
    for sub_info in sub_info_list:
        match_point = 0;
        hit_video = None
        for video_info in video_info_list:
            new_match_point = check_match_point(sub_info, video_info)
            # print("[{0}%] {1} >>> {2}".format(new_match_point, sub_info['file_name'], video_info['file_name']))
            if new_match_point > match_point:
                hit_video = video_info
                match_point = new_match_point
            if new_match_point >= 100:
                break
        if hit_video:
            print(
                u"[{0}%] {1} >>> {2}".format(match_point, sub_info['file_name'],
                                             hit_video['name'] + "." + sub_info['ext']))
            old_name = os.path.join(path, sub_info['file_name'].encode(sys.getfilesystemencoding()))
            new_name = os.path.join(path,
                                    (hit_video['name'] + "." + sub_info['ext']).encode(sys.getfilesystemencoding()))
            if old_name != new_name:
                rename_list.append({'old': old_name, 'new': new_name})

    if rename_list:
        choice = raw_input("Rename now ?")
        if choice.lower() in ('y', 'yes'):
            for rename in rename_list:
                os.rename(rename['old'], rename['new'])
            print 'All done.'
    else:
        print 'No file need rename.'


def init_video_info(file_name):
    m = re.match(r"^(?P<name>.+)\.(?P<ext>[^\.]+)$", file_name)
    name = m.group("name")
    ext = m.group("ext")
    words = name.lower().split(".")
    words.extend(re.findall(r'\w*\d+', name))
    return {"name": name,
            "ext": ext,
            "words": words,
            "file_name": file_name}


def init_sub_info(file_name):
    m = re.match(r"^(?P<name>.+)\.(?P<ext>[^\.]+)$", file_name)
    name = m.group("name")
    ext = m.group("ext")
    words = name.lower().split(".")
    if is_l10n_info(words[len(words) - 1]):
        ext = words.pop() + "." + ext
    words.extend(re.findall(r'\d+', name))
    return {"name": name,
            "ext": ext,
            "words": words,
            "file_name": file_name}


def is_l10n_info(word):
    for key in (u'简', u'繁', u'英', 'chs', 'cht', 'eng'):
        if key in word:
            return True
    return False


def check_match_point(sub_info, video_info):
    if sub_info['name'].lower() == video_info['name'].lower():
        return 100
    word_hit = 0.0
    for word in sub_info['words']:
        if word in video_info['words']:
            word_hit += 1
    return round((word_hit / len(sub_info['words'])) * 100, 2)


if __name__ == "__main__":
    if TESTRUN:
        import doctest

        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats

        profile_filename = 'sub_syncer_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())
