from django import template

register = template.Library()


@register.filter
def format_duration(seconds):
    if not seconds:
        return '—'
    total = int(float(seconds))
    return f'{total // 60}:{total % 60:02d}'


@register.filter
def initials(name):
    parts = str(name).split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return parts[0][0].upper() if parts else '?'


@register.filter
def genre_icon(genre):
    return {
        'POP': '🎤', 'ROCK': '🎸', 'JAZZ': '🎷',
        'CLASSICAL': '🎹', 'HIP_HOP': '🎧', 'OTHER': '🎵',
    }.get(genre, '🎵')


@register.filter
def genre_art_class(genre):
    return {
        'POP': 'art-pink', 'ROCK': 'art-teal', 'JAZZ': 'art-amber',
        'CLASSICAL': 'art-purple', 'HIP_HOP': 'art-pink', 'OTHER': 'art-purple',
    }.get(genre, 'art-purple')
