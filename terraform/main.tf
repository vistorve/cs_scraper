

locals {
    s3_bucket = "my_scraper
}

resource aws s3_bucket {
    name = local.s3_bucket
}

module house_scraper {
    source = "./scraper"

    tags = {}

    filename = "../house_scraper.zip"
    name = "house_scraper"
    s3_resources = [
        "arn:aws:s3:::${local.s3_bucket}/cs_scrape/house_scraper.json"
    ]
    cron_schedule = "cron(0 20 * * ? *)
    password = var.EMAIL_PASSWORD
}