from greshunkel.build import POSTS_DIR
from greshunkel.utils import parse_variable
from greshunkel.slimdown import Slimdown

from os import listdir, walk
import subprocess, re

INCLUDE_DIR = "./OlegDB/include/"
DOCUMENTATION_DIR = "./OlegDB/docs/"
DEFAULT_LANGUAGE = "en"
# Question: Hey qpfiffer, why is this indented all weird?
# Man I don't know leave me alone.
BASE_CONTEXT = { "questions":
            [ "Is this a joke?"
            , "Why are you doing this?"
            , "Can I use this in production?"
            , "Should I use this in production?"
            , "Why did you make X the way it is? Other people do Y."
            , "Are you guys CS 100 students?"
            , "What sets OlegDB apart from Leading NoSQL Data Solution X&trade;?"
            , "What other projects do you like?"
            , "When I upload a large file via curl, it comes back different. What gives?"
            ],
            "answers":
            [ "No. We use this everyday for all of our projects."
            , "\"My goal is to outrank redis with one of the worst OSS products on the free market.\"<p class=\"italic\">Kyle Terry, Senior Developer</p>"
            , "Yeah, sure whatever."
            , "Yes, most definitely."
            , "Well, we're trend-setters. Clearly our way of accomplishing things just hasn't been accepted yet."
            , "We were. Never really made it past that."
            , "With our stubborn dedication to quality, C and a lack of experience, we bring a unique perspective to an otherwise ugly and lacking marketplace. Arbitrary decisions, a lack of strong leadership and internal arguments haved turned the project into a double-edged sword, ready to cut into anyone and anything."
            ,
            """ We like every flavor-of-the-week database. Here are a couple:
            <ul>
                <li><a href="http://fallabs.com/kyotocabinet/">Kyoto Cabinet</a></li>
                <li><a href="http://redis.io/">Redis</a></li>
                <li><a href="http://www.postgresql.org/">PostgreSQL</a></li>
                <li><a href="http://sphia.org/">Sophia</a></li>
                <li><a href="http://www.actordb.com/">ActorDB</a></li>
                <li><a href="https://github.com/shuttler/nessDB">NessDB</a></li>
            </ul>
            """
            , "Don't use curl to upload files into Oleg. Use something else. See <a href=\"https://github.com/infoforcefeed/OlegDB/issues/26\">here.</a>"
            ],
        "ALL_DOWNLOADS": [
                { "codename": "Spider Marketplace",
                  "version": "v.0.1.5",
                  "release_date": "2015/01/25",
                  "md5": "d1312d845f0d3eab5ff559f029ab49a3",
                  "tar_link": "https://github.com/infoforcefeed/OlegDB/archive/v.0.1.5.tar.gz",
                },
                { "codename": "Proven LAMP-Stack Event",
                  "version": "v.0.1.4",
                  "release_date": "2014/09/09",
                  "md5": "12b0b1d65730c1a29fbb5a8d3ec72b99",
                  "tar_link": "https://github.com/infoforcefeed/OlegDB/archive/v.0.1.4.tar.gz",
                },
                { "codename": "Perilous Pomegranate",
                  "version": "v.0.1.3",
                  "release_date": "2014/07/04",
                  "md5": "a421e6c9e2d51f7485e647456d3e91f3",
                  "tar_link": "https://github.com/infoforcefeed/OlegDB/archive/v.0.1.3.tar.gz",
                },
                { "codename": "Mayo Indoctrination",
                  "version": "v.0.1.2",
                  "release_date": "2014/06/25",
                  "md5": "2571e637cd7275b3a97c0636715a66fd",
                  "tar_link": "https://github.com/infoforcefeed/OlegDB/archive/v.0.1.2.tar.gz",
                },
                { "codename": "Cartwheeling Trespassers",
                  "version": "v.0.1.1",
                  "release_date": "2014/05/05",
                  "md5": "cd9632d69f718aa5cb16f60d72ddf251",
                  "tar_link": "https://github.com/infoforcefeed/OlegDB/archive/v.0.1.1.tar.gz",
                },
                { "codename": "Affirmitive Affirmation",
                  "version": "v.0.1.0",
                  "release_date": "2014/03/31",
                  "md5": "adcf56a2be2bceb6fa10657b35dab2a9",
                  "tar_link": "https://github.com/infoforcefeed/OlegDB/archive/v.0.1.0.tar.gz",
                },
            ],
        }
# Fuck doing anything intelligent in the templating framework:
BASE_CONTEXT["FIRST_DOWNLOAD"] = [BASE_CONTEXT["ALL_DOWNLOADS"][0]]

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

        new_post['content'] = slimmin.render(all_text)
        new_post['preview'] = new_post['content'][:300] + "&hellip;"
        new_post['link'] = "blog/{}".format(post.replace("markdown", "html"))
        new_post['filename'] = post
        new_post['built_filename'] = post.replace("markdown", "html")
        default_context['POSTS'].append(new_post)
        muh_file.close()
    default_context['POSTS'] = sorted(default_context['POSTS'], key=lambda x: x["date"], reverse=True)
    return default_context

