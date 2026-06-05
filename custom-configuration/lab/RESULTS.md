## Run 1: Baseline run with no config

### Task 1
- Output summary:

  Prompt: Add a `GET /api/users` endpoint to the backend that returns all users as JSON. Follow the conventions of the existing endpoints.  
- Evaluation:

    - Did Copilot use Flask (matching the codebase) or propose another framework?
        -> Implemented the backend collection endpoint and matching tests using the existing Flask blueprint conventions.

    - Did it match the naming conventions of the existing file?
        -> Yes, it followed the naming conventions
    - Did it add error handling, validation, or response shaping in line with the existing endpoint?
        -> it did not added error handling or validation. it did added test cases for positive scenarios only. It did followed response shaping in line with the existing endpoint
    - Did it touch files outside `backend/api/users.py`?
        -> Yes, it did. it added a new GET route for retriving all the users and updated test_users.py

### Task 2
- Output summary:

- Prompt : Write a pytest test for the `GET /api/users` endpoint. Follow the conventions of the existing tests.
- Evaluation:

    - Did Copilot use `pytest` fixtures, or did it import `unittest`?
        -> it used pytest
    - Did it match the file / function naming patterns of the existing tests?
        -> it matched the naming patterns of existing tests
    - Did it use the existing `client` fixture or invent its own?
        -> it used the existing client fixture

### Task 3
- Output summary:

- Prompt : Add an `is_active` boolean field to the User model that defaults to `True`. Propose how to implement this change across the codebase.
- Evaluation:

    - Did Copilot edit an existing migration file or propose a *new* migration?
        -> used created a new migration file
    - Did it update the model, the API serializer, and the tests?
        -> it updated user model and tests but not the api serializer
    - Did it flag the migration directory as append-only, or did it silently treat migrations as editable?
        -> it flagged directory as append-only



## Run 2: after copilot-instructions.md

### Task 1
- Output summary:

  Prompt: Add a `GET /api/users` endpoint to the backend that returns all users as JSON. Follow the conventions of the existing endpoints.  
- Evaluation:

    - Did Copilot use Flask (matching the codebase) or propose another framework?
        -> Implemented the backend collection endpoint using the existing Flask blueprint conventions.

    - Did it match the naming conventions of the existing file?
        -> Yes, it followed the naming conventions
    - Did it add error handling, validation, or response shaping in line with the existing endpoint?
        -> it did not added error handling or validation. It did followed response shaping in line with the existing endpoint
    - Did it touch files outside `backend/api/users.py`?
        ->  No, it only edited users.py file only

### Task 2
- Output summary:

- Prompt : Write a pytest test for the `GET /api/users` endpoint. Follow the conventions of the existing tests.
- Evaluation:

    - Did Copilot use `pytest` fixtures, or did it import `unittest`?
        -> it used pytest
    - Did it match the file / function naming patterns of the existing tests?
        -> it matched the naming patterns of existing tests
    - Did it use the existing `client` fixture or invent its own?
        -> it used the existing client fixture

### Task 3
- Output summary:

- Prompt : Add an `is_active` boolean field to the User model that defaults to `True`. Propose how to implement this change across the codebase.
- Evaluation:

    - Did Copilot edit an existing migration file or propose a *new* migration?
        -> No, it created new migration file
    - Did it update the model, the API serializer, and the tests?
        -> it updated user model and tests but not the api serializer
    - Did it flag the migration directory as append-only, or did it silently treat migrations as editable?
        -> it did not flaged migration directory as append-only now compared to previous run

### Overall delta vs previous run:

-> in task 1 it only modified users.py file , in previous it edited both test and source files
-> Not much changes in task 2
-> in task in previous run it flagged migration folder as append only but in this run it didn't , but compared to previous run this run layed out a clear plan and called out that it's reading the current file pattern and naming conventions before it's starting making changes.


## Run 3: after path-specific instructions

### Task 1
- Output summary:

  Prompt: Add a `GET /api/users` endpoint to the backend that returns all users as JSON. Follow the conventions of the existing endpoints.  
- Evaluation:

    - Did Copilot use Flask (matching the codebase) or propose another framework?
        -> Implemented the backend collection endpoint using the existing Flask blueprint conventions.

    - Did it match the naming conventions of the existing file?
        -> Yes, it followed the naming conventions
    - Did it add error handling, validation, or response shaping in line with the existing endpoint?
        -> it did not added error handling but added a test case to validate api response code nad body. It did followed response shaping in line with the existing endpoint
    - Did it touch files outside `backend/api/users.py`?
        ->  yes, it did. it edited test_users.py and added test cases for new route

### Task 2
- Output summary:

- Prompt : Write a pytest test for the `GET /api/users` endpoint. Follow the conventions of the existing tests.
- Evaluation:

    - Did Copilot use `pytest` fixtures, or did it import `unittest`?
        -> it used pytest
    - Did it match the file / function naming patterns of the existing tests?
        -> it matched the naming patterns of existing tests
    - Did it use the existing `client` fixture or invent its own?
        -> it used the existing client fixture

### Task 3
- Output summary:

- Prompt : Add an `is_active` boolean field to the User model that defaults to `True`. Propose how to implement this change across the codebase.
- Evaluation:

    - Did Copilot edit an existing migration file or propose a *new* migration?
        -> No, it created new migration file
    - Did it update the model, the API serializer, and the tests?
        -> it updated user model and tests but not the api serializer
    - Did it flag the migration directory as append-only, or did it silently treat migrations as editable?
        -> it did not flaged migration directory as append-only now compared to base run and added new migration file

