# Configuration
Currently supports two types of searches. For sale and housing. For each type all of the filters that are specified in the base and specific class are supported.

Base filters: https://github.com/juliomalegria/python-craigslist/blob/master/craigslist/base.py#L33
Sale Filters: https://github.com/juliomalegria/python-craigslist/blob/master/craigslist/craigslist.py#L78
Housing filters: https://github.com/juliomalegria/python-craigslist/blob/master/craigslist/craigslist.py#L142

```
type: house # 'sale' or 'house'

email:
  subject: Apartment Search
  from: some_bot_account@gmail.com
  password_env_var: PASSWORD
  smtp:
    host: smtp.gmail.com
    port: 465

  to:
    - hello_world@gmail.com

craigslist:
  category: apa
  site: portland
  filters:
    max_price: 1300
    min_bedrooms: 1
    min_bathrooms: 1
    posted_today: true
    zip_code: 97202
    search_distance: 5

geo_boundary: # optionally filter further down based on the coordinates given in the posting
  se:
    - 45.457
    - -122.575
  nw:
    - 45.563
    - -122.660

storage: s3://some_bucket/cs_scrape/storage.json
```

# Running locally

This will run the scraper locally without sending any email and simply write out the html for the email to stdout

1. `python3 -m venv venv`
2. `source ./venv/bin/activate`
3. `pip install -r requirements.txt`
4. `python3 craiglist_rss.py f local_storage.json > out.html`

# Setup

# Package scrapers

1. Create your conf.yaml file
2. Run package.sh `package.sh [name] [config file]` names need to match the filenames you specify in the terraform

## Create infrastructure

Create the lambda, s3 bucket and cloudwatch rule. Update the s3 bucket to a name you want or remove if reusing an existing bucket. Add any additional scrapers you want to run. You will also need to supply the email password for the sending account.
```
$> cd terraform
$> terraform init
$> terraform apply -var EMAIL_PASSWORD=12345689
```

# Updating configs

1. Rebuild the package zip file with package.sh
2. Re apply the terraform to update the code