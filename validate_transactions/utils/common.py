def any_posting_has_metadata_key(postings, metadata_key):
    return any(metadata_key in item.meta for item in postings)

def any_tag_starts_with(tags, str):
    return any(tag.startswith(str) for tag in tags)