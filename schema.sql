CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
    username TEXT,
    password TEXT,
    role INT
);

CREATE TABLE IF NOT EXISTS courses(
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER REFERENCES users,
    name TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS course_students(
    course_id INT REFERENCES courses,
    student_id INT REFERENCES users,
    UNIQUE (course_id, student_id)
);