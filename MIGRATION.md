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
* `config`
* UniqueConstraint has been added for (thing_type and thing_id)
* the config field is currently important for the transition phase, since some configs are still being stored in the DB
    from the frontend side. This field should be removed in the future and configs will be directly reflected in the
    data object.

## `comparison_responses` Table

* Completely removed.
* `response_hash` and `save_response` parameters from the comparison service removed.
* Instead, `POST and GET /thing` will be used for saving and fetching a published
    comparison. The `thing_key` will have the value of resource_id for published ones and
    the response_hash/uuid/short_link for unpublished ones for backward compatibility.
    Frontend team will disable the share link feature in the future.
* `GET /thing/export` is also provided to export different things based on their type and the desired format.


## Other
* The `Review` service is not a stand-alone service anymore. It's simply an XML export functionality for
    the `ThingType.REVIEW`.
* `snake_case` convention applies everywhere, especially in JSON field names in the DB.
