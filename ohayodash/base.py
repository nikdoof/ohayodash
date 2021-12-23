from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
import datetime
import kubernetes
import yaml

ANNOTATION_BASE = 'ohayodash.github.io'

base = Blueprint('base', __name__, template_folder='templates')

def get_k8s_applications():
    kubernetes.config.load_kube_config()
    v1 = kubernetes.client.NetworkingV1Api()
    ret = v1.list_ingress_for_all_namespaces(watch=False)

    results = []
    for ingress in ret.items:

        # Skip if
        if f'{ANNOTATION_BASE}/enable' not in ingress.metadata.annotations or \
                ingress.metadata.annotations[f'{ANNOTATION_BASE}/enable'] == 'false':
            continue

        values = {
            'name': ingress.metadata.name,
            'namespace': ingress.metadata.namespace,
            'url': f'https://{ingress.spec.rules[0].host}',
            'show_url': False,
        }

        for key in ingress.metadata.annotations:
            if key.startswith(ANNOTATION_BASE):
                val = key.split('/')[1]
                values[val] = ingress.metadata.annotations[key]

        results.append(values)
    return sorted(results, key=lambda i: i['appName'])


def get_bookmarks():
    kubernetes.config.load_kube_config()
    v1 = kubernetes.client.CoreV1Api()
    ret = v1.list_config_map_for_all_namespaces(watch=False)

    bookmarks = {}
    for cm in ret.items:

        # Skip if
        if not cm.metadata.annotations or f'{ANNOTATION_BASE}/bookmarks' not in cm.metadata.annotations:
            continue

        data = yaml.safe_load(cm.data['bookmarks'])
        for bookmark in data:
            if 'group' not in bookmark:
                group = 'default'
            else:
                group = bookmark['group'].lower()
            if group not in bookmarks:
                bookmarks[group] = []
            bookmarks[group].append(bookmark)

    return bookmarks


@base.route('/')
def index():
    return render_template(f'index.j2', **{
        'now': datetime.datetime.utcnow(),
        'applications': get_k8s_applications(),
        'bookmarks': get_bookmarks(),
    })
