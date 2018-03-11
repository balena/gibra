#!/bin/env python3
# -*- coding: utf-8 -*-

import sys
import ast
import codecs
import os
import pytz
import re
import subprocess
import tempfile
import uuid
import shutil

from flask import Flask, render_template_string, request, flash, redirect, url_for, session
from flaskext.markdown import Markdown, Extension
from werkzeug.utils import secure_filename
from zipfile import ZipFile
from dateutil.tz import tzlocal

from pprint import pprint
from datetime import datetime

import markdown
from markdown.inlinepatterns import Pattern

__version__ = "1.0.0"

ALLOWED_EXTENSIONS = set(['zip'])
CHANGELOG_FILE = 'CHANGELOG.md'
BRANCHES_FILE = '.branches.py'
BUGTRACKING_URL = 'https://github.com/balena/artifacts/issues/'

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
md = Markdown(app)

class TicketsPattern(Pattern):

  def handleMatch(self, m):
    ticket_number = m.group(2)
    text = '#' + ticket_number
    url = BUGTRACKING_URL + ticket_number
    el = markdown.util.etree.Element("a")
    el.set('href', url)
    el.text = markdown.util.AtomicString(text)
    return el

@md.extend()
class TicketsExtension(Extension):

  def extendMarkdown(self, md, md_globals):
    md.inlinePatterns['tickets'] = TicketsPattern(r'#([0-9]{2,4})')

index_html = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="author" content="Guilherme Balena Versiani">
    <meta name="description" content="Artifacts assistant provides a minimal interface of a binary repository manager using Git.">
    <title>Release Assistant</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,300italic,700,700italic">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/normalize/3.0.3/normalize.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/milligram/1.3.0/milligram.min.css">
    <link rel="stylesheet" href="https://milligram.github.io/styles/main.css">
  </head>
  <body>
    <main class="wrapper">
      <nav class="navigation">
        <section class="container">
          <span class="navigation-title">
            <svg class="img" version="1.1" viewBox="0 0 50 50">
              <polyline points="30 14 30 10 35 10 35 6 21 6 21 10 26 10 26 14" fill="none" stroke="#000" stroke-linejoin="round" stroke-miterlimit="10" stroke-width="2"/>
              <polyline points="9 27 5 27 5 21 1 21 1 37 5 37 5 31 9 31" fill="none" stroke="#000" stroke-linejoin="round" stroke-miterlimit="10" stroke-width="2"/>
              <path d="M45,20v5h-3v-8.157C42,15.826,41.189,15,40.191,15H19.99c-0.479,0-0.941,0.195-1.28,0.542L14,21h-3c-1,0-2,1-2,2v12 c0,1.018,1.002,2,2,2h3l4.712,5.461C19.051,42.806,19.511,43,19.99,43h12.855c0.479,0,0.939-0.194,1.278-0.539l7.346-7.482 c0.341-0.346,0.53-0.814,0.53-1.303V31h3v5h4V20H45z" fill="none" stroke="#000" stroke-linecap="round" stroke-linejoin="round" stroke-miterlimit="10" stroke-width="2.0077"/>
              <polygon points="32 28 24 39 27 30 22 30 27 20 32 20 27 28"/>
            </svg>
            &nbsp;
            <h1 class="title">Artifacts Assistant</h1>
            <span class="float-right">version {{__version__}}</span>
          </span>
        </section>
      </nav>

      {%- if branches %}
      <section class="container" id="change-branch">
        <h5 class="title">Branch</h5>
        <p><strong>Current branch</strong>: {{current_branch}}</p>
        <p>
          <form method="POST" action="{{url_for('.change_branch')}}">
            <div class="row">
              <div class="column column-75">
                <select name="branch" id="branch">
                  {%- for branch in branches|sort %}
                  <option value="{{branch}}"{{' selected' if branch == current_branch else ''}}>{{branch}}</option>
                  {%- endfor %}
                </select>
              </div>
              <div class="column column-25">
                <input class="button-primary" type="submit" value="Change" onclick="document.getElementById('branch-progress').style.display='block'">
              </div>
            </div>
            <div class="row">
              <div class="column">
                <progress id="branch-progress" style="display: none;"><small>In progress…</small></progress>
              </div>
            </div>
          </form>
        </p>
      </section>
      {%- endif %}

      {%- if not branches or current_branch in branches %}
      <section class="container" id="new-release">
        <h5 class="title">New release</h5>
        {%- with messages = get_flashed_messages(with_categories=True) %}
        {%- if messages %}
        <blockquote style="color: #9b4dca;">
          <p><em>
            {%- for cat, msg in messages %}
            <strong>{{ cat }}</strong>: {{ msg }}
            {%- endfor %}
          </em></p>
        </blockquote>
        {%- endif %}
        {%- endwith %}
        <p>
          <form method="POST" action="{{url_for('.index')}}" enctype="multipart/form-data">
            <fieldset>
              <div class="row">
                <div class="column column-33">
                  <label for="release-version">Version</label>
                  <input type="text" name="version" id="release-version" value="{{version}}">
                </div>
                <div class="column">
                  <label for="package">Add a file</label>
                  <input type="file" name="package" id="package">
                </div>
              </div>
              <div class="row">
                <div class="column">
                  <label for="release-notes">What's new in this release?</label>
                  <small>
                    Use the <a href="https://daringfireball.net/projects/markdown/syntax">Markdown</a>
                    format below.
                  </small>
                  <textarea placeholder="Enter or paste your release notes here…"
                            name="description" id="release-notes">{{''.join(description)|safe}}</textarea>
                </div>
              </div>
              <div class="row">
                <div class="column column-20">
                  <input class="button-primary" type="submit" value="Create" onclick="document.getElementById('release-progress').style.display='block'">
                </div>
                <div class="column column-80">
                  <progress id="release-progress" style="margin-top: .5em; display: none;"><small>In progress…</small></progress>
                </div>
              </div>
            </fieldset>
          </form>
        </p>
      </section>

      <section class="container" id="changelog">
        <h3 class="title">Changelog</h3>
        {%- if changelog %}
        {%- for c in changelog %}
        <h4><strong>{{ c['version'] }}</strong> &mdash; {{ c['date'] }}</h4>
        {{ '\n'.join(c['description'])|markdown }}
        {%- endfor %}
        {%- else %}
        <p><em>Pssst! It's empty...</em></p>
        {%- endif %}
      </section>
      {%- endif %}

    </main>

    <script src="https://milligram.github.io/scripts/main.js"></script>

  </body>
