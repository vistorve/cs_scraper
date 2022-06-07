variable password {
    type = string
    description = "Password for email sending"
}

variable filename {
    type = string
    description = "Path to lambda .zip archive"
}

variable tags {
    type = map
    description = "Tags for resources"
}

variable name {
    type = string
    description = "Name of lambda"
}

variable s3_resources {
    type = list(string)
    description = "List of s3 arns the lambda is allowed to read/write from
}

variable cron_schedule {
    type = string
    description = "AWS cron expression to trigger lambda with"
}