# Online teaching application

This application can be used to arrange online courses. Courses contains learning material and automatically checked tasks. Every user is either teacher or student. Application is used via web browser.

Application features:
-  User can:
    - [x] log in
    - [x] log out
    - [x] create new account
- Student can:
    - [x] view all courses
    - [x] join course
    - [x] solve tasks
    - [ ] read course material
    - [ ] view statistics of which tasks he has solved
- Teacher can:
    - [x] create new course
    - [ ] modify existing course
    - [x] remove course
    - [ ] add learning material for course
    - [x] add open tasks for course
    - [ ] add multiple choice tasks for course
    - [x] view enrolled students
    - [ ] view statistics which tasks they had solved

Application can be found [here](https://onlinte-teaching-application.herokuapp.com/)  

To test the application:
1. Create new user with teacher role and login
2. Create new course; give name and short description
3. Create few tasks for the course (**remember correct answers so you can test those**)
4. Log out teacher
5. Create new user with student role and login
6. See all courses available and enroll the course you previously created
7. Go to course page and start solving tasks
    * You can check your progress from the course site any time
8. Log out student when you have tested everything
9. Login with teacher and remove the course you previously did. Course is not visible anymore. Log out
10. Login in with student so you can see that the removed course is not visible on your list of enrolled courses.