--List the top 20 regions by percentage share of total reservations booked between 2020-01-01 and 2020-06-30 (be sure to include each region’s share)
SELECT DISTINCT region_id,
                CAST(COUNT(*) OVER (PARTITION BY region_id) AS FLOAT) / COUNT(*) OVER () AS percent_total_reservations
FROM search_request
JOIN reservation r ON search_request.id = r.search_request_id
WHERE r.date_created BETWEEN '2020-01-01' AND '2020-06-30'
ORDER BY percent_total_reservations DESC
LIMIT 20;

--List all hotels with at least 500 non-cancelled room-nights checked out between 2020-01-01 and 2020-06-30 
SELECT reservation.hotel_id
FROM reservation
JOIN search_request sr ON reservation.search_request_id = sr.id
WHERE sr.check_out BETWEEN '2020-01-01' AND '2020-06-30'
  AND reservation.date_cancelled IS NULL
GROUP BY hotel_id
HAVING SUM(DATE_PART('DAY', sr.check_out - sr.check_in)) >= 500;

--For each week between 2020-01-01 and 2020-06-30, list the percentage breakdown of bookings made by repeat customers vs. first-time customers w/ promotion vs. first-time customers w/o promotion 
WITH user_reservation_lookup AS
  (SELECT reservation.date_created,
          user_id,
          LAG(reservation.date_created) OVER (PARTITION BY user_id
                                              ORDER BY reservation.date_created ASC) AS previous_reservation_date,
                                             reward_program_id
   FROM reservation
   JOIN search_request sr ON reservation.search_request_id = sr.id),
     user_type_by_week AS
  (SELECT CASE
              WHEN previous_reservation_date IS NOT NULL THEN 'returning'
              WHEN reward_program_id IS NULL THEN 'first_time_without_promotion'
              ELSE 'first_time_with_promotion'
          END AS customer_type,
          EXTRACT('week'
                  FROM date_created::date - cast(date_part('day', DATE('2020-01-01') - DATE_TRUNC('week', DATE('2020-01-01'))) AS int)) AS week_counter
   FROM user_reservation_lookup
   WHERE date_created BETWEEN '2020-01-01' AND '2020-06-30' ),
     customer_count_by_week AS
  (SELECT week_counter,
          customer_type,
          count(customer_type) customer_type_count
   FROM user_type_by_week
   GROUP BY week_counter,
            customer_type),
     percent_by_week AS
  (SELECT week_counter,
          customer_type,
          (CAST (customer_type_count AS decimal) / SUM(customer_type_count) OVER (PARTITION BY week_counter) * 100) percent_breakdown,
          row_number() OVER (PARTITION BY customer_type) rn
   FROM customer_count_by_week
   ORDER BY week_counter),
     percent_columns AS
  (SELECT week_counter,
          max(CASE
                  WHEN customer_type = 'returning' THEN percent_breakdown
                  ELSE 0
              END) AS returning_customer_percent,
          max(CASE
                  WHEN customer_type = 'first_time_without_promotion' THEN percent_breakdown
                  ELSE 0
              END) first_time_without_promotion_percent,
          max(CASE
                  WHEN customer_type = 'first_time_with_promotion' THEN percent_breakdown
                  ELSE 0
              END) first_time_with_promotion_percent
   FROM percent_by_week
   GROUP BY week_counter),
     week_series AS
  (SELECT week_start,
          row_number() OVER () rn
   FROM
     (SELECT generate_series('2020-01-01'::date, '2020-06-30'::date, '1 week') week_start)t)
SELECT week_start,
       COALESCE(first_time_with_promotion_percent, 0) first_time_with_promotion_percent,
       COALESCE(first_time_without_promotion_percent, 0) first_time_without_promotion_percent,
       COALESCE(returning_customer_percent, 0) returning_customer_percent
FROM percent_columns
RIGHT JOIN week_series ON percent_columns.week_counter = rn;

--For reward_program_ids 5, 35 , list their respective top 3 regions by total number of reservations made between 2020-01-01 and 2020-06-30
WITH t AS
  (SELECT sr.reward_program_id,
          sr.region_id,
          count(region_id) AS region_count
   FROM search_request sr
   JOIN reservation r ON sr.id = r.search_request_id
   WHERE r.date_created BETWEEN '2020-01-01' AND '2020-06-30'
   GROUP BY sr.reward_program_id,
            region_id),
     rankings AS
  (SELECT t.reward_program_id,
          t.region_id,
          ROW_NUMBER() OVER (PARTITION BY t.reward_program_id
                             ORDER BY region_count DESC) AS rn
   FROM t
   WHERE t.reward_program_id in (5,
                                 35) )
SELECT reward_program_id,
       region_id
FROM rankings
WHERE rankings.rn < 3;