### Overall delta vs previous run:

-> like base run and run3 it edited both test and source files
-> Not much changes in task 2
-> in task in base run it flagged migration folder as append only but in this run it didn't , but compared to previous run this run layed out a clear plan and called out that it's reading the current file pattern and naming conventions before it's starting making changes.


## Run 4:  after AGENTS.md


### Task 3
- Output summary:

- Prompt : Add an `is_active` boolean field to the User model that defaults to `True`. Propose how to implement this change across the codebase.
- Evaluation:

    - Did Copilot edit an existing migration file or propose a *new* migration?
        -> No, it created new migration file
    - Did it update the model, the API serializer, and the tests?
        -> it updated user model and tests but not the api serializer
    - Did it flag the migration directory as append-only, or did it silently treat migrations as editable?
        -> it did flagged migration directory as append-only now compared to previous run

### Overall delta vs previous run:

-> in this task run it flagged migration folder as append only and created new migration file


## Run 5:  after Content Exclusion

-> Did not much change between previous run and this run, probably because i did not applied any content exclusions in github ui, only thing i noticed is it marked .venv folder as autogenerated


## Run 6: after Agent Skill

### Task 1
- Output summary:

  Prompt: Add a `GET /api/users` endpoint to the backend that returns all users as JSON. Follow the conventions of the existing endpoints.  
- Evaluation:

    - Did Copilot use Flask (matching the codebase) or propose another framework?
        -> Implemented the backend collection endpoint using the existing Flask blueprint conventions.

    - Did it match the naming conventions of the existing file?
        -> Yes, it followed the naming conventions
    - Did it add error handling, validation, or response shaping in line with the existing endpoint?
        -> it did not added error handling but added a test case to validate api response code nad body. It did followed response shaping in line with the existing endpoint
    - Did it touch files outside `backend/api/users.py`?
        ->  yes, it did. it edited test_users.py and added test cases for new route

### Task 2
- Output summary:

- Prompt : Write a pytest test for the `GET /api/users` endpoint. Follow the conventions of the existing tests.
- Evaluation:

    - Did Copilot use `pytest` fixtures, or did it import `unittest`?
        -> it used pytest
    - Did it match the file / function naming patterns of the existing tests?
        -> it matched the naming patterns of existing tests
    - Did it use the existing `client` fixture or invent its own?
        -> it used the existing client fixture

### Task 3
- Output summary:

- Prompt : Add an `is_active` boolean field to the User model that defaults to `True`. Propose how to implement this change across the codebase.
- Evaluation:

    - Did Copilot edit an existing migration file or propose a *new* migration?
        -> No, it did not crated new migration file or modified existiing one. when i specifically asked about the need creating a new migration file , it replied following 

        for this current lab runtime, no migration is required to make the feature work.

Why:

The app is currently using an in-memory store in store.py:1, not a live database.
The new field is handled at the dataclass/model level, so behavior is already covered by code + tests.
If you want to follow the repository migration convention for completeness/future DB parity:

Create a new migration file (do not edit existing ones), e.g. 0003_add_is_active.py in migrations.
Mark it append-only, consistent with README.md:16.


    - Did it update the model, the API serializer, and the tests?
        -> it updated user model and tests but mentioned there is no seperate serializer 
    - Did it flag the migration directory as append-only, or did it silently treat migrations as editable?
        -> it did marked migration directory append only and explicitly called out don't make any chanegs to existed migration file and create a new migration file for the new use cases

### Overall delta vs previous run:

-> like base run and run3 it edited both test and source files, but this time it followed the instructions we provided in the skills folder, clearly see the difference in agent output
-> Not much changes in task 2 from previous runs, but this time one clear difference is that its first checking the existing test case pattern and matching convention when its creating new test cases
-> in task in base run it flagged migration folder as append only but in this run it didn't , but compared to previous run this run layed out a clear plan and called out that it's reading the current file pattern and naming conventions before it's starting making changes. clearly called out migration folder is append only and called out don't make any changes to existing files and create new files for new use cases


## Run 7: final verification

## Retrospective

-> Which configuration layer produced the largest quality improvement on which task?

    After adding files in skills folder produced better results across all three tasks, specifically in task 1

-> Which layer produced no observable change? What does that tell you about where to invest next time?

    Skills and agent layers produced a observable change in task 1 and task 3. It tells me to invest time into core functinoality of the app you are trying to develop and document the structure, format , what are the files/folders off limits to agents and patterns agent need to follow and where they can look for examples to establish patterns/namin conventions in the codebase. Spening time on these and writing them out upfront before we start asking agent to develop xyz functionality saves a lot of time refactoring 

-> Were there rules you wrote in one layer that would have been better in another (e.g., wrote a scope rule in copilot-instructions.md that belongs in AGENTS.md)?

    after first run i put a scope rule about migration folder in global copilot-instructions.md which did not do much and then moved that scope rule to agent.md file, after that i have sceen clar difference in agnent output calling out migration folder is append-only and editing existing files in that folder or offlimits  

-> How much of the improvement came from what you wrote vs. where you put it?

    Much of improvemnt came from Agent.md and skills file
