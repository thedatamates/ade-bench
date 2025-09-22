WITH date_series AS (
    SELECT
        DATEADD(
            day,
            ROW_NUMBER() OVER (ORDER BY SEQ4()) - 1,
            DATE('2014-01-01')
        ) AS d
    FROM TABLE(GENERATOR(ROWCOUNT => 13500))  -- enough rows to reach 2050-01-01
)
SELECT
    TO_CHAR(d, 'YYYY-MM-DD') AS id,            -- Format date as 'YYYY-MM-DD'
    d AS full_date,                            -- Full date
    EXTRACT(YEAR FROM d) AS year,              -- Year
    EXTRACT(WEEK FROM d) AS year_week,         -- Week of year (1–53)
    DAYOFYEAR(d) AS year_day,                  -- Day of year (1–366)
    EXTRACT(YEAR FROM d) AS fiscal_year,       -- Fiscal year (same as year here)
    CEIL(EXTRACT(MONTH FROM d) / 3) AS fiscal_qtr, -- Fiscal quarter
    EXTRACT(MONTH FROM d) AS month,            -- Month number
    TO_CHAR(d, 'MMMM') AS month_name,          -- Month name
    DAYOFWEEK(d) AS week_day,                  -- Day of week (1=Sunday)
    DAYNAME(d) AS day_name,                    -- Day name
    CASE WHEN DAYOFWEEK(d) IN (0,6) THEN 0 ELSE 1 END AS day_is_weekday -- 0=weekend, 1=weekday
FROM date_series