</html>
"""

def allowed_file(filename):
  return '.' in filename and \
         filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_branches():
  if os.path.exists(BRANCHES_FILE):
    with open(BRANCHES_FILE, 'r') as f:
      return ast.literal_eval(f.read())
  return []

def read_changelog():
  changelog = []
  if os.path.exists(CHANGELOG_FILE):
    with codecs.open(CHANGELOG_FILE, 'r', 'utf-8') as f:
      state = 'preamble'
      for line in f.readlines():
        if state == 'preamble':
          if line.startswith('## '):
            state = 'version_date'
          else:
            continue
        if state == 'body':
          if line.startswith('## '):
            state = 'version_date'
          else:
            changelog[-1].setdefault('description',[]).append(line.rstrip())
            continue
        if state == 'version_date':
          m = re.match(r'^## ([^ ]+) - (.*)$', line)
          changelog.append({'version': m.group(1), 'date': m.group(2).strip()})
          state = 'body'
  return changelog

def save_changelog(changelog):
  lines = []
  for c in changelog:
    pprint(c)
    lines.append(u'## {} - {}'.format(c['version'], c['date']))
    description = [line.strip() for line in c['description']]
    while description and description[0] == '':
      del description[0]
    while description and description[-1] == '':
      del description[-1]
    lines.extend(description)
    lines.append('')

  with codecs.open(CHANGELOG_FILE, 'w') as f:
    f.write(u'\n'.join(lines))

def unzip(filename):
  shutil.rmtree('dist', ignore_errors=True)
  os.mkdir('dist')
  with ZipFile(filename, 'r') as zf:
    zf.extractall('dist')

def get_entry():
  new_entry = {
    'version': request.form.get('version'),
    'date': datetime.now(tzlocal()).strftime('%Y-%m-%d %H:%M:%S %z'),
    'description': [request.form.get('description').replace('\r', '')],
  }
  result = False
  package = None
  if 'package' not in request.files:
    flash('No file part', 'error')
  else:
    package = request.files['package']
    if package.filename == '':
      flash('No selected file', 'error')
    elif package and not allowed_file(package.filename):
      flash('Please add a .zip file', 'error')
    else:
      output = subprocess.check_output(['git', 'tag']).decode('utf-8')
      tags = [x.strip() for x in output.split('\n')]
      if new_entry['version'] in tags:
        flash('Version {} already exists'.format(new_entry['version']), 'error')
      else:
        result = True
  return (result, new_entry, package)

def get_current_branch():
  output = subprocess.check_output(['git', 'branch']).decode('utf-8')
  selected = [line.split()[1] for line in output.split('\n') if line.startswith('*')]
  return selected[0]

@app.route('/', methods=['GET', 'POST'])
def index():
  new_entry = {}
  if request.method == 'POST':
    result, new_entry, package = get_entry()
    if result:
      filename = secure_filename(package.filename)
      uploaded_file = os.path.join(tempfile.gettempdir(), filename)
      package.save(uploaded_file)
      unzip(uploaded_file)

      subprocess.check_call(['git', 'fetch', '--all'])

      changelog = read_changelog()
      save_changelog([new_entry] + changelog)

      subprocess.check_call(['git', 'add', '*'])
      subprocess.check_call(['git', 'commit', '-m', 'Bump to version {}'.format(new_entry['version'])])
      subprocess.check_call(['git', 'push'])

      subprocess.check_call(['git', 'tag', new_entry['version']])
      subprocess.check_call(['git', 'push', '--tags'])

      return redirect(request.url)

  return render_template_string(index_html,
          current_branch=get_current_branch(),
          branches=load_branches(),
          changelog=read_changelog(),
          __version__=__version__,
          **new_entry)

@app.route('/branches', methods=['POST'])
def change_branch():
  branch = request.form.get('branch')
  subprocess.check_call(['git', 'fetch', '--all'])
  subprocess.check_call(['git', 'pull', '--tags'])
  subprocess.check_call(['git', 'checkout', branch])
  return redirect(url_for('.index'))

if __name__ == "__main__":
  if len(sys.argv) == 2 and sys.argv[1] == 'reqs':
    requirements = [
        'pytz>=2017.2',
        'Flask>=0.12.2',
        'Werkzeug>=0.14.1',
        'Flask-Markdown>=0.3',
        'python-dateutil>=2.6.1',
    ]
    print('\n'.join(requirements))
  else:
    app.run(debug=True, port=5757)
