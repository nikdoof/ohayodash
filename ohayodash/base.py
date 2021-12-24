import datetime
import logging
import os
import zoneinfo

import kubernetes
import yaml
from flask import Blueprint, render_template

ANNOTATION_BASE = 'ohayodash.github.io'

base = Blueprint('base', __name__, template_folder='templates')


def get_k8s_applications() -> list:
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


def get_bookmarks() -> list:
    """Get all 'bookmark' ConfigMaps from the cluster and produce a bookmark list."""
    if 'KUBERNETES_SERVICE_HOST' in os.environ:
        kubernetes.config.load_incluster_config()
    else:
        kubernetes.config.load_kube_config()
    v1 = kubernetes.client.CoreV1Api()
    ret = v1.list_config_map_for_all_namespaces(watch=False)

    bookmarks = {}
    for cm in ret.items:

        # Skip if
        if not cm.metadata.annotations or '{0}/bookmarks'.format(ANNOTATION_BASE) not in cm.metadata.annotations:
            continue

        bookmark_data = yaml.safe_load(cm.data['bookmarks'])
        for bookmark in bookmark_data:
            if 'group' not in bookmark:
                group = 'default'
            else:
                group = bookmark['group'].lower()
            if group not in bookmarks:
                bookmarks[group] = []
            bookmarks[group].append(bookmark)

    return bookmarks


def get_greeting():
    """Generate the greeting string based on the defined timezone."""
    try:
        tz = zoneinfo.ZoneInfo(os.environ.get('TZ', 'UTC'))
    except zoneinfo.ZoneInfoNotFound:
        logging.warning('Timezone {0} is invalid, using UTC'.format(os.environ.get('TZ', 'UTC')))
        tz = zoneinfo.ZoneInfo('UTC')

    current_time = datetime.datetime.now(tz)

    if 0 < current_time.hour < 12:
        return 'おはようございます!'
    elif current_time.hour >= 19:
        return 'こんばんは'
    return 'こんにちは'


@base.route('/')
def index():
    return render_template('index.j2',
                           greeting=get_greeting(),
                           now=datetime.datetime.utcnow(),
                           applications=get_k8s_applications(),
                           bookmarks=get_bookmarks(),
                           )
