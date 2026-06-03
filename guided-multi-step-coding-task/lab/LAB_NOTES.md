1. When i gave following prompt to the agent after it implemented all four end points, agent only updated the error code and body for only put and post end points as mentioned in the prompt instead of applying that change to all the 4 end points [GET/POST/PUT/DELETE]


2. I reverted all the changes agent made in all the steps and asked agent to implement features step by step again but this time i asked it implment GET/POST in one step and PUT/DELETE in another step. so it did first implmented GET/POST  and then i gave following prompt before implenting the PUT/DELETE then agent gave a response saying it already included followingr equirements changes , probably becuase it already has this change in memory from the previous implementation.

   " Change the validation: instead of returning 400 for an invalid
    status,
    reject with 422 and include the list of valid statuses in the
    error body.
    Apply this to both POST and PUT."

    Note : Try this again by clearing the agent memory and see how agent responds and adjust the plan

3. Upon comparing the summary and the actual implementation i found one discrepancy which is, when i try to update a task status by provding invalid filed tile like below i still got 200 but this should validated , this is happening probably because under the validation rules we explicitly mentioned about checking values of the status filed and checkin whether a task is existed or not and did not talked about validting the field names also, and agent is claiing all the validations are added but this validation clearly not added becuase from agent pov this validaiton was not explicitly documeted in the feature_breif.md file 

"curl -X PUT http://localhost:5000/tasks/4 -H "Content-Type: application/json" -d "{\"status1\": \"done4\"}""