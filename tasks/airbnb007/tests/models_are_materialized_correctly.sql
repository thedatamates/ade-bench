{% set fct_reviews = graph.nodes["model." ~ project_name ~ "." ~ "fct_reviews"] %}
{% set fct_reviews_mat = fct_reviews.config.materialized %}

{% set dim_hosts = graph.nodes["model." ~ project_name ~ "." ~ "dim_hosts"] %}
{% set dim_hosts_mat = dim_hosts.config.materialized %}

{% set dim_listings = graph.nodes["model." ~ project_name ~ "." ~ "dim_listings"] %}
{% set dim_listings_mat = dim_listings.config.materialized %}

{% set dim_listings_hosts = graph.nodes["model." ~ project_name ~ "." ~ "dim_listings_hosts"] %}
{% set dim_listings_hosts_mat = dim_listings_hosts.config.materialized %}

{% set daily_agg_nps_reviews = graph.nodes["model." ~ project_name ~ "." ~ "daily_agg_nps_reviews"] %}
{% set daily_agg_nps_reviews_mat = daily_agg_nps_reviews.config.materialized %}

{% set listing_agg_nps_reviews = graph.nodes["model." ~ project_name ~ "." ~ "listing_agg_nps_reviews"] %}
{% set listing_agg_nps_reviews_mat = listing_agg_nps_reviews.config.materialized %}


{% if fct_reviews_mat != 'incremental' %}
    select 'fct_views is not incremental' as error_message

{% elif daily_agg_nps_reviews_mat != 'table' %}
    select 'daily_agg_nps_reviews is not a table' as error_message
{% elif dim_hosts_mat != 'table' %}
    select 'dim_hosts is not a table' as error_message
{% elif dim_listings_mat != 'table' %}
    select 'dim_listings is not a table' as error_message
{% elif dim_listings_hosts_mat != 'table' %}
    select 'dim_listings_hosts is not a table' as error_message
{% elif listing_agg_nps_reviews_mat != 'table' %}
    select 'listing_agg_nps_reviews is not a table' as error_message
{% else %}
    select 1 where false
{% endif %}