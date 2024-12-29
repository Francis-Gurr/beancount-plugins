def any_posting_has_metadata_key(postings, metadata_key):
    return any(metadata_key in item for item in postings)

def any_tag_starts_with(tags, string):
    return any(tag.startswith(string) for tag in tags)