# Ohayo Dash

Ohayo Dash is a Kubernetes driven start page and dashboard. All configuration is done by standard Kubernetes objects and ConfigMaps.

This is inspired by [Hajimari](https://github.com/toboshii/hajimari) and [SUI](https://github.com/jeroenpardon/sui) projects.

## Ingresses

All namespaces as processed by default, only Ingress objects with `ohayodash.github.io/enabled` annotation are then displayed.

Annotations can be used to customize the display of the Ingress objects:

* `ohayodash.github.io/name` - Display name of the app, defaults to the Ingress name.
* `ohayodash.github.io/url` - Target URL of the service, defaults to `https://<ingress host>`
* `ohayodash.github.io/show_url` - Shows the URL under the link, defaults to `false`

## Bookmarks

Bookmark are stored in `ConfigMap` resources, which are identified by the `ohayodash.github.io/bookmarks` annotation.

Values are pulled from the `bookmarks` key in the config map, which consists of a list of objects with the following keys:

* `name` - the display name of the link
* `url` - the target URL.
* `group` - the name the link is to be grouped under.

```
apiVersion: v1
kind: ConfigMap
metadata:
  name: ohayodash-bookmarks
  namespace: web
  annotations:
    ohayodash.github.io/bookmarks: 'true'
data:
  bookmarks: |
    - name: Renovate Dashboard
      url: "https://app.renovatebot.com/dashboard#github/nikdoof/flux-gitops"
      group: Github
```

## Providers

Providers are stored in `ConfigMap` resources, which are identified by the `ohayodash.github.io/providers` annotation.

Values are pulled from the `providers` key in the config map, which consists of a list of objects with the following keys:

* `name` - the display name of the link
* `url` - the target URL of the service.
* `search` - suffix to add to search on the service, this will combine the URL, Search value and the text to search for into a URL.
* `prefix` - prefix to use on the URL bar on Ohayodash.

```
apiVersion: v1
kind: ConfigMap
metadata:
  name: ohayodash-providers
  namespace: web
  annotations:
    ohayodash.github.io/providers: 'true'
data:
  providers: |
    - name: Allmusic
      url: https://www.allmusic.com/
      search: search/all/
      prefix: /a
```
