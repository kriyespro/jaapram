from django.templatetags.static import static
from django.urls import reverse, NoReverseMatch
from jinja2 import Environment
from datetime import datetime
from django.template.defaultfilters import date as django_date


def environment(**options):
    env = Environment(**options)

    # Enhanced URL reverser
    def url_reverse(view_name, *args, **kwargs):
        # Try with args first
        try:
            return reverse(view_name, args=args)
        except NoReverseMatch:
            # If that fails, try with kwargs
            try:
                return reverse(view_name, kwargs=kwargs)
            except NoReverseMatch:
                # If both fail but we have one positional arg and it's named in URL
                # Try to convert to kwargs based on the URL pattern
                if len(args) == 1 and not kwargs:
                    try:
                        # Common parameter names for IDs
                        for param_name in ['id', 'pk', f"{view_name.split(':')[-1]}_id"]:
                            try:
                                return reverse(view_name, kwargs={param_name: args[0]})
                            except NoReverseMatch:
                                continue
                    except Exception:
                        pass
                # If all approaches fail, raise the original error
                raise
    
    env.globals.update({
        'static': static,  # ManifestStaticFilesStorage already content-hashes URLs in prod
        'url': url_reverse,  # Use our enhanced reverser
        'now': datetime.now,
        'hasattr': hasattr,  # Add Python's built-in hasattr function
    })
    
    # Add filters
    env.filters['date'] = django_date
    
    return env 