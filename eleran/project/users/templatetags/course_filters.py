"""
Custom template filters for course-related functionality
"""
from django import template

register = template.Library()


@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Get an item from a dictionary using a key.
    
    Usage in template:
        {{ my_dict|get_item:key }}
    
    Args:
        dictionary: Dictionary to access
        key: Key to look up in the dictionary
        
    Returns:
        The value associated with the key, or None if key doesn't exist
    """
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter(name='get_attr')
def get_attr(obj, attr_name):
    """
    Get an attribute from an object dynamically.
    
    Usage in template:
        {{ obj|get_attr:"attribute_name" }}
    
    Args:
        obj: Object to get attribute from
        attr_name: Name of the attribute
        
    Returns:
        The attribute value, or None if attribute doesn't exist
    """
    try:
        return getattr(obj, attr_name, None)
    except (AttributeError, TypeError):
        return None


@register.filter(name='replace')
def replace(value, args):
    """
    Replace occurrences of a substring in a string.
    
    Usage in template:
        {{ text|replace:"old:new" }}
        {{ url|replace:"watch?v=:embed/" }}
    
    Args:
        value: The string to perform replacement on
        args: Colon-separated old:new values
        
    Returns:
        String with replacements made
    """
    if not value:
        return value
    
    try:
        # Split the argument into old and new strings
        old, new = args.split(':', 1)
        return str(value).replace(old, new)
    except (ValueError, AttributeError):
        return value


@register.filter(name='youtube_embed')
def youtube_embed(url):
    """
    Convert a YouTube URL to an embeddable format.
    
    Usage in template:
        {{ video_url|youtube_embed }}
    
    Handles:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - Already embedded URLs (returns as-is)
    
    Args:
        url: YouTube URL string
        
    Returns:
        Embeddable YouTube URL
    """
    if not url:
        return url
    
    url = str(url)
    
    # Already an embed URL
    if 'youtube.com/embed/' in url:
        return url
    
    # Convert watch URL to embed
    if 'youtube.com/watch?v=' in url:
        return url.replace('watch?v=', 'embed/')
    
    # Convert youtu.be short URL to embed
    if 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[-1].split('?')[0].split('&')[0]
        return f'https://www.youtube.com/embed/{video_id}'
    
    return url
