---
hide:
 - navigation
---

# Research Experience

## Research Positions
{% for position in load_data('research.yaml')['positions'] %}
### {{ position.organization }}
*{{ position.position }}, {{ position.period }}*<br>
>{{ position.details }}<br>
{% endfor %}

## Research Visits
{% for visit in load_data('research.yaml')['visits'] %}
### {{ visit.institution }}
*{{ visit.location }}, {{ visit.period }}*<br>
>{{ visit.details }}<br>
{% endfor %}

## Research Projects
{% for project in load_data('research.yaml')['projects'] %}
### {{ project.name }}
*{{ project.organization }}, {{ project.period }}{% if project.id %}, project id: {{ project.id }} {% endif %}*<br>
>{{ project.details }}<br>
{% endfor %}
