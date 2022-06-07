import yaml
import json
import os
import sys

import boto3
from boto3.s3.transfer import S3Transfer

from craigslist import CraigslistHousing, CraigslistForSale

object_map = {
    "sale": CraigslistForSale,
    "house": CraigslistHousing
}

def fetch_listings(object_type, **kwargs):
    return object_map[object_type](**kwargs).get_results(geotagged=True)

def read_storage(storage):
    listing_hash = set()
    listings = []
    for l in storage.split("\n"):
        if not l:
            continue
        l = json.loads(l)
        listing_hash.add(l['url'])
        listings.append(l)

    return listing_hash, listings

def _gen_html_line(l):
    lat, lon = l['geotag']
    gmaps = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
    location = f'<a href="{gmaps}">{l["where"]}</a>'
    return location, float(l['price'].replace("$", "").replace(",", "")), f'{l["price"]} - {location} - {l["last_updated"]} <a href="{l["url"]}">{l["name"]}</a>'

def generate_output(new_listings, old_listings):
    data = "<html><body>"
    data += "<br>".join([html for loc, price, html in sorted(map(_gen_html_line, new_listings), key=lambda x: (x[1]))])

    data += "<br>--------------------<br>"
    data += "<br>".join([html for loc, price, html in sorted(map(_gen_html_line, old_listings[-20:]), key=lambda x: (x[1]))])
    data += "</body></html>"

    return data

def send_mail(content, config):
    import smtplib, ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    message = MIMEMultipart("alternative")
    message["Subject"] = config['subject']
    message["From"] = config['from']
    message["To"] = ",".join(config['to'])
    message.attach(MIMEText(content, "html"))

    password = os.getenv(config['password_env_var'])
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(config['smtp']['host'], config['smtp']['port'], context=context) as server:
        server.login(config['from'], password)
        server.sendmail(
            config['from'], config['to'], message.as_string()
        )

def filter_by_geo(listings, geo_boundary):
    max_lat = geo_boundary['nw'][0]
    min_lat = geo_boundary['se'][0]
    min_long = geo_boundary['nw'][1]
    max_long = geo_boundary['se'][1]

    for l in listings:
        if l['geotag'][0] < min_lat or l['geotag'][0] > max_lat:
            continue
        if l['geotag'][1] < min_long or l['geotag'][1] > max_long:
            continue

        yield l

def run(*args, config=None, sendmail=True, storage_override=None):
    config = yaml.full_load(open("conf.yaml", "r") if config is None else  config)

    if storage_override is not None:
        config['storage'] = storage_override

    is_s3 = config['storage'].startswith("s3")
    if is_s3:
        c = boto3.client('s3')
        bucket, key = config['storage'].replace("s3://", "").split("/", 1)
        storage = c.get_object(Bucket=bucket, Key=key)['Body'].read().decode('utf-8')
    else:
        if not os.path.exists(config['storage']):
            open(config['storage'], 'w').close()
        storage = open(config['storage'], 'r').read()

    listing_hash, listings = read_storage(storage)
    sys.stderr.write(f"N old listings {len(listings)}\n")
    fetched = fetch_listings(config['type'], **config['craigslist'])
    new_listings = []

    if config.get('geo_boundary'):
        fetched = filter_by_geo(fetched, config['geo_boundary'])
    
    for l in fetched:
        if l['url'] not in listing_hash:
            new_listings.append(l)

    #print(f"N new listings {len(new_listings)}")
    # Escape out if nothing new
    if not new_listings:
        sys.stderr.write("Nothing new, exiting.\n")
        return

    storage += "\n".join(map(json.dumps, new_listings)) + "\n"
    if is_s3:
        c = boto3.client('s3')
        bucket, key = config['storage'].replace("s3://", "").split("/", 1)
        c.put_object(Bucket=bucket, Key=key, Body=storage.encode('utf-8'))
    else:
        open(config['storage'], 'w').write(storage)

    out = generate_output(new_listings, listings)
    if sendmail:
        send_mail(out, config["email"])
    else:
        sys.stdout.write(out)

if __name__ == "__main__":
    sendmail = sys.argv[1] == "t"
    storage_override = sys.argv[2]
    if storage_override == "s3":
        storage_override = None
    run(config=sys.stdin, sendmail=sendmail, storage_override=storage_override)
