import os

import kubernetes
import pkg_resources
import yaml
from flask import Blueprint, jsonify, render_template

ANNOTATION_BASE = 'ohayodash.github.io'

base = Blueprint('base', __name__, template_folder='templates')

if 'KUBERNETES_SERVICE_HOST' in os.environ:
    kubernetes.config.load_incluster_config()
else:
    kubernetes.config.load_kube_config()


def check_tags(tag, kubeobj):
    # Skip if we're limited to a tag, and the CM has tags but not that one.
    tags = kubeobj.metadata.annotations.get('{0}/tags'.format(ANNOTATION_BASE), '')
    obj_tags = {tagname for tagname in tags.split(',') if tagname != ''}

    # If its not tagged, allow
    if not obj_tags:
        return True

    # If tag is on the object, allow
    return tag in obj_tags


def get_k8s_applications(tag: str = None) -> list:
    """Get all ingresses from the cluster and produce a application list."""
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
    data_file = pkg_resources.resource_filename(__name__, 'data/providers.yaml')
    with open(data_file, 'r') as fobj:
        providers = yaml.safe_load(fobj)
    return jsonify({'providers': providers})


@base.route('/apps.json')
@base.route('/<tag>/apps.json')
def applications(tag=None):
    return jsonify({
        'apps': get_k8s_applications(tag),
    })


@base.route('/links.json')
@base.route('/<tag>/links.json')
def bookmarks(tag=None):
    return jsonify({
        'bookmarks': get_bookmarks(tag),
    })
