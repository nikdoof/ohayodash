import os

import kubernetes
import yaml
from flask import Blueprint, jsonify, render_template

ANNOTATION_BASE = 'ohayodash.github.io'

base = Blueprint('base', __name__, template_folder='templates')


def check_tags(tag, object):
    # Skip if we're limited to a tag, and the CM has tags but not that one.
    tags = object.metadata.annotations.get('{0}/tags'.format(ANNOTATION_BASE), '')
    obj_tags = {x for x in tags.split(',') if x != ''}

    # If its not tagged, allow
    if not obj_tags:
        return True

    # If tag is on the object, allow
    if tag in obj_tags:
        return True

    # Else, disallow
    return False


def get_k8s_applications(tag: str = None) -> list:
    """Get all ingresses from the cluster and produce a application list."""
    if 'KUBERNETES_SERVICE_HOST' in os.environ:
        kubernetes.config.load_incluster_config()
    else:
        kubernetes.config.load_kube_config()
    api = kubernetes.client.NetworkingV1Api()

    applications = []
    for ingress in api.list_ingress_for_all_namespaces(watch=False).items:

        # Skip if not enabled
        enable_annotation = '{0}/enable'.format(ANNOTATION_BASE)
        if enable_annotation not in ingress.metadata.annotations:
            continue
        if ingress.metadata.annotations[enable_annotation] == 'false':
            continue

        # Skip if we're limited to a tag, and the Ingress has tags but not that one.
        if not check_tags(tag, ingress):
            continue

        # Set to some basic values from the ingress
        application_values = {
            'name': ingress.metadata.name,
            'namespace': ingress.metadata.namespace,
            'url': 'https://{0}'.format(ingress.spec.rules[0].host),
            'show_url': False,
        }

        # Read annotations and override the values if defined
        for key, value in ingress.metadata.annotations.items():
            if key.startswith(ANNOTATION_BASE):
                annotation_key = key.split('/')[1]
                application_values[annotation_key] = value

        applications.append(application_values)
    return sorted(applications, key=lambda item: item['name'])


def get_bookmarks(tag: str = None) -> list:
    """Get all 'bookmark' ConfigMaps from the cluster and produce a bookmark list."""
    if 'KUBERNETES_SERVICE_HOST' in os.environ:
        kubernetes.config.load_incluster_config()
    else:
        kubernetes.config.load_kube_config()
    v1 = kubernetes.client.CoreV1Api()
    ret = v1.list_config_map_for_all_namespaces(watch=False)

    bookmarks = []
    for cm in ret.items:
        # Skip if the CM has no annotations
        if cm.metadata.annotations is None:
            continue

        # Skip if its not tagged as bookmark CM
        if '{0}/bookmarks'.format(ANNOTATION_BASE) not in cm.metadata.annotations:
            continue

        # Skip if we're limited to a tag, and the CM has tags but not that one.
        if not check_tags(tag, cm):
            continue

        # Load bookmark data
        bookmark_data = yaml.safe_load(cm.data['bookmarks'])

        # Iterate each bookmark
        for bookmark in bookmark_data:
            if 'group' not in bookmark:
                group = 'default'
            else:
                group = bookmark['group'].lower()

            # Find category dict and append or create
            for cat in bookmarks:
                if cat['category'] == group:
                    cat['links'].append(bookmark)
                    break
            else:
                bookmarks.append({'category': group, 'links': [bookmark]})

    return bookmarks


@base.route('/')
@base.route('/<tag>/')
def index(tag=None):
    return render_template('index.j2')


@base.route('/providers.json')
@base.route('/<tag>/providers.json')
def providers(tag=None):
    return jsonify({
        'providers': [
            {'name': 'Allmusic', 'url': 'https://www.allmusic.com/search/all/', 'prefix': '/a'},
            {'name': 'Discogs', 'url': 'https://www.discogs.com/search/?q=', 'prefix': '/di'},
            {'name': 'Duck Duck Go', 'url': 'https://duckduckgo.com/?q=', 'prefix': '/d'},
            {'name': 'iMDB', 'url': 'https://www.imdb.com/find?q=', 'prefix': '/i'},
            {'name': 'TheMovieDB', 'url': 'https://www.themoviedb.org/search?query=', 'prefix': '/m'},
            {'name': 'Reddit', 'url': 'https://www.reddit.com/search?q=', 'prefix': '/r'},
            {'name': 'Qwant', 'url': 'https://www.qwant.com/?q=', 'prefix': '/q'},
            {'name': 'Soundcloud', 'url': 'https://soundcloud.com/search?q=', 'prefix': '/so'},
            {'name': 'Spotify', 'url': 'https://open.spotify.com/search/results/', 'prefix': '/s'},
            {'name': 'TheTVDB', 'url': 'https://www.thetvdb.com/search?query=', 'prefix': '/tv'},
            {'name': 'Trakt', 'url': 'https://trakt.tv/search?query=', 'prefix': '/t'}
        ]
    })


@base.route('/apps.json')
@base.route('/<tag>/apps.json')
def applications(tag=None):
    return jsonify({
        'apps': get_k8s_applications(tag)
    })


@base.route('/links.json')
@base.route('/<tag>/links.json')
def bookmarks(tag=None):
    return jsonify({
        'bookmarks': get_bookmarks(tag)
    })
