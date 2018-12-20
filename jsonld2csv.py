#!/usr/bin/env python3
import sys
import json
import csv
import re


def ldget(obj, path, default=None):
    "Descente dans le graphe de données"
    if obj is not None and path[0] in obj:
        if len(path) == 1:
            return obj[path[0]]
        else:
            return ldget(obj[path[0]], path[1:], default=default)
    else:
        return default


# fichier CSV de sortie
with open(re.sub(r'json.*', 'csv', sys.argv[1]), 'w') as csvfile:
    fields = ['id', 'label', 'type', 'theme', 'startdate', 'enddate',
              'street', 'postalcode', 'city', 'insee',
              'latitude', 'longitude', 'email', 'web', 'tel',
              'lastupdate', 'linkimg', 'comment']
    csv_out = csv.writer(csvfile)
    csv_out.writerow(fields)

    # fichier json-ld en entrée
    with open(sys.argv[1], 'r') as json_file:
        data = json.load(json_file)
        for e in data['@graph']:
            # extraction des éléments du graphe à sortir en CSV
            uri = ldget(e, ['@id'])
            labelobj = ldget(e, ['rdfs:label'])
            labellang = ldget(labelobj, ['@language'])
            label = ""
            if labellang == 'fr':
                label = ldget(labelobj, ['@value'])
            commentobj = ldget(e, ['rdfs:comment'])
            commentlang = ldget(commentobj, ['@language'])
            comment = ""
            if commentlang == 'fr':
                comment = ldget(commentobj, ['@value'])
            startdate = ldget(e, ['takesPlaceAt', 'startDate', '@value'])
            enddate = ldget(e, ['takesPlaceAt', 'endDate', '@value'])
            geo = ldget(e, ['isLocatedAt', 'schema:geo'])
            lat = ldget(geo, ['schema:latitude', '@value'])
            lon = ldget(geo, ['schema:longitude', '@value'])
            addr = ldget(e, ['isLocatedAt', 'schema:address'])
            street = ldget(addr, ['schema:streetAddress'])
            cp = ldget(addr, ['schema:postalCode'], '')
            city = ldget(addr, ['schema:addressLocality'])
            insee = ldget(addr, ['hasAddressCity', 'insee'])
            last_update = ldget(e, ['lastUpdate', '@value'])
            event_type = '/'.join(ldget(e, ['@type']))
            email = ldget(e, ['hasContact', 'schema:email'])
            web = ldget(e, ['hasContact', 'foaf:homepage'])
            tel = ldget(e, ['hasContact', 'schema:telephone'])
            linkimg = ldget(e, ['hasMainRepresentation','ebucore:hasRelatedResource', 'ebucore:locator', '@value'])
            img = ""
            if linkimg is not None:
                img = linkimg
            themes = ldget(e, ['hasTheme'])
            event_theme = ''
            if themes is not None:
                if 'rdfs:label' in themes and '@language' in themes['rdfs:label'] and  themes['rdfs:label']['@language'] == 'fr' :
                    event_theme = event_theme + themes['rdfs:label']['@value'] + ', '
                else:
                    if len(themes) > 0:
                        for t in themes :
                            if 'rdfs:label' in t and '@language' in t['rdfs:label'] and t['rdfs:label']['@language'] == 'fr':
                                event_theme = event_theme + t['rdfs:label']['@value'] + ', '
                event_theme = event_theme[:-2]

            # écriture dans le fichier CSV
            csv_out.writerow([uri, label, event_type, event_theme, startdate, enddate, street, cp, city, insee, lat, lon, email, web, tel, last_update, img, comment])
