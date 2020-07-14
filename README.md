# es-success-handler
Module is called during the Imputation step function if for some reason there is an error in one of the modules. It will send an sns message with a summary of error information.

### Parameters
run_id: The id of the current run - Type: String<br>
