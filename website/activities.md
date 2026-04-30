---
hide:
 - navigation
---
# Activities and Rewards
## Positions
{% for position in load_data_for('activities.yaml', 'website')['positions'] %}
### {{ position.position }}
{{ position.organization }}, {{ position.period }}{% if position.details %}
>{{ position.details }}{% endif %}
{% endfor %}

## Rewards and Nominations
{% for reward in load_data_for('activities.yaml', 'website')['rewards'] %}
### {{ reward.name }}
{{ reward.organization }}, {{ reward.date }}<br>
>{{ reward.details }}
{% endfor %}

## Grants
{% for funding in load_data_for('activities.yaml', 'website')['fundings'] %}
### {{ funding.name }}
{{ funding.organization }}, {{ funding.date }}<br>
>{{ funding.details }}
{% endfor %}

## Conference Organizing
{% for conf in load_data_for('activities.yaml', 'website')['conferences_organized'] %}
### {{ conf.name }}
{{ conf.role }}, {{ conf.organization }}, {{ conf.date }}{% if conf.details %}<br>
>{{ conf.details }}{% endif %}
{% endfor %}

## Editorial and Review Committees
{% for er in load_data_for('activities.yaml', 'website')['editorial_roles'] %}
### {{ er.role }}
{{ er.organization }}, {{ er.period }}{% if er.details %}<br>
>{{ er.details }}{% endif %}
{% endfor %}

## Peer Review for Scientific Journals
{% for pr in load_data_for('activities.yaml', 'website')['peer_reviews'] %}
- *{{ pr.journal }}*: {{ pr.summary }}
{% endfor %}