def try_to_build_documentation_tree(default_context):
    root = []

    # Murderous material, made by a madman
    # It's the mic wrecker, Inspector, bad man
    # Wu-Tang Clan, 7th Chamber.
    def _build_tree(directory):
        only_name = directory.split("/")[-1]
        to_return = {
            "children": [],
            "name": only_name,
            "body": "",
            "nav": ""
        }

        for _, dirs, files in walk(directory):
            for dir_name in dirs:
                to_return["children"].append(_build_tree(directory + "/" + dir_name))

            for file_name in sorted(files):
                if not file_name.endswith(".markdown"):
                    continue
                subsection_name = re.compile(r'[a-zA-Z][a-zA-Z0-9_]*')
                thing = subsection_name.search(file_name)
                slug = thing.group().lower()
                name = thing.group().replace("_", " ")
                rendered_section_name = \
                    '<h2 class="perma" id="{slug}">{name} <a href="#{slug}">&para;</a></h2>'.format(
                        slug=slug, name=name)

                opened = open(directory + "/" + file_name)
                all_text = opened.read()

                slimmin = Slimdown()
                to_return["body"] = ''.join([to_return["body"], rendered_section_name, slimmin.render(all_text)])
                to_return["nav"] = ''.join([to_return["nav"], '<li><a href="#{slug}">{name}</a></li>'.format(slug=slug, name=name)])
                opened.close()

        # Build the thing for the main section
        slug = only_name.lower().replace(" ", "_")
        name = only_name.replace("_", " ")
        rendered_section_name = \
            '<h2 class="perma" id="{slug}">{name} <a href="#{slug}">&para;</a></h2>'.format(
                slug=slug, name=name)
        to_return["body"] = ''.join(['<div class="doc_chunk">', rendered_section_name, to_return["body"], "</div>"])
        master_nav = '<a href="#{slug}">{name}</a>'.format(slug=only_name.lower().replace(" ", "_"), name=only_name)
        to_return["nav"] = "<li>{master_nav}<ul>{nav}</ul></li>".format(master_nav=master_nav, nav=to_return["nav"])

        return to_return

    for _, dirs, _ in walk(DOCUMENTATION_DIR):
        for x in dirs:
            root.append(_build_tree(DOCUMENTATION_DIR + x))

    return root

def build_doc_context(default_context):
    output = subprocess.check_output("cd OlegDB && git tag --list", shell=True)
    default_context['docs'] = {}
    default_context['ALL_VERSIONS'] = []
    versions = sorted(output.strip().split("\n"))
    versions.append("master")

    # Prepare a default documentation for versions pre 0.1.2
    default_documentation_html = open("./templates/documentation_default.html")
    default_documentation_nav_html = open("./templates/documentation_default_nav.html")
    DEFAULT_DOCUMENTATION = to_return = [{
        "children": [],
        "name": "Overview",
        "body": default_documentation_html.read(),
        "nav": default_documentation_nav_html.read()
    }]
    default_documentation_html.close()
    default_documentation_nav_html.close()

    for version in versions:
        print "Checking out {}".format(version)
        cmd = "cd OlegDB && git checkout {} &> /dev/null".format(version)
        subprocess.check_output(cmd, shell=True)
        headers = ["oleg.h", "defs.h"]
        headers = map(lambda x: "{}/{}".format(INCLUDE_DIR, x), headers)
        version_context = {}
        for header_file in headers:
            try:
                oleg_header = open(header_file)
            except IOError as e:
                print e
                continue

            docstring_special = ["DEFINE", "ENUM", "STRUCT", "DESCRIPTION",
                    "RETURNS", "TYPEDEF"]

            reading_docs = False
            raw_code = ""
            doc_object = {}

            for line in oleg_header:
                docline = False
                stripped = line.strip()
                if stripped == '*/':
                    continue

                # ThIs iS sOmE wEiRd FaLlThRouGh BuLlShIt
                if reading_docs and stripped.startswith("/*"):
                    raise Exception("Yo I think you messed up your formatting. Read too far.")
                if "xXx" in line and "*" in stripped[:2]:
                    (variable, value) = parse_variable(stripped)

                    docline = True
                    if not reading_docs:
                        doc_object["name"] = value
                        doc_object["type"] = variable
                        doc_object["params"] = []
                        reading_docs = True
                    else:
                        if variable in docstring_special:
                            # SpEcIaL
                            doc_object[variable] = value
                        else:
                            doc_object["params"].append((variable, value))
                if reading_docs and not docline and stripped != "":
                    raw_code = raw_code + line
                if stripped == "" and reading_docs:
                    reading_docs = False
                    doc_object["raw_code"] = raw_code
                    if version_context.get(doc_object["type"], False):
                        version_context[doc_object["type"]].append(doc_object)
                    else:
                        version_context[doc_object["type"]] = [doc_object]
                    doc_object = {}
                    raw_code = ""

            oleg_header.close()

        key_raw_code = [x for x in version_context['DEFINE'] if x['name'] == 'KEY_SIZE'][0]['raw_code']
        version_raw_code = [x for x in version_context['DEFINE'] if x['name'] == 'VERSION'][0]['raw_code']
        extracted_ks = key_raw_code.split(' ')[2].strip()
        extracted_version = version_raw_code.split(' ')[2].strip()
        extracted_version = extracted_version.replace('"', '')
        if version == 'master':
            default_context['EXTRACTED_KEY_SIZE'] = extracted_ks
            default_context['EXTRACTED_VERSION'] = extracted_version
        default_context['docs'][extracted_version] = version_context
        default_context['ALL_VERSIONS'].append(extracted_version)
        handwritten = try_to_build_documentation_tree(default_context)
        if len(handwritten) != 0:
            default_context["docs"][extracted_version]["DEFAULT_DOCUMENTATION"] = handwritten
        else:
            default_context["docs"][extracted_version]["DEFAULT_DOCUMENTATION"] = DEFAULT_DOCUMENTATION

    return default_context
