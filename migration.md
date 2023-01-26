# Notes to Data Migration

We here document the database changes we need to consider while migration from the 
**recent** [`orkg-similarity`](https://gitlab.com/TIBHannover/orkg/orkg-similarity) app
to the **current** [`orkg-simcomp-api`](https://gitlab.com/TIBHannover/orkg/orkg-simcomp/orkg-simcomp-api)
one.

## `links` Table

### Recent
* `long_url`
* `short_code`
* `contributions`
* `properties`
* `transpose`
* `json_code`
* `response_hash`

### Current
* `long_url`
* `short_code`

## `visualization_models` Table

### Recent
* `resource_id`
* `data`

### Current renamed to `things`
* `thing_type`
* `thing_id`
* `data`
* UniqueConstraint has been added for (thing_type and thing_id)