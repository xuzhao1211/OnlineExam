from misago.markup import checksums


def is_post_valid(post):
    valid_checksum = make_post_checksum(post)
    return post.checksum == valid_checksum


def make_post_checksum(post):
    post_seeds = [unicode(v) for v in (post.id, post.poster_ip)]
    return checksums.make_checksum(post.parsed, post_seeds)


def update_post_checksum(post):
    post.checksum = make_post_checksum(post)
    return post.checksum


def is_report_valid(report):
    valid_checksum = make_report_checksum(report)
    return report.checksum == valid_checksum


def make_report_checksum(report):
    report_seeds = [unicode(v) for v in (report.id, report.reported_by_ip)]
    return checksums.make_checksum(report.message, report_seeds)


def update_report_checksum(report):
    report.checksum = make_report_checksum(report)
    return report.checksum


def is_event_valid(event):
    valid_checksum = make_event_checksum(event)
    return event.checksum == valid_checksum


def make_event_checksum(event):
    event_seeds = [unicode(v) for v in (event.id, event.occured_on)]
    return checksums.make_checksum(event.message, event_seeds)


def update_event_checksum(event):
    event.checksum = make_event_checksum(event)
    return event.checksum
