from greshunkel.build import POSTS_DIR
from greshunkel.utils import parse_variable
from greshunkel.slimdown import Slimdown

from os import listdir, walk
import subprocess, re, json

DEFAULT_LANGUAGE = "en"
BASE_CONTEXT = {}

def build_blog_context(default_context):
    default_context['POSTS'] = []

    slimmin = Slimdown()
    for post in listdir(POSTS_DIR):
        if not post.endswith(".markdown"):
            continue

        new_post = {}
        dashes_seen = 0
        reading_meta = True
        muh_file = open(POSTS_DIR + post)
        all_text = ""
        for line in muh_file:
            stripped = line.strip()
            if stripped == '---':
                dashes_seen += 1
                if reading_meta and dashes_seen < 2:
                    continue
            elif reading_meta and dashes_seen >= 2:
                reading_meta = False
                continue

            if reading_meta and ':' in line:
                split_line = stripped.split(":")
                new_post[split_line[0]] = split_line[1]

            if not reading_meta:
                all_text += line

        new_post['content'] = json.dumps(slimmin.render(all_text))
        new_post['preview'] = new_post['content'][:300] + "&hellip;"
        # ThIs DoEsNt WoRk WiTh JsON StuFf
        # SO FUCKIIN HACK IT
        new_post['link'] = "blog/{}".format(post.replace("markdown", "json"))
        new_post['filename'] = post
        new_post['built_filename'] = post.replace("markdown", "json")
        default_context['POSTS'].append(new_post)
        muh_file.close()
    default_context['POSTS'] = sorted(default_context['POSTS'], key=lambda x: x["date"], reverse=True)
    for index in range(len(default_context['POSTS'])):
        # Hacks on fucking hacks
        if index != len(default_context['POSTS']) - 1:
            default_context['POSTS'][index]['comma'] = ','
        else:
            default_context['POSTS'][index]['comma'] = ''
    return default_context

