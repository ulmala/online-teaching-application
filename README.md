# Online teaching application

This application can be used to arrange online courses. Courses contains learning material and automatically checked tasks. Every user is either teacher or student. Application is used via web browser.

Application features:
* User can log in and out and create new account.
* Student can view all courses and join them
* Student can read course material and solve tasks
* Student can view statistics about which course's tasks he has solved
* Teacher can create new course, modify existing one and remove course
* Teacher can add learning material and tasks for the course. Task can be multiple choice or open task where student needs to type the correct answer
* Teacher can view statistics of his course; which students are participating and which tasks they had solved.


## Status 26.9.2021
Implemented features:
* User can log in and out and create new account (user is teacher or student)
* Teacher can create new course and remove it (only teacher who created the course can remove it)
* Teacher can add tasks to courses (currently only open type tasks)
* Student can view all courses available and join them
* Student can solve course tasks and see overall status how many course tasks he has succesfully solved

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