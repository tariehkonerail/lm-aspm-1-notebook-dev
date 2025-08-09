SELECT scsla.id AS "shipperContractSlaId"
-- scsla.shippercontractid
-- IF(sc.organizationId='c98b6217-8ace-49eb-b812-8b892ea1f8f5', TRUE, FALSE) as time_limited
FROM
shippercontractslas scsla
INNER JOIN shippercontracts sc on scsla.shipperContractId = sc.id

AND (
        (sc.organizationId IN ('260bc6c9-3c9a-4ac4-9561-2ebeb82a8b88', -- tbc
                        'f0e32bc1-316a-446c-8b5e-a9c62b046539', -- atd
                        '39334c55-8827-4388-82e5-87ff25989139', -- signet
                        'c98b6217-8ace-49eb-b812-8b892ea1f8f5' -- Lowe's
                    )
             AND
                (scsla.active = 1
                     OR (scsla.UPDATEDAT BETWEEN '%%da.createdAt.start%%' AND '%%da.createdAt.end%%')
                    )
            )
                    OR scsla.id IN (
                        -- aap
                        'f630a98a-b6ff-4713-bea2-168afae050d6',
                        'ea74019f-b735-4d53-a9db-d89aafb2b0d4'
                    )
            )
INNER JOIN servicelevels sl on scsla.serviceLevelId = sl.id