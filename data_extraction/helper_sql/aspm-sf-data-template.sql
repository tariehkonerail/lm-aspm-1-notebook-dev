-- DATA-SCI ASPM1
WITH filtered_deliveries AS (
  SELECT *,
         TIMESTAMPADD(
           MINUTE,
           FLOOR(DATE_PART('MINUTE', delivery_created_at) / 10) * 10,
           DATE_TRUNC('HOUR', delivery_created_at)
         ) AS bucket_time
  FROM DT_DELIVERIES
  WHERE
    network_type = 'OneRail'
    AND delivery_created_at BETWEEN '%%da.createdAt.start%%' AND '%%da.createdAt.end%%'
    AND shipper_contract_sla_id = '%%scsla.id%%'
),

joined_deliveries AS (
  SELECT
    vwd.delivery_id,
    vwd.delivery_created_at,
    vwd.shipper_cost,
    vwd.bucket_time,
    vwd.shipper_contract_sla_id,
    vwd.delivery_start,
    vwd.dwshippingmodeid
  FROM filtered_deliveries vwd
),

ranked_deliveries AS (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY shipper_contract_sla_id, bucket_time
           ORDER BY RANDOM()
         ) AS row_num
  FROM joined_deliveries
),

sampled_deliveries AS (
  SELECT *
  FROM ranked_deliveries
  WHERE row_num <= %%sample_rate%%
  LIMIT %%da.limit%%
)

SELECT
  dat.delivery_id AS "deliveryId",
  dat.delivery_attempt_id AS "attemptId",
  DIMLP.lporgid AS "lpOrganizationId",
  dat.attempt_number AS "attemptNumber",
  dimds.deliverystatus AS "deliveryStatus",
  dimas.attemptstatus AS "attemptStatus",
  swd.shipper_cost AS "shipperCost",
  DIMSL.SERVICELEVEL  AS "serviceLevel",
--   dat.lp_cost_core AS "lpCost",
  swd.delivery_created_at AS "dispatchedOn",
--   swd.delivery_start AS "startedAt",
  dat.miles AS "distanceMi",
  dat.items_weight_lbs AS "weightLbsTotal",
  dat.items_max_weight_lbs AS "largestWeightLbs",
  dat.items_cubic_inches AS "sizeCuInTotal",
  dat.longest_dimension AS "largestDimIn",
  dat.second_longest_dimension AS "secondDimIn",
  dat.third_longest_dimension AS "thirdDimIn",
  dat.items_quantity AS "itemCount",
  fromLoc.latitude AS "fromLat",
  fromLoc.LONGITUDE AS "fromLon",
  toLoc.LATITUDE AS "toLat",
  toLoc.LONGITUDE AS "toLon",
  fromLoc.STATECODE AS "stateCode",
  dat.network_type,
  dat.shipper_contract_sla_id
FROM DT_ATTEMPTS dat
INNER JOIN DIM_DELIVERYSTATUS dimds ON dat.dwdeliverystatusid = dimds.dwdeliverystatusid
INNER JOIN DIM_LOGISTICPARTNER dimlp ON dat.dwlporgid = dimlp.dwlporgid
INNER JOIN sampled_deliveries swd ON dat.delivery_id = swd.delivery_id
INNER JOIN DIM_ATTEMPTSTATUS dimas ON dat.dwattemptstatusid = dimas.dwattemptstatusid
INNER JOIN DIM_SHIPPINGMODE dimsm ON swd.dwshippingmodeid = dimsm.dwshippingmodeid
INNER JOIN DIM_SERVICELEVEL DIMSL ON dat.DWSERVICELEVELID = DIMSL.DWSERVICELEVELID
INNER JOIN vw_locations fromloc on dat.from_id = fromLoc.id
INNER JOIN vw_locations toLoc on dat.to_id = toLoc.id
WHERE dimas.attemptstatus IN (
    'DELIVERED', 'DISPATCH_ERROR', 'CANCELED_BY_LP',
    'REVOKED_BY_ONERAIL'
)
AND dimsm.shippingModeId <> '69f9e2af-93ef-11ec-886a-f12e12cfdad6' -- Exclude parcel
-- LIMIT 5000;