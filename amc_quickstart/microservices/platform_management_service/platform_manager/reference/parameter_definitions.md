```md

* ENV [str] = `The environment set in the ddk.json file (default is 'dev').`

* TEAM_NAME [str] = `The name set in data_pipeline_parameters of the ddk.json file (default is 'demoteam').`

* customerId [str] = `Unique identifier for the customer.`

* customerName [str] = `Reference customer name.`

* customerPrefix [str] = `Prefix to associate the customer with. Customers with the same prefix that run a common workflow will have data stored in the same table (table = {customerPrefix}-{WorkflowId}). This can also be used to synchronize workflows between customers in the Workflow Library.`

* endemicType [str] = `Either 'ENDEMIC' or 'NONDEMIC'. ENDEMIC: brands that sell on Amazon, NONDEMIC: brands that do not sell on Amazon. This can be used to synchronize workflows between customers in the Workflow Library.`

* amcDatasetName [str] = `The dataset set in data_pipeline_parameters of the ddk.json file (default is 'amcdataset').`

* amcApiEndpoint [str] = `The API endpoint URL associated with the given AMC instance.`

* amcOrangeAwsAccount [str] = `The data upload account associated with the given AMC instance.`

* amcS3BucketName [str] = `The S3 bucket name assocaited with the given AMC instance.`

* workflowId [str] = `Unique identifier for the workflow.`

* sqlQuery [str] = `SQL query to run when the workflow is invoked.`

* filteredMetricsDiscriminatorColumn [str] = `If provided, rows which do not meet the minimum distinct user count requirements will have values removed and then the output will be re-aggregated with AggregationType.SUM. The value provided will return as the additional column name.`

* distinctUserCountColumn [str] = `If provided, the count of distinct users considered by AMC’s privacy mechanisms will be returned. The value provided will return as the additional column name.`

* filteredReasonColumn [str] = `If provided, an additional column with this name will be included in the workflow output, that will contain a description of the reason why that data was filtered out of the row for privacy reasons, and null if no data was filtered out of the row.`

* timeWindowEnd [str] = `End Date of the report. E.g. today(-1) will set the end time to be 1 day back from current time.`

* timeWindowStart [str] = `Start date of the report. E.g today(-15) will set the start time to be 15 days back from current time.`

* timeWindowType [str] = `The type of time window to use to for specifying input data for the workflow execution. If not provided, the time window type of MOST_RECENT_DAY will be used.`
    `E.g`
        `EXPLICIT: The start and end of the time window must be explicitly provided in the request.`
        `MOST_RECENT_DAY: The time window will be the most recent 1-day window for which the instance is likely to have data, aligned to day boundaries.`
        `MOST_RECENT_WEEK: The time window will be the most recent 1-week window for which the instance is likely to have data, aligned to day boundaries.`
        `CURRENT_MONTH: The time window will be the start of the current month up to the most recent time for which the instance is likely to have data.`
        `PREVIOUS_MONTH: The time window will be the entire previous month.`

* workflowExecutedDate [str] = `E.g. now() will execute the workflow immediately when invoked.`

* ignoreDataGaps [bool] = `When enabled this setting allows queries to run over data gaps. Set to False as default.`

* state [str] = `Either 'ENABLED' or 'DISABLED' to set whether schedule is active.`

* scheduleExpression [str]= `Schedule that the workflow should be run on. Format is 'custom({H/D/W/M} {Day of the week/month} {Hour of the day})'.`
    `E.g.`
        `custom(H * *) will be run every hour.`
        `custom(W 2 8) will be run weekly, on the 2nd day of the week, between 8:00 and 8:59 UTC.`
        `custom(D * 14) will be run daily, between 14:00 and 14:59 UTC.`
        `custom(M 15 2) will be run monthly, on the 15th day of the month, between 2:00 and 2:59 UTC.`

```


