---
hide:
 - navigation
---
# Publications
{% for publication in load_data('publications.yaml')['publications'] %}
### {{ publication.title }}
*{{ publication.authors }}*<br>
{{ publication.journal }}, {{ publication.year }}.<br>
{% if publication.doi %}[DOI]({{ publication.doi }}){% else %}[URI]({{ publication.uri }}){% endif %}{% if publication.open_access %} | [open-access]({{ publication.open_access }}){% if publication.open_access_note %} ({{ publication.open_access_note }}){% endif %}{% endif %}
{% endfor %}