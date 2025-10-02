{{
	config(
		materialized="table" ,
		alias="dim_dates" ,
		schema="public" ,
		unique_key="date_id"
	)
}}

SELECT
    TO_CHAR(datum, 'YYYYMMDD')::INTEGER                                   AS date_id,
    datum                                                                 AS date_actual,
    DATEDIFF('second', TO_TIMESTAMP_NTZ('1970-01-01'), datum::timestamp)  AS epoch,

    TO_CHAR(datum, 'DD') ||
      CASE TO_CHAR(datum, 'DD')
        WHEN '01' THEN 'st'
        WHEN '02' THEN 'nd'
        WHEN '03' THEN 'rd'
        ELSE 'th'
      END                                                                 AS day_suffix,

    TRIM(TO_CHAR(datum, 'Day'))                                           AS day_name,
    DAYOFWEEKISO(datum)                                                   AS day_of_week,
    DATE_PART('day', datum)                                               AS day_of_month,
    DATEDIFF('day', DATE_TRUNC('quarter', datum), datum) + 1              AS day_of_quarter,
    DATE_PART('doy', datum)                                               AS day_of_year,
    (DATE_PART('WEEK', datum) - DATE_PART('WEEK', DATE_TRUNC('MONTH', datum)) + 1)
                                                                          AS week_of_month,

    WEEKOFYEAR(datum)                                                     AS week_of_year,
    TO_CHAR(datum, 'YYYY') || '-W' || LPAD(WEEKOFYEAR(datum),2,'0') || '-' ||
      DAYOFWEEKISO(datum)                                                 AS week_of_year_iso,

    DATE_PART('month', datum)                                             AS month_actual,
    TRIM(TO_CHAR(datum, 'Month'))                                         AS month_name,
    TRIM(TO_CHAR(datum, 'Mon'))                                           AS month_name_abbreviated,

    DATE_PART('quarter', datum)                                           AS quarter_actual,
    CASE DATE_PART('quarter', datum)
      WHEN 1 THEN 'First'
      WHEN 2 THEN 'Second'
      WHEN 3 THEN 'Third'
      WHEN 4 THEN 'Fourth'
    END                                                                   AS quarter_name,

    DATE_PART('year', datum)                                              AS year_actual,

    DATEADD(day, 1 - DAYOFWEEKISO(datum), datum)                          AS first_day_of_week,
    DATEADD(day, 7 - DAYOFWEEKISO(datum), datum)                          AS last_day_of_week,

    DATE_TRUNC('month', datum)                                            AS first_day_of_month,
    LAST_DAY(datum, 'month')                                              AS last_day_of_month,

    DATE_TRUNC('year', datum)                                             AS first_day_of_year,
    LAST_DAY(datum, 'year')                                               AS last_day_of_year,

    TO_CHAR(datum, 'MMYYYY')                                              AS mmyyyy,
    TO_CHAR(datum, 'MMDDYYYY')                                            AS mmddyyyy,

    CASE WHEN DAYOFWEEKISO(datum) IN (6, 7) THEN TRUE ELSE FALSE END      AS weekend_indr
FROM (
  SELECT DATEADD(day, SEQ4(), DATE '1970-01-01') AS datum
  FROM TABLE(GENERATOR(ROWCOUNT => 29220))
) dq
ORDER BY 1
