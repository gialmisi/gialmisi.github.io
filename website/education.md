---
hide:
 - navigation
---
## Education
{% for edu in load_data_for('education.yaml', 'website')['educations'] %}
### {{ edu.degree }}
*{{ edu.institution }} ({{ edu.year }})*<br>
[Link to thesis]({{ edu.url }})<br>
>{{ edu.details }}
{% endfor %}

## Teaching
{% for teaching in load_data_for('teaching.yaml', 'website')['teachings'] %}
### {{ teaching.course }}
*{{ teaching.position }}, {{ teaching.institution }}, {{ teaching.period }}*<br>
>{{ teaching.details }}<br>
{% endfor %